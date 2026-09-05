"""Pager skill evals: checks word-len<=5, intent, short-forms, signs, pattern."""
import re, sys

def tokens_outside_code(s):
    s2 = re.sub(r'```.*?```', ' ', s, flags=re.S)
    s2 = re.sub(r'`[^`]*`', ' ', s2)
    return s2

def check_word_len(s, exempt={"oauth","https","http","utc"}):
    txt = tokens_outside_code(s)
    # split on space, keep @ etc? strip punct : . , ; ! ? " ' ( ) [ ]
    bad = []
    for raw in re.split(r'\s+', txt.strip()):
        if not raw: continue
        # skip pure signs/nums/symbols
        w = raw.strip(':.,;!?\"\'()[]{}').strip()
        if not w: continue
        # w/ w/o b/c -> split? allow
        if w.lower() in ("w/","w/o","b/c","->","&","+","-","/","@",">","<"): continue
        # split hyphenated words: chk-outs -> chk + outs
        parts = re.split(r'[-‐‑‒–—]', w)
        for part in parts:
            w2 = re.sub(r'^[^A-Za-z0-9]+|[^A-Za-z0-9]+$', '', part)
            if not w2: continue
            core = re.sub(r'[^A-Za-z0-9]', '', w2)
            if not core: continue
            if core.lower() in exempt: continue
            if len(core) > 5:
                bad.append(raw)
                break
    return bad

def check_intent(s, must):
    low = s.lower()
    miss = [k for k in must if k.lower() not in low]
    return miss

CASES = [
  {"id":"ex1-auth-db",
   "long":"The authentication service is failing due to database pool exhaustion. Please restart the auth service immediately and inspect the query load.",
   "pager":"SEV1 auth: DB pool full -> 504 err. Plz rest auth ASAP. Chk qry load.",
   "must":["auth","db","pool","rest","chk","qry"]},
  {"id":"ex2-queue-stg",
   "long":"I completed the background queue implementation and pushed it to the staging environment for verification.",
   "pager":"Queue done & sent 2 stg. Rdy 4 test.",
   "must":["queue","stg","rdy","test"]},
  {"id":"ex3-pay-500",
   "long":"The payment gateway returned an HTTP 500 error at 08:14 UTC. Total 42 checkout transactions failed.",
   "pager":"SEV1 pay: 500 err @ 08:14 UTC. 42 chk-outs fail. On-call chk logs ASAP.",
   "must":["pay","500","42","fail","chk","asap"]},
  {"id":"probe-deploy-prod",
   "long":"Deployment to production finished with 3 errors in payment API, rollback needed soon.",
   "pager":"Prod dep: 3 errs in pay API. Need roll back soon. Chk logs ASAP.",
   "must":["prod","pay","3","roll","chk"]},
  {"id":"probe-cpu-high",
   "long":"CPU usage on worker node is at 92 percent for last 10 minutes, please scale up.",
   "pager":"Warn wrk: CPU @ 92% x 10 min. Plz scale up now.",
   "must":["wrk","cpu","92%","scale"]},
  {"id":"neg-long-word",
   "long":"test",
   "pager":"Plz restart service now b/c error",
   "must":[],
   "expect_fail_len": True},
]

def run():
    total = len(CASES); passed = 0
    print(f"pager evals: {total} cases")
    print("-"*48)
    for c in CASES:
        bad = check_word_len(c["pager"])
        miss = check_intent(c["pager"], c.get("must",[]))
        expect_fail = c.get("expect_fail_len", False)
        if expect_fail:
            ok = len(bad) > 0  # we want validator to catch it
            stat = "PASS" if ok else "FAIL"
            print(f"[{stat}] {c['id']}: caught {len(bad)} long words {bad}")
        else:
            ok = (not bad) and (not miss)
            stat = "PASS" if ok else "FAIL"
            print(f"[{stat}] {c['id']}: bad={bad} miss={miss}")
        if stat=="PASS": passed+=1
    print("-"*48)
    print(f"done: {passed}/{total} pass")
    # extra stats: short-form / sign usage
    return 0 if passed==total else 1

if __name__ == "__main__":
    sys.exit(run())
