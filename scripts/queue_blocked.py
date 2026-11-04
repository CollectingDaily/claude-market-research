#!/usr/bin/env python3
"""Queue a captured page for the user's sign-in, unless it already shows a sold price.

    python3 queue_blocked.py "$W" "<attested/file.txt>" "<site> hides the sold price: sign in to it in your Chrome"

A reader that finds no price on a lot page next to sign-in wording queues it here, never by
writing briefs/blocked.tsv itself: on 29 October 2026 a reader queued a Bonhams lot whose
capture read "Sold for £7,040 inc. premium", and the run stopped to ask the user to sign in.
"""
import pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from attest import HEADER_END, SOLD

W, cap, what = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
cap = cap if cap.is_absolute() else W / cap
raw = cap.read_text(encoding='utf-8', errors='replace')
head, _, body = raw.partition(HEADER_END)
m = SOLD.search(body)
if m:
    sys.exit(f'NOT QUEUED: the page shows a sold price ("...{" ".join(body[max(0, m.start() - 120):m.end() + 20].split())}"). '
             'Read it and log it if it is this lot\'s; if it belongs to another lot on the page, log nothing from this page.')
url = (re.search(r'^Requested:\s*(\S+)', head, re.M) or re.search(r'^URL:\s*(\S+)', head, re.M)).group(1)
(W / 'briefs').mkdir(exist_ok=True)
with open(W / 'briefs' / 'blocked.tsv', 'a', encoding='utf-8') as fh:
    fh.write(f'BLOCKED {url}\t{what}\n')
print(f'QUEUED {url}: the user is asked to sign in.')
