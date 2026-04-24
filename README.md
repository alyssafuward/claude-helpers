# claude-helpers

A collection of utilities for working with Claude Code outside the normal interactive session — browsing history, replaying conversations, and anything else that's useful but not built in.

## Skills

Reusable [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) — invoke them with `/skill-name` in any Claude Code session.

Skills are just markdown files that live in `~/.claude/skills/<skill-name>/skill.md`. When you type `/skill-name`, Claude Code loads the file and follows the instructions inside it.

### `rename-sug`

Looks at the current conversation and suggests a short, specific chat title (under 60 characters). Copies `/rename <title>` to your clipboard so you can paste and confirm in one keystroke.

**Install:** [Download `skill.md`](https://github.com/alyssafuward/claude-helpers/blob/main/skills/rename-sug/skill.md) from this repo, then drag it into a Claude Code conversation and say, "Install this skill."

**Usage:** type `/rename-sug` in any Claude Code session.

---

## Utilities

### `utilities/render_chat.py`

> **Note:** This script is out of date and may not work correctly with recent versions of Claude Code.

Renders a saved Claude Code conversation in your terminal, styled to match the Claude Code TUI (grey boxes for user messages, `●` prefix for Claude responses, dim tool call lines).

Useful for:
- Scrolling through and screenshotting old conversations
- Reviewing what happened in a long session
- Sharing a conversation as a terminal recording

**Requirements:** Python 3.6+, no dependencies.

**Usage:**

```bash
# List all your sessions
python3 utilities/render_chat.py --list

# Render a session by UUID
python3 utilities/render_chat.py a1b2c3d4-e5f6-7890-abcd-ef1234567890

# Render from a file path directly
python3 utilities/render_chat.py ~/.claude/projects/-Users-you/a1b2c3d4-....jsonl
```

Sessions are stored in `~/.claude/projects/` as `.jsonl` files. The UUID is the filename without the extension.

---

## Contributing

This repo is a scratchpad for Claude Code quality-of-life tools. PRs and issues welcome.
