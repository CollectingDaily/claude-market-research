#!/usr/bin/env python3
"""Merge the research agents' log files into the one evidence log.

    python3 merge_logs.py --workings "<topic>-workings"

Each researcher writes `research-<part>.log.md` in the sources-log format
(`references/verification.md`). This joins them into `sources-log.md`, numbers
the items once from 1, records which file each came from, and carries the
"Source files read" lines to the top. It never edits an item.

It exists so the main session never reads a research file and types it back
out: in the comics run, merging three of them by hand added 50,000 tokens to a
context every later step paid for again.

It will not overwrite a sources-log.md that already exists, because by then
someone may have corrected it by hand. --force moves the old one to
sources-log.prev.md first.
"""
import argparse, pathlib, re, sys

ITEM = re.compile(r"^\*\*Item\s+(\d+)\s*:\s*(.+?)\*\*\s*$", re.M)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--workings', required=True)
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    work = pathlib.Path(a.workings).expanduser()
    parts = sorted(work.glob('research-*.log.md'))
    if not parts:
        sys.exit(f'no research-*.log.md in {work}')
    dest = work / 'sources-log.md'
    if dest.exists():
        if not a.force:
            sys.exit(f'{dest.name} exists. Re-run with --force to rebuild it '
                     '(the old one is kept as sources-log.prev.md).')
        dest.replace(work / 'sources-log.prev.md')

    read, blocks, urls = [], [], {}
    for p in parts:
        raw = p.read_text(encoding='utf-8')
        marks = list(ITEM.finditer(raw))
        head = raw[:marks[0].start()] if marks else raw
        read += [l.strip() for l in head.splitlines()
                 if re.match(r'(?i)\s*(source files read|read:)', l)]
        for i, m in enumerate(marks):
            end = marks[i + 1].start() if i + 1 < len(marks) else len(raw)
            body = raw[m.end():end].strip('\n')
            u = re.search(r'^\s*-\s*URL:\s*(\S+)', body, re.M)
            pr = re.search(r'^\s*-\s*Price:\s*(.+)$', body, re.M)
            key = (u.group(1) if u else '', pr.group(1).strip() if pr else '')
            urls.setdefault(key, []).append(f'{p.name} "{m.group(2)[:40]}"')
            blocks.append((m.group(2), p.stem.replace('research-', '').replace('.log', ''), body))
        print(f'{p.name}: {len(marks)} items')

    out = ['# Evidence log', '']
    out += list(dict.fromkeys(read)) or ['Source files read: (none recorded: add them)']
    out.append('')
    for n, (name, part, body) in enumerate(blocks, 1):
        out += [f'**Item {n}: {name}**', f'- From: {part}', body, '']
    dest.write_text('\n'.join(out), encoding='utf-8')
    print(f'{len(blocks)} items -> {dest}')
    for (u, pr), who in urls.items():
        if u and len(who) > 1:
            print(f'  same URL and price twice: {u} {pr}\n    ' + '\n    '.join(who))


if __name__ == '__main__':
    main()
