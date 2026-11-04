#!/usr/bin/env python3
"""The one thing a market research run does next, decided from its files.

    python3 next_step.py "$W" --usage <N>          # after plan.md is written (N: the 5-hour limit's % used)
    python3 next_step.py "$W" --returned <name>    # after every agent notification
    python3 next_step.py "$W" --cleared            # the user has cleared the blocked pages
    python3 next_step.py "$W" --drop-blocked       # the user says to go on without them (handover lists them)
    python3 next_step.py "$W" --retry              # after a STOP, the user says to try the step again
    python3 next_step.py "$W" --usage <N> --gap <name> "<sections>" "<what is missing>"
    python3 next_step.py "$W" --usage <N> --close  # the phase 7 checkpoint found no gap
    python3 next_step.py "$W" --usage <N>          # at delivery: the points this run used
    python3 next_step.py "$W" --usage <N> --from-logs  # research is already on disk: start at the log step

The main session runs it after planning and after every agent notification and
launches exactly what it prints, with the description and prompt it prints, and
nothing else. It exists because prose limits did not hold: the wine plan of 28
October 2026 said "one capture sweep follows research, then a lean researcher
logs the captures", and the main session still answered each returning card with
more agents (eighteen on top of the thirteen planned) and stopped before
drafting; the art run's main session made 233 requests at a mean context of
549k tokens doing work agents should have done.

The order it enforces:
  1. every card in plan.md's "## Cards", all at once, with one capturer for the
     bulleted URLs or GOOGLE lines under "## Walled pages";
  2. once every card is back, the walled pages the cards queued in
     walled-<card>.tsv, captured in parts of 24, one after another (one Chrome);
     a page not reached gets two more tries, then is listed in
     briefs/not-captured.tsv; a page reported BLOCKED is put to the user at once
     and sent again each time they clear it (--cleared), even past the cap on
     parts; each page keeps its own clearing time, so clearing one page never
     sends again the pages already saved after an earlier clearing;
  3. readers for the captures, at most 12 pages each, all at once; a reader back
     with no log has its pages read once more, by readers of half the size, and a
     page saved again after a sign-in is read again;
  4. the phase 7 checkpoint: at most two gap cards in the run, and none once the
     run has used 25 points of the 5-hour limit; otherwise --close;
  5. the log agent (merge, prove, fix until check_log.py exits zero); then the
     compiler's compile phase, which writes the research document; the reviewer; the compiler's fix phase;
     delivery. Nothing is drafted, no image is sourced and no PDF is built: a
     person writes the report from the research document.
A step whose file is missing afterwards (briefs/log-ok, the
research document, the review file, the document compiled again after the
review) gets one more fresh agent; a second miss stops the run with a line for
the user. Nothing here
changes what is checked. State and briefs live in $W/briefs/.
"""
import collections, datetime, json, pathlib, re, sys, time, urllib.parse

PART = 24     # pages per capture part: about ten browser calls, inside the capturer's cap of 15
READ = 12     # captured pages per reader
GAPS = 2      # gap cards per run
PARTS = 10    # capture parts per run, retries included
BUDGET = 25   # points of the 5-hour limit after which research takes no gap card
URLISH = re.compile(r'(https?://[^\s`<>)\]]+|GOOGLE site:[^`\n]+)')
SKILL = pathlib.Path('~/.claude/skills/claude-market-research').expanduser()


def norm(line):
    """Comparable form of a URL (no scheme, www, fragment or trailing slash); a GOOGLE line as it is."""
    line = line.strip()
    if line.startswith('GOOGLE'):
        return line
    u = urllib.parse.urlsplit(line)
    return u.netloc.lower().removeprefix('www.') + u.path.rstrip('/') + ('?' + u.query if u.query else '')


def site(line):
    if line.startswith('GOOGLE'):
        m = re.search(r'site:(\S+)', line)
        return m.group(1).split('/')[0].lower().removeprefix('www.') if m else ''
    return urllib.parse.urlsplit(line).netloc.lower().removeprefix('www.')


def read_plan(W):
    text = (W / 'plan.md').read_text(encoding='utf-8')
    body, head = collections.defaultdict(list), None
    for line in text.splitlines():
        if line.startswith('## '):
            head = line[3:].strip().lower()
        elif head:
            body[head].append(line)
    cards = next((v for k, v in body.items() if k.startswith('cards')), None)
    if cards is None:
        sys.exit('plan.md has no "## Cards" section: write the cards there first')
    names = [m.group(1) for l in cards for m in [re.match(r'### ([a-z0-9][a-z0-9-]*)', l)] if m]
    walled = next((v for k, v in body.items() if k.startswith('walled pages')), [])
    first = [m.group(1).strip() for l in walled if re.match(r'\s*[-*] ', l) and '<' not in l   # '<' marks a template line
             for m in [URLISH.search(l)] if m]
    m = re.search(r'^# Plan: (.+?)(?:, (?:research|report) date (\d{4}-\d{2}-\d{2}))?\s*$', text, re.M)
    return names, first, (m.group(1).strip() if m else 'market research'), (m.group(2) if m and m.group(2) else '')


def stamp(text):
    """An ISO time as an aware datetime (captures are stamped in local time, the state in UTC)."""
    try:
        t = datetime.datetime.fromisoformat(text.strip())
        return t if t.tzinfo else t.replace(tzinfo=datetime.timezone.utc)
    except ValueError:
        return datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)


def captures(W):
    """[(file name, {normalised URL read, normalised URL requested}, read time)] for every capture."""
    out = []
    for f in sorted((W / 'attested').glob('*.txt')):
        urls, when = set(), ''
        with open(f, encoding='utf-8', errors='replace') as fh:
            for line in fh:
                if line.startswith(('URL: ', 'Requested: ')):
                    urls.add(norm(line.split(':', 1)[1]))
                elif line.startswith('Read: '):
                    when = line[6:].strip()
                elif line.startswith('Hidden: '):
                    urls = set()                         # the signed-out page: never found, never read
                    break
                elif line.startswith('--- page text'):
                    break
        if urls:
            out.append((f.name, urls, stamp(when)))
    return out


def queued(W, names):
    """Walled pages the named agents asked for: [url or GOOGLE line, agent, wanted, section]."""
    rows, seen = [], set()
    for n in names:
        p = W / f'walled-{n}.tsv'
        if not p.exists():
            continue
        for line in p.read_text(encoding='utf-8', errors='replace').splitlines():
            cols = [c.strip() for c in line.split('\t')] + ['', '']
            if not URLISH.match(cols[0]) or (norm(cols[0]), n) in seen:
                continue
            seen.add((norm(cols[0]), n))
            rows.append([cols[0], n, cols[1], cols[2]])
    return rows


def blocks(W):
    """{normalised URL: (times reported BLOCKED, what the user must do)}, from the capturers' file."""
    out = {}
    p = W / 'briefs' / 'blocked.tsv'
    for line in p.read_text(encoding='utf-8', errors='replace').splitlines() if p.exists() else []:
        cols = [c.strip() for c in line.removeprefix('BLOCKED').strip().split('\t')] + ['']
        m = URLISH.match(cols[0])
        if m:
            k = norm(m.group(1))
            out[k] = (out.get(k, (0, ''))[0] + 1, cols[1] or cols[0][m.end():].strip())
    return out


def found(page, caps, st):
    """The capture file for a queued page, or None. A GOOGLE line is found by any capture on its
    site made after the part that ran it went out."""
    k = norm(page)
    if not page.startswith('GOOGLE'):
        return next((f for f, us, _ in caps if k in us), None)
    tied = [f for f, us, _ in caps if k in us]           # captured with this GOOGLE line as its Requested
    if tied:
        return tied
    sent = [stamp(p['issued']) for p in st['captures'] if page in p['pages']]
    if not sent:
        return None
    t0, s = min(sent), site(page)
    return [f for f, us, when in caps if when >= t0
            and any(u.split('/')[0] == s or u.split('/')[0].endswith('.' + s) for u in us)] or None


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')


def save(sp, st):
    sp.write_text(json.dumps(st, indent=1))


def launch(kind, name, prompt):
    print(f'LAUNCH {kind} | description: {name} | prompt: {prompt}')


def capture_part(W, st, pages):
    name = f'capture-{len(st["captures"]) + 1}'
    pages = sorted(pages, key=lambda r: site(r[0]))
    (W / 'briefs' / f'{name}.tsv').write_text(''.join('\t'.join(r) + '\n' for r in pages), encoding='utf-8')
    st['captures'].append({'name': name, 'pages': [r[0] for r in pages], 'issued': now()})
    for r in pages:
        st['tries'][norm(r[0])] = st['tries'].get(norm(r[0]), 0) + 1
    launch('market-research-capturer', name,
           f'Capture list: {W}/briefs/{name}.tsv (page, card, what it should state, section). Workings: {W}. '
           f'Append each BLOCKED line to {W}/briefs/blocked.tsv as well as returning it.')


def used(st):
    """Points of the 5-hour limit used since the start, or None when it cannot be told."""
    u = [x for x in st.get('usage', []) if x[1] is not None]
    if len(u) < 2 or u[0][0] != 'start':
        return None
    d = u[-1][1] - u[0][1]
    return d if d >= 0 else None


# ---- after research: the file each step leaves, and the briefs --------------------------------

def files(W, title):
    return {'md': W.parent / f'{title}.md', 'analysis': W / 'analysis.md'}   # the document sits beside $W


def mtime(p):
    return p.stat().st_mtime if p.exists() else 0


def step_ok(step, W, st, f):
    t0 = st['launched'].get(step, 0)
    # A compiler phase launched with a marker in its brief is done only when it touched it: on 29 October 2026
    # a writer was cut off by the usage limit after its files and before its last check, and the files alone
    # told the run the phase was complete.
    if step in st.get('marked', []) and mtime(W / 'briefs' / f'{step}-ok') < t0:
        return False
    if step == 'log':
        return mtime(W / 'briefs' / 'log-ok') >= t0 > 0
    if step == 'compile':
        return mtime(f['md']) >= t0 > 0
    if step == 'review':
        return any(mtime(p) >= t0 > 0 for p in W.glob('review-*.md'))
    if step == 'fix':
        # compile_research.py writes the document only when its checks pass, so a document newer than the
        # review is one compiled again, and passed, after it
        review = max((mtime(p) for p in W.glob('review-*.md')), default=0)
        return mtime(f['md']) >= max(review, t0) > 0
    return True


def brief(W, st, step, name, title, date, f):
    """Write the brief for one agent after research, and print its launch."""
    common = (f'Research: the {title}, research date {date}. Workings ($W): {W}. plan.md\'s header gives the field, '
              f'the scope, the ranking basis and whether sections 9 and 10 are in.')
    compiler = (f'{common}\nResearch document: {f["md"]}, which compile_research.py writes from {f["analysis"]} '
                f'(you write that) and the evidence. Evidence: {W}/sources-log.md (check_log.py exits zero). Stock: '
                f'{W}/stock/stock.tsv when sections 9 and 10 are in. Dropped and not captured:'
                f' {W}/dropped.md and {W}/briefs/not-captured.tsv.\nSections: Dan\'s eleven, in structure.md '
                f'order, named for the field; sections 9 and 10 as plan.md says.\nReturn at most 15 lines.')
    kind = 'market-research-compiler'
    if step == 'log':
        kind = 'market-research-researcher'
        text = (f'# Log brief: merge and prove the evidence log\n\n{common}\n\n'
                f'1. `python3 {SKILL}/scripts/merge_logs.py --workings "{W}" --force` (it keeps the old log as '
                f'sources-log.prev.md), then '
                f'`python3 {SKILL}/scripts/check_log.py "{W}/sources-log.md"` (Bash timeout 600000).\n'
                f'2. Fix each failure it prints in the research-*.log.md file that holds the item, never in '
                f'sources-log.md and never in a gate: re-read the saved page with find_figures.py and copy the quote, '
                f'price and basis as the page states them. If the page does not state the figure, delete the block and '
                f'add a line to {W}/dropped.md: the item, its URL and the reason.\n'
                f'3. Repeat 1 and 2 until check_log.py exits zero, then `touch "{W}/briefs/log-ok"`. Nothing else is '
                f'researched or fetched. Call cap 25.\n')
    elif step == 'review':
        kind = 'market-research-reviewer'
        text = (f'# Review brief\n\nResearch date {date}. Research document: {f["md"]}. Analysis: {f["analysis"]}. '
                f'Workings ($W): {W}. Write the findings to {W}/review-{date}.md.\n')
    elif step == 'fix':
        review = max(W.glob('review-*.md'), key=mtime, default=W / f'review-{date}.md')
        text = f'# Compiler brief: phase fix\n\n{compiler}\nReview findings: {review}.\nPhase: fix.\n'
    else:
        text = f'# Compiler brief: phase {step}\n\n{compiler}\nPhase: {step}.\n'
    if kind == 'market-research-compiler':
        text += (f'Last: when every step of the phase is done, and only then, run `touch "{W}/briefs/{step}-ok"`. '
                 f'A phase that stops before that is given to a fresh agent.\n')
        st.setdefault('marked', []).append(step) if step not in st.get('marked', []) else None
    (W / 'briefs' / f'{name}.md').write_text(text, encoding='utf-8')
    st['post'].append(name)
    st['launched'][step] = time.time()
    st['tries'][f'step:{step}'] = st['tries'].get(f'step:{step}', 0) + 1
    launch(kind, name, f'Brief: {W}/briefs/{name}.md. Read it, then follow your agent file.')


ORDER = ['log', 'compile', 'review', 'fix']


def after_research(W, st, sp, title, date):
    f = files(W, title)
    if not st['post']:
        print('Research is closed. Launch this now.')
        brief(W, st, 'log', 'log', title, date, f)
        save(sp, st)
        return
    for step in ORDER:
        tries = st['tries'].get(f'step:{step}', 0)
        if tries and step_ok(step, W, st, f):
            continue
        extra = st.setdefault('extra', {})
        if tries >= 2 + extra.get(step, 0) and st.pop('retry', False):
            extra[step] = extra.get(step, 0) + 1          # the user's go-ahead: one more fresh agent
        if tries >= 2 + extra.get(step, 0):
            st.pop('retry', None)
            save(sp, st)
            print(f'STOP: {tries} fresh agents have not completed the {step} step. Tell the user in one line what '
                  f'the last one returned for it, and wait for their answer. If they say to try again, run '
                  f'next_step.py "$W" --retry; it launches one more fresh agent for the step.')
            return
        brief(W, st, step, step if not tries else f'{step}-{tries + 1}', title, date, f)
        save(sp, st)
        return
    st['delivered'] = True
    save(sp, st)
    pts = used(st)
    print(f'DELIVER: the research document is compiled, reviewed and fixed: {f["md"]}. Read the 5-hour limit with '
          f'get_usage and run next_step.py "$W" --usage <N> for the points this run used; run run_cost.py; write the '
          f'handover from the fix compiler\'s return, {W}/dropped.md and {W}/briefs/not-captured.tsv.'
          + (f' So far: {pts} points of the 5-hour limit.' if pts is not None else ''))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    W = pathlib.Path(sys.argv[1]).expanduser()
    args = sys.argv[2:]
    (W / 'briefs').mkdir(exist_ok=True)
    sp = W / 'briefs' / 'state.json'
    names, first, title, date = read_plan(W)
    pct = None
    if '--usage' in args:
        try:
            pct = int(str(args[args.index('--usage') + 1]).rstrip('%'))
        except (IndexError, ValueError):
            sys.exit('--usage takes the 5-hour limit\'s percent used, a whole number')

    if not sp.exists() and '--from-logs' in args:
        logs = sorted(W.glob('research-*.log.md'))
        if not logs:
            sys.exit('--from-logs: no research-*.log.md in the workings folder')
        st = {'cards': names, 'gaps': [], 'returned': list(names), 'captures': [], 'tries': {}, 'cleared': {},
              'asked': [], 'readers': [], 'read': [], 'closed': True, 'post': [], 'launched': {},
              'usage': [['start', pct, now()]] if pct is not None else []}
        print(f'Starting from the {len(logs)} research logs on disk; no research is run.')
        after_research(W, st, sp, title, date)
        return
    if not sp.exists():
        if not 8 <= len(names) <= 12:
            sys.exit(f'plan.md has {len(names)} cards under "## Cards"; the skill allows 8 to 12')
        st = {'cards': names, 'gaps': [], 'returned': [], 'captures': [], 'tries': {}, 'cleared': {},
              'asked': [], 'readers': [], 'read': [], 'closed': False, 'post': [], 'launched': {},
              'usage': [['start', pct, now()]] if pct is not None else []}
        print(f'Research for the {title}: launch all of these now, in the background, in one message.'
              + ('' if pct is not None else ' No --usage was given, so the run cannot measure its share of the 5-hour limit.'))
        for n in names:
            launch('market-research-researcher', n,
                   f'Card {n} of the {title}. Workings: {W}. Read your card in plan.md, then follow your agent file.')
        if first:
            capture_part(W, st, [[u, 'walled-first', 'the page as plan.md names it', ''] for u in first])
        save(sp, st)
        return

    st = json.loads(sp.read_text())
    if pct is not None:
        st['usage'].append(['now', pct, now()])
    every = (st['cards'] + st['gaps'] + [c['name'] for c in st['captures']] + [r['name'] for r in st['readers']]
             + st['post'])
    if '--returned' in args:
        said = args[args.index('--returned') + 1] if len(args) > args.index('--returned') + 1 else ''
        hits = sorted((n for n in every if n not in st['returned'] and re.search(rf'(^|[^a-z0-9-]){re.escape(n)}($|[^a-z0-9-])', said)),
                      key=len, reverse=True)
        if not hits:
            sys.exit(f'"{said}" is none of the agents still out: {", ".join(n for n in every if n not in st["returned"])}')
        st['returned'].append(hits[0])
    if '--cleared' in args:                              # each page keeps the time it was itself cleared
        cw = st.setdefault('cleared_when', {})
        for k, (n, _) in blocks(W).items():
            if n > st['cleared'].get(k, 0):
                cw[k] = now()
            elif k in st['cleared'] and k not in cw and st.get('cleared_at'):
                cw[k] = st['cleared_at']                 # cleared before the state kept a time per page
        st['cleared'] = {k: n for k, (n, _) in blocks(W).items()}
        st['cleared_at'] = now()
    if '--retry' in args:                                # the user's go-ahead after a STOP
        st['retry'] = True
    if '--drop-blocked' in args:                         # the user's decision: go on without them
        still = {k for k, (n, _) in blocks(W).items() if n > st['cleared'].get(k, 0)}
        st['dropped_blocked'] = sorted(set(st.get('dropped_blocked', [])) | still)
    if st.get('delivered'):
        save(sp, st)
        pts = used(st)
        print('DELIVERED. ' + (f'This run used {pts} points of the 5-hour limit ({st["usage"][0][1]}% to '
              f'{st["usage"][-1][1]}%).' if pts is not None else 'The points used cannot be told: no reading at the '
              'start, or the 5-hour window reset during the run.'))
        return
    if '--gap' in args:
        i = args.index('--gap')
        g, sec, what = (args[i + 1:i + 4] + ['', '', ''])[:3]
        pts = used(st)
        if st['closed']:
            print('REFUSED: research is closed. Put the gap in the handover.')
        elif len(st['gaps']) >= GAPS:
            print('REFUSED: both gap cards are used. Put the gap in the handover.')
        elif pts is not None and pts >= BUDGET:
            print(f'REFUSED: the run has used {pts} points of the 5-hour limit, and research takes no gap card past '
                  f'{BUDGET}. Put the gap in the handover and run next_step.py "$W" --close.')
        elif not set(st['cards']) <= set(st['returned']):
            print('REFUSED: wait until every planned card is back; a gap is judged on all of them.')
        elif not re.fullmatch(r'[a-z0-9][a-z0-9-]*', g or '') or g in every:
            print(f'REFUSED: "{g}" is not a new card name (lower case, digits and hyphens).')
        else:
            st['gaps'].append(g)
            with open(W / 'plan.md', 'a', encoding='utf-8') as fh:
                fh.write(f'\n## Gap card {g} (sections {sec})\n{what}\n')
            launch('market-research-researcher', g,
                   f'Gap card {g} of the {title}, sections {sec}: {what} Workings: {W}. '
                   f'Read the rules in plan.md, then follow your agent file.')
        save(sp, st)
        return

    out = [n for n in every if n not in st['returned']]
    if '--close' in args and not st['closed']:
        if out:
            save(sp, st)
            print('REFUSED: agents are still out; close at the checkpoint, when everything is back.')
            return
        st['closed'] = True
    caps, blk = captures(W), blocks(W)
    # a BLOCKED page is put to the user as soon as its capturer is back, never held for the checkpoint
    fresh = [(k, how) for k, (n, how) in blk.items() if n > st['cleared'].get(k, 0) and f'{k}#{n}' not in st['asked']]
    if fresh:
        st['asked'] += [f'{k}#{blk[k][0]}' for k, _ in fresh]
        print(f'ASK the user now, one line per site: {len(fresh)} page(s) are blocked in their Chrome, each left open in '
              f'the Claude tab group there for them to sign in on. When they say it is done, run next_step.py "$W" '
              f'--cleared; if they say to go on without them, next_step.py "$W" --drop-blocked.')
        for k, how in fresh:
            print(f'  BLOCKED {k}  {how}')
    if out:
        save(sp, st)
        print(f'WAIT: {len(out)} out ({", ".join(out)}). Do nothing until the next notification.')
        return
    if st['closed']:
        after_research(W, st, sp, title, date)
        return

    # A reader back with no log ran out of calls before writing: its pages are read again, once, by readers of
    # half the size. On 29 October 2026 read-2 logged nothing, and its pages, three of them lots the user had
    # signed in for, were never read.
    for r in st['readers']:
        if r.get('checked'):
            continue
        r['checked'] = True
        log = W / f'research-{r["name"]}.log.md'
        if log.exists() and re.search(r'^\*\*Item', log.read_text(encoding='utf-8', errors='replace'), re.M):
            continue
        f, keys = None, set()
        for line in (W / 'briefs' / f'{r["name"]}.md').read_text(encoding='utf-8').splitlines():
            if line.startswith('- attested/'):
                f = line[len('- attested/'):].strip()
            elif f and (m := re.match(r'  - card (\S+) \(', line)):
                keys.add(f'{f}\t{m.group(1)}')
        keys -= set(st.setdefault('reread', []))
        st['read'] = [x for x in st['read'] if x not in keys]
        st['reread'] += sorted(keys)

    needs = queued(W, st['cards'] + st['gaps'])
    # a page of the plan's own walled list that came back blocked is retried like any queued page
    needs += [[u, 'walled-first', 'what plan.md wants from this page', ''] for u in first if norm(u) in blk]
    # a blocked page reached through a search line, or under another address, is retried on its own once cleared
    have = {norm(r[0]) for r in needs}
    needs += [[k if k.startswith('GOOGLE') else 'https://' + k, 'blocked', 'the sold price and details of this lot, '
               'reached through a search line in the cards\' walled lists', ''] for k in blk if k not in have]
    todo, ask, dropped, seen = [], [], [], set()
    for r in needs:
        k = norm(r[0])
        if k in seen:
            continue
        tries, (nblk, how) = st['tries'].get(k, 0), blk.get(k, (0, ''))
        # A blocked page's capture is the signed-out one (or none): it waits for the user, and once they
        # have cleared it, only a capture made after the clearing counts.
        if k in st.get('dropped_blocked', []):
            seen.add(k)
            dropped.append(r)
            continue
        if nblk > st['cleared'].get(k, 0):              # blocked, or blocked again after a clearing
            seen.add(k)
            ask.append(r)
            continue
        owed = False
        if nblk:
            t = stamp(st.get('cleared_when', {}).get(k) or st.get('cleared_at') or '')
            if any(k in us and when >= t for _, us, when in caps):
                continue
            # one capture is owed after the user clears a page, whatever the parts used: on 29 October 2026
            # the user signed in to Bonhams after the tenth part, and the page went to not-captured.tsv unread
            owed = not any(stamp(p['issued']) >= t and k in {norm(x) for x in p['pages']} for p in st['captures'])
        elif found(r[0], caps, st):
            continue
        seen.add(k)
        if tries - nblk < 3 and (owed or len(st['captures']) < PARTS):
            todo.append(r)
        else:
            dropped.append(r)
    if ask and all(st['tries'].get(norm(r[0]), 0) for r in todo):
        todo = []                       # only retries left: they go with the cleared pages
    if todo:
        part = todo[:PART]
        print(f'Capture {len(part)} walled page(s) in the user\'s Chrome'
              + (f'; {len(todo) - PART} more go in the next part.' if len(todo) > PART else '.'))
        capture_part(W, st, part)
        save(sp, st)
        return
    if ask:
        save(sp, st)
        print(f'HOLD: {len(ask)} page(s) are blocked in the user\'s Chrome and everything else is captured. Wait for '
              f'the user: when they say it is done, run next_step.py "$W" --cleared; if they say to go on without '
              f'them, next_step.py "$W" --drop-blocked.')
        return
    if dropped:
        (W / 'briefs' / 'not-captured.tsv').write_text(''.join('\t'.join(r) + '\n' for r in dropped), encoding='utf-8')

    pages, saved = collections.OrderedDict(), {name: when for name, _, when in caps}
    for r in sorted(needs, key=lambda r: r[1]):
        k = norm(r[0])
        if k in st.get('dropped_blocked', []) or blk.get(k, (0, ''))[0] > st['cleared'].get(k, 0):
            continue                                    # its capture is the signed-out page: never read
        f = found(r[0], caps, st)
        for name in ([f] if isinstance(f, str) else f or []):
            # A page is read once per card that wants it, and again once saved again: a recapture after a
            # sign-in overwrites the same file. On 29 October 2026 the Bonhams lot the user signed in for
            # would never have been read again, its file name already marked read.
            key, at = f'{name}\t{r[1]}', st.get('read_at', {}).get(f'{name}\t{r[1]}')
            if key not in st['read'] or (at and saved.get(name, stamp(at)) > stamp(at)):
                pages.setdefault(name, []).append(r)
    if pages:
        items, first_reader, again = list(pages.items()), len(st['readers']), set(st.get('reread', []))
        weight = [2 if any(f'{f}\t{r[1]}' in again for r in rs) else 1 for f, rs in items]  # a page read again counts double
        total = sum(weight)
        n = -(-total // READ)               # as few readers as the cap allows, evenly filled
        groups, acc = [[] for _ in range(n)], 0
        for it, w in zip(items, weight):
            groups[min(n - 1, acc * n // total)].append(it)
            acc += w
        print(f'Read {len(items)} captured page(s): launch these {len(groups)} reader(s) now, in one message.')
        for k, group in enumerate(groups, first_reader + 1):
            name = f'read-{k}'
            text = [f'# Reader brief {name}: captured pages for the {title}', '',
                    f'Workings: {W}. Log to research-{name}.log.md. The rules are in plan.md and your agent file.',
                    'Read only the pages below, from attested/, with find_figures.py, and log each item as an',
                    'assisted read. Fetch nothing walled and queue nothing: a page that does not state what was',
                    'wanted yields only what it states. Before logging, grep the item headings of the other',
                    'research-*.log.md files and skip what they already hold.',
                    'Every block carries `- Access: assisted (user-chrome, <site>)` and `- Attested: attested/<the',
                    'file below>`: without them the gate fetches the live page, gets a 403 and fails the item.',
                    'Write each block to your log as soon as it checks, never all at the end: a reader that reaches',
                    'its cap with nothing written has all its work lost.', '']
            for f, rs in group:
                text.append(f'- attested/{f}')
                text += [f'  - card {r[1]} ({r[3] or "its sections"}): {r[2]}' for r in rs]
            (W / 'briefs' / f'{name}.md').write_text('\n'.join(text) + '\n', encoding='utf-8')
            st['readers'].append({'name': name, 'pages': len(group)})
            st['read'] += [f'{f}\t{r[1]}' for f, rs in group for r in rs]
            st.setdefault('read_at', {}).update({f'{f}\t{r[1]}': now() for f, rs in group for r in rs})
            launch('market-research-researcher', name,
                   f'Reader brief: {W}/briefs/{name}.md. Workings: {W}. Read the brief, then follow your agent file.')
        save(sp, st)
        return

    pts = used(st)
    if len(st['gaps']) >= GAPS or (pts is not None and pts >= BUDGET):
        st['closed'] = True
        after_research(W, st, sp, title, date)
        return
    save(sp, st)
    note = f' {len(dropped)} page(s) could not be captured (briefs/not-captured.tsv, for the handover).' if dropped else ''
    print(f'CHECKPOINT (phase 7): everything launched is back.{note} Read the 5-hour limit with get_usage. From the '
          f'returns, check each section against its fact budget. A gap ({GAPS - len(st["gaps"])} left, none past '
          f'{BUDGET} points used): next_step.py "$W" --usage <N> --gap <name> "<sections>" "<what is missing>". '
          f'No gap: next_step.py "$W" --usage <N> --close.')


if __name__ == '__main__':
    main()
