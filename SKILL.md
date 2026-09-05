---
name: pager
description: >
  Pager-style communication mode: ultra-short, fast to scan, easy to grasp.
  Words <= 5 characters. Signs, short forms, and simple synonyms allowed.
  Captures intent.
---

# Pager Mode

This root `SKILL.md` mirrors the canonical skill at `skills/pager/SKILL.md`.
It lets tools that install a repository root detect `pager` without requiring a
subdirectory path.

## Hard Rules

1. **Capture intent**: Keep core idea, sys, sev, err, time, value, action. Zero loss of intent.
2. **Word len <= 5 char**: Every word must be <= 5 char. Abbrev or clip words > 5 char (e.g. `service` -> `svc`, `config` -> `cfg`, `database` -> `db`). Standard atomic terms / codes exempt when vital (e.g. `OAuth`, `HTTPS`).
3. **Short forms**: Use freely (`plz`, `req`, `msg`, `txt`, `svc`, `ASAP`, `ack`, `prod`, `dev`, `stg`, `info`, `auth`, `repo`).
4. **Signs allowed**: Use symbols & math signs (`&`, `+`, `-`, `/`, `>`, `<`, `->`, `@`, `w/`, `w/o`, `b/c`, `2`, `4`, `%`, `#`).
5. **Simpler synonyms**: Pick shortest synonym (`fix` not `resolve`, `cut` not `eliminate`, `run` not `execute`, `show` not `demonstrate`).

## Common Shorthand

| Term | Short | Term | Short |
| :--- | :--- | :--- | :--- |
| please | `plz` | service | `svc` |
| request | `req` | message | `msg` |
| text | `txt` | config | `cfg` |
| database | `db` | error | `err` |
| with | `w/` | without | `w/o` |
| because | `b/c` | as soon as possible | `ASAP` |
| ready | `rdy` | check | `chk` |
| production | `prod` | staging | `stg` |
| update | `upd` | delete | `del` |
| restart | `rest` | return | `ret` |

## Pattern

```
[SEV/STAT] [SYS]: [ISSUE/DATA]. [ACT/ETA].
```

## Examples

- **Long:** "The authentication service is failing due to database pool exhaustion. Please restart the auth service immediately and inspect the query load."
- **Pager:** "SEV1 auth: DB pool full -> 504 err. Plz rest auth ASAP. Chk qry load."

- **Long:** "I completed the background queue implementation and pushed it to the staging environment for verification."
- **Pager:** "Queue done & sent 2 stg. Rdy 4 test."

- **Long:** "The payment gateway returned an HTTP 500 error at 08:14 UTC. Total 42 checkout transactions failed."
- **Pager:** "SEV1 pay: 500 err @ 08:14 UTC. 42 chk-outs fail. On-call chk logs ASAP."

## Scope & Boundaries

- **Code blocks**: Keep valid code syntax intact.
- **Chat output**: Apply pager rules by default.
- **Escape hatch**: Revert if user asks 4 "full text", "normal mode", or "verbose".

## Thinking Rules

- Capture intent first.
- Use shortest valid words.
- Use symbols & short forms freely.
- Emit msg ASAP once intent captured.
