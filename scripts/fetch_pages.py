#!/usr/bin/env python3
"""Fetch many pages to disk in one call, and say which ones are walled.

    python3 fetch_pages.py --workings "<topic>-workings" URL [URL ...]
    python3 fetch_pages.py --workings "<topic>-workings" --list urls.txt

Prints one line per page: status, size, title, and the file it went to. The
page text itself stays on disk; read what you need from it with
`find_figures.py`, never by printing the file.

It fetches with `verify_sources.py`'s own fetch_text (imported, never edited),
so the text saved is byte for byte the text the gate will check. A quote copied
from a saved page passes the gate's verbatim test, and a page that saves cleanly
here will not come back DEAD/BLOCKED later.

A page that will not give its content (an error, an interstitial, a JavaScript
shell, a sold price behind a sign-in) is appended to `walled.tsv` with the
reason, for the browser rung in `references/capture.md`. Re-running is cheap:
a page already saved is skipped unless --refresh.

Our own articles' hosts (justcollecting.com, news.justcollecting.com,
collectingdaily.com) are refused, never fetched: they are never read.
"""
import argparse, concurrent.futures as cf, hashlib, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from verify_sources import fetch_text  # noqa: E402  (read-only reuse)
from attest import error_page, price_hidden  # noqa: E402

WALL = re.compile(r"just a moment|attention required|verify(ing)? you are human|"
                  r"verifying website traffic|access denied|enable javascript|"
                  r"checking your browser|captcha|please turn javascript on", re.I)
TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
# Our own articles are used for photographs only and are never read (the user's
# instruction, 13 October 2026), so a page on these hosts is never saved.
BLOCKED = re.compile(r'^https?://(www\.)?((news\.)?justcollecting\.com|collectingdaily\.com)(/|$)', re.I)


def name_for(url):
    bare = re.sub(r'^https?://(www\.)?', '', url.strip())
    stem = re.sub(r'[^a-z0-9]+', '-', bare.lower()).strip('-')[:60].strip('-')
    return f"{stem}-{hashlib.sha1(url.strip().encode()).hexdigest()[:8]}.txt"


def verdict(text):
    """None for a readable page, else the reason it is not one."""
    if len(text) < 400:
        return f"empty or JavaScript shell ({len(text)} chars)"
    err = error_page(text)
    if err:
        return f"server error page ({err})"
    m = WALL.search(text)
    if m and len(text) < 4000:
        return f"interstitial ({m.group(0)})"
    if price_hidden(text):
        return "price behind a sign-in"
    return None


def one(url, folder, refresh):
    path = folder / name_for(url)
    if path.exists() and not refresh:
        head = dict(l.split(': ', 1) for l in
                    path.read_text(encoding='utf-8', errors='replace').split('\n', 6)[:5]
                    if ': ' in l)
        why = head.get('Verdict', 'readable')
        return url, 'cached', path, head.get('Title', ''), None if why == 'readable' else why
    text, err = fetch_text(url)
    if text is None:
        return url, 'failed', None, '', f"no response ({err[:70]})"
    # fetch_text has already stripped tags, so recover the title from the text
    # head: the <title> was the first thing on the page.
    title = text.strip()[:90]
    why = verdict(text)
    path.write_text(f"URL: {url}\nFetched-by: verify_sources.fetch_text\n"
                    f"Chars: {len(text)}\nTitle: {title}\n"
                    f"Verdict: {why or 'readable'}\n--- page text follows ---\n{text}\n",
                    encoding='utf-8')
    return url, 'saved', path, title, why


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('urls', nargs='*')
    ap.add_argument('--list', help='file with one URL per line')
    ap.add_argument('--workings', required=True)
    ap.add_argument('--refresh', action='store_true')
    a = ap.parse_args()
    urls = list(a.urls)
    if a.list:
        urls += [l.strip() for l in open(a.list) if l.strip().startswith('http')]
    urls = list(dict.fromkeys(urls))
    for u in [u for u in urls if BLOCKED.match(u)]:
        print(f'REFUSED  our own article, never read (SKILL.md, 13 October 2026): {u}')
    urls = [u for u in urls if not BLOCKED.match(u)]
    if not urls:
        sys.exit('no URLs to fetch')
    work = pathlib.Path(a.workings).expanduser()
    folder = work / 'pages'
    folder.mkdir(parents=True, exist_ok=True)
    walled = work / 'walled.tsv'

    with cf.ThreadPoolExecutor(6) as pool:
        rows = list(pool.map(lambda u: one(u, folder, a.refresh), urls))

    new_walls = []
    for url, state, path, title, why in rows:
        where = f"pages/{path.name}" if path else '-'
        size = f"{path.stat().st_size // 1000:>4}k" if path else '    -'
        mark = f"WALLED: {why}" if why else 'ok'
        print(f"{state:6} {size}  {mark:42.42}  {where}  | {title[:60]}")
        if why:
            new_walls.append(f"{url}\t{why}")
    if new_walls:
        seen = set(walled.read_text().splitlines()) if walled.exists() else set()
        with walled.open('a') as f:
            for row in new_walls:
                if row not in seen:
                    f.write(row + '\n')
        print(f"\n{len(new_walls)} walled -> {walled}. They go to the browser rung "
              "(references/capture.md); do not cite them from here.")
    ok = sum(1 for r in rows if not r[4])
    print(f"{ok}/{len(rows)} readable unattended")


if __name__ == '__main__':
    main()
