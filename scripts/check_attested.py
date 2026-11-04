#!/usr/bin/env python3
"""Gate. Check the evidence log's assisted reads against what was actually read.

    python3 check_attested.py "<topic>-workings/sources-log.md"
    python3 check_attested.py "<...>/sources-log.md" --no-fetch

`verify_sources.py` re-fetches every URL in the log and hard-fails a bot-walled
one as DEAD/BLOCKED. It is right to: an unattended fetch of that page really does
return an interstitial. But a page a person cleared in front of us was read,
and the figure really was on it. This checks those items against the capture
`attest.py` saved at the moment of reading, so a source does not have to be
thrown away to get a clean run.

For every block carrying `Access: assisted` it checks:

  the capture exists, and its URL is the URL in the log
  the price in the log appears in the captured text
  the quote in the log appears in the captured text
  the method, the wall and who was present are all recorded

and, unless --no-fetch, it tries the URL unattended anyway. **A page that fetches
perfectly well does not need an attestation**, and one that has grown one is
either a transient failure recorded as permanent or a step being skipped. That is
reported, because an exception nobody re-examines stops being an exception and
becomes the route.

Every assisted source is printed, with its date, its method and what was in the
way. The count goes on the PASS line. A run that leaned on someone's presence
says so, in the same breath as it says it passed.
"""
import argparse, pathlib, re, sys, urllib.error, urllib.request

ITEM = re.compile(r"^\*\*Item\s+(\d+)\s*:\s*(.+?)\*\*\s*$", re.M)
FIELD = re.compile(r"^\s*[-*]\s*([A-Za-z ]+?)\s*:\s*(.+?)\s*$", re.M)
MONEY = re.compile(r"(?:US\$|\$|£|GBP|USD|EUR|€|HK\$)\s?([\d][\d,\.]{2,})")
# A whole number of millions written in words, "$6 million", has too few
# characters for MONEY. It is matched as the whole phrase, never as a bare digit,
# so a stray 6 on the page cannot pass it.
WORDS_MONEY = re.compile(r"((?:US\$|\$|£|€)\s?\d{1,3})\s?(million|billion)\b", re.I)
HEADER_END = '--- page text follows ---'
METHODS = ('browser-pane', 'user-chrome')
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def digits(s):
    return re.sub(r"[,\s  ]", "", s)


def parse_log(path):
    raw = pathlib.Path(path).read_text(encoding='utf-8', errors='replace')
    marks = list(ITEM.finditer(raw))
    out = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(raw)
        f = {k.strip().lower(): v.strip()
             for k, v in FIELD.findall(raw[m.end():end])}
        out.append({'n': int(m.group(1)), 'name': m.group(2).strip(),
                    'url': f.get('url', ''), 'price': f.get('price', ''),
                    'quote': f.get('quote', '') or f.get('evidence quote', ''),
                    'access': f.get('access', ''), 'attested': f.get('attested', '')})
    return out


def read_capture(path):
    raw = pathlib.Path(path).read_text(encoding='utf-8', errors='replace')
    if HEADER_END not in raw:
        return None, None
    head, body = raw.split(HEADER_END, 1)
    meta = {k.strip().lower(): v.strip()
            for k, v in re.findall(r"^([A-Za-z]+):\s*(.+)$", head, re.M)}
    return meta, body


def reachable(url):
    """True when an unattended fetch gets the real page, not a wall."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            if r.status != 200:
                return False
            text = r.read(400_000).decode('utf-8', 'replace')
    except Exception:
        return False
    flat = re.sub(r'<[^>]+>', ' ', text).lower()
    walls = ('just a moment', 'enable javascript and cookies',
             'checking your browser', 'verify you are human', 'cf-browser-verification')
    return len(flat.split()) > 250 and not any(w in flat for w in walls)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('log')
    ap.add_argument('--no-fetch', action='store_true',
                    help='skip the "did this actually need help?" re-test')
    a = ap.parse_args()

    log = pathlib.Path(a.log).expanduser()
    if not log.exists():
        sys.exit(f'not found: {log}')
    base = log.parent
    items = parse_log(log)
    if not items:
        sys.exit(f'no "**Item N: name**" blocks found in {log}')

    failures, warnings, noted = [], [], []

    for it in items:
        tag = f"item {it['n']:02d} {it['name'][:44]}"
        assisted = it['access'].lower().startswith('assisted')

        if it['attested'] and not assisted:
            failures.append(f"{tag}: has Attested: but no 'Access: assisted' line, "
                            "so nothing marks it as a page that needed help")
            continue
        if not assisted:
            continue
        if not it['attested']:
            failures.append(f"{tag}: marked assisted but carries no Attested: path. "
                            "Run attest.py at the moment you read the page.")
            continue

        cap = (base / it['attested']).resolve()
        if not cap.exists():
            failures.append(f"{tag}: Attested: {it['attested']} does not exist")
            continue
        meta, body = read_capture(cap)
        if meta is None:
            failures.append(f"{tag}: {cap.name} is not an attest.py capture "
                            "(no header). Do not hand-write these.")
            continue

        for field in ('url', 'read', 'method', 'wall', 'present'):
            if not meta.get(field):
                failures.append(f"{tag}: capture records no {field.title()}:")
        if meta.get('method') and meta['method'] not in METHODS:
            failures.append(f"{tag}: unknown method {meta['method']!r}; "
                            f"expected one of {', '.join(METHODS)}")
        if meta.get('url') and meta['url'].rstrip('/') != it['url'].rstrip('/'):
            failures.append(f"{tag}: the capture is of a different page.\n"
                            f"          log:     {it['url']}\n"
                            f"          capture: {meta['url']}")
            continue

        flat, page = re.sub(r'\s+', ' ', body).lower(), digits(body)   # a one-line Quote never holds the page's line breaks
        priceless = it['price'].strip().lower() in ('', 'not stated', 'none', 'n/a')
        want = [] if priceless else [digits(x) for x in MONEY.findall(it['price'])]
        if priceless:
            # A source cited for a fact rather than a figure: a catalyst, a
            # demographic, a specification change. The Royal Mint's "from 2026
            # all gold Sovereigns will return to being crafted from yellow gold"
            # is a real, checkable claim with no price in it, and failing it for
            # having no price would push the writer either to invent a figure or
            # to drop a verified fact. The quote still has to be on the page.
            if not it['quote'].strip():
                failures.append(f"{tag}: no price and no quote. An item has to "
                                "claim something checkable.")
        elif not want and WORDS_MONEY.search(it['price']):
            m = WORDS_MONEY.search(it['price'])
            phrase = re.sub(r'\s+', '', (m.group(1) + m.group(2)).lower())
            if phrase not in re.sub(r'\s+', '', flat):
                failures.append(f"{tag}: {m.group(0)!r} does not appear in the "
                                "captured text. The page we read does not state the "
                                "price the log claims for it.")
        elif not want:
            failures.append(f"{tag}: no figure parsed from the Price line")
        elif not any(w and w in page for w in want):
            failures.append(f"{tag}: {'/'.join(want[:2])} does not appear in the "
                            "captured text. The page we read does not state the "
                            "price the log claims for it.")
        q = re.sub(r'\s+', ' ', it['quote'].strip().strip('"').strip("'"))[:60]
        # " / " in a Quote joins lines of the page ("Sold For / $536"), unless the page itself prints it
        if q and not any(c.lower() in flat for c in (q, re.sub(r' / ', ' ', q))) and digits(q) not in page:
            failures.append(f"{tag}: the recorded quote is not in the captured "
                            f"text: {q[:56]!r}")

        noted.append(f"{tag}{' (no price claimed)' if priceless else ''}"
                     f"\n          {meta.get('wall','?')} cleared by "
                     f"{meta.get('present','?')} via {meta.get('method','?')}, "
                     f"{(meta.get('read') or '?')[:10]}\n          {it['url']}")

        if not a.no_fetch and reachable(it['url']):
            warnings.append(f"{tag}: this page fetches unattended right now. "
                            "Re-read it normally and drop the attestation, or say "
                            "in the log why the wall is intermittent.")

    for n in noted:
        print(f'  assisted  {n}')
    for w in warnings:
        print(f'  warn  {w}')
    for f in failures:
        print(f'  FAIL  {f}')

    tail = ', '.join(p for p in (
        f'{len(noted)} assisted' if noted else '',
        f'{len(warnings)} warning(s)' if warnings else '') if p)
    if failures:
        print(f'\nattested: {len(failures)} problem(s)' + (f', {tail}' if tail else '')
              + '.\nAn assisted read is still a read. Fix the record, or re-source '
                'the figure.')
        return 1
    print(f'\nattested: PASS' + (f' ({tail})' if tail else ' (no assisted reads)'))
    if noted:
        print('Say which sources needed a person, in the handover. '
              'verify_sources.py will report these URLs DEAD/BLOCKED; those lines '
              'are accounted for and every other one is not.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
