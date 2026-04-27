# ai-builder-toolkit

A collection of tools built with AI, for building with AI. Utilities for navigating your Claude Code sessions, editing transcripts, browsing project history, and anything else that makes AI-assisted development smoother.

## Tools

### `tools/transcript-cutter/`

A browser app for editing video transcripts. Load a `.vtt` file, select the segments you want to keep across multiple named selection sets (e.g. Video, GitHub), adjust section boundaries, and export timestamps or transcript text.

### `tools/version-switcher.js`

A local dev tool for browsing meaningful versions of a project. Runs a small Node server that injects a version bar into your app — click a version, the app reloads at that commit. Great for tutorials and walkthroughs.

Add a `versions.json` to any git repo listing the commits you want to show, then run from that repo's root:

```bash
node ~/src/ai-builder-toolkit/tools/version-switcher.js
```

### `tools/render-chat.py`

> **Note:** This script is out of date and may not work correctly with recent versions of Claude Code.

Renders a saved Claude Code conversation in your terminal, styled to match the Claude Code TUI.

**Requirements:** Python 3.6+, no dependencies.

**Usage:**

```bash
python3 tools/render-chat.py --list
python3 tools/render-chat.py a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

---

## Skills

Reusable [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) — invoke them with `/skill-name` in any Claude Code session.

Skills are just markdown files that live in `~/.claude/skills/<skill-name>/skill.md`. When you type `/skill-name`, Claude Code loads the file and follows the instructions inside it.

### `rename-sug`

Looks at the current conversation and suggests a short, specific chat title (under 60 characters). Copies `/rename <title>` to your clipboard so you can paste and confirm in one keystroke.

**Install:** [Download `skill.md`](https://github.com/alyssafuward/ai-builder-toolkit/blob/main/skills/rename-sug/skill.md) from this repo, then drag it into a Claude Code conversation and say, "Install this skill."

**Usage:** type `/rename-sug` in any Claude Code session.

---

## Contributing

PRs and issues welcome.
