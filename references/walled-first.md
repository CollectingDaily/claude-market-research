# Walled pages to capture first

Read at phase 1. These are pages a research agent cannot fetch and the report almost always needs. The main session captures them in the user's own Chrome (`capture.md`, one `browser_batch` per house, receipts only) while the research agents start, so the agents read them from `$W/attested/` instead of finding them walled and waiting for a second pass. Add to this file whenever a run finds another page every report in the field needs.

## Every field

- **Heritage press releases** for the department's records and the company's year-end and midyear results (`ha.com/heritage-auctions-press-releases-and-news/...`). Read in their Chrome; the login must be live for lot prices ("Sold For: Sign-in" means it has lapsed: ask).
- **Heritage archive search**, which lists sold lots with prices: `https://<department>.ha.com/c/search/results.zx?term=<words>&mode=archive` (coins add `&dept=1909`; test the department code for other fields). Results come in relevance order across all years, so filter by date.
- **Sotheby's** lot pages show "Log in to view results" until the user signs in: ask, then capture. Its press releases are public.

## Coins

Captured on 22 October 2026, all through the user's Chrome:

- Stack's Bowers world-record list: `https://stacksbowers.com/sell-consign/world-record-prices/` (the record chain with year ranges).
- Stack's Bowers archive, which opens sorted by price realised (its top 100 coins): `https://archive.stacksbowers.com/`.
- Stack's Bowers year-end releases (2025: `.../sbpressreleases/stacks-bowers-galleries-announces-record-shattering-325-million-year-of-auctions-in-2025/`; 2024: `.../stacks-bowers-galleries-announces-record-year-in-2024/`), the latest Showcase releases, the events calendar and the terms page (buyer's premium).
- Heritage: the 2025 annual release (releaseId 5383), the latest coin sale pages (`coins.ha.com/c/auction-home.zx?saleNo=<n>`, with "Realized" totals and the premium line), the schedule, and archive searches for the field's top series.
- PCGS: the three index pages (`pcgs.com/prices/coin-index/pcgs3000`, `key-dates-and-rarities`, `mint-state-rare-gold`), the grading standards and Lingo pages, CoinFacts for the record coins, the statistics page (capture its tables as rows: the plain text loses the labels).
- Sotheby's 1933 double eagle lot page (record price; needs their sign-in).
- Noonans: the year's coin review (`noonans.co.uk/news-and-events/latest-news/...`) and the buying and help pages (capture `main.textContent`: the sections are collapsed).
- US Mint pages (glossary and penny FAQ also need `textContent`); Royal Mint sovereign pages sometimes fail unattended.
- Known blocks: GreatCollections shows a "Verifying Website Traffic" check (ask the user); MagnifyMoney is a hard Cloudflare block with nothing to clear; Künker prices are hammer ("Zuschlag").

## Art

Learned in the art run, 26 to 27 October 2026. Give these to the capturer at the start.

- **Christie's lot pages** (`christies.com/en/lot/lot-<id>`) show "Price realised" only when rendered, and WebSearch cannot see christies.com: capture with `GOOGLE site:christies.com/en/lot <artist> "<title>"`. Lot pages state no premium basis; Christie's results releases state "Sales totals are hammer price plus buyer's premium."
- **Christie's marquee-week releases** on press.christies.com list each New York sale's top lots (November 2024 $689m, May 2025 $693m, November 2025 $965m, May 2026 $1.45bn): any "best result since <date>" ranking needs them.
- **Sotheby's** lot prices need the user's sign-in. Each sale page (`sothebys.com/en/buy/auction/<year>/<sale>`) states that its results are "inclusive of any Sotheby's Premiums": capture it beside the lot. Season wrap-ups are articles: `the-new-york-sales-november-2025-breuer-results`, `editorial-new-york-2026-spring-season-wrap-up`, `sothebys-fall-2024-auction-results`, `the-10-most-valuable-lots-sold-by-sothebys-in-2025`.
- **Phillips** sale pages (`phillips.com/auction/NY0xxxxx`) and the half-year editorial read in Chrome; its press releases are PDFs.
- **Bonhams online sale pages** list every lot as "Sold for US$x inc. premium" (e.g. auction 31709, Prints & Multiples Online, February 2026): the budget bands come from these.
- Walled to a fetch, fine in Chrome: Heritage annual and half-year releases (`releaseId=5383`, `5499`), Artnet News (`news.artnet.com/market/top-artists-auction-2025-2735297` is the 2025 artist ranking), Artprice report pages, Swann, Dorotheum, LAPADA, FBI and Justice Department pages, Art Basel fair pages (`artbasel.com/basel`, `/hong-kong`), EUR-Lex.
- **Dead ends, do not try:** IFAR (certificate error), the Warhol Foundation FAQ (hangs), every PDF (Art Basel and UBS report, Artprice, Sotheby's year-end and marquee releases, Phillips and Christie's press PDFs).
