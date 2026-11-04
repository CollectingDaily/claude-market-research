#!/usr/bin/env python3
"""Read a saved page the cheap way: only the sentences that carry a figure or a
term you name, numbered so you can ask for the context around one.

    find_figures.py <files or folders> [--terms "superman,action comics"]
    find_figures.py pages/x.txt --around 41            # sentences 39 to 43
    find_figures.py pages/x.txt --quote "sold for $9.12 million" [--price '$9.12 million']

Works on what `fetch_pages.py` and `capture_server.py` save, and on attest.py
captures. The page header (URL, size, verdict) is printed for every file, so you
always know whether you are reading the real page before you read a figure on it.

The research agents of the comics report made roughly 330 shell calls between
them, most of them grep, sed and awk nibbling at the same saved pages, and each
call's output stayed in a context that every later call paid for again. One
call of this per batch of pages replaces them.

--quote checks a quote the way the gates do (verify_sources.py: the first 60
characters, case-insensitive, whitespace collapsed; check_attested.py the same
on the capture), and --price checks the price line the same way, so a log block
that passes here passes there.
"""
import argparse, pathlib, re, sys

HEADER_END = '--- page text follows ---'
MONEY = re.compile(r"(?:US\$|HK\$|A\$|C\$|\$|£|€|¥|\ufffd|GBP|USD|EUR|CHF)\s?\d[\d,\.]*"
                   r"(?:\s?(?:million|billion|m|bn|k)\b)?|\d[\d,\.]*\s(?:million|billion)\s"
                   r"(?:dollars|pounds|euros)|\d+(?:\.\d+)?\s?(?:%|per ?cent)", re.I)
GATE_MONEY = re.compile(r"(?:US\$|\$|£|GBP|USD|EUR|€|HK\$)\s?([\d][\d,\.]{2,})")
SPLIT = re.compile(r"(?<=[.!?])[\"”’)]?\s+(?=[\"“‘(]?[A-Z0-9£$€])")


def load(path):
    raw = path.read_text(encoding='utf-8', errors='replace')
    head, _, body = raw.partition(HEADER_END)
    if not body:
        head, body = '', raw
    meta = dict(l.split(': ', 1) for l in head.splitlines() if ': ' in l)
    return meta, body.strip()


ABBREV = re.compile(r"(?:\b(?:No|Nos|Vol|St|Mr|Mrs|Ms|Dr|Inc|Ltd|Co|Jr|Sr|vs|approx|est|"
                    r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)|\b[A-Z]|\bU\.S)\.$")


def sentences(body):
    """Split into sentences, but not after "No." in "Superman No. 1" or "Nov."
    in a date: a quote broken there no longer matches the page."""
    out = []
    for line in body.splitlines():
        joined = []
        for piece in SPLIT.split(line):
            piece = piece.strip()
            if joined and ABBREV.search(joined[-1]):
                joined[-1] += ' ' + piece
            elif piece:
                joined.append(piece)
        out += joined
    return [s for s in out if len(s) > 2]


def clip(s, terms, width):
    """A sentence that fits, or the windows of a long one around what matched.
    A lot list with no full stops arrives as one "sentence" the length of the
    page; cutting it at the start would hide the very figure being looked for."""
    if len(s) <= width:
        return s
    low = s.lower()
    hits = sorted({m.start() for m in MONEY.finditer(s)} |
                  {i for t in terms for i in [low.find(t)] if i >= 0})
    if not hits:
        return s[:width] + '…'
    spans, half = [], width // 3
    for h in hits[:4]:
        a, b = max(0, h - half), min(len(s), h + 2 * half)
        if spans and a <= spans[-1][1]:
            spans[-1][1] = b
        else:
            spans.append([a, b])
    return ' … '.join(s[a:b] for a, b in spans) + (' …' if spans[-1][1] < len(s) else '')


def digits(s):
    return re.sub(r"[,\s  ]", "", s)


def header(path, meta, body):
    state = meta.get('Verdict') or (f"attested {meta.get('Method', '')}, {meta.get('Wall', '')}"
                                    if meta.get('Method') else 'raw file')
    print(f"== {path} | {len(body):,} chars | {state} | {meta.get('URL', '?')}")
    if '\ufffd' in body:
        print("   NB: this page is not UTF-8, so the gates read its £ as \ufffd. Prices still "
              "match on their digits; copy a quote exactly as printed here, or quote a "
              "stretch without the sign.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--terms', default='', help='comma-separated, case-insensitive')
    ap.add_argument('--max', type=int, default=25, help='sentences per file (default 25)')
    ap.add_argument('--total', type=int, default=40, help='sentences in all (default 40)')
    ap.add_argument('--width', type=int, default=320)
    ap.add_argument('--around', type=int, help='print sentence N with two either side')
    ap.add_argument('--quote', help='check this quote is on the page as the gates check it')
    ap.add_argument('--price', help='check this Price line is on the page as the gates check it')
    a = ap.parse_args()

    files = []
    for p in map(pathlib.Path, a.paths):
        files += sorted(p.glob('*.txt')) if p.is_dir() else [p]
    terms = [t.strip().lower() for t in a.terms.split(',') if t.strip()]
    total_shown = 0

    for f in files:
        meta, body = load(f)
        header(f, meta, body)
        sents = sentences(body)

        if a.quote or a.price:
            flat = re.sub(r"\s+", " ", body)
            if a.quote:
                q = re.sub(r"\s+", " ", re.sub(r"\[.*?\]", " ", a.quote.strip().strip('"\''))).strip()[:60]
                ok = q.lower() in flat.lower() or digits(q) in digits(flat)
                print(f"   quote {'ON PAGE' if ok else 'NOT ON PAGE'}: {q!r}")
            if a.price:
                want = [digits(x) for x in GATE_MONEY.findall(a.price)]
                if not want:
                    print(f"   price: the gates parse no figure from {a.price!r} "
                          "(a whole-number '$6 million' has too few characters for "
                          "verify_sources.py; check_attested.py accepts it on a capture)")
                else:
                    hit = [w for w in want if w in digits(flat)]
                    print(f"   price {'ON PAGE' if hit else 'NOT ON PAGE'}: {'/'.join(want)}")
            continue

        if a.around is not None:
            for i in range(max(0, a.around - 2), min(len(sents), a.around + 3)):
                print(f"   [{i}] {sents[i][:a.width * 2]}")
            continue

        # No terms: every sentence with a figure in it. Terms: every sentence
        # naming one, plus a figure sentence straight after it, because "It sold
        # for $9.12 million" rarely repeats the name of the thing it sold.
        named = [any(t in s.lower() for t in terms) for s in sents]
        if total_shown >= a.total:
            print(f"   (not read: the {a.total}-sentence limit is reached; narrow --terms "
                  "or name fewer files)")
            continue
        shown, seen = 0, set()
        for i, s in enumerate(sents):
            low = s.lower()
            if terms:
                hit = named[i] or (i > 0 and named[i - 1] and MONEY.search(s))
            else:
                hit = bool(MONEY.search(s))
            if not hit:
                continue
            key = low[:120]
            if key in seen:
                continue
            seen.add(key)
            print(f"   [{i}] {clip(s, terms, a.width)}")
            shown += 1
            total_shown += 1
            if shown >= a.max or total_shown >= a.total:
                rest = sum(1 for j in range(i + 1, len(sents))
                           if (named[j] if terms else MONEY.search(sents[j])))
                if rest:
                    print(f"   … {rest} more; narrow with --terms or raise --max")
                break
        if not shown:
            print("   (nothing matched)")


if __name__ == '__main__':
    main()
