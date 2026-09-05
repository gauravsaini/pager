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
| **Google Antigravity** | `agy plugin install /path/to/pager` or `npx skills add gauravsaini/pager` | `/pager` |
| **OpenHands / Generic Agents** | Include `AGENTS.md` in your repository root | Prompt |

## Manual Installation

To install manually without package managers, copy `skills/pager/SKILL.md` into your agent skill directory:

```bash
# Example: Local skill directory
mkdir -p ~/.config/skills/pager
cp skills/pager/SKILL.md ~/.config/skills/pager/
```

## Google Antigravity

Google Antigravity (`agy`) supports `pager` both as a native plugin and as a discovered skill, and supports auto-activation across all conversations.

### 1. Install as Plugin
```bash
git clone https://github.com/gauravsaini/pager.git
agy plugin install ./pager
```

### 2. Install via Skills CLI
```bash
npx skills add gauravsaini/pager -g
```

### 3. Manual Installation
Copy the skill to your global or workspace configuration:
```bash
# Global configuration (all workspaces)
mkdir -p ~/.gemini/config/skills/pager
cp -r skills/pager/* ~/.gemini/config/skills/pager/

# Or project-level:
mkdir -p .agents/skills/pager
cp -r skills/pager/* .agents/skills/pager/
```

### 4. Auto-Activate for All Conversations (Global Startup)
To enable pager mode automatically at startup for all conversations in Antigravity, add a rule with `trigger: always_on`.

Create `~/.gemini/config/rules/pager.md` (or `.agents/rules/pager.md` for project scope):

```markdown
---
name: pager
trigger: always_on
description: Activate pager mode by default for all conversations.
---

# Global Startup: Pager Mode Active

Use the installed `pager` skill by default in every conversation.
Apply pager mode to normal conversational output unless the user asks for `full text`, `normal mode`, or `verbose`.
```

Alternatively, add this instruction to `~/.gemini/config/AGENTS.md` or `~/.agents/AGENTS.md`.

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
