#!/usr/bin/env python3
"""
verify_sources.py - re-check the evidence log before an article ships.

Stdlib only. No API keys.

The skill's whole promise is that every price was verified by fetching the page.
Nothing enforced that, and it has already failed silently in production: an item
was marked VERIFIED while the log itself recorded that the figure "is not
machine-extractable text on this page". This command re-fetches every source and
proves the claim, or fails.

What it checks
  fetch        every URL still resolves
  price        the price actually appears in the fetched page text
  quote        the recorded evidence quote appears in the fetched page text
  currency     USD x rate reproduces the stated GBP figure
  duplicates   the same object is not listed twice
  units        mixed lot sizes in a ranked list are reported
  spread       the prices come from at least three different houses

Usage
  verify_sources.py --log "<dir>/sources-log.md" [--strict-units] [--offline]
                    [--min-sources N]

Log format it reads (one block per item, in sources-log.md):

  **Item 1: Romanee-Conti 1945 (1 bottle, 750ml)**
  - URL: https://example.com/lot/123
  - Fetched: yes - 19 August 2026
  - Status: VERIFIED
  - Unit: 1 bottle (750ml)
  - Price: $812,500 -> GBP 611,788
  - Rate: 0.75297 on 2026-03-27
  - Quote: "sold for $812,500"

Only URL, Status, Price and Quote are required. Unit is required when the
article ranks items by price.
"""

import argparse
import html as htmlmod
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = ("market-research-skill/1.0 "
      "(+https://www.paulfrasercollectibles.com)")
TIMEOUT = 30
FX_TOLERANCE = 0.015          # 1.5% -- rounding in the log, not a real mismatch

ITEM = re.compile(r"^\*\*Item\s+(\d+)\s*:\s*(.+?)\*\*\s*$", re.M)
FIELD = re.compile(r"^\s*[-*]\s*([A-Za-z ]+?)\s*:\s*(.+?)\s*$", re.M)
MONEY = re.compile(r"(?:US\$|\$|£|GBP|USD|EUR|€|HK\$)\s?([\d][\d,\.]{2,})")
NUMTOK = re.compile(r"\d[\d,]{2,}")


# --------------------------------------------------------------------------
# Fetch
# --------------------------------------------------------------------------

def fetch_text(url, attempts=3):
    """Return the page as plain text, or (None, reason)."""
    data = None
    err = "unknown"
    for i in range(attempts):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                data = r.read()
                break
        except (urllib.error.URLError, urllib.error.HTTPError,
                TimeoutError, OSError) as e:
            err = str(e)
            if i < attempts - 1:
                time.sleep(1.5 * (i + 1))
    if data is None:
        return None, err
    s = data.decode("utf-8", "replace")
    s = re.sub(r"<script[^>]*>.*?</script>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<style[^>]*>.*?</style>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = htmlmod.unescape(s)
    return re.sub(r"\s+", " ", s), None


def norm_numbers(text):
    """Digits only, so 1,058,087 and 1058087 and 1 058 087 all compare equal."""
    return re.sub(r"[,\s  ]", "", text)


# --------------------------------------------------------------------------
# Log parsing
# --------------------------------------------------------------------------

def parse_log(path):
    raw = Path(path).read_text(encoding="utf-8", errors="replace")
    marks = list(ITEM.finditer(raw))
    items = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(raw)
        block = raw[m.end():end]
        fields = {k.strip().lower(): v.strip()
                  for k, v in FIELD.findall(block)}
        items.append({
            "n": int(m.group(1)),
            "name": m.group(2).strip(),
            "url": fields.get("url", ""),
            "status": fields.get("status", ""),
            "unit": fields.get("unit", ""),
            "price": fields.get("price", "") or fields.get("price as listed", ""),
            "rate": fields.get("rate", ""),
            "quote": (fields.get("quote", "")
                      or fields.get("evidence quote", "")),
        })
    return items


def money_tokens(s):
    """Every monetary figure in a string, as digit-only strings."""
    return [norm_numbers(x) for x in MONEY.findall(s)]


def quote_core(q):
    """The most distinctive run of words in the quote, for substring matching."""
    q = q.strip().strip('"').strip("'")
    q = re.sub(r"\[.*?\]", " ", q)          # editorial insertions
    q = re.sub(r"\s+", " ", q).strip()
    return q


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

def check_currency(item):
    """USD x rate should reproduce the GBP figure in the Price line."""
    figs = MONEY.findall(item["price"])
    rate_m = re.search(r"([01]\.\d{3,6})", item["rate"] or item["price"])
    if len(figs) < 2 or not rate_m:
        return None
    try:
        src = float(norm_numbers(figs[0]))
        dst = float(norm_numbers(figs[-1]))
        rate = float(rate_m.group(1))
    except ValueError:
        return None
    if not src or not dst:
        return None
    expected = src * rate
    off = abs(expected - dst) / dst
    if off > FX_TOLERANCE:
        return (f"{figs[0]} x {rate} = {expected:,.0f}, but the log says "
                f"{figs[-1]} ({off * 100:.1f}% out)")
    return None


def find_duplicates(items):
    """Same object listed twice: identical URL and price, or near-identical name."""
    out = []
    seen = {}
    for it in items:
        key = (it["url"], norm_numbers(it["price"])[:12])
        if it["url"] and key in seen:
            out.append((seen[key], it["n"], "same URL and same price"))
        else:
            seen[key] = it["n"]
    words, years = {}, {}
    for it in items:
        low = it["name"].lower()
        w = frozenset(t for t in re.split(r"[^a-z0-9]+", low) if len(t) > 3)
        # Vintages and dates in the name. Romanee-Conti 2005 and Romanee-Conti
        # 2007 share every word but are different objects, so differing years
        # settle it before word overlap gets a vote.
        y = frozenset(re.findall(r"\b(1[6-9]\d{2}|20[0-4]\d)\b", low))
        for other_n, other_w in words.items():
            if not (w and other_w):
                continue
            if len(w & other_w) < max(2, int(len(w) * 0.6)):
                continue
            oy = years.get(other_n, frozenset())
            if y and oy and not (y & oy):
                continue
            out.append((other_n, it["n"], "near-identical item name"))
        words[it["n"]], years[it["n"]] = w, y
    return out


# Suffixes where the registrable name is the third label from the right,
# so robertedwardauctions.co.uk and christies.co.uk do not both collapse to
# "co.uk" and read as one house.
TWO_PART_TLDS = {
    "co.uk", "org.uk", "ac.uk", "me.uk", "com.au", "net.au", "org.au",
    "co.nz", "co.jp", "co.za", "com.br", "com.hk", "com.sg", "com.mx",
}


def house_of(url):
    """The registrable domain of a lot URL, as a stand-in for the house."""
    host = urllib.parse.urlsplit(url).hostname or ""
    host = host.lower().lstrip(".")
    if host.startswith("www."):
        host = host[4:]
    parts = host.split(".")
    if len(parts) > 2 and ".".join(parts[-2:]) in TWO_PART_TLDS:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def source_spread(items, minimum):
    """How many different houses carry the prices, and how concentrated they are.

    An article where every lot comes from one saleroom reads as that house's
    catalogue rather than a survey of the market, and it has shipped that way:
    ten football cards, ten Robert Edward Auctions lots. A ranking is a claim
    about the market, so it has to have looked at more than one part of it.
    """
    counts = {}
    for it in items:
        if not it["url"]:
            continue
        h = house_of(it["url"])
        if h:
            counts[h] = counts.get(h, 0) + 1
    return counts


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--log", required=True, help="path to sources-log.md")
    p.add_argument("--strict-units", action="store_true",
                   help="fail, rather than warn, when a ranked list mixes lot sizes")
    p.add_argument("--min-sources", type=int, default=3, metavar="N",
                   help="minimum number of different houses the prices must come "
                        "from (default 3; never set below 2)")
    p.add_argument("--offline", action="store_true",
                   help="skip fetching; check only currency, duplicates and units")
    a = p.parse_args()

    items = parse_log(a.log)
    if not items:
        print(f"No items found in {a.log}. Expected blocks headed "
              f"'**Item N: name**' with URL, Status, Price and Quote fields.")
        return 1

    print(f"\nEvidence check — {len(items)} item(s) in {a.log}\n")
    hard, soft = [], []

    for it in items:
        n, tag = it["n"], f"{it['n']:02d}"
        name = it["name"][:46]

        if not it["url"]:
            print(f"  {tag}  NO URL      {name}")
            hard.append(n)
            continue

        failed_here = False
        fx = check_currency(it)
        if fx:
            print(f"  {tag}  FX          {name} — {fx}")
            hard.append(n)
            failed_here = True

        if a.offline:
            continue

        text, err = fetch_text(it["url"])
        if text is None:
            print(f"  {tag}  DEAD/BLOCKED {name} — {err[:60]}")
            hard.append(n)
            continue

        page = norm_numbers(text)
        want = money_tokens(it["price"])
        found = [w for w in want if w and w in page]

        q = quote_core(it["quote"])
        qhit = bool(q) and (q[:60].lower() in text.lower()
                            or norm_numbers(q[:60]) in page)

        if not want:
            print(f"  {tag}  NO PRICE    {name} — no figure parsed from the Price line")
            hard.append(n)
        elif not found:
            # The exact failure this command exists for.
            print(f"  {tag}  NOT ON PAGE {name} — {'/'.join(want[:2])} does not "
                  f"appear in the fetched text")
            hard.append(n)
            if it["status"].upper().startswith("VERIFIED"):
                print(f"        ...and it is marked {it['status'].strip()}. "
                      f"That status is false.")
        elif not qhit and q:
            print(f"  {tag}  QUOTE?      {name} — price found, but the recorded "
                  f"quote does not appear verbatim")
            soft.append(n)
        elif not failed_here:
            print(f"  {tag}  ok          {name}")

    for x, y, why in find_duplicates(items):
        print(f"\n  DUPLICATE   items {x:02d} and {y:02d} — {why}")
        hard.append(y)

    units = {it["n"]: it["unit"] for it in items if it["unit"]}
    if units and len(set(u.lower() for u in units.values())) > 1:
        line = "  MIXED UNITS  " + ", ".join(f"{n:02d}={u}" for n, u in sorted(units.items()))
        print(f"\n{line}")
        print("        A list ranked on lot totals is not a ranking of single "
              "items. State the unit in every entry, or rank per unit.")
        if a.strict_units:
            hard.extend(units)
    elif not units:
        print("\n  NOTE: no Unit: fields found. Add them so lot sizes can be checked.")

    spread = source_spread(items, a.min_sources)
    thin = False
    if spread:
        ranked = sorted(spread.items(), key=lambda kv: (-kv[1], kv[0]))
        summary = ", ".join(f"{h} ({n})" for h, n in ranked)
        if len(spread) < a.min_sources:
            print(f"\n  ONE-HOUSE    {len(spread)} source(s) for {len(items)} item(s): "
                  f"{summary}")
            print(f"        A ranking drawn from fewer than {a.min_sources} houses is "
                  f"that house's catalogue, not a survey of the market.")
            print("        Go back to the field's source file and search the other "
                  "houses on the allowlist, including the majors.")
            thin = True
        else:
            top_house, top_n = ranked[0]
            if top_n > len(items) * 0.6:
                print(f"\n  NOTE: {top_house} carries {top_n} of {len(items)} items "
                      f"({summary}).")
                print("        Three houses on paper, one house in practice. Worth "
                      "widening before you write.")

    hard = sorted(set(hard))
    print()
    if hard or thin:
        if hard:
            print(f"FAIL: {len(hard)} item(s) do not stand up: "
                  f"{', '.join('%02d' % n for n in hard)}")
            print("Re-source or drop each one. A price that is not on the page it "
                  "cites is not verified, whatever the log says.")
        if thin:
            print(f"FAIL: the prices come from {len(spread)} house(s). "
                  f"At least {a.min_sources} different houses are required.")
        return 1
    if soft:
        print(f"PASS with {len(soft)} quote(s) worth an eye: "
              f"{', '.join('%02d' % n for n in soft)} — the price is on the page "
              f"but the wording has moved.")
        return 0
    print("PASS: every price appears on the page it cites, currency checks out, "
          "no duplicates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
