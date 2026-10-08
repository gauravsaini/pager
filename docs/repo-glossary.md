# Repo Glossary — `.pager.json` Spec

A repo-level identifier→code map. Long identifiers that get repeated across a
session (service names, components, pools) get short codes; the map is read
**once per session**, so the savings compound with every mention.

## 1. File format

Location: repo root, named `.pager.json` (shipped template:
`.pager.json.example`). Valid JSON, top-level object:

```json
{
  "_comment": "optional free-text note",
  "codes": {
    "authentication-service": "as",
    "payment-gateway-processor": "pg",
    "database-connection-pool": "dcp"
  }
}
```

- `codes`: object, key = exact identifier string (see §2 case rules),
  value = short code.
- Only `codes` and `_comment` are read; unknown keys ignored.
- Invalid JSON or non-object `codes` → file ignored entirely (graceful, §3).

## 2. Rules

- **Code length**: ≤3 chars, `[a-z0-9]` lowercase only.
- **Reserved codes**: a code MUST NOT collide with pager's standing short
  forms: `svc db cfg err msg txt req plz ack prod dev stg info auth repo
  ASAP rdy chk upd del rest ret`. (Also avoid `w/` `w/o` `b/c` — they contain
  symbols and can never be codes anyway.)
- **Case**: identifiers are case-sensitive and matched verbatim (matches how
  they appear in the repo: kebab-case, snake_case, or CamelCase all fine).
  Codes are always lowercase.
- **Uniqueness**: one code per identifier, one identifier per code.
  Duplicate code → first entry in file order wins, later entries ignored.
- **Scoping**: per repo. The file at the repo root applies to the whole
  repo. In a monorepo, the **nearest** `.pager.json` walking up from the
  working directory wins; search stops at the first hit.
- **Where codes apply**: prose/chat mentions only. Never rewrite identifiers
  inside code blocks, diffs, file paths, or terminal commands (pager hard
  rule: exact code stays exact).

## 3. Session-loading contract

1. At session start, if the agent's working repo root contains `.pager.json`,
   read it **once** and keep the map in session state.
2. If the file is absent, unreadable, or invalid: fall back gracefully —
   continue with no glossary, no error, no retry per request.
3. Never re-read the file per request. One read per session amortizes the
   load cost (§4); per-request reads would erase the savings.
4. Mid-session file edits take effect next session only.

## 4. Measured token economics (tiktoken cl100k_base)

Method: `~/workspace/pager/.venv/bin/python` with tiktoken
`cl100k_base`. Three example identifiers:

| Identifier                  | Id tok | Code | Code tok | Save/mention |
|-----------------------------|--------|------|----------|--------------|
| `authentication-service`    | 2      | `as` | 1        | 1            |
| `payment-gateway-processor` | 5      | `pg` | 1        | 4            |
| `database-connection-pool`  | 5      | `dcp`| 2        | 3            |

**Compounding math.** Per-mention saving is linear in mention count:

```
session_saved = Σ (id_tokens − code_tokens) × mentions
```

Example: a session mentions the 3 identifiers above 20×, 10×, 12×
respectively → `20×1 + 10×4 + 12×3 = 96` tokens saved.

**Amortized load cost.** The 6-entry example file costs ~92 tokens to read
(measured). Breakeven for the full example map (avg save ≈2.8 tok/mention):
`92 / 2.8 ≈ 33` mentions. A 60-mention session saves ~170 tokens → net
≈ +78 tokens. Anything past breakeven is pure gain, and the one-time read
cost is fixed while savings grow with session length.

## 5. Hook line for SKILL.md / AGENTS.md

Minimal hook to add to `skills/pager/SKILL.md` (or the root skill mirror):

> ```
> 6. **Repo glossary**: If the working repo root has `.pager.json`, read it once at session start (`{"codes": {...}}`) and use its codes for repeated identifiers. Absent/invalid → ignore silently. Never re-read per request; never rewrite identifiers inside code blocks/paths. See `docs/repo-glossary.md`.
> ```
