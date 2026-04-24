#!/usr/bin/env python3
"""Render a Claude Code JSONL conversation in terminal style."""

import json
import re
import sys
import textwrap
import shutil
import glob as globmod
from pathlib import Path

RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
ITALIC  = "\033[3m"

# Colors
BLUE    = "\033[38;5;75m"
GREY    = "\033[38;5;245m"
WHITE   = "\033[38;5;252m"
GREEN   = "\033[38;5;114m"
YELLOW  = "\033[38;5;221m"
RED     = "\033[38;5;203m"

# Backgrounds
BG_USER = "\033[48;5;252m"   # light grey for user messages
BG_TOOL = "\033[48;5;235m"   # dark grey for tool results

TERM_WIDTH = shutil.get_terminal_size((100, 40)).columns

CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"


def render_markdown(text):
    """Convert basic markdown to ANSI."""
    lines = text.split('\n')
    out = []
    in_code_block = False
    code_lang = ''

    for line in lines:
        # Code blocks
        if line.startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_lang = line[3:].strip()
                out.append(f"{BG_TOOL}{DIM}  {code_lang or 'code'}{RESET}")
            else:
                in_code_block = False
                out.append(f"{BG_TOOL}{DIM}{'─' * min(40, TERM_WIDTH - 4)}{RESET}")
            continue

        if in_code_block:
            out.append(f"{BG_TOOL}{GREEN}  {line}{RESET}")
            continue

        # Headers
        if line.startswith('### '):
            out.append(f"{BOLD}{WHITE}{line[4:]}{RESET}")
            continue
        if line.startswith('## '):
            out.append(f"{BOLD}{WHITE}{line[3:]}{RESET}")
            continue
        if line.startswith('# '):
            out.append(f"{BOLD}{WHITE}{line[2:]}{RESET}")
            continue

        # Horizontal rule
        if re.match(r'^---+$', line.strip()):
            out.append(f"{DIM}{'─' * min(60, TERM_WIDTH - 4)}{RESET}")
            continue

        # Inline formatting: bold, italic, inline code
        line = re.sub(r'\*\*(.+?)\*\*', f"{BOLD}\\1{RESET}", line)
        line = re.sub(r'\*(.+?)\*',     f"{ITALIC}\\1{RESET}", line)
        line = re.sub(r'`(.+?)`',       f"{GREEN}\\1{RESET}", line)

        # Bullet points
        if re.match(r'^[\*\-] ', line):
            line = f"  {GREY}•{RESET} {line[2:]}"
        elif re.match(r'^\d+\. ', line):
            m = re.match(r'^(\d+\.) (.*)', line)
            if m:
                line = f"  {GREY}{m.group(1)}{RESET} {m.group(2)}"

        out.append(line)

    return '\n'.join(out)


def wrap_text(text, width, prefix=''):
    """Wrap text to width, preserving blank lines."""
    result = []
    for para in text.split('\n'):
        if para.strip() == '':
            result.append('')
        else:
            wrapped = textwrap.fill(para, width=width - len(prefix),
                                    subsequent_indent='  ' if re.match(r'^  [•\-\*]', para) else '')
            result.append(wrapped)
    return '\n'.join(result)


def render_user(text):
    """Render a user message in a grey box with > prefix."""
    text = text.strip()
    inner_width = min(TERM_WIDTH - 4, 96)
    lines = text.split('\n')

    print()
    for line in lines:
        if len(line) > inner_width:
            chunks = textwrap.wrap(line, width=inner_width) or ['']
        else:
            chunks = [line]
        for chunk in chunks:
            padding = ' ' * (inner_width - len(re.sub(r'\033\[[0-9;]*m', '', chunk)))
            print(f"{BG_USER}\033[38;5;238m > {RESET}{BG_USER}\033[38;5;232m{chunk}{padding} {RESET}")
    print()


def render_assistant(text):
    """Render an assistant text message with ● prefix."""
    text = text.strip()
    rendered = render_markdown(text)
    inner_width = min(TERM_WIDTH - 4, 96)
    wrapped = wrap_text(rendered, inner_width)

    print(f"\n{BLUE}●{RESET} ", end='')
    lines = wrapped.split('\n')
    for i, line in enumerate(lines):
        if i == 0:
            print(line)
        else:
            print(f"  {line}")
    print()


def render_tool_use(name, input_data):
    """Render a tool call."""
    label = name
    if name == 'Bash' and 'command' in input_data:
        cmd = input_data['command'][:80].replace('\n', ' ')
        label = f"Bash: {cmd}"
    elif name in ('Read', 'Glob', 'Grep', 'Write', 'Edit'):
        path = input_data.get('file_path') or input_data.get('pattern') or input_data.get('path') or ''
        label = f"{name}: {str(path)[:70]}"
    elif name == 'Agent':
        label = f"Agent: {input_data.get('description','')[:60]}"

    print(f"  {DIM}{GREY}⚙ {label}{RESET}")


def render_tool_result(content_blocks):
    """Render tool result(s) briefly."""
    for block in content_blocks:
        if isinstance(block, dict) and block.get('type') == 'tool_result':
            result_content = block.get('content', '')
            if isinstance(result_content, str):
                preview = result_content.strip()[:120].replace('\n', ' ')
            elif isinstance(result_content, list):
                texts = [c.get('text','') for c in result_content if isinstance(c, dict) and c.get('type')=='text']
                preview = ' '.join(texts)[:120].replace('\n', ' ')
            else:
                preview = ''
            if preview:
                print(f"  {DIM}{GREY}  ↳ {preview}…{RESET}")


def build_thread(entries):
    """
    Build the main conversation thread from JSONL entries.

    Claude Code stores conversations as a linked list via parentUuid.
    This walks from the root (parentUuid=None) following the most recent
    branch at each step, skipping sidechains (subagent calls).
    """
    # Build children map only for entries with real UUIDs.
    # Metadata entries (file-history-snapshot, custom-title, etc.) have uuid=None
    # and must be excluded — they all have parentUuid=None too, which would
    # flood the root and hide the real first message.
    # We DO include system entries (e.g. turn_duration) because they have real
    # UUIDs and appear as intermediate links in the chain between real messages.
    children = {}
    for e in entries:
        if e.get('isSidechain') or not e.get('uuid'):
            continue
        parent = e.get('parentUuid')
        if parent not in children:
            children[parent] = []
        children[parent].append(e)

    thread = []
    current_uuid = None
    visited = set()

    RENDERABLE = ('user', 'assistant')
    TRAVERSABLE = ('user', 'assistant', 'system')

    while True:
        kids = children.get(current_uuid, [])
        if not kids:
            break

        # Prefer user/assistant children over progress/metadata.
        # progress entries branch off with later timestamps and would
        # hijack the chain if we just took kids[-1].
        real_kids = [k for k in kids if k.get('type') in TRAVERSABLE]
        next_entry = sorted(real_kids or kids, key=lambda e: e.get('timestamp', ''))[-1]

        uuid = next_entry.get('uuid')
        if uuid in visited:
            break
        visited.add(uuid)
        if next_entry.get('type') in RENDERABLE:
            thread.append(next_entry)
        current_uuid = uuid

    return thread


def find_session(arg):
    """Resolve a session ID or path to a .jsonl file path."""
    if arg.endswith('.jsonl'):
        return arg

    # Direct match in projects dir
    matches = globmod.glob(str(CLAUDE_PROJECTS_DIR / '**' / f'{arg}.jsonl'), recursive=True)
    if matches:
        return matches[0]

    print(f"Could not find session: {arg}")
    print(f"Looked in: {CLAUDE_PROJECTS_DIR}")
    print("Pass a full path to a .jsonl file, or a session UUID.")
    sys.exit(1)


def list_sessions():
    """Print all available sessions with their start time and first message."""
    pattern = str(CLAUDE_PROJECTS_DIR / '**' / '*.jsonl')
    files = globmod.glob(pattern, recursive=True)

    sessions = []
    for f in files:
        if '/subagents/' in f:
            continue
        ts, first_msg = '', ''
        with open(f) as fh:
            for line in fh:
                try:
                    obj = json.loads(line)
                    if not ts and obj.get('timestamp'):
                        ts = obj['timestamp']
                    if obj.get('type') == 'user':
                        msg = obj.get('message', {})
                        content = msg.get('content', '')
                        if isinstance(content, str):
                            first_msg = content[:80]
                            break
                        elif isinstance(content, list):
                            for b in content:
                                if isinstance(b, dict) and b.get('type') == 'text':
                                    first_msg = b['text'][:80]
                                    break
                            if first_msg:
                                break
                except:
                    pass
        sid = Path(f).stem
        sessions.append((ts, sid, first_msg.replace('\n', ' ')))

    sessions.sort(reverse=True)
    print(f"\n{BOLD}Claude Code Sessions{RESET}\n")
    for ts, sid, msg in sessions:
        date = ts[:10] if ts else 'unknown'
        print(f"  {DIM}{date}{RESET}  {GREY}{sid}{RESET}")
        print(f"           {WHITE}{msg}{RESET}\n")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print(f"\n{BOLD}render_chat{RESET} — Replay a Claude Code conversation in your terminal\n")
        print("Usage:")
        print("  render_chat.py <session-id>          # render by session UUID")
        print("  render_chat.py <path/to/file.jsonl>  # render by file path")
        print("  render_chat.py --list                # list all sessions\n")
        print("Session UUIDs are found in ~/.claude/projects/")
        sys.exit(0)

    if sys.argv[1] == '--list':
        list_sessions()
        sys.exit(0)

    path = find_session(sys.argv[1])
    print(f"\n{DIM}Loading: {path}{RESET}\n")

    entries = []
    with open(path) as f:
        for line in f:
            try:
                entries.append(json.loads(line))
            except:
                pass

    thread = build_thread(entries)

    # Scan entries for session metadata
    session_id, version = '', ''
    for e in entries:
        if not session_id and e.get('sessionId'):
            session_id = e['sessionId']
        if not version and e.get('version'):
            version = e['version']
        if session_id and version:
            break

    ts_start = thread[0].get('timestamp', '') if thread else ''
    print(f"{BOLD}{'━' * min(TERM_WIDTH, 80)}{RESET}")
    print(f"{BOLD}Claude Code{RESET}  {DIM}v{version}{RESET}")
    print(f"{DIM}Session: {session_id}{RESET}")
    print(f"{DIM}Started: {ts_start[:10] if ts_start else 'unknown'}{RESET}")
    print(f"{BOLD}{'━' * min(TERM_WIDTH, 80)}{RESET}")

    for entry in thread:
        t = entry.get('type')
        msg = entry.get('message', {})
        content = msg.get('content', '')

        if t == 'user':
            if isinstance(content, str):
                render_user(content)
            elif isinstance(content, list):
                texts = [b for b in content if isinstance(b, dict) and b.get('type') == 'text']
                tool_results = [b for b in content if isinstance(b, dict) and b.get('type') == 'tool_result']
                if texts:
                    for b in texts:
                        render_user(b.get('text', ''))
                elif tool_results:
                    render_tool_result(tool_results)

        elif t == 'assistant':
            if isinstance(content, list):
                text_parts = []
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    btype = block.get('type')
                    if btype == 'text':
                        text_parts.append(block.get('text', ''))
                    elif btype == 'tool_use':
                        render_tool_use(block.get('name', ''), block.get('input', {}))
                if text_parts:
                    render_assistant('\n'.join(text_parts))

    print(f"\n{BOLD}{'━' * min(TERM_WIDTH, 80)}{RESET}\n")


if __name__ == '__main__':
    main()
