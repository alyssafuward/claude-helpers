# ai-builder-toolkit

A collection of tools built with AI, for building with AI. Utilities for navigating your Claude Code sessions, editing transcripts, browsing project history, and anything else that makes AI-assisted development smoother.

## Skills

Reusable [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) — invoke them with `/skill-name` in any Claude Code session.

Skills are just markdown files that live in `~/.claude/skills/<skill-name>/skill.md`. When you type `/skill-name`, Claude Code loads the file and follows the instructions inside it.

### `rename-sug`

Looks at the current conversation and suggests a short, specific chat title (under 60 characters). Copies `/rename <title>` to your clipboard so you can paste and confirm in one keystroke.

**Install:** [Download `skill.md`](https://github.com/alyssafuward/ai-builder-toolkit/blob/main/skills/rename-sug/skill.md) from this repo, then drag it into a Claude Code conversation and say, "Install this skill."

**Usage:** type `/rename-sug` in any Claude Code session.

---

## Transcript Cutter

A browser app for editing video transcripts. Load a `.vtt` file, select the segments you want to keep across multiple named selection sets (e.g. Video, GitHub), adjust section boundaries, and export timestamps or transcript text.

See [`transcript-cutter/`](transcript-cutter/) for details.

---

## Version Switcher

A local dev tool for browsing meaningful versions of a project. Runs a small Node server that injects a version bar into your app — click a version, the app reloads at that commit. Great for tutorials and walkthroughs.

Add a `versions.json` to any git repo listing the commits you want to show, then run:

```bash
node path/to/version-switcher.js
```

See [`transcript-cutter/version-switcher.js`](transcript-cutter/version-switcher.js) for the current implementation (will be extracted into a standalone utility).

---

## Utilities

### `utilities/render_chat.py`

> **Note:** This script is out of date and may not work correctly with recent versions of Claude Code.

Renders a saved Claude Code conversation in your terminal, styled to match the Claude Code TUI.

**Requirements:** Python 3.6+, no dependencies.

**Usage:**

```bash
# List all your sessions
python3 utilities/render_chat.py --list

# Render a session by UUID
python3 utilities/render_chat.py a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

---

## Contributing

PRs and issues welcome.
