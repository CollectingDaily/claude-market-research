# When a source will not open

A Cloudflare interstitial is not a readable page. That rule stands and nothing
here softens it. What changed is the assumption underneath it: that the only two
outcomes are an unattended fetch or `not stated`.

There is a third: the user's own Chrome. They stay signed in there to the houses
whose prices sit behind a login (Heritage, Propstore, Sotheby's) and to the titles
they subscribe to. A page read there loads, the figure is on it, and it has been
read with our own eyes -- which is exactly what the workspace rule asks for.

**Use it without asking, and use it first.** The user's standing instruction (24
September 2026): "you should use chrome when needed without asking. just use it".
And on 7 October 2026: "YOU MUST USE GOOGLE CHROME WHERE THE CREDENTIALS FOR
LOGGING IN ARE ALREADY THERE". A page that will not fetch goes straight to their
Chrome. The in-app browser is not a rung: it holds none of their logins, and on
7 October 2026 it met Heritage's verification slider while their Chrome read the
same page.

**Ask them when their Chrome is blocked.** Also 7 October 2026: "if you cannot see
something due to captcha, ask me". A CAPTCHA, a verification slider, a "verify
you are human" page or a sign-in wall in their Chrome is the one thing you raise
with them, at once, in one line: the page, and what to do ("Heritage shows a
verification slider on <url> in your Chrome: please move it and tell me").
Pause there. When they say it is done, read the page and carry on with the
report from that point. Asking is a pause, not the end of the run ("it should
stop to ask me to connect chrome or to move the slide or login, not to stop the
whole process", 7 October 2026): never abandon the report, never skip the page
as if it had been read, never drop the figure without asking. Never clear it
yourself and never type a credential. Do not hold such pages back
for a batch at the checkpoint, and do not ask about anything else.

**Check the connection before research starts.** The first capturer does it,
at the start of phase 1, with `mcp__claude-in-chrome__tabs_context_mcp`; the
main session never touches the browser. If the extension is not connected, the
capturer reports BLOCKED and the user is asked to connect it ("Chrome is not
connected: open Chrome and click the Claude extension"); the run carries on once
they have. Never discover this halfway through.

## The ladder

Work down it. Stop at the first rung that gets you the real page.

**1. `WebFetch`.** The default. Cheap, unattended, fine for most of the corpus.

**2. The user's own Google Chrome** (`mcp__claude-in-chrome__*`). Every page that
will not fetch comes here, without asking: a 403, a JavaScript shell, a price
behind a login ("Sold for: Sign-in", "Login to see sold price", "Log in to view
results"), a subscription title. It runs the page's JavaScript, so **a large
share of what looks like a bot wall is simply a page that renders client-side**,
and it carries their logins, so the page opens as it would for them. Save it with
the receiver in `capture.md`, so the text goes to disk and only a receipt comes
back; never `get_page_text` it and type the text out again. Read the page you came
for; do not wander the site or change anything. The in-app browser is not used.

**3. Ask them.** If their Chrome shows a CAPTCHA, a verification check or a
sign-in wall, or a price still reads "Sign-in" (their login has lapsed), ask them
in one line, at that moment, as above. Pause, and when they say it is done,
read it and carry on with the report.

**A house's own search failing is not the page being missing.** Christie's site
search renders blank in both browsers, and `WebSearch` cannot see christies.com at
all. On 24 September 2026 two resale pairs were cut from the movie report as
unverifiable, when a Google search in the user's Chrome
(`site:christies.com <lot words>`) found Christie's own 2012 results PDF and a lot
page quoting the 1999 price, both public. Before dropping anything, run that
`site:` search for the house.

**4. Drop it** only when the page, once open, does not state the figure, or the
user tells you to. List every dropped figure, with its URL and the reason, in the
handover. A row or claim that depended on it comes out with it.

## Where the walls actually are

Measured on 2026-09-22, by fetching each unattended and then opening it in the
in-app browser. Since 7 October 2026 every page in the browser column is read in
the user's Chrome instead; the column still says which pages need a browser at
all. Re-test rather than trusting this table: these change.

| Source | Unattended fetch | In-app browser | Note |
| --- | --- | --- | --- |
| `ha.com` (Heritage) | **walled** (403) | reads | See below. Archive search and press releases both work. |
| `goldin.co` | **walled** | untested | Heavily used for cards. Expect to need rung 2 or 3. |
| `antiquestradegazette.com` | **walled** | untested | Subscription title. Rung 3, their Chrome. |
| `christies.com` | reads | — | |
| `sothebys.com` | reads | — | |
| `bonhams.com` | reads | — | |
| `propstore.com` | reads | — | |
| `news.justcollecting.com` | **never read** | — | Our own: photographs only, never read (SKILL.md, 13 October 2026). |
| `stacksbowers.com` | **walled** | reads | Coins. Its `world-record-prices` page is the best single numismatic source we have found. |
| `pcgs.com` | **walled** | untested | Coin grading and census. |
| `greatcollections.com` | **walled** | untested | Coins. |
| `spink.com`, `baldwin.co.uk`, `ngccoin.com`, `coinworld.com` | read | — | Coins. |

### Every numismatic house, tested 2026-09-22

Rung 1 is a plain fetch; rung 2 was measured in the in-app browser and is now read in the user's Chrome; rung 3 is a page that needed their login or met a challenge, which you now ask them to clear.

| Source | Rung | Note |
| --- | --- | --- |
| Spink, Baldwin's, Heritage Coins UK | 1 | Read unattended. |
| NGC, CNG, Numismatica Ars Classica | 1 | Read unattended. |
| Sovereign Rarities, Morton & Eden, Atlas Numismatics | 1 | Read unattended. |
| Coin World, Numismatic News, COINage | 1 | Trade press. Read unattended. |
| **PCGS** | 2 | 403 to a fetch, reads in the browser. |
| **Stack's Bowers** | 2 | 403 to a fetch, reads in the browser. The record-prices page is the best single numismatic source found. |
| **Heritage coins** (`coins.ha.com`) | 2 | Loads, but lazy-renders; realised prices still need the free account. |
| **Noonans, Künker, Sixbid** | 2 | 403 to a fetch, read in the browser. |
| **NumisBids** | 2 | 403 to a fetch, reads in the browser. An aggregator carrying auction results across houses — verify on the house's own page. |
| **DLRC** (`davidlawrence.com`) | 2 | A JavaScript app: empty to a fetch, fine in the browser. `dlrcauctions.com` redirects to it. |
| **Royal Mint** | 2 | 302 to a fetch, reads in the browser. |
| **Noonans** | 2 / **3** | Homepage loads in the browser; `/archive/`, where the prices are, serves a challenge. |
| **PCGS Auction Prices Realized** | 2 | `pcgs.com/auctionprices` — realised prices across houses, loads in the browser. An aggregator: verify at the selling house. |
| **GreatCollections** | **3** | Active "Verifying Website Traffic" challenge, twice, in the browser. Open it in their Chrome; if the challenge shows there too, ask them to clear it. Never attempt to solve it. |
| Roma Numismatics | — | `522`, origin down. Not a block; retry another day. |
| Goldberg (`goldbergcoins.com`) | — | No DNS. Find the current domain before listing it. |
| ~~Legend Rare Coin (`legendauctions.com`)~~ | — | **The domain has lapsed and now serves a Danish casino site. Do not cite it.** |

**A rung belongs to a page, not to a domain.** Noonans was first recorded at
rung 2 on the strength of its homepage; its results archive turned out to be
rung 3. Test the page that carries the figure you want, not the front door.

**Everything a numismatic report needs is reachable; two sources need the
user's Chrome.** That matters because `sources-coins.md` currently demotes
Spink, Baldwin's, Stack's Bowers and Heritage Coins UK to "context only, cannot
be the sole source for price claims". Six of the eight it demotes read with a
plain unattended fetch. Access is not the reason, whatever the reason is.

Coins are the worst-affected field measured so far: five of the sources a
numismatic report needs are walled, including Stack's Bowers, which is to coins
what Heritage is to cards. A coins report without the ladder loses most of its
record book.

**Heritage needs an account for the number you came for.** A browser opens
ha.com and its sold archive without anyone being asked anything -- 468,000
sold sports lots, filterable by grade, year and price band. But every realised
price reads `Sold For: Sign-in or Join (free & quick)`. The lot, the date, the
auction number and the grade are all there in public; the hammer is not.

So Heritage is read in the user's Chrome, where they are signed in, for prices and
everything else. If a price there still reads "Sign-in", their login has lapsed:
ask them to sign in again. Its archive also holds the
records of Profiles in History sales, such as the 2011 Debbie Reynolds auction
(#997080), with "includes Buyer's Premium" stated against each price. You never
create an account and you never type into a sign-in form.

**But the record prices are public, in the press releases.** Heritage announces
every record in a press release that states the figure in its headline, with no
account needed. `sports.ha.com/heritage-auctions-press-releases-and-news/...`
returns 403 to an unattended fetch, like the rest of the domain, and opens fully
in a browser. The delivered trading cards report already cites the
Logoman record this way, and the page does carry `$12,932,000`, dated 25 August
2025 -- checked at rung 2, nobody asked anything.

So the routing for Heritage is:

- **a record, or any figure they have announced** -- the press release, in their
  Chrome. Try this first; it covers most of what these reports quote.
- **an ordinary lot's price** -- the lot page, in their Chrome, signed in, because
  `Sold For` is behind the free account.

This is worth knowing before you plan the research, because Heritage is the
most-cited house in this series, and the difference between those two routes is
the difference between an uninterrupted run and a dozen interruptions.

## What you never do

You never clear a check yourself. The user clears it; you read the page.

- **Never solve a CAPTCHA or tick a bot-detection box.** Not a puzzle, not a
  checkbox, not a slider. If one appears in their Chrome, ask them to clear it.
- **Never type a credential**, and never ask for one. Not a password, not a card,
  not a one-time code. If a page wants a login their Chrome does not have, ask
  them to sign in themselves.
- **In their Chrome you are in their signed-in session.** Read the page you came for.
  Do not wander the site, do not change a setting, do not sign anything out.
- **Never present a wall as cleared when it is not.** A capture of an interstitial
  is a fabricated source with extra steps. `attest.py` refuses anything under 200
  characters for that reason, and it is not the only check you should be applying.

## When to ask, and when not to

Ask only when Chrome is not connected, or cannot show you a page because of a
CAPTCHA, a verification check or a sign-in wall, and ask at the moment you meet
it, in one line. Then carry on once they have done it. Do not ask them to open a page their Chrome would open for you, do not ask
before trying their Chrome, and do not save the questions for the phase 7
checkpoint.

## Recording it

An assisted read has to leave a record, for a mechanical reason as well as an
honest one.

`verify_sources.py` re-fetches every URL in the evidence log, and it will report a
bot-walled one as **DEAD/BLOCKED**, a hard failure, on every run. It is right to:
an unattended fetch of that page really does return an interstitial. Left
unreconciled, an assisted source becomes a gate nobody can pass, and the quiet way
out is to drop the figure -- which throws away the good source we just went to the
trouble of opening.

So capture the page at the moment you read it. In either browser,
`capture_server.py` does this for you (`capture.md`): it writes the capture in
this format and the receipt names the file. For text that reached you any other
way:

```bash
python3 ~/.claude/skills/claude-market-research/scripts/attest.py \
    --url "https://..." --method user-chrome --wall cloudflare \
    --workings "./<topic>-workings" --text page.txt
```

It writes the page text, the URL, the timestamp, what was in the way and who
cleared it into `<topic>-workings/attested/`, and prints the two lines to add to
the item's block in `sources-log.md`:

```
- Access: assisted (user-chrome, cloudflare)
- Attested: attested/heritage-com-lot-7734-1f2c9ab3.txt
```

Then:

```bash
python3 ~/.claude/skills/claude-market-research/scripts/check_attested.py "./<topic>-workings/sources-log.md"
```

It checks the log's price and quote against the captured text, confirms the
capture is of the URL claimed, and prints every assisted source with its date,
its method and what was in the way. **A run that leaned on someone's presence says so
on the PASS line.**

It also re-tries each assisted URL unattended. A page that fetches perfectly well
does not need an attestation, and one that has grown an attestation anyway is
either a transient failure written down as permanent or a rung being skipped.
That gets reported. An exception nobody re-examines stops being an exception and
becomes the route.

## Reconciling the two checkers

Run both; `check_log.py` does, in one call, and reports only what fails.
`check_attested.py` accounts for exactly the URLs marked assisted;
`verify_sources.py` covers everything else.

So: **a DEAD/BLOCKED line in `verify_sources.py` is accounted for only if
`check_attested.py` passed that same URL. Every other one is a real failure.**
Say which is which in the handover, by URL. "Verified except three that needed
a person, listed" is a sentence someone can act on. "It passed" is not, when it did
not.

## This is not a relaxation of the sourcing rules

The sourcing rules ask for four things before a figure is written down: fetch the page,
confirm the content actually loaded, find the figure on the page with your own
eyes, and only then write it down against that URL.

An assisted read satisfies all four. The page loads, the content is there, the
figure is on it, and you read it. The rule was never "do not use a browser". It
was "do not cite what you have not read", and this is a way of reading it.

What stays exactly as it was: a search-result summary is not a source, a figure
you cannot see is not verified, a conflict between two sources gets stated rather
than resolved quietly, and a gap you could not fill is `not stated`.
