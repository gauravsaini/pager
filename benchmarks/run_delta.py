#!/usr/bin/env python3
"""Delta-mode bench: multi-turn debugging sessions, offline, no API.

Strategy A (full-repeat): every turn re-sends the full pager message.
Strategy B (delta): turn 1 = full pager message, turns 2+ = `Δ:` changed
lines only. Measures token saving with tiktoken cl100k_base.

Run from worktree root: ~/workspace/pager/.venv/bin/python benchmarks/run_delta.py
"""
import json, sys
from pathlib import Path
from datetime import datetime, timezone

import tiktoken

ENC = tiktoken.get_encoding("cl100k_base")


def toks(s):
    return len(ENC.encode(s))


# Each session: turn 1 full message, turns 2-4 updates.
# FULL holds the full-repeat text for each turn; DELTA holds the delta text.
SESSIONS = [
    {
        "id": "prod-api-500s",
        "category": "debugging",
        "full": [
            "SEV2 prod-api: 500s up 12%. Pool 20/20 busy. P99 4.2s. Fix: bump pool 20->50. Watch err.",
            "SEV2 prod-api: 500s down to 3%. Pool 50/50 (bumped 20->50). P99 1.1s. Still above base 0.5%. Watch err.",
            "SEV2 prod-api: 500s 0.4%. Pool 50/60. P99 0.8s. New: 1 DB timeout spike 09:41 UTC. Watch.",
            "SEV3 prod-api: 500s 0%. Pool 50/60. P99 0.6s. Sev downgrade 2->3. Close soon.",
        ],
        "delta": [
            "SEV2 prod-api: 500s up 12%. Pool 20/20 busy. P99 4.2s. Fix: bump pool 20->50. Watch err.",
            "\u0394: pool 20->50 done. 500s 12%->3%. P99 4.2s->1.1s.",
            "\u0394: 500s 3%->0.4%. Pool 50->60. New: DB timeout spike 09:41.",
            "\u0394: 500s 0.4%->0%. P99 0.8s->0.6s. Sev 2->3. Close soon.",
        ],
    },
    {
        "id": "payment-webhook-retries",
        "category": "bugfix",
        "full": [
            "SEV1 pay-svc: webhook retries at 40%. 429s from PSP. Queue 12k msgs. Fix: add backoff 2s->30s. Page PSP.",
            "SEV1 pay-svc: retries 40%->18%. Backoff set 2s->30s. Queue 12k->9k. PSP ack issue, eta 1h. Watch.",
            "SEV2 pay-svc: retries 18%->4%. Queue 9k->2k. PSP fix live. Sev downgrade 1->2. DLQ 30 msgs to fix.",
            "SEV3 pay-svc: retries 4%->0%. Queue 2k->0. DLQ 30->0. Sev downgrade 2->3. Close.",
        ],
        "delta": [
            "SEV1 pay-svc: webhook retries at 40%. 429s from PSP. Queue 12k msgs. Fix: add backoff 2s->30s. Page PSP.",
            "\u0394: backoff 2s->30s set. Retries 40%->18%. Queue 12k->9k. PSP ack, eta 1h.",
            "\u0394: retries 18%->4%. Queue 9k->2k. New: PSP fix live. Sev 1->2. DLQ 30 msgs to fix.",
            "\u0394: retries 4%->0%. Queue 2k->0. DLQ 30->0. Sev 2->3. Close.",
        ],
    },
    {
        "id": "deploy-rollback",
        "category": "deploy",
        "full": [
            "SEV2 api-gw: deploy v2.14.0 bad. Err 5%. CPU 80->95%. Fix: roll back to v2.13.9. Hold new deploys.",
            "SEV2 api-gw: rollback v2.14.0->v2.13.9 done. Err 5%->1%. CPU 95%->70%. Canary 10% clean. Watch.",
            "SEV2 api-gw: err 1%->0.2%. CPU 70%->62%. Canary 10%->50% clean. Hold on bad flag flip.",
            "SEV3 api-gw: err 0.2%->0%. CPU 62%. Canary 50%->100%. Sev downgrade 2->3. Rollback done.",
        ],
        "delta": [
            "SEV2 api-gw: deploy v2.14.0 bad. Err 5%. CPU 80->95%. Fix: roll back to v2.13.9. Hold new deploys.",
            "\u0394: rollback v2.14.0->v2.13.9 done. Err 5%->1%. CPU 95%->70%. Canary 10% clean.",
            "\u0394: err 1%->0.2%. CPU 70%->62%. Canary 10%->50% clean.",
            "\u0394: err 0.2%->0%. Canary 50%->100%. Sev 2->3. Rollback done.",
        ],
    },
]


def pct(a, b):
    return round((1 - b / a) * 100, 1) if a > 0 else 0


def main():
    dry = "--dry-run" in sys.argv
    if dry:
        nturns = sum(len(s["full"]) for s in SESSIONS)
        print(f"Model: local-mock\nSessions: {len(SESSIONS)}")
        for s in SESSIONS:
            print(f"  [{s['id']}] ({s['category']}) {len(s['full'])} turns")
        print(f"\nTotal calls: {nturns * 2} (full-repeat + delta)")
        print("\nDry run done. No API used.")
        return

    print("delta-mode bench: 3 sessions x 4 turns (full-repeat vs delta)")
    print("-" * 64)
    rows = []
    tot_a = tot_b = 0
    tot_fa = tot_fb = 0  # follow-up turns (2+) only
    for s in SESSIONS:
        a = sum(toks(t) for t in s["full"])
        b = sum(toks(t) for t in s["delta"])
        fa = sum(toks(t) for t in s["full"][1:])
        fb = sum(toks(t) for t in s["delta"][1:])
        sv = pct(a, b)
        svf = pct(fa, fb)
        rows.append((s["id"], s["category"], len(s["full"]), a, b, sv, fa, fb, svf))
        tot_a += a
        tot_b += b
        tot_fa += fa
        tot_fb += fb
        print(f"[{s['id']}] turns={len(s['full'])} full={a} delta={b} save={sv}% "
              f"(follow-ups: {fa}->{fb}, save={svf}%)")
    print("-" * 64)
    sv = pct(tot_a, tot_b)
    svf = pct(tot_fa, tot_fb)
    print(f"total full={tot_a} delta={tot_b} save={sv}% ({tot_a - tot_b} tokens)")
    print(f"follow-ups only: full={tot_fa} delta={tot_fb} save={svf}% ({tot_fa - tot_fb} tokens)")
    print("\n| Session | Turns | Full | Delta | Save |")
    print("|---------|------:|-----:|------:|-----:|")
    for sid, cat, n, a, b, sv_i, _fa, _fb, _svf in rows:
        print(f"| {sid} | {n} | {a} | {b} | {sv_i}% |")
    print(f"| **Total** |  | **{tot_a}** | **{tot_b}** | **{sv}%** |")
    out = {
        "date": datetime.now(timezone.utc).isoformat(),
        "encoder": "cl100k_base",
        "total": {"full_repeat": tot_a, "delta": tot_b, "save_pct": sv,
                  "save_tokens": tot_a - tot_b,
                  "followups_full": tot_fa, "followups_delta": tot_fb,
                  "followups_save_pct": svf},
        "rows": [{"id": r[0], "category": r[1], "turns": r[2],
                  "full_repeat": r[3], "delta": r[4], "save_pct": r[5],
                  "followups_full": r[6], "followups_delta": r[7],
                  "followups_save_pct": r[8]}
                 for r in rows],
    }
    Path("delta_bench_results.json").write_text(json.dumps(out, indent=2))
    print("\nsaved to delta_bench_results.json")


if __name__ == "__main__":
    main()
