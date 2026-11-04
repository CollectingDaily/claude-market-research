#!/usr/bin/env python3
"""Prove the evidence log in one call: phase 5, with nothing left to reconcile
by hand.

    python3 check_log.py "<topic>-workings/sources-log.md"
    python3 check_log.py --part "<topic>-workings/research-<part>.log.md"

--part is for one researcher's share: the spread of houses is judged on the
merged log, where it means something, and nowhere else is anything relaxed.

It runs the same gates as before, each on the items it can actually judge, and
prints only what failed. Nothing is weaker: every item is still checked against
the page it cites, by the gates' own code.

  lint            every item: one bare URL, a Quote, a Price (or `not stated`),
                  a Basis for a price. A note on the URL line crashed
                  verify_sources.py in the comics run; this catches it first.
  whole log       verify_sources.py --offline: duplicates, currency
                  reproduction, mixed units and the spread of houses, which
                  only mean something across every item.
  priced items    verify_sources.py, online, on the items read unattended:
                  the price on the page, the quote verbatim.
  fact items      `Price: not stated` (a catalyst, a count, a definition):
                  the quote on the page, fetched with verify_sources.py's own
                  fetch_text. verify_sources.py reports these NO PRICE, so the
                  old rule "do not write until it exits zero" could never be
                  met by a log carrying facts.
  assisted reads  check_attested.py: price and quote against the capture.
                  verify_sources.py is not asked to re-fetch these, because it
                  can only report them DEAD/BLOCKED, three tries and ninety
                  seconds each, and every one of those lines then had to be
                  reconciled by hand.

A whole-number price in words ("$6 million") is too short for verify_sources.py
to parse; it is checked here by the rule check_attested.py uses, the exact
phrase on the page.

Full output of every gate goes to check-log.out beside the log. Exit 0 only
when every item stands up.
"""
import pathlib, re, subprocess, sys, tempfile

MEMO = pathlib.Path(__file__).resolve().parent   # verify_sources.py sits beside this script
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(MEMO))
from verify_sources import fetch_text, norm_numbers  # noqa: E402  (read-only reuse)

ITEM = re.compile(r"^\*\*Item\s+(\d+)\s*:\s*(.+?)\*\*\s*$", re.M)
FIELD = re.compile(r"^\s*[-*]\s*([A-Za-z ]+?)\s*:\s*(.+?)\s*$", re.M)
GATE_MONEY = re.compile(r"(?:US\$|\$|£|GBP|USD|EUR|€|HK\$)\s?([\d][\d,\.]{2,})")
WORDS_MONEY = re.compile(r"((?:US\$|\$|£|€)\s?\d{1,3})\s?(million|billion)\b", re.I)
PRICELESS = ('', 'not stated', 'none', 'n/a')


def parse(raw):
    marks = list(ITEM.finditer(raw))
    out = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(raw)
        block = raw[m.start():end]
        f = {k.strip().lower(): v.strip() for k, v in FIELD.findall(block)}
        out.append(dict(n=int(m.group(1)), name=m.group(2), block=block, **{
            'url': f.get('url', ''), 'price': f.get('price', ''), 'quote': f.get('quote', ''),
            'basis': f.get('basis', ''), 'access': f.get('access', ''),
            'copy': f.get('copy', '')}))
    return out


AMOUNT = re.compile(r"(?:US\$|\$|£|€|GBP|USD|EUR|HK\$)\s?(\d[\d,]*(?:\.\d+)?)\s?(million|billion|m|bn)?\b", re.I)


def amount(price):
    """The first sum on a Price line, as a number: $15,000,000 and $15 million agree."""
    m = AMOUNT.search(price)
    if not m:
        return None
    mult = {'million': 1e6, 'm': 1e6, 'billion': 1e9, 'bn': 1e9}.get((m.group(2) or '').lower(), 1)
    return round(float(m.group(1).replace(',', '')) * mult)


# Our own published articles are used for photographs only and are never read (the
# user's instruction, 13 October 2026; on 7 October: "those articles seem not to be
# quite reliable"). A PFC product page is a stock listing, not an article, and stays
# allowed.
OWN = re.compile(r'^https?://(www\.)?((news\.)?justcollecting\.com|collectingdaily\.com|'
                 r'paulfrasercollectibles\.com/blogs)(/|$)', re.I)


def run(args):
    p = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def quote_on(page, quote):
    q = re.sub(r"\s+", " ", re.sub(r"\[.*?\]", " ", quote.strip().strip('"\''))).strip()[:60]
    return bool(q) and (q.lower() in page.lower() or norm_numbers(q) in norm_numbers(page))


def main():
    if any(a in ('-h', '--help') for a in sys.argv[1:]):
        print(__doc__)
        return 0
    args = [a for a in sys.argv[1:] if a != '--part']
    part = '--part' in sys.argv  # one researcher's share: spread is judged on the merged log
    if len(args) != 1:
        sys.exit(__doc__)
    log = pathlib.Path(args[0]).expanduser().resolve()
    raw = log.read_text(encoding='utf-8')
    items = parse(raw)
    if not items:
        sys.exit(f'no "**Item N: name**" blocks in {log}')
    out = log.parent / 'check-log.out'
    record, fails = [], []

    # 1. lint: cheap, and a bad line here crashes or blinds everything after it
    for it in items:
        tag = f"{it['n']:02d} {it['name'][:50]}"
        if OWN.match(it['url']):
            fails.append(f"{tag}: our own articles are never used except for photographs, and never read (SKILL.md, 13 October 2026). "
                         f"Log the house's or publisher's own page instead: {it['url'][:70]}")
        if not re.fullmatch(r'https?://\S+', it['url']):
            fails.append(f"{tag}: URL line must hold one bare URL (notes go in a Note: line): {it['url'][:70]!r}")
        if not it['quote']:
            fails.append(f"{tag}: no Quote")
        if not it['price']:
            fails.append(f"{tag}: no Price line (write `not stated` for a fact)")
        elif it['price'].lower() not in PRICELESS and not it['basis']:
            fails.append(f"{tag}: a price with no Basis line (hammer, total, or not stated by the source)")
    if fails:
        print('LINT: fix these before anything is fetched\n  ' + '\n  '.join(fails))
        return 1

    assisted = [it for it in items if it['access'].lower().startswith('assisted')]
    facts = [it for it in items if it not in assisted and it['price'].lower() in PRICELESS]
    words = [it for it in items if it not in assisted and it not in facts
             and not GATE_MONEY.search(it['price']) and WORDS_MONEY.search(it['price'])]
    priced = [it for it in items if it not in assisted and it not in facts and it not in words]

    # 2. whole log, offline: the checks that only mean something across every item
    code, txt = run([MEMO / 'verify_sources.py', '--log', log, '--offline',
                     '--min-sources', '1' if part else '3'])
    record.append(f'### verify_sources.py --offline (whole log)\n{txt}')
    # verify_sources.py calls two Action Comics #1 at different grades
    # "near-identical", because the name is all it can see. The Copy line names
    # what tells a copy apart (grade, pedigree, restoration), so the pair can be
    # judged: different copies pass, the same copy at two prices is a resale
    # pair, the same copy at the same price is one sale logged twice and fails.
    by_n = {it['n']: it for it in items}
    distinct, resales = 0, []
    for line in txt.splitlines():
        s = line.strip()
        if s.startswith('DUPLICATE'):
            m = re.search(r'items (\d+) and (\d+)', s)
            x, y = (by_n.get(int(m.group(1))), by_n.get(int(m.group(2)))) if m else (None, None)
            if (x and y and x['price'].lower() in PRICELESS and y['price'].lower() in PRICELESS
                    and x['quote'].strip().lower() != y['quote'].strip().lower()):
                continue  # two different facts quoted off one page are not one object twice
            if not (x and y and x['copy'] and y['copy']):
                fails.append(f"{s}: give both a `- Copy:` line (grade, pedigree, restoration)")
            elif x['copy'].lower() != y['copy'].lower():
                distinct += 1
            elif amount(x['price']) != amount(y['price']):
                resales.append(f"items {x['n']:02d} and {y['n']:02d}: {x['copy']}")
            else:
                fails.append(f"{s}: the same copy at the same price is one sale logged "
                             "twice. Keep one; put the other URL in its Note")
        elif re.match(r'\d+\s+FX', s) or s.startswith(('ONE-HOUSE', 'FAIL: the prices come')):
            fails.append(s)
    notes = [l.strip() for l in txt.splitlines() if l.strip().startswith(('NOTE:', 'MIXED UNITS'))]

    # 3. priced items read unattended: the gate itself, online
    if priced:
        with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False) as t:
            t.write('\n'.join(it['block'] for it in priced))
        code, txt = run([MEMO / 'verify_sources.py', '--log', t.name, '--min-sources', '1'])
        record.append(f'### verify_sources.py (priced, unattended: {len(priced)})\n{txt}')
        for line in txt.splitlines():
            s = line.strip()
            if re.match(r'\d+\s+(NOT ON PAGE|DEAD/BLOCKED|NO PRICE|NO URL|QUOTE\?)', s):
                fails.append(s + ('' if 'QUOTE?' not in s else '  (price found; fix the quote)'))

    # 4. facts and whole-million prices, fetched with the gate's own fetch_text
    pages = {}
    for it in facts + words:
        tag = f"{it['n']:02d}  {it['name'][:46]}"
        if it['url'] not in pages:
            pages[it['url']] = fetch_text(it['url'])
        page, err = pages[it['url']]
        if page is None:
            fails.append(f"{tag}  DEAD/BLOCKED {err[:60]} -- browser rung, then mark it assisted")
            continue
        if it in words:
            m = WORDS_MONEY.search(it['price'])
            if re.sub(r'\s+', '', (m.group(1) + m.group(2)).lower()) not in re.sub(r'\s+', '', page.lower()):
                fails.append(f"{tag}  NOT ON PAGE {m.group(0)!r}")
        if not quote_on(page, it['quote']):
            fails.append(f"{tag}  QUOTE NOT ON PAGE {it['quote'][:50]!r}")
    record.append(f'### quotes checked here: {len(facts)} facts, {len(words)} whole-million prices')

    # 5. assisted reads, against their captures
    if assisted:
        code, txt = run([HERE / 'check_attested.py', log])
        record.append(f'### check_attested.py ({len(assisted)} assisted)\n{txt}')
        fails += [l.strip() for l in txt.splitlines() if l.strip().startswith('FAIL')]

    # The raw gate output below has FAIL lines of its own (verify_sources.py fails every name-alike pair, which
    # this script judges by the Copy lines). On 29 October 2026 a log agent spent its whole cap on 53 such items.
    head = (f"## check_log.py: {len(fails)} failure(s). Only these are failures; the raw gate output after them "
            f"is what they were judged from.\n" + ''.join(f"  {f}\n" for f in fails))
    out.write_text(head + '\n' + '\n\n'.join(record), encoding='utf-8')
    print(f"{len(items)} items: {len(priced)} priced read unattended, {len(words)} whole-million "
          f"prices, {len(facts)} facts, {len(assisted)} assisted reads")
    for n in notes:
        print('  ' + n)
    if distinct:
        print(f"  {distinct} name-alike pair(s) are different copies by their Copy lines")
    for r in resales:
        print(f"  same copy sold twice (resale pair, one entry in any ranking): {r}")
    if fails:
        print(f"\nFAIL: {len(fails)}\n  " + '\n  '.join(fails))
        print(f"\nFull gate output: {out}")
        return 1
    print(f"\nPASS: every item stands up on the page it cites. Full output: {out}")
    if assisted:
        print("Name the assisted sources in the handover (check-log.out lists them).")
    return 0


if __name__ == '__main__':
    sys.exit(main())
