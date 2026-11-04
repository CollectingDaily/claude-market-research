#!/usr/bin/env python3
"""Build the research document from the proven evidence log and the compiler's analysis.

    python3 compile_research.py "$W"            # check, then write the research document
    python3 compile_research.py "$W" --check    # check only; write nothing
    python3 compile_research.py "$W" --items    # the log, one line per item, for the compiler to read

$W is <root>/Market research/<Topic>/workings. The document is written beside
it as <title>.md, the title from plan.md's first line, and as <title>.docx too
when pandoc is installed, for Word, LibreOffice and Google Docs.

The compiler agent writes only $W/analysis.md: per section, the items that serve
it, what they cover and what is missing; the rankings, resale pairs, heat
signals and conflicts, each figure with the item it comes from. Everything else
is copied here, never retyped: every item of sources-log.md in full, under the
first section that lists it; the stock; what was dropped or not captured; the
Sources. Images are the writer's: none is sourced here. A figure retyped is a figure that can be wrong.

analysis.md, one paragraph per line (a table row is a line):

    # Analysis
    Tags: <optional, comma-separated subject and object tags>

    ## Overview
    <what the research found, each figure with its item: [Item 12]>

    ## 1. <section title, named for the field>
    Items: 3, 4, 17-19        (or: Items: none)
    <what the section needs, from article-structure.md, and which items cover it>
    Missing: <what no item covers, or: nothing>

    ... sections 2 to 11, in structure.md order ...

    ## Heat signals
    ## Conflicts
    ## For the writer          (optional)

It refuses to write the document, printing one FAIL line each, when:
  - analysis.md lacks a heading it needs (Overview, sections 1 to 11, Heat
    signals, Conflicts), carries one it does not know, or a section lacks its
    Items: or Missing: line;
  - it names an item the log does not hold;
  - a price or percentage in it is not in the Price or Quote of an item named on
    the same line, in the same currency: nothing in the research document is
    converted, rounded or computed;
  - a count of a hundred or more, other than a year, is in no item named on its
    line;
  - it carries a URL that no item or stock line holds, or one of our own sites.
A line that starts "Rate:" is fx.py's rate line, pasted as it prints, and one
that starts "Bands:" names the budget bands' limits ("Bands: entry, under
£1,000; ..."): neither is checked for figures, because neither reports one.
An item no section lists, or one its card's sections do not list, is a WARN:
it is still printed in full.
"""
import collections, datetime, json, os, pathlib, re, shutil, subprocess, sys

ITEM = re.compile(r"^\*\*Item\s+(\d+)\s*:\s*(.+?)\*\*\s*$", re.M)
FIELD = re.compile(r"^\s*[-*]\s*([A-Za-z][A-Za-z ]*?)\s*:\s*(.*?)\s*$")
OURS = ('justcollecting.com', 'collectingdaily.com')
CUR = r'(US\$|HK\$|A\$|C\$|S\$|NZ\$|\$|£|€|¥|CHF|USD|GBP|EUR|HKD|JPY|AUD|CAD)'
MONEY = re.compile(CUR + r'\s?(\d[\d,]*(?:\.\d+)?)(?:\s?(million|billion|thousand|mn|bn|m|k)\b)?', re.I)
PCT = re.compile(r'(?<![\d.,])(\d+(?:\.\d+)?)\s?(%|per\s?cent\b|percent\b)', re.I)
COUNT = re.compile(r'(?<![\w$£€¥.,#/-])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?\s?(?:million|billion)\b|\d{3,})(?![\w%.,]*\d)', re.I)
REF = re.compile(r'\bItems?\s+(\d+(?:\s*(?:,|and|&|to|–|-)\s*\d+)*)', re.I)
URL = re.compile(r'https?://[^\s<>|`"\]]+')
MULT = {'million': 1e6, 'mn': 1e6, 'm': 1e6, 'billion': 1e9, 'bn': 1e9, 'thousand': 1e3, 'k': 1e3}
NEEDED = ['Overview'] + [str(n) for n in range(1, 12)] + ['Heat signals', 'Conflicts']
KNOWN = set(NEEDED) | {'For the writer'}


def cur(sym):
    s = sym.upper()
    return {'US$': '$', 'USD': '$', '$': '$', '£': '£', 'GBP': '£', '€': '€', 'EUR': '€', '¥': '¥', 'JPY': '¥',
            'HKD': 'HK$', 'AUD': 'A$', 'CAD': 'C$'}.get(s, s)


def num(text, unit=''):
    return float(text.replace(',', '')) * MULT.get((unit or '').lower(), 1)


def monies(text):
    return {(cur(m.group(1)), round(num(m.group(2), m.group(3)), 4)) for m in MONEY.finditer(text)}


def pcts(text):
    return {round(float(m.group(1)), 4) for m in PCT.finditer(text)}


def counts(text):
    out = set()
    for m in COUNT.finditer(text):
        t = m.group(1)
        w = re.match(r'([\d.]+)\s?(million|billion)', t, re.I)
        out.add(round(num(w.group(1), w.group(2)), 4) if w else round(num(t), 4))
    return out


def refs(text):
    out = set()
    for m in REF.finditer(text):
        nums = re.findall(r'\d+|–|-|to', m.group(1))
        prev = None
        for i, tok in enumerate(nums):
            if tok in ('–', '-', 'to') and prev is not None and i + 1 < len(nums) and nums[i + 1].isdigit():
                out.update(range(prev, int(nums[i + 1]) + 1))
            elif tok.isdigit():
                prev = int(tok)
                out.add(prev)
    return out


def item_list(text):
    """The numbers of an Items: line: 3, 4, 17-19."""
    out = set()
    for a, b in re.findall(r'(\d+)\s*(?:[-–]\s*(\d+))?', text):
        out.update(range(int(a), int(b or a) + 1))
    return out


def parse_log(path):
    raw = path.read_text(encoding='utf-8', errors='replace')
    marks = list(ITEM.finditer(raw))
    items = collections.OrderedDict()
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(raw)
        lines = [l.rstrip() for l in raw[m.end():end].strip('\n').splitlines() if l.strip()]
        fields = {}
        for l in lines:
            fm = FIELD.match(l)
            if fm:
                fields.setdefault(fm.group(1).strip().lower(), fm.group(2))
        items[int(m.group(1))] = {'name': m.group(2).strip(), 'lines': lines, 'f': fields}
    return items


def read_plan(W):
    text = (W / 'plan.md').read_text(encoding='utf-8')
    m = re.search(r'^# Plan: (.+?)(?:, (?:research|report) date (\d{4}-\d{2}-\d{2}))?\s*$', text, re.M)
    if not m:
        sys.exit('plan.md has no "# Plan: <Topic> market research, research date YYYY-MM-DD" line')
    lines = text.splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith('# Plan:'))
    head = []
    for l in lines[i + 1:]:
        if l.startswith('## '):
            break
        head.append(l)
    cards = {}
    for c, secs in re.findall(r'^#{2,3} (?:Gap card )?([a-z0-9][a-z0-9-]*) \(sections? ([^;)]*)', text, re.M):
        cards[c] = item_list(secs)
    return m.group(1).strip(), m.group(2) or '', [l for l in head if l.strip()], cards


def reader_cards(W):
    """{reader name: {attested file: {cards}}}, from the reader briefs next_step.py wrote."""
    out = {}
    for b in (W / 'briefs').glob('read-*.md'):
        cur_file, d = None, {}
        for line in b.read_text(encoding='utf-8', errors='replace').splitlines():
            if line.startswith('- attested/'):
                cur_file = line[len('- attested/'):].strip()
            elif cur_file and (m := re.match(r'  - card (\S+) \(', line)):
                d.setdefault(cur_file, set()).add(m.group(1))
        out[b.stem] = d
    return out


def parse_analysis(path):
    text = path.read_text(encoding='utf-8')
    pre, secs, head = [], collections.OrderedDict(), None
    for line in text.splitlines():
        if line.startswith('## '):
            head = line[3:].strip()
            secs[head] = []
        elif head is None:
            pre.append(line)
        else:
            secs[head].append(line)
    return pre, secs


def key(heading):
    m = re.match(r'(\d{1,2})\.\s+\S', heading)
    return m.group(1) if m else heading


def tsv(path):
    if not path.exists():
        return []
    rows = [l.split('\t') for l in path.read_text(encoding='utf-8', errors='replace').splitlines() if l.strip()]
    return rows


def spaced(lines):
    """analysis.md is one paragraph per line: a blank line between paragraphs, none inside a table or a list,
    so a line after a table is not read as one of its rows and two paragraphs do not run together."""
    out, prev = [], ''
    for l in lines:
        if not l.strip():
            continue
        kind = '|' if l.lstrip().startswith('|') else '-' if re.match(r'\s*([-*]|\d+\.) ', l) else 'p'
        if out and not (kind == prev and kind in '|-'):
            out.append('')
        out.append(l)
        prev = kind
    return out


def yq(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


def link(target, base):
    return '<' + os.path.relpath(target, base) + '>'


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    W = pathlib.Path(sys.argv[1]).expanduser().resolve()
    only_check = '--check' in sys.argv[2:]
    title, date, head, cards = read_plan(W)
    md = W.parent / f'{title}.md'
    log = W / 'sources-log.md'
    if not log.exists():
        sys.exit(f'no {log}: the log agent merges and proves it first')
    if '--items' in sys.argv[2:]:
        for i, it in parse_log(log).items():
            g = it['f'].get
            print(f'{i} | {g("from", "")} | {it["name"][:80]} | {g("status", "")[:26]} | {g("price", "")} | '
                  f'{g("basis", "")[:40]} | {g("house", "")} | {g("date", "")} | {g("copy", "")[:40]}')
        return
    if not (W / 'briefs' / 'log-ok').exists():
        print('WARN no briefs/log-ok: check_log.py has not been recorded as passing this log')
    items = parse_log(log)
    pre, secs = parse_analysis(W / 'analysis.md')
    fails, warns = [], []

    by_key = {}
    for h in secs:
        k = key(h)
        if k not in KNOWN:
            fails.append(f'FAIL heading "## {h}" is not one analysis.md uses (Overview, 1. to 11., Heat signals, '
                         f'Conflicts, For the writer)')
        elif k in by_key:
            fails.append(f'FAIL heading "## {h}" twice')
        else:
            by_key[k] = h
    fails += [f'FAIL no "## {k}{"." if k.isdigit() else ""}" heading in analysis.md' for k in NEEDED if k not in by_key]
    order = [by_key[k] for k in NEEDED + ['For the writer'] if k in by_key]
    shown = [h for h in order if h != 'For the writer']      # For the writer is printed last

    listed = collections.OrderedDict()           # item number -> sections that list it, in order
    for n in range(1, 12):
        h = by_key.get(str(n))
        if not h:
            continue
        il = [l for l in secs[h] if l.startswith('Items:')]
        ml = [l for l in secs[h] if l.startswith('Missing:')]
        if len(il) != 1:
            fails.append(f'FAIL "## {h}" needs exactly one "Items:" line')
        if len(ml) != 1:
            fails.append(f'FAIL "## {h}" needs exactly one "Missing:" line')
        for i in sorted(item_list(il[0][6:]) if il else []):
            listed.setdefault(i, []).append(h)

    stock = tsv(W / 'stock' / 'stock.tsv')[1:]
    known_urls = {r[3] for r in stock if len(r) > 3}
    for it in items.values():
        known_urls |= set(URL.findall('\n'.join(it['lines'])))
    known_urls = {u.rstrip('.,;)') for u in known_urls}

    for h in order:
        for line in secs[h]:
            if not line.strip():
                continue
            named = refs(line) | (item_list(line[6:]) if line.startswith('Items:') else set())
            for i in sorted(named - set(items)):
                fails.append(f'FAIL "## {h}": Item {i} is not in sources-log.md')
            for u in URL.findall(line):
                u = u.rstrip('.,;)')
                if any(d in u for d in OURS):
                    fails.append(f'FAIL "## {h}": {u} is one of our own sites, never read and never cited')
                elif u not in known_urls:
                    fails.append(f'FAIL "## {h}": {u} is in no item or stock line')
            if line.startswith(('Items:', 'Rate:', 'Bands:')):
                continue
            text = URL.sub(' ', line)
            text = REF.sub(' ', text)
            cited = [items[i] for i in named if i in items]
            pool = ' '.join(it['f'].get('price', '') + ' ' + it['f'].get('quote', '') for it in cited)
            allf = ' '.join(' '.join(it['lines']) + ' ' + it['name'] for it in cited)
            got_m, got_p = monies(pool), pcts(pool)
            got_c = counts(allf) | {v for _, v in monies(allf)} | {   # lenient: any number the item holds, lot numbers too
                round(float(x), 4) for x in re.findall(r'\d+(?:\.\d+)?', re.sub(r'(?<=\d),(?=\d{3})', '', allf))}
            for m in MONEY.finditer(text):
                if (cur(m.group(1)), round(num(m.group(2), m.group(3)), 4)) not in got_m:
                    fails.append(f'FAIL "## {h}": "{m.group(0).strip()}" ' + (
                        f'is not in the Price or Quote of Item {", ".join(map(str, sorted(named)))}, in that currency'
                        if named else 'names no item on its line'))
            for m in PCT.finditer(text):
                if round(float(m.group(1)), 4) not in got_p:
                    fails.append(f'FAIL "## {h}": "{m.group(0).strip()}" ' + (
                        f'is not in the Price or Quote of Item {", ".join(map(str, sorted(named)))}'
                        if named else 'names no item on its line'))
            bare = PCT.sub(' ', MONEY.sub(' ', text))
            for m in COUNT.finditer(bare):
                t = m.group(1)
                if re.fullmatch(r'1[0-9]\d\d|20\d\d|21\d\d', t):
                    continue                                    # a year
                w = re.match(r'([\d.]+)\s?(million|billion)', t, re.I)
                v = round(num(w.group(1), w.group(2)), 4) if w else round(num(t), 4)
                if v < 100:
                    continue
                if v not in got_c:
                    fails.append(f'FAIL "## {h}": the count "{t}" ' + (
                        f'is in no field of Item {", ".join(map(str, sorted(named)))}' if named
                        else 'names no item on its line'))

    # an item listed nowhere, or not under any section its card was planned for, is printed but flagged
    readers = reader_cards(W)
    for i, it in items.items():
        if i not in listed:
            warns.append(f'WARN Item {i} ({it["name"][:60]}) is listed under no section: printed under "Other evidence"')
            continue
        src = it['f'].get('from', '')
        want = set(cards.get(src, set()))
        if src in readers:
            att = it['f'].get('attested', '').removeprefix('attested/').strip()
            for c in readers[src].get(att, set()):
                want |= cards.get(c, set())
        got = {int(key(h)) for h in listed[i]}
        if want and not (want & got):
            warns.append(f'WARN Item {i} (from {src}, planned for sections {", ".join(map(str, sorted(want)))}) is '
                         f'listed under section {", ".join(map(str, sorted(got)))} only')

    for f in fails:
        print(f)
    for w in warns:
        print(w)
    if fails:
        print(f'FAILED: {len(fails)} failure(s); the research document was not written. Fix analysis.md, never the log.')
        sys.exit(1)
    if only_check:
        print(f'PASS (check only): {len(items)} items, {len(warns)} warning(s)')
        return

    # ---- the document ---------------------------------------------------------------------------------------
    tags = ['market_research', re.sub(r'[^a-z0-9]+', '_', title.lower().removesuffix(' market research')).strip('_')]
    for l in pre:
        if l.startswith('Tags:'):
            tags += [re.sub(r'[^a-z0-9]+', '_', t.strip().lower()).strip('_') for t in l[5:].split(',') if t.strip()]
    tags = list(dict.fromkeys(t for t in tags if t))
    sources = collections.OrderedDict()
    for it in items.values():
        u = it['f'].get('url', '').strip()
        if u:
            sources.setdefault(u, it['name'])
    # the stock was read from each collection's listing, not from its product pages: those listings are the sources
    for j in sorted((W / 'stock').glob('*.json')):
        sources.setdefault(f'https://www.paulfrasercollectibles.com/collections/{j.stem}/products.json?limit=250&page=1',
                           f'Paul Fraser Collectibles, {j.stem} collection listing')

    assisted = sum(1 for it in items.values() if it['f'].get('access', '').startswith('assisted'))
    out = ['---', f'Title: "{yq(title)}"', f'Date researched: {date}', 'tags:']
    out += [f'  - {t}' for t in tags]
    out += ['Sources:'] + [f'  - "{yq(n + " " + u)}"' for u, n in sources.items()]
    out += ['---', '', f'# {title}', '',
            f'Researched {date}. {len(items)} evidence items from {len(sources)} pages ({assisted} read in the user\'s '
            f'own Chrome), each one checked against its saved page before this document was compiled. '
            f'Every figure is exactly as its page states it, in its own currency and on its own basis (hammer, or total '
            f'with buyer\'s premium, as shown beside each price): nothing here is converted, rounded or computed. Every '
            f'item ends with the link to check it, and the pages as read are saved in workings/pages/ and workings/attested/.', '',
            '## The brief', ''] + head + ['', '## Coverage', '', '| Section | Items | Missing |', '| --- | --- | --- |']
    for n in range(1, 12):
        h = by_key[str(n)]
        il = next(l for l in secs[h] if l.startswith('Items:'))
        ml = next(l for l in secs[h] if l.startswith('Missing:'))
        out.append(f'| {h} | {len(item_list(il[6:]))} | {ml[8:].strip().replace("|", "/")} |')
    out.append('')

    def block(i):
        """One item for a reader: the price and its basis, house and date, the copy, the sentence off the page,
        the note, and the link to check it. Every field of the log is shown; only the working ones are not."""
        it, shown = items[i], {'from', 'url', 'status', 'price', 'basis', 'unit', 'copy', 'house', 'date', 'quote',
                               'note', 'access', 'attested'}
        g = lambda k: it['f'].get(k, '').strip()
        status = g('status').upper()
        kind = ('private sale' if 'PRIVATE' in status else 'fact' if status.startswith('CONTEXT')
                else 'auction record' if status else '')
        out = [f'**Item {i}: {it["name"]}**' + (f' ({kind})' if kind else ''), '']
        price = g('price')
        if price and price.lower() not in ('not stated', 'none', 'n/a'):
            out.append(f'- **{price}**, {g("basis") or "basis not recorded"}' + (f' ({g("unit")})' if g('unit') else ''))
        house, when = g('house') or 'not stated', g('date') or 'not stated'
        out.append('- House and date not stated' if house.lower() == when.lower() == 'not stated'
                   else f'- {house if house.lower() != "not stated" else "House not stated"}, '
                        f'{when if when.lower() != "not stated" else "date not stated"}')
        if g('copy') and g('copy').lower() != 'not stated':
            out.append(f'- Copy: {g("copy")}')
        if g('note'):
            out.append(f'- Note: {g("note")}')
        out += [f'- {k.capitalize()}: {v}' for k, v in it['f'].items() if k not in shown and v]
        if g('quote'):
            out += ['', f'> {g("quote")}']
        site = g('access').split(',', 1)[1].strip(' )') if g('access').startswith('assisted') and ',' in g('access') else ''
        out += ['', f'Check it: <{g("url")}>' + (f' (read signed in to {site}: the price may show only to someone '
                                                   f'signed in)' if site else ''), '']
        return out

    printed = set()
    for h in shown:
        out += [f'## {h}', '']
        out += spaced([l for l in secs[h] if not l.startswith(('Items:', 'Missing:'))])
        if key(h).isdigit():
            ml = next(l for l in secs[h] if l.startswith('Missing:'))
            nums = sorted(item_list(next(l for l in secs[h] if l.startswith('Items:'))[6:]))
            out += ['', f'**Missing:** {ml[8:].strip()}', '']
            fresh = [i for i in nums if i not in printed]
            again = [i for i in nums if i in printed]
            if nums:
                out += [f'### Evidence ({len(nums)} item{"s" if len(nums) != 1 else ""})', '']
            for i in fresh:
                out += block(i)
                printed.add(i)
            if again:
                out += ['Also for this section, in full under the section named:', '']
                out += [f'- Item {i}: {items[i]["name"]} ({listed[i][0]})' for i in again] + ['']
            if key(h) == '9' and stock:
                out += [f'### PFC stock ({len(stock)} available piece{"s" if len(stock) != 1 else ""}, stock.tsv pulled '
                        f'{datetime.date.fromtimestamp((W / "stock" / "stock.tsv").stat().st_mtime)})', '',
                        '| Piece | Price as listed | Image |', '| --- | --- | --- |']
                out += [f'| [{r[0].replace("|", "/")}]({r[3]}) | {r[1]} | '
                        + (f'[image]({link(r[4], md.parent)})' if len(r) > 4 and r[4] else 'none') + ' |'
                        for r in stock]
                out.append('')
        out.append('')

    out += ['## Dropped, not captured and not cleared', '']
    dropped = W / 'dropped.md'
    dl = [l for l in dropped.read_text(encoding='utf-8', errors='replace').splitlines() if l.strip()] if dropped.exists() else []
    out += ['### Dropped by the log check (dropped.md)', ''] + (dl or ['Nothing.']) + ['']
    nc = tsv(W / 'briefs' / 'not-captured.tsv')
    out += ['### Walled pages never captured (briefs/not-captured.tsv)', '']
    out += [f'- {r[0]}: wanted by {r[1] if len(r) > 1 else "?"} for {r[2] if len(r) > 2 else "?"}' for r in nc] or ['Nothing.']
    st = W / 'briefs' / 'state.json'
    db = json.loads(st.read_text()).get('dropped_blocked', []) if st.exists() else []
    out += ['', '### Blocked pages the user said to go on without', '']
    out += [f'- {k}' for k in db] or ['Nothing.']
    other = [i for i in items if i not in listed]
    if other:
        out += ['', f'## Other evidence ({len(other)} items no section lists)', '']
        for i in other:
            out += block(i)
    if 'For the writer' in by_key:
        out += ['', '## For the writer', ''] + spaced(secs[by_key['For the writer']])
    md.parent.mkdir(parents=True, exist_ok=True)
    md.write_text(re.sub(r'\n{3,}', '\n\n', '\n'.join(out)).rstrip() + '\n', encoding='utf-8')

    if shutil.which('ruby'):
        r = subprocess.run(['ruby', '-ryaml', '-rdate', '-e',
                            's=File.read(ARGV[0], encoding: "UTF-8"); fm=s[/\\A---\\n(.*?)\\n---\\n/m,1]; '
                            'd=YAML.safe_load(fm, permitted_classes: [Date]); bad=d["Sources"].reject{|x| x.is_a?(String)}; '
                            'puts bad.empty? ? "OK" : "BROKEN: #{bad.inspect}"', str(md)], capture_output=True, text=True)
        if r.stdout.strip() != 'OK':
            print(f'FAIL frontmatter does not parse as Obsidian needs: {(r.stdout + r.stderr).strip()[:300]}')
            sys.exit(1)
    docx = ''
    if shutil.which('pandoc'):                      # the same document for Word, LibreOffice and Google Docs
        ref = pathlib.Path(__file__).resolve().parent.parent / 'assets' / 'research-reference.docx'   # the house style
        r = subprocess.run(['pandoc', str(md), '-f', 'markdown-tex_math_dollars-raw_tex', '-o', str(md.with_suffix('.docx')),
                            f'--resource-path={md.parent}'] + ([f'--reference-doc={ref}'] if ref.exists() else []),
                           capture_output=True, text=True)
        docx = f' and {md.with_suffix(".docx").name}' if r.returncode == 0 else f' (no .docx: {r.stderr.strip()[:200]})'
    print(f'PASS: {len(items)} items ({len(other)} under Other evidence), {len(sources)} sources, '
          f'{len(warns)} warning(s) -> {md}{docx}')


if __name__ == '__main__':
    main()
