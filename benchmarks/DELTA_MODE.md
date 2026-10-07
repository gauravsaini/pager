# Delta Mode (Δ:) — follow-up pattern for iterative debugging sessions

Like video P-frames: the first message is a full pager message (I-frame);
every follow-up sends **only the changed lines**, never a full repeat.

## Activation rules

1. **Turn 1 of an incident = full pager message.** Full state: severity,
   scope, key metrics, error codes, remediation action.
2. **Turn 2+ of the same incident = delta mode.** Each follow-up is one
   (or a few) `Δ:` lines listing only what changed since the last turn.
3. **New incident = back to turn 1.** A different incident, service, or
   root cause restarts the counter — deltas only ever resolve against
   the immediately preceding turn of the same incident.

## The `Δ:` line format

```
Δ: <field> <old>-><new>, <field> <old>-><new>, <new fact>
```

- `field` = short label (`pool`, `500s`, `p99`, `sev`, `err`).
- Old value may be omitted if implied by the last turn (`Δ: pool 50`).
- New facts with no old value just state themselves (`Δ: new: DB timeout spike 09:41`).
- One turn = one `Δ:` line unless changes are unrelated; keep to 1–3 fields.

## What must still be included

- **Severity changes**, always with explicit arrow: `Δ: sev 2->3`.
- **New errors** as they appear: `Δ: new: 429s on /charge (11%)`.
- **Resolved facts**: `Δ: 500s 12%->0%` — absence of a delta means no change,
  so an error that stops must be closed out explicitly.
- Remediation actions when they change state (`pool 20->50 done`).

## Fallback: full re-send

Send a full pager message (not `Δ:`) when:

- the receiver signals context lost (`re:?` / "lost state, resend"),
- the incident scope changes (new root cause, different service),
- deltas have chained 10+ turns without a full frame (re-sync).

A full re-send restarts delta chaining from turn 1.

## Receiver contract

- Receiver holds the last full frame + applies each `Δ:` in order.
- Missing/undelivered turn → ask for a full re-send, never guess.
- `ack` confirms receipt; it never confirms intent.
