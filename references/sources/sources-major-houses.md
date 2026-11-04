# Sources: major auction houses (read for EVERY subject field)

These houses sell across all the fields this skill covers. Read this file **in
addition to** the file for the subject field, never instead of it.

A realised price may come only from a page on one of these sites that you have
fetched in this session. The house's own lot or results page is the record;
a press report of the same sale is context, not the source.

## Authorised for every field

- Christie's — https://www.christies.com/
- Sotheby's — https://www.sothebys.com/
- Bonhams — https://www.bonhams.com/
- Phillips — https://www.phillips.com/
- Heritage Auctions — https://www.ha.com/
- Julien's Auctions — https://www.juliensauctions.com/
- Paul Fraser Collectibles — https://www.paulfrasercollectibles.com/

Paul Fraser Collectibles is the house publication's own dealership. Cite its
stock and archive where it genuinely trades in the field; do not present a PFC
asking price as an auction result.

## Cross-field aggregators (context only, never a realised price)

These index other people's sales and their records are frequently incomplete or
stale. Use them to find a sale, then verify it on the house's own site.

- Invaluable — https://www.invaluable.com/
- Barnebys — https://www.barnebys.co.uk/

## Sotheby's realised prices are behind a login

Sotheby's publishes estimates freely but gates every realised price: lot pages
and sale pages both show "Log in to view results" where the hammer figure
should be. This was tested on 19 August 2026 and is not a bot-detection
problem — an anonymous fetch and a fetch replaying a logged-in browser's
cookies returned byte-identical pages. The session is an Auth0 token held in
browser storage, so **no cookie file or scripted fetch will ever reach the
price.** Do not spend time trying.

Two acceptable routes:

1. **Sotheby's own press releases and results announcements** are public,
   permanent and authoritative. `sothebys.com/en/press/...` carries headline
   results for significant sales. Cite these, and say in sources-log.md that
   the figure came from the press release rather than the lot page. Prices
   there are often rounded and lot numbers are usually absent — do not invent
   the missing precision.
2. **A logged-in browser session**, driven interactively, when an article
   genuinely needs lot-level detail. The operator logs in; the skill never
   handles the credentials.

An estimate is not a realised price. If only the estimate is visible, either
find the result in a press release or drop the item. Never present
"300,000 - 450,000 GBP" as what something sold for.

## Access, as at 19 August 2026

Tested with a standard browser user agent. Heritage Auctions and Julien's
returned 403 and refuse automated clients; Christie's refuses the image
script's own user agent but answers a browser one. Everything else responded
normally. Where a house blocks the fetch, find the sale on a fetchable source or
drop the item. Never cite from memory or from a search snippet.
