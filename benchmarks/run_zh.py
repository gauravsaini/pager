#!/usr/bin/env python3
"""Pager ZH bench: same 10 tasks, normal ZH vs pager ZH."""
import re, json
from pathlib import Path

# 5 rep tasks for speed, same ids as pager_bench.py
TASKS = [
 {"id":"react-rerender","cat":"debug","normal_zh":"你的 React 组件每次渲染都会重新渲染，原因是每次传递了新的对象引用作为属性，浅比较每次都认为不同。建议使用 useMemo 缓存对象，并用 memo 缓存子组件。","pager_zh":"React 重渲: obj 属性 = 新引用. 用 memo 缓存. 按 id 查."},
 {"id":"auth-middleware-fix","cat":"bugfix","normal_zh":"你的认证中间件放过了过期的令牌，因为 Date.now 返回毫秒而令牌过期时间是秒级时间戳，直接比较会导致过期判断失效。应该统一单位后再比较，过期返回401。","pager_zh":"SEV1 认证: exp 秒级 now 毫秒级. 除 1000 对齐. 过期退 401."},
 {"id":"postgres-pool","cat":"setup","normal_zh":"在 Node.js 中使用 pg 创建连接池，建议最大连接数二十，空闲超时三十秒，连接超时五秒，并添加错误监听和退避重试，关闭时正确释放。","pager_zh":"PG 池: 最大 20 空闲 30s. 查错 + 重试."},
 {"id":"git-rebase-merge","cat":"explain","normal_zh":"合并会保留完整历史并产生合并提交，适合共享分支。变基会改写提交形成线性历史，更干净但不适合共享分支。本地用变基，主干用合并。","pager_zh":"Git: 变基 = 干净历史 合并 = 安全. 本地用前者 主干用后者."},
 {"id":"race-condition-debug","cat":"debug","normal_zh":"并发递增出现竞态是因为先读后写不是原子操作，高并发下会读到相同值。应该使用单条原子更新并返回，或用事务加行锁，重试序列化错误。","pager_zh":"竞态: 递增非原子. 用事务 + 锁行. 退新值."},
]

def cjk_len(tok):
    # count CJK + alnum, ignore punct
    core = re.sub(r'[^A-Za-z0-9\u4e00-\u9fff]','',tok)
    return len(core)

def check_pager_zh(s):
    bad=[]
    s2=re.sub(r'```.*?```',' ',s,flags=re.S)
    s2=re.sub(r'`[^`]*`',' ',s2)
    for raw in re.split(r'\s+', s2.strip()):
        if not raw: continue
        w=raw.strip(':.,;!?\"\'()[]{}。，、；：！？').strip()
        if not w: continue
        if w.lower() in ("w/","w/o","b/c","->","&","+","-","/","@",">","<","="): continue
        # split hyphen
        for part in re.split(r'[-‐‑‒–—]', w):
            # if part has CJK run >5 -> split further on CJK punct? else fail
            # allow SEV1, PG, Git, numbers
            core=re.sub(r'^[^A-Za-z0-9\u4e00-\u9fff]+|[^A-Za-z0-9\u4e00-\u9fff]+$','',part)
            if not core: continue
            # exempt codes
            if core.lower() in ("oauth","https","http","utc","sql","api","jwt","pg","git","sev1","401","1000","20","30s"): continue
            # count: if mixed, total chars
            n=len(re.sub(r'[^A-Za-z0-9\u4e00-\u9fff]','',core))
            if n>5:
                # allow time like 08:14 -> core 0814 len4 ok, already handled
                bad.append(raw); break
    return bad

def toks(s): return len(s.split())

def main():
    print(f"ZH bench: {len(TASKS)} tasks")
    print("-"*52)
    tot_n=tot_p=0; ok=0
    rows=[]
    for t in TASKS:
        n,p=t["normal_zh"],t["pager_zh"]
        # char-based tokens: use chars for ZH fair cut
        nc,pc=len(n),len(p)
        nw,pw=toks(n),toks(p)
        bad=check_pager_zh(p)
        good=len(bad)==0
        ok+=1 if good else 0
        cut=round((1-pc/nc)*100) if nc else 0
        rows.append((t["id"],nc,pc,cut,good,bad,nw,pw))
        tot_n+=nc; tot_p+=pc
        print(f"[{t['id']}] chars N={nc} P={pc} cut={cut}% words N={nw} P={pw} chk={'ok' if good else bad}")
    print("-"*52)
    avg_cut=round((1-tot_p/tot_n)*100) if tot_n else 0
    print(f"avg chars N={tot_n} P={tot_p} cut={avg_cut}%")
    print(f"comply: {ok}/{len(TASKS)} pass")
    print("\n| Task | Base chars | Pager chars | cut | chk |")
    print("|------|----------:|-----------:|----:|:---:|")
    for i,nc,pc,cut,good,bad in [(r[0],r[1],r[2],r[3],r[4],r[5]) for r in rows]:
        print(f"| {i} | {nc} | {pc} | {cut}% | {'ok' if good else 'FAIL'} |")
    print(f"| **Avg** | **{tot_n}** | **{tot_p}** | **{avg_cut}%** | **{ok}/{len(rows)}** |")
    Path("pager_bench_zh_results.json").write_text(json.dumps({"avg_cut":avg_cut,"comply":f"{ok}/{len(TASKS)}","rows":[{"id":r[0],"base_chars":r[1],"pager_chars":r[2]} for r in rows]},ensure_ascii=False,indent=2),encoding="utf-8")
    print("\nsaved to pager_bench_zh_results.json")

if __name__=="__main__": main()
