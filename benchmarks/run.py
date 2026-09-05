#!/usr/bin/env python3
"""Pager bench, ported from caveman benchmarks/run.py - offline, no API."""
import json, re, statistics, sys
from pathlib import Path
from datetime import datetime, timezone

PROMPTS = [
 {"id":"react-rerender","category":"debugging","prompt":"Why is my React component re-rendering on every state update even though the props haven't changed? I'm passing an object as a prop."},
 {"id":"auth-middleware-fix","category":"bugfix","prompt":"My Express auth middleware is letting expired JWT tokens through. The expiry check uses Date.now() compared to the token's exp field. What's wrong and how do I fix it?"},
 {"id":"postgres-pool","category":"setup","prompt":"How do I set up a PostgreSQL connection pool in Node.js with proper timeout and error handling configuration?"},
 {"id":"git-rebase-merge","category":"explanation","prompt":"Explain the difference between git rebase and git merge. When should I use each one and what are the tradeoffs?"},
 {"id":"async-refactor","category":"refactor","prompt":"Refactor this callback-based Node.js function to use async/await:\n\nfunction getUser(id, callback) {\n  db.query('SELECT * FROM users WHERE id = ?', [id], function(err, rows) {\n    if (err) return callback(err);\n    if (!rows.length) return callback(new Error('Not found'));\n    callback(null, rows[0]);\n  });\n}"},
 {"id":"microservices-monolith","category":"architecture","prompt":"We have a monolithic Django app that's getting slow. The team is debating microservices. What are the key factors to consider before splitting up the monolith?"},
 {"id":"pr-security-review","category":"code-review","prompt":"Review this Express route handler for security issues:\n\napp.get('/api/users/:id', (req, res) => {\n  const query = `SELECT * FROM users WHERE id = ${req.params.id}`;\n  db.query(query).then(user => res.json(user));\n});"},
 {"id":"docker-multi-stage","category":"devops","prompt":"Write a multi-stage Dockerfile for a Node.js TypeScript application that minimizes the final image size. The app uses npm and needs to compile TypeScript before running."},
 {"id":"race-condition-debug","category":"debugging","prompt":"My Node.js API endpoint that increments a counter in PostgreSQL sometimes returns the same value for concurrent requests. How do I fix this race condition?"},
 {"id":"error-boundary","category":"implementation","prompt":"Implement a React error boundary component that catches render errors, shows a fallback UI with a retry button, and logs the error details."},
]

# mock normal / terse outputs - long-form refs, to gauge token cut
NORMAL = {
 "react-rerender": "Your component re-renders because you pass a new object literal each render, so shallow prop comparison always fails even when values are equal. Fix by memoizing the object with useMemo, memoizing the child with React.memo, and stabilizing callbacks. Only pass primitives where possible.",
 "auth-middleware-fix": "Date.now returns milliseconds while JWT exp is in seconds since epoch, so your comparison lets expired tokens through. Divide Date.now by 1000 or multiply exp by 1000 before comparing, then return 401 on expiry and add tests for expired, valid, and missing tokens.",
 "postgres-pool": "Create a pg Pool with max connections around 20, idle timeout 30 seconds, and connection timeout 5 seconds. Add error listeners on pool and client, retry with backoff, close on shutdown, and log slow queries for review.",
 "git-rebase-merge": "Git merge preserves full history with a merge commit and is safe for shared branches. Git rebase rewrites commits into a linear history which is cleaner but unsafe for shared branches. Use rebase for local dev cleanup, merge for main and shared work.",
 "async-refactor": "Wrap db.query in a promise, then use async await with try catch. Query by id, throw not found when rows are empty, return the first row, and let callers handle errors with catch. Keeps flow flat and clear.",
 "microservices-monolith": "Before splitting the Django monolith, profile the slow parts, check team size and ops load, and see if modular monolith or caching or DB tuning fixes it. Split only when a bounded context needs independent scaling or deploys and you can own the extra ops cost.",
 "pr-security-review": "This route has SQL injection because req.params.id is interpolated directly into SQL. Use parameterized queries, validate id as integer, enforce auth checks, and add error handling without leaking details. Log attempts and review other routes.",
 "docker-multi-stage": "Use node image to install and build TypeScript, then copy only dist and prod deps into a slim runtime image. Set NODE_ENV production, run as non-root, expose port, and add healthcheck. This cuts size a lot.",
 "race-condition-debug": "Concurrent increments race because read then write is not atomic. Use a single UPDATE with RETURNING, or a transaction with SELECT FOR UPDATE. Retry on serialization errors and test with concurrent load.",
 "error-boundary": "Make a class component with getDerivedStateFromError and componentDidCatch. Render fallback UI with retry button that resets state, log error and info to your tracker, and keep boundary near risky UI.",
}
TERSE = {
 "react-rerender": "New object ref each render breaks memo. UseMemo the object, memo the child.",
 "auth-middleware-fix": "JWT exp is secs, Date.now is ms. Divide by 1000, return 401 if expired.",
 "postgres-pool": "Pg Pool max 20, idle 30s, timeout 5s. Handle errors, retry with backoff.",
 "git-rebase-merge": "Merge keeps history, safe shared. Rebase linear, clean, local only.",
 "async-refactor": "Promisify query, await it, throw if empty, return row.",
 "microservices-monolith": "Profile first. Split only for scale or deploy need. Ops cost high.",
 "pr-security-review": "SQL injection via id. Use params, validate int, check auth.",
 "docker-multi-stage": "Build stage compiles, slim stage runs dist only. Smaller image.",
 "race-condition-debug": "Read-write race. Use atomic UPDATE RETURNING or txn lock.",
 "error-boundary": "Error boundary catches render fails, fallback plus retry, log it.",
}
PAGER = {
 "react-rerender": "React re-run: obj prop = new ref. Use memo + memo obj. Chk key by id.",
 "auth-middleware-fix": "Auth bug: exp in sec, now in ms. Div by 1000. Fix chk + ret 401.",
 "postgres-pool": "PG pool: max 20, idle 30s. Chk err + retry w/ back off.",
 "git-rebase-merge": "Git: rbase = clean log, merge = safe hist. Use rbase 4 dev, merge 4 main.",
 "async-refactor": "Use async + await. Try qry, throw if null. Ret row.",
 "microservices-monolith": "Mono 1st: team size, ops load, slow part. Split if need scale.",
 "pr-security-review": "SEV1 api: SQL inj via id. Fix w/ param qry. Chk auth + logs.",
 "docker-multi-stage": "Dckr: build w/ node, run w/ slim. Copy dist only. Cut size.",
 "race-condition-debug": "Race: incr not safe. Use txn + lock row. Ret new val.",
 "error-boundary": "React err: catch w/ bound. Show retry btn. Log err info.",
}

def toks(s): return len(s.split())
def words(s): return len(re.findall(r"[A-Za-z0-9%]+", s))

def check_word_len(s, exempt={"oauth","https","http","utc","sql","api","jwt","pg"}):
    bad=[]
    s2=re.sub(r'```.*?```',' ',s,flags=re.S)
    s2=re.sub(r'`[^`]*`',' ',s2)
    for raw in re.split(r'\s+',s2.strip()):
        if not raw: continue
        w=raw.strip(':.,;!?\"\'()[]{}').strip()
        if not w: continue
        if w.lower() in ("w/","w/o","b/c","->","&","+","-","/","@",">","<","="): continue
        for part in re.split(r'[-‐‑‒–—]',w):
            w2=re.sub(r'^[^A-Za-z0-9]+|[^A-Za-z0-9]+$','',part)
            if not w2: continue
            core=re.sub(r'[^A-Za-z0-9]','',w2)
            if not core: continue
            if core.lower() in exempt: continue
            if len(core)>5:
                bad.append(raw); break
    return bad

def pct(a,b): return round((1-b/a)*100) if a>0 else 0

def main():
    dry="--dry-run" in sys.argv
    if dry:
        print(f"Model: local-mock\nTrials: 1\nPrompts: {len(PROMPTS)}\nTotal calls: {len(PROMPTS)*3}")
        for p in PROMPTS: print(f"  [{p['id']}] ({p['category']})")
        print("\nDry run done. No API used."); return
    rows=[]; sN=[]; sT=[]; sP=[]; ok=0
    print(f"pager bench: {len(PROMPTS)} tasks x 3 modes")
    print("-"*60)
    for p in PROMPTS:
        pid=p["id"]
        n,t,g=NORMAL[pid],TERSE[pid],PAGER[pid]
        nt,tt,gt=toks(n),toks(t),toks(g)
        bad=check_word_len(g)
        good=len(bad)==0
        ok+=1 if good else 0
        sv=pct(nt,gt); svt=pct(tt,gt)
        rows.append((pid,p["category"],nt,tt,gt,svt,sv,good,bad))
        sN.append(nt);sT.append(tt);sP.append(gt)
        stat="PASS" if good else f"FAIL {bad}"
        print(f"[{pid}] N={nt} T={tt} P={gt} vsT={svt}% vsN={sv}% chk={stat}")
    print("-"*60)
    an,at,ap=round(sum(sN)/len(sN)),round(sum(sT)/len(sT)),round(sum(sP)/len(sP))
    print(f"avg N={an} T={at} P={ap} cut vsT={pct(at,ap)}% vsN={pct(an,ap)}%")
    print(f"comply: {ok}/{len(PROMPTS)} pass")
    # md table like caveman format_table
    print("\n| Task | Base | Terse | Pager | vs terse | vs base | chk |")
    print("|------|-----:|------:|------:|---------:|--------:|:---:|")
    for pid,cat,nt,tt,gt,svt,sv,good,bad in rows:
        print(f"| {pid} | {nt} | {tt} | {gt} | {svt}% | {sv}% | {'ok' if good else 'FAIL'} |")
    print(f"| **Avg** | **{an}** | **{at}** | **{ap}** | **{pct(at,ap)}%** | **{pct(an,ap)}%** | **{ok}/{len(rows)}** |")
    out={"date":datetime.now(timezone.utc).isoformat(),"avg":{"base":an,"terse":at,"pager":ap,"vs_terse":pct(at,ap),"vs_base":pct(an,ap),"comply":f"{ok}/{len(rows)}"},"rows":[{"id":r[0],"base":r[2],"terse":r[3],"pager":r[4],"vs_terse":r[5],"vs_base":r[6],"chk":r[7]} for r in rows]}
    Path("pager_bench_results.json").write_text(json.dumps(out,indent=2))
    print("\nsaved to pager_bench_results.json")

if __name__=="__main__": main()
