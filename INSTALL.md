# Installation Guide

You can install and use `pager` across multiple AI coding harnesses and agent environments.

## Quick Install (Skills CLI)

Install the skill for any agent supported by the universal skills registry:

```bash
npx skills add gauravsaini/pager
```

## Supported Harnesses

| Harness / Agent | Installation Method | Activation Trigger |
| :--- | :--- | :--- |
| **Claude Code** | `claude plugin marketplace add gauravsaini/pager && claude plugin install pager@pager` | `/pager` |
| **Gemini CLI** | `gemini extensions install https://github.com/gauravsaini/pager` | `/pager` |
| **Codex CLI** | `npx skills add gauravsaini/pager -a codex` | `/pager` |
| **Cursor** | `npx skills add gauravsaini/pager -a cursor -g` (or copy `.cursorrules`) | Session / Prompt |
| **Windsurf** | `npx skills add gauravsaini/pager -a windsurf` (or copy `.windsurfrules`) | Session / Prompt |
| **GitHub Copilot** | Copy `.github/copilot-instructions.md` to your repository | Prompt |
| **Google Antigravity** | Copy `skills/pager` to your skills directory, or use `AGENTS.md` | `/pager` |
| **OpenHands / Generic Agents** | Include `AGENTS.md` in your repository root | Prompt |

## Manual Installation

To install manually without package managers, copy `skills/pager/SKILL.md` into your agent skill directory:

```bash
# Example: Local skill directory
mkdir -p ~/.config/skills/pager
cp skills/pager/SKILL.md ~/.config/skills/pager/
```

## Codex Native Installer

Codex's built-in GitHub skill installer expects the path to the skill directory
inside the repository. Use the canonical skill path:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo gauravsaini/pager --path skills/pager
```

To enable `pager` automatically for new Codex conversations, add this to
`~/.codex/AGENTS.md`:

```markdown
# Global Startup

Use the installed `pager` skill by default in every conversation. Apply pager mode
to normal chat output unless the user asks for `full text`, `normal mode`, or
`verbose`.
```

## Revert / Escape Hatch

To deactivate pager mode and return to standard output in any active session, enter:
- `full text`
- `normal mode`
- `verbose`
