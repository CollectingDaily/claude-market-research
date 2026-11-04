#!/usr/bin/env python3
"""Save pages read in a browser straight to disk, so their text never passes
through the session that read them.

    python3 capture_server.py --workings "<root>/Market research/<Topic>/workings"   # background

A walled page used to cost twice. The browser tool returned its text into the
conversation, and the only way to get it into an attest.py capture was to type
it back out into a heredoc: twenty Heritage pages read once and written once,
every word of them then carried by every later request. The first attempt to
skip that, a page POSTing its text to a server on 127.0.0.1, fails: Chrome's
Local Network Access blocks a public page from making requests to localhost,
and the in-app browser has no second window to postMessage to.

What it does not block is a top-level navigation. So the page's own script
puts its text in the URL fragment and navigates the tab here; the fragment
never leaves the machine (browsers do not send it in the request), and this
page, being local, saves it with a same-origin request. The tool call returns
nothing but a receipt.

Each capture is written in exactly attest.py's format, into the same
`attested/` folder, so `check_attested.py` checks it unchanged. A token printed
at start-up must accompany every payload, so nothing but our own snippets can
write there. The snippets to paste are in `references/capture.md`.
"""
import argparse, http.server, json, os, pathlib, re, secrets, sys, urllib.parse
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from attest import METHODS, HEADER_END, error_page, price_hidden, slug  # noqa: E402

# Text that means the page we got is not the page we wanted. A capture that is
# mostly this is an interstitial, and attesting one is a fabricated source.
WALL = re.compile(r"just a moment|attention required|verify(ing)? you are human|"
                  r"verifying website traffic|access denied|enable javascript and "
                  r"cookies|checking your browser|complete the captcha|solve the captcha|"
                  r"captcha to continue|press (?:&|and) hold", re.I)

PAGE = """<!doctype html><meta charset=utf-8><title>capture receiver</title>
<body style="font:14px ui-monospace,monospace;white-space:pre-wrap"><div id=o>ready</div>
<script>
(async () => {
  const o = document.getElementById('o');
  if (location.pathname === '/log') {
    o.textContent = await (await fetch('/receipts' + location.search)).text(); return;
  }
  if (!location.hash.startsWith('#pfc=')) return;
  const body = decodeURIComponent(location.hash.slice(5));
  history.replaceState(null, '', '/');
  const r = await fetch('/save', {method: 'POST', body});
  o.textContent = await r.text(); document.title = 'saved';
})();
</script>"""


class Receiver(http.server.BaseHTTPRequestHandler):
    workings = token = None
    receipts = []

    def log_message(self, *a):
        pass

    def reply(self, code, body, ctype='text/plain; charset=utf-8'):
        data = body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path)
        if path.path == '/receipts':
            q = urllib.parse.parse_qs(path.query)
            last = int(q.get('last', ['0'])[0] or 0)
            rows = self.receipts[-last:] if last else self.receipts
            return self.reply(200, '\n'.join(rows) or 'no captures yet')
        self.reply(200, PAGE, 'text/html; charset=utf-8')

    def do_POST(self):
        try:
            d = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        except Exception as e:
            return self.reply(400, f'REFUSED unreadable payload: {e}')
        if d.get('token') != self.token:
            return self.reply(403, 'REFUSED wrong token')
        out = [self.save(it, d) for it in d.get('items', [])]
        self.receipts.extend(out)
        self.reply(200, '\n'.join(out) or 'REFUSED no items')

    def blocked(self, it, url, what):
        """Queue the page for the user: next_step.py reads briefs/blocked.tsv, asks them, and sends the page
        again once they have cleared it. Written here so the ask never depends on the capturer remembering."""
        req = (it.get('requested') or '').strip() or url
        site = urllib.parse.urlsplit(url).netloc.removeprefix('www.')
        (self.workings / 'briefs').mkdir(exist_ok=True)
        with open(self.workings / 'briefs' / 'blocked.tsv', 'a', encoding='utf-8') as fh:
            fh.write(f'BLOCKED {req}\t{site} {what}\n')

    def save(self, it, d):
        url = (it.get('url') or '').strip()
        method = it.get('method') or d.get('method')
        wall = (it.get('wall') or d.get('wall') or '').strip()
        body = re.sub(r'[ \t]+', ' ', it.get('text') or '')
        body = re.sub(r'\s*\n\s*', '\n', body).strip()
        title = body.split('\n', 1)[0][:70]
        if not url.startswith('http'):
            return f'REFUSED no url  | {title}'
        if method not in METHODS:
            return f'REFUSED method {method!r}, expected {"/".join(METHODS)}  | {url}'
        if not wall:
            return f'REFUSED no wall named  | {url}'
        if re.match(r'https?://(www\.)?google\.[a-z.]+/search', url):
            return f'REFUSED a search results page, not a source: the result was not reached.  | {url[:90]}'
        err = error_page(body)
        if err:
            return f'REFUSED an error page ({err}), not the page: nothing saved; it is tried again later.  | {url}'
        walled = WALL.search(body)
        if len(body) < 200 or (walled and len(body) < 2500):
            why = walled.group(0) if walled else f'{len(body)} characters'
            self.blocked(it, url, 'shows a verification check in your Chrome: clear it')
            return (f'REFUSED not the page ({why}). Do not attest an interstitial. '
                    f'Next rung, or drop it.  | {url}')
        flags = []
        hidden = price_hidden(body)
        if hidden:
            flags.append('PRICE HIDDEN: sold price needs a sign-in')
            self.blocked(it, url, 'shows the lot but not the sold price: sign in to it in your Chrome')
        if walled:
            flags.append(f'check: page mentions {walled.group(0)!r}')
        if it.get('status') and int(it['status']) != 200:
            flags.append(f"HTTP {it['status']}")
        if it.get('final') and it['final'].rstrip('/') != url.rstrip('/'):
            flags.append(f"redirected to {it['final']}")

        folder = self.workings / 'attested'
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / slug(url)
        path.write_text(
            "# Attested read\n"
            f"URL: {url}\n"
            + (f"Requested: {req}\n" if (req := (it.get('requested') or '').strip()) and req.rstrip('/') != url.rstrip('/') else '')
            + ("Hidden: the sold price needs a sign-in; this is the signed-out page\n" if hidden else '')
            + f"Read: {datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')}\n"
            f"Method: {method}\n"
            f"Wall: {wall}\n"
            f"Present: {os.environ.get('USER', '')}\n"
            f"Characters: {len(body)}\n"
            f"{HEADER_END}\n{body}\n", encoding='utf-8')
        rel = os.path.relpath(path, self.workings)
        return (f"saved {rel}  {len(body):,} chars  | {title}"
                + (f"  | {'; '.join(flags)}" if flags else ''))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--workings', required=True, help="the report's <topic>-workings folder")
    ap.add_argument('--port', type=int, default=8766)
    a = ap.parse_args()
    Receiver.workings = pathlib.Path(a.workings).expanduser().resolve()
    Receiver.workings.mkdir(parents=True, exist_ok=True)
    Receiver.token = secrets.token_hex(6)
    (Receiver.workings / '.capture-token').write_text(Receiver.token)
    print(f"receiver http://127.0.0.1:{a.port}/  token {Receiver.token}  "
          f"-> {Receiver.workings / 'attested'}", flush=True)
    http.server.ThreadingHTTPServer(('127.0.0.1', a.port), Receiver).serve_forever()


if __name__ == '__main__':
    main()
