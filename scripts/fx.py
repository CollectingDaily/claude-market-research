#!/usr/bin/env python3
"""Fetch the ECB daily reference rate and convert, in either direction.

The workspace sourcing rules forbid inventing a number. That includes an
exchange rate. This pulls the published ECB reference rate so the rate in
the report is one that can be checked, and prints the date it applies to.

    python3 fx.py                    # just print today's rate
    python3 fx.py 3875000            # USD -> GBP (a bare number is dollars)
    python3 fx.py 3875000 1490000    # convert several
    python3 fx.py £2600000           # GBP -> USD, direction from the symbol
    python3 fx.py --gbp 2600000      # the same, said explicitly
    python3 fx.py £2.6m $50,000      # m / bn / million / billion, and commas
    python3 fx.py €1200000           # euros in, sterling and dollars out
    python3 fx.py --on 2026-02-16 $16492000   # the rate on a sale date instead

**Test "published" sterling before trusting it.** The house currency rules keep sterling that
a house or Guinness published at the sale-day rate. Our own articles' "approx. £"
figures are not that: the Pokémon top ten carries nine of them at about 1.28,
between -6.3% and +3.5% off the ECB rate on each sale's date. `--on` gives the
sale-day rate, so the test takes one line: if the published sterling does not
match the conversion on that date to within about 1%, it is not sale-day sterling
and it gets converted at the report's rate like any other figure.

Every amount prints in both sterling and dollars whatever went in, because the
house rule is sterling first with the dollar beneath it and a third currency
never stands in for either. Euros are here because numismatics needs them:
Stack's Bowers publishes its Scandinavian record at EUR 1,200,000 and nothing
else, and a report quoting that figure alone carries a price most of its readers
cannot size.

**The rate is bidirectional and so is the rule.** The house currency rules ask for sterling
first with the dollar beneath it, so a source publishing only dollars needs the
sterling computed, and a source publishing only sterling -- a private sale
reported in the British press, say -- needs the dollar computed. Both are
conversions and both get disclosed in the footnote. This script used to take
dollars only, which is how a Gretzky rookie at a published £2.6m reached a draft
with no dollar beside it: the reverse case looked like a gap in the tooling
rather than the same rule read backwards.
"""
import re, sys, urllib.request, xml.etree.ElementTree as ET

URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
HIST = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip"
SCALE = {"m": 1e6, "million": 1e6, "bn": 1e9, "b": 1e9, "billion": 1e9, "k": 1e3}
CCY = ("USD", "GBP", "EUR")

def rate():
    """(date, {currency: units per EUR}). The ECB quotes against the euro, so
    EUR is the native base here and every cross rate comes out of one table."""
    with urllib.request.urlopen(URL, timeout=20) as r:
        root = ET.fromstring(r.read())
    ns = {"x": "http://www.ecb.int/vocabulary/2002-08-01/eurofxref"}
    day = root.find(".//x:Cube[@time]", ns)
    per_eur = {c.get("currency"): float(c.get("rate")) for c in day.findall("x:Cube", ns)}
    per_eur["EUR"] = 1.0
    return day.get("time"), per_eur

def rate_on(date):
    """(date actually used, {currency: units per EUR}) from the ECB's full
    history. A weekend or holiday takes the last business day before it, and
    the date printed says which day that was."""
    import csv, io, zipfile
    with urllib.request.urlopen(HIST, timeout=60) as r:
        z = zipfile.ZipFile(io.BytesIO(r.read()))
    rows = csv.DictReader(io.TextIOWrapper(z.open(z.namelist()[0]), encoding="utf-8"))
    best = None
    for row in rows:                      # newest first
        if row["Date"] <= date:
            best = row
            break
    if best is None:
        sys.exit(f"no ECB rate on or before {date}")
    per_eur = {c: float(best[c]) for c in ("USD", "GBP")}
    per_eur["EUR"] = 1.0
    return best["Date"], per_eur


def parse(arg, default_ccy):
    """'£2.6m' -> ('GBP', 2600000.0). A bare number takes the default."""
    s = arg.strip().replace(",", "")
    ccy = default_ccy
    if s[:1] == "£":
        ccy, s = "GBP", s[1:]
    elif s[:1] == "$":
        ccy, s = "USD", s[1:]
    elif s[:1] == "€":
        ccy, s = "EUR", s[1:]
    m = re.fullmatch(r"(\d*\.?\d+)\s*([a-zA-Z]*)", s)
    if not m:
        sys.exit(f"cannot read amount: {arg}")
    n, suf = float(m.group(1)), m.group(2).lower()
    if suf:
        if suf not in SCALE:
            sys.exit(f"unknown suffix in {arg}: {suf}")
        n *= SCALE[suf]
    return ccy, n

def tidy(n):
    """Round the way a published price is written, not to the penny.

    Coarse at the top, exact at the bottom. This used to round anything under
    £100,000 to the nearest hundred, which is invisible on a seven-figure
    auction record and catastrophic below it: a £25 coin came out as $0 and a
    £50 coin as $100. Numismatics is the first field here with prices in two and
    three figures -- section 3's budget entry points are the whole reason a
    newcomer reads the report -- and no gate would have caught it, because the
    cell did carry both currencies.
    """
    if n >= 100_000:
        return round(n, -3)
    if n >= 10_000:
        return round(n, -2)
    if n >= 1_000:
        return round(n, -1)
    return round(n)

def main():
    args = sys.argv[1:]
    default = "USD"
    if "--gbp" in args:
        default, args = "GBP", [a for a in args if a != "--gbp"]
    if "--usd" in args:
        default, args = "USD", [a for a in args if a != "--usd"]
    if "--eur" in args:
        default, args = "EUR", [a for a in args if a != "--eur"]

    on = None
    for a in list(args):
        if a.startswith("--on="):
            on = a[5:]
            args.remove(a)
    if "--on" in args:
        i = args.index("--on")
        on = args[i + 1] if i + 1 < len(args) else sys.exit("--on needs a date, YYYY-MM-DD")
        del args[i:i + 2]
    if on and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", on):
        sys.exit(f"--on wants YYYY-MM-DD, got {on}")

    when, per_eur = rate_on(on) if on else rate()
    gbp_per_usd = per_eur["GBP"] / per_eur["USD"]
    print(f"ECB reference rate, {when}")
    print(f"  GBP per USD : {gbp_per_usd:.5f}")
    print(f"  £1          : ${1/gbp_per_usd:.4f}")
    print(f"  €1          : £{per_eur['GBP']:.4f}  ${per_eur['USD']:.4f}")
    print(f"\nFootnote text to paste:")
    print(f'  "converted at the ECB reference rate of {when}, £1 = ${1/gbp_per_usd:.4f}"')

    sym = {"GBP": "£", "USD": "$", "EUR": "€"}
    if args:
        print()
        for a in args:
            ccy, n = parse(a, default)
            eur = n / per_eur[ccy]                      # via the ECB's own base
            out = "  ".join(f"{sym[c]}{tidy(eur * per_eur[c]):,.0f}"
                            for c in ("GBP", "USD") if c != ccy)
            print(f"  {sym[ccy]}{n:,.0f}  ->  {out}")
        print("\nEvery line above is a conversion, not a published price. Say so in "
              "the footnote, and never compute a percentage across two conversion "
              "dates -- see the house currency rules.")

if __name__ == "__main__":
    main()
