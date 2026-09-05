<p align="center">
  <img src="assets/logo.svg" alt="pager logo" width="800">
</p>

# pager

> Ultra-short communication mode for AI coding agents: words &lt;= 5 characters, zero fluff, 100% technical intent preserved.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Compatibility](https://img.shields.io/badge/harnesses-Claude%20%7C%20Gemini%20%7C%20Codex%20%7C%20Cursor-emerald)](#installation)
[![Token Cut](https://img.shields.io/badge/token_cut-~66%25-brightgreen)](#benchmarks--evals)

`pager` reduces token usage and scanning latency by enforcing a 5-character word limit on conversational output while keeping code blocks, paths, commands, and diagnostic data completely intact.

---

## Comparison

| Standard Response | Pager Mode |
| :--- | :--- |
| "The PostgreSQL connection pool has been exhausted due to unclosed database connections in the authentication middleware. Please restart the auth service immediately and review active query pool limits." | `SEV1 auth: DB pool full -> 504 err. Plz rest auth ASAP. Chk qry load.` |
| **34 words / 48 tokens** | **13 words / 16 tokens (~66% reduction)** |

Code blocks, diffs, terminal commands, and identifiers remain unchanged.

---

## Installation

### 1. Universal Skills CLI

Install for any skills-compatible agent environment:

```bash
npx skills add gauravsaini/pager
```

### 2. Native Harness Support

- **Claude Code**:
  ```bash
  claude plugin marketplace add gauravsaini/pager && claude plugin install pager@pager
  ```
- **Gemini CLI**:
  ```bash
  gemini extensions install https://github.com/gauravsaini/pager
  ```
- **Cursor IDE**:
  ```bash
  npx skills add gauravsaini/pager -a cursor -g
  ```
  *(or use the included [.cursorrules](.cursorrules))*
- **Codex CLI**:
  ```bash
  npx skills add gauravsaini/pager -a codex
  ```
  *(or use the included [AGENTS.md](AGENTS.md))*
- **Windsurf**:
  Use the included [.windsurfrules](.windsurfrules).
- **GitHub Copilot**:
  Use the included [.github/copilot-instructions.md](.github/copilot-instructions.md).

For complete harness configuration details, see [INSTALL.md](INSTALL.md).

---

## Usage

- **Trigger**: Run `/pager`, invoke `$pager`, or request `"pager mode"`.
- **Revert**: Say `"full text"`, `"normal mode"`, or `"verbose"` to disable.

---

## Repository Layout

```
pager/
  assets/logo.svg                  # Vector branding banner
  skills/pager/SKILL.md            # Canonical skill definition
  .claude-plugin/                  # Claude Code plugin manifest & marketplace definition
  gemini-extension.json            # Gemini CLI extension manifest
  AGENTS.md                        # Universal agent instructions (Codex, Antigravity, OpenHands)
  CLAUDE.md                        # Claude Code rules
  GEMINI.md                        # Gemini CLI rules
  .cursorrules                     # Cursor rules
  .windsurfrules                   # Windsurf rules
  .github/copilot-instructions.md  # GitHub Copilot custom instructions
  INSTALL.md                       # Comprehensive installation guide
  evals/test_pager.py              # Word-length & intent test suite
  benchmarks/run.py                # English benchmark suite (10 tasks)
  benchmarks/run_zh.py             # Chinese benchmark suite (5 tasks)
  benchmarks/prompts.json          # Shared benchmark prompts
```

---

## Benchmarks & Evals

Run the evaluation and benchmark suites using `uv`:

```bash
# Run unit tests and intent validation
uv run python evals/test_pager.py

# Run English benchmark suite
uv run python benchmarks/run.py

# Run Chinese benchmark suite
uv run python benchmarks/run_zh.py

# Dry run (list tasks without executing)
uv run python benchmarks/run.py --dry-run
```

- **English Benchmark**: ~66% token reduction compared to baseline, 10/10 compliance.
- **Chinese Benchmark**: ~51% character reduction, 5/5 pass.

---

## License

MIT. See [LICENSE](LICENSE).
