# claude-helpers — AI context

This repo contains utility scripts for working with Claude Code session data.

## Purpose

Claude Code stores all conversations as JSONL files in `~/.claude/projects/`. These tools operate on those files directly — reading, rendering, or analyzing them without needing an active Claude Code session.

## Current tools

### `render_chat.py`

Reads a `.jsonl` session file and prints the conversation to stdout using ANSI escape codes styled to match the Claude Code TUI.

**Key design decisions:**
- No external dependencies — plain Python stdlib only
- Resolves session UUIDs automatically by searching `~/.claude/projects/` recursively
- Builds the conversation thread by walking the `parentUuid` linked list, always taking the most recent branch at each fork, skipping `isSidechain: true` entries (those are subagent calls). Importantly, the children map includes ALL entry types (including `system` entries like `turn_duration`) because they appear as intermediate links in the chain — filtering by type when building the map would break the thread.
- Renders markdown inline using regex (bold, italic, inline code, headers, bullets, code blocks) — not a full parser, handles the common cases Claude produces
- Skips `thinking` blocks entirely (they're internal and not part of the visible conversation)

**JSONL structure (what we rely on):**
- `type`: `"user"` | `"assistant"` | `"file-history-snapshot"` | others (we only use user/assistant)
- `uuid`: unique ID for this entry
- `parentUuid`: links to parent entry, `null` for root
- `isSidechain`: `true` for subagent messages, skip these for the main thread
- `timestamp`: ISO 8601
- `message.role`: `"user"` | `"assistant"`
- `message.content`: string (simple user messages) or array of blocks
  - Block types: `text`, `tool_use`, `tool_result`, `thinking`
- `sessionId`, `version`: session metadata, may only appear on some entries

## Conventions

- Keep tools as single self-contained scripts where possible
- No dependencies outside stdlib unless genuinely necessary
- Scripts should work on any machine with Claude Code installed (use `Path.home()` not hardcoded paths)
- When adding a new tool, add a section to this file and to README.md
