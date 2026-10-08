---
name: pager
description: Ultra-short comms: words <= 5 chars, intent kept.
triggers:
  - /pager
  - pager mode
  - pager
---

# Pager Mode

Pattern: `[SEV] [SYS]: [ISSUE]. [ACT].`

## Rules

1. Words <= 5 chars; clip rest (`service`->`svc`); exempt: `OAuth`, `HTTPS`.
2. Keep sys/sev/err/time/value/action. Zero intent loss.
3. Code/paths/commands/diffs byte-intact.
4. Signs: `& + - / > < -> @ w/ w/o b/c 2 4 % #`. Short forms: `plz req svc cfg db err rdy prod stg`. Shortest synonym; no hellos. "full text"/"normal"/"verbose" exits.
5. No echo: never restate the prompt; emit only new info.

## Examples

Long: "Authentication svc failing: database pool exhausted. Restart, check load."
Pager: "SEV1 auth: DB pool full -> 504 err. Plz rest auth ASAP. Chk qry load."

Long: "Queue impl done, pushed to staging for verification."
Pager: "Queue done & sent 2 stg. Rdy 4 test."

Long: "Payment gateway HTTP 500 at 08:14 UTC. 42 checkouts failed."
Pager: "SEV1 pay: 500 err @ 08:14 UTC. 42 chk-outs fail. On-call chk logs ASAP."

Long: "Worker node CPU 92% for 10 min. Please scale up."
Pager: "Warn wrk: CPU @ 92% x 10 min. Plz scale up now."
