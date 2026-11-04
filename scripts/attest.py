#!/usr/bin/env python3
"""Record a page that could only be read with a person in the room.

    <extract the page text, then>
    python3 attest.py --url "https://..." --method browser-pane \
        --wall cloudflare --workings "./trading-cards-workings" < page.txt

Some sources sit behind a bot check or a subscription. The workspace rule is
that a Cloudflare interstitial is not a readable page, and that rule is right:
you cannot cite what you have not read. But it was being applied as though the
only two outcomes were an unattended fetch or `not stated`, and there is a third.
Whoever is running the session is present and can clear the check themselves.
The page then loads, the figure is on it, and it has been read -- which is what
the rule actually asks for.

What this script exists to solve is the aftermath. `verify_sources.py` re-fetches
every URL in the evidence log and will report a bot-walled one as DEAD/BLOCKED, a
hard failure, every time. Without something to reconcile that against, an
assisted source is a gate nobody can pass, and the quiet way out is to drop the
figure -- which puts us back where we started, with the good source thrown away.

So the read leaves an artefact: the page text as it stood when it was read, with
the URL, the timestamp, what was in the way and who cleared it. `check_attested.py`
checks the log's price and quote against that capture. A person can open the file.
That is a stronger record than a re-fetch, not a weaker one: a re-fetch proves
what the page says today, a capture proves what we actually read.

Never solve the challenge yourself, and never type a credential. You open the
page; the person present clears it. See `references/blocked-sources.md`.
"""
import argparse, hashlib, os, pathlib, re, sys
from datetime import datetime, timezone

# A real page whose sold price needs the user's sign-in: sign-in wording where the price would be,
# and no sold price on the page. Both halves matter: Sotheby's prints "Create or log in to your
# account to view the sale prices of past lots" on pages that show them, and a signed-in Heritage
# lot shows "Sold ... for: $2,220,000.00" beside "Resold for: Sign-in" (live, 29 October 2026).
# Tested on 535 captures: the nine signed-out Heritage, Propstore and Whisky Auctioneer pages.
HIDDEN = re.compile(r"sold for:?\s*sign-?in|for:\s*sign-?in|sign-?in or join|log ?in to (see|view)", re.I)
SOFT_HIDDEN = re.compile(r"log ?in or register to access hammer price|create or log ?in to your account to view "
                         r"the sale prices|log ?in to view results|please log ?in or register", re.I)
# Any site's way of saying "sign in to see the price" (29 October 2026): checked against 535 real
# captures and the research pages with no false alarm, and on ten wordings sites use.
GENERIC_HIDDEN = re.compile(r"\b(?:sign|log)[ -]?in\b[^.\n]{0,50}?\b(?:to|and)\b[^.\n]{0,15}\b(?:see|view|access|reveal|unlock|"
                            r"show)\b[^.\n]{0,40}?\b(?:price|prices|result|results|hammer|sold|realised|realized|winning bid)\b|"
                            r"\b(?:price|prices|result|results)\b[^.\n]{0,25}\b(?:available|visible|shown)\b[^.\n]{0,20}"
                            r"\bto (?:registered|signed[- ]in|logged[- ]in|members)\b", re.I)
SOLD = re.compile(r"(?:lot sold|sale price:?|sold for:?|price realised|price realized|hammer price:?|winning bid:?|\bfor:)"
                  r"\s*(?:[£$€]|HK\$|US\$)?\s?\d[\d,]{2,}", re.I)


# A server or Cloudflare error page in place of the page: nothing for the user to clear, and never
# a capture. Heritage served "520: Web server is returning an unknown error" in the live test of
# 29 October 2026, and the receiver saved it over the real lot page.
ERROR_PAGE = re.compile(r"page not found|can(?:'|\u2019|no)?t be found|could not be found|does not exist|no longer exists|\b404\b[^\n]{0,40}not found|not found[^\n]{0,20}\b404\b|"
                        r"web server is returning an unknown error|error code 5\d\d\b|\b5\d\d: [a-z ]+error|"
                        r"bad gateway|gateway time-?out|origin is unreachable|service (?:temporarily )?unavailable|"
                        r"too many requests|internal server error", re.I)


def error_page(text):
    """The matched wording when a short page is a server error page, else None."""
    m = ERROR_PAGE.search(text[:3000])
    return m.group(0) if m and len(text) < 4000 else None


def price_hidden(text):
    return bool(HIDDEN.search(text) or SOFT_HIDDEN.search(text) or GENERIC_HIDDEN.search(text)) and not SOLD.search(text)

METHODS = ('browser-pane', 'user-chrome')
HEADER_END = '--- page text follows ---'


def slug(url):
    """A filename that says which page it is, and cannot collide."""
    bare = re.sub(r'^https?://(www\.)?', '', url.strip())
    stem = re.sub(r'[^a-z0-9]+', '-', bare.lower()).strip('-')[:60].strip('-')
    return f"{stem}-{hashlib.sha1(url.strip().encode()).hexdigest()[:8]}.txt"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--url', required=True, help='the page that was read')
    ap.add_argument('--method', required=True, choices=METHODS,
                    help='browser-pane: the in-app browser. user-chrome: the '
                         'session operator\'s own Chrome, for a subscription '
                         'they hold.')
    ap.add_argument('--wall', required=True,
                    help='what was in the way, in a few words: cloudflare, '
                         'js-shell, subscription, age-gate')
    ap.add_argument('--workings', required=True,
                    help='the report\'s <topic>-workings directory')
    ap.add_argument('--present', default=os.environ.get('USER', ''),
                    help='who cleared it (default: the logged-in user)')
    ap.add_argument('--text', help='file holding the extracted page text '
                                   '(default: stdin)')
    a = ap.parse_args()

    body = (pathlib.Path(a.text).read_text(encoding='utf-8') if a.text
            else sys.stdin.read())
    body = re.sub(r'\s+\n', '\n', body).strip()
    if len(body) < 200:
        sys.exit(f"only {len(body)} characters of page text. That is an "
                 "interstitial or an error page, not the article. Do not attest "
                 "a page you have not actually got in front of you.")
    if not a.present.strip():
        sys.exit("--present is required: an attestation names who cleared the check.")

    out = pathlib.Path(a.workings).expanduser() / 'attested'
    out.mkdir(parents=True, exist_ok=True)
    path = out / slug(a.url)
    path.write_text(
        "# Attested read\n"
        f"URL: {a.url.strip()}\n"
        f"Read: {datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')}\n"
        f"Method: {a.method}\n"
        f"Wall: {a.wall.strip()}\n"
        f"Present: {a.present.strip()}\n"
        f"Characters: {len(body)}\n"
        f"{HEADER_END}\n{body}\n", encoding='utf-8')

    rel = os.path.relpath(path, pathlib.Path(a.workings).expanduser())
    print(f"wrote {path}  ({len(body):,} characters)")
    print("\nAdd these two lines to the item's block in sources-log.md, and put "
          "the quote you copied off the page in the Quote field as usual:\n")
    print(f"- Access: assisted ({a.method}, {a.wall.strip()})")
    print(f"- Attested: {rel}")
    print("\nThen: check_attested.py, which checks the price and the quote "
          "against this capture.\nExpect verify_sources.py to report this URL "
          "DEAD/BLOCKED. That line is accounted for; every other one is not.")


if __name__ == '__main__':
    main()
