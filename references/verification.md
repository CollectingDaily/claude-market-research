# Verification

The report goes out under Paul Fraser Collectibles' name to strangers who have given us an email address. Every figure in it has to survive someone checking it.

The source lists are in `references/sources/` and the checker is `scripts/verify_sources.py`, both in this skill.

## The allowlist, by field

Before a single search, identify the field and read its source file. A house or dealer not on the list may not be cited for a price.

| Field | Read before researching |
|---|---|
| Art, prints, sculpture, works on paper | `~/.claude/skills/claude-market-research/references/sources/sources-art.md` |
| Coins, gold, silver, bullion | `.../sources-coins.md` |
| Comics and original comic art | `.../sources-comics.md` |
| Music, entertainment, film, general memorabilia | `.../sources-music-memorabilia.md` |
| Stamps and postal history | `.../sources-stamps.md` |
| Trading cards, sports cards, TCGs | `.../sources-trading-cards.md` |
| Wine, whisky, cognac, spirits | `.../sources-wine-spirits.md` |
| Toys | `~/.claude/skills/claude-market-research/references/sources/sources-toys.md` |
| Autographs and historical documents | `~/.claude/skills/claude-market-research/references/sources/sources-autographs.md` |
| Political memorabilia | `~/.claude/skills/claude-market-research/references/sources/sources-political.md` (plus `sources-autographs.md` for signed material) |
| Sports memorabilia | `~/.claude/skills/claude-market-research/references/sources/sources-sports.md` (plus `~/.claude/skills/claude-market-research/references/sources/sources-trading-cards.md` for cards) |
| Royal memorabilia | `~/.claude/skills/claude-market-research/references/sources/sources-royal.md` (plus `sources-autographs.md` for signed material) |
| Space and aviation | `~/.claude/skills/claude-market-research/references/sources/sources-space-aviation.md` (plus `sources-autographs.md` for signed material) |
| Photography, photobooks and cameras | `~/.claude/skills/claude-market-research/references/sources/sources-photography.md` (plus `~/.claude/skills/claude-market-research/references/sources/sources-art.md` for fine art photography) |
| Rare books, first editions, maps | `~/.claude/skills/claude-market-research/references/sources/sources-books.md` (plus `sources-autographs.md` for signed copies) |
| **Every field**, the major houses | `~/.claude/skills/claude-market-research/references/sources/sources-major-houses.md` |
| **Every field**, press and context | `~/.claude/skills/claude-market-research/references/sources/sources-press.md` |

**Every report reads three files**: the field's own, `sources-major-houses.md`, and `sources-press.md`. The majors sell across all these fields. The press can support context, provenance and narrative, and can never carry a price on its own.

A report spanning two fields reads both files and uses the union. A topic that fits no file means you stop and say so. Never improvise a source list.

Each field file ends with verification notes on how that field in particular produces a wrong number: hammer versus premium in art, grade and census in comics and cards, catalogue versus market value in stamps, per lot versus per bottle in wine. Read those before you record a single figure.

**The allowlist is a list to work through, not to pick one from.** Searching one house and stopping produces the ten highest prices at that house, which are not the ten highest prices in the field.

## The evidence log

Keep `sources-log.md` in the workings folder. One block per figure, in exactly this shape, because a script parses it:

```
**Item 1: Judy Garland's ruby slippers, The Wizard of Oz**
- URL: https://...
- Status: VERIFIED AUCTION RECORD
- Price: £25,700,000
- Unit: single lot
- Rate: 0.79
- Quote: the exact sentence from the page that states the price
```

Researchers also record `- Copy:` (grade, pedigree, restoration: what tells this
copy apart), `- House:` and `- Date:`, each `not stated` when the page does not
say. `Copy` is how `check_log.py` judges `verify_sources.py`'s name-alike
duplicates: two copies of Action Comics #1 pass, a resale of one copy is
reported as a pair, and one sale logged twice fails. A fact with no price is
`Status: CONTEXT` and `Price: not stated`, and its quote must be on the page.

Two more fields appear only on a page that needed a person's help to open.
`attest.py` prints them for you:

```
- Access: assisted (user-chrome, cloudflare)
- Attested: attested/heritage-com-lot-7734-1f2c9ab3.txt
```

The **Quote** is a sentence copied off the page, not a paraphrase. If you cannot copy one, you have not read the page.

State at the top of the log which source files you read.

## Proving it

Before compiling, prove the log in one call:

```bash
python3 ~/.claude/skills/claude-market-research/scripts/check_log.py "./sources-log.md"
```

It runs `verify_sources.py` on the whole log offline
(duplicates, currency, units, spread of houses) and online on the prices read
unattended, checks the quote of every fact item on its page, and runs
`check_attested.py` on the assisted reads. It prints only failures; the full
output of each gate goes to `check-log.out`. Between them, every price is
checked in the page text, every currency conversion reproduced, the same object
logged twice caught, mixed lot sizes flagged and a minimum spread of houses
enforced. **Nothing is compiled until `check_log.py` exits zero.**

Three failures and what they actually mean:

- **NOT ON PAGE** is not a formatting complaint. The figure is not on the page you cited, so the item is not verified whatever your Status line says. Re-source it from a page that states the figure in text, or drop it.
- **ONE HOUSE** means the research stopped at the first archive with enough lots. Go back and work the rest of the allowlist.
- **DUPLICATE** means the same object appears twice. One object that sold twice is one entry telling that story, never two entries in a ranking.

Then, over the research document:

```bash
python3 ~/.claude/skills/claude-market-research/scripts/compile_research.py "<workings>"
```

It copies every item of the proven log into the document, so no figure is
retyped, and refuses to write it while any price or percentage in the
compiler's analysis is not in the Price or Quote of the item named on its line,
in the same currency.

**Not `verify_citations.py`.** It reads `[^n]` footnotes.
The research document carries none, so that script has nothing to check: it
prints NOTHING CHECKED and exits 2.

`check_log.py` also runs this, whenever anything in the log is marked `Access: assisted`:

```bash
python3 ~/.claude/skills/claude-market-research/scripts/check_attested.py "./sources-log.md"
```

It checks the price and the quote against the text captured at the moment of reading, and prints every source that needed a person. **A DEAD/BLOCKED line from `verify_sources.py` is accounted for only if this passed that same URL.** Every other one is a real failure, and the handover says which is which, by URL.

## The Sources field

**The research document's frontmatter carries every source**: each URL in the evidence log, with its item's title, and each PFC collection listing the stock was read from. `compile_research.py` writes it, double-quoted, from the log itself. Each item in the body carries its own URL line as well, so the person writing can open the page beside the figure.

The report written from it carries no citations, no footnote markers and no Sources section: its Sources field lists only the URLs whose items it prints. That is the writer's job, not the research's.

A source goes in that field only if you opened it in this session. A URL you have not opened does not exist.

Never cite one of our own articles (`Archive/1 - COLLECTING DAILY`, justcollecting.com, news.justcollecting.com, collectingdaily.com), and never read one: they are used for photographs only (SKILL.md, 13 October 2026).

## Every price item carries a Basis line

`- Basis: total including buyer's premium, stated on the page`, or `hammer`, or
`not stated by the source`. Record it when you read the page, not afterwards. In
the Pokémon log one item in ten had it, so the report could not say for nine
prices which measure they were.

## A house, a date or a grade is a figure

It goes in the log only if the cited page states it. The Pokémon log recorded
"Goldin Auctions, June 2023" for the Snap Pikachu from an article that names no
house, and the table printed it. Where the page gives no house, search further (the lot page, the house's own press, a
results site). If none can be found, the **log** says `House not stated`, and the research document shows it as the log has it, so the person writing knows. A report shows the date alone or what the page does say: `House not stated` is never printed in a report.

## Our own articles are never read

The user's instruction of 13 October 2026: our own published articles, justcollecting.com, news.justcollecting.com and collectingdaily.com are used for photographs only and are never read, not even as leads. Every figure, date, grade, house and claim is found, read and logged on the house's or the publisher's own page. `check_log.py` fails any log entry that cites one, `compile_research.py` any analysis line, and `fetch_pages.py` refuses their URLs.

They have been wrong in ways that reached print. The Pokémon top ten dated the Topsun Charizard "1995/1997" and said the cards predate the TCG "by two years", when the franchise itself launched in February 1996; the report carried "1995" into two sentences and a pull quote. The Amazing Fantasy #15 article gives Spider-Man's first appearance as 10 August 1962, when the issue went on sale in June and August is its cover month. And the Pokémon report took its whole top ten from one article whose list stops at February 2026, so it missed every sale from March to September and built a headline "+74%" on a Charizard that carried the "Logan Paul Break" label.

## Where two sources disagree

Log both figures with both sources. **The research document decides nothing**: its Conflicts section lists both figures, both items and what kind of page each is (the house's own sale record, the house's magazine or release, Guinness, the press), and the person writing decides. For their information: a market report prints one figure with no dispute note, the house's own sale record beating its magazine, which beats Guinness, which beats press (the client's instruction of 5 October 2026: correct it in the next issue if wrong).

## Absence is a claim

"There is no published index", "no registry", "nothing tracks": each needs the
search that failed recorded in the log. A 403 is not absence. The Pokémon report
said no Pokémon index existed because Card Ladder returned 403 to a fetch; it
opens in a browser and publishes four. The claim is checked and logged, and the research document carries it on the section's Missing line. A report never prints what we searched for and did not find.

## Two traps that have already cost us

**A search result is not a source.** `WebSearch` returns a summary written by a model that read the page for you. It reads like content. Use it to find a candidate URL and nothing else.

**A 200 is not a readable page.** A Cloudflare interstitial, a paywall or a JavaScript shell returns a status code and no content. If you cannot see the figure in the text you fetched, you have not verified it.

**But a page you could not fetch is not automatically a page you cannot read.** Take it straight to the user's own Google Chrome (`blocked-sources.md`): it runs the page's JavaScript and carries their logins. Use it without asking; the in-app browser is not used. If their Chrome shows a CAPTCHA, a verification check or a sign-in wall, ask them in one line to clear it, and read the page when they have. You never solve a challenge yourself and never type a credential.

An assisted read is recorded with `attest.py` and checked by `check_attested.py`. This is not optional bookkeeping: `verify_sources.py` re-fetches every URL and will report a walled one DEAD/BLOCKED on every run, so without the capture the source becomes a gate nobody can pass and gets dropped.
