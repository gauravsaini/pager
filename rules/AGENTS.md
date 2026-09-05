# Pager Protocol

When pager mode is requested or activated:

1. **Length Constraint**: All explanatory words must contain 5 characters or fewer. Use abbreviations or clipping when necessary (for example: `service` -> `svc`, `config` -> `cfg`, `database` -> `db`, `update` -> `upd`). Standard technical terms and identifiers (e.g. `HTTPS`, `OAuth`, `PostgreSQL`) are exempt.
2. **Intent Preservation**: Preserve complete core intent, system names, error status codes, operational metrics, and remediation actions without loss of critical context.
3. **Exact Code & Commands**: Code blocks, file paths, diff blocks, and terminal commands must remain completely unmodified.
4. **Shorthand & Symbols**: Use standard short forms (`plz`, `req`, `msg`, `txt`, `svc`, `ASAP`, `ack`, `prod`, `dev`, `stg`) and mathematical or logical symbols (`&`, `+`, `-`, `/`, `>`, `<`, `->`, `@`, `w/`, `w/o`, `b/c`).
5. **No Salutations**: Omit conversational greetings, pleasantries, and redundant closing statements.
