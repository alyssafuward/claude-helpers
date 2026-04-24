# claude-helpers

A collection of utilities for working with Claude Code outside the normal interactive session — browsing history, replaying conversations, and anything else that's useful but not built in.

## Tools

### `render_chat.py`

Renders a saved Claude Code conversation in your terminal, styled to match the Claude Code TUI (grey boxes for user messages, `●` prefix for Claude responses, dim tool call lines).

Useful for:
- Scrolling through and screenshotting old conversations
- Reviewing what happened in a long session
- Sharing a conversation as a terminal recording

**Requirements:** Python 3.6+, no dependencies.

**Usage:**

```bash
# List all your sessions
python3 render_chat.py --list

# Render a session by UUID
python3 render_chat.py a1b2c3d4-e5f6-7890-abcd-ef1234567890

# Render from a file path directly
python3 render_chat.py ~/.claude/projects/-Users-you/a1b2c3d4-....jsonl
```

Sessions are stored in `~/.claude/projects/` as `.jsonl` files. The UUID is the filename without the extension.

**What it shows:**
- Your messages in a dark grey block
- Claude's responses with markdown rendered (bold, bullets, code blocks, headers)
- Tool calls (Bash, Read, Grep, etc.) as dim one-liners
- Tool results as brief previews

**What it skips:**
- `<thinking>` blocks
- Subagent sidechains
- Compacted summary entries (the raw messages before compaction are still shown)

---

## Skills

Reusable [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) — invoke them with `/skill-name` in any Claude Code session.

### `rename-sug`

Looks at the current conversation and suggests a short, specific chat title (under 60 characters). Copies `/rename <title>` to your clipboard so you can paste and confirm in one keystroke.

**Install:**
```bash
mkdir -p ~/.claude/skills/rename-sug
curl -o ~/.claude/skills/rename-sug/skill.md \
  https://raw.githubusercontent.com/alyssafuward/claude-helpers/main/skills/rename-sug/skill.md
```

**Usage:** type `/rename-sug` in any Claude Code session.

---

## Contributing

This repo is a scratchpad for Claude Code quality-of-life tools. PRs and issues welcome.
