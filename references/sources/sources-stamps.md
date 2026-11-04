# Sources: stamps and postal history

Read `sources-major-houses.md` and `sources-press.md` alongside this file.

## Primary authorised sources — specialist houses

Realised prices only, verified by fetching the lot or results page.

- Stanley Gibbons — https://www.stanleygibbons.com/
- Spink — https://www.spink.com/
- David Feldman — https://www.davidfeldman.com/
- Robert A. Siegel — https://siegelauctions.com/
- Cherrystone — https://www.cherrystoneauctions.com/
- Corinphila — https://www.corinphila.ch/
- Heinrich Köhler — https://www.heinrich-koehler.de/
- Grosvenor (UK) — https://www.grosvenorauctions.com/
- H.R. Harmer — https://hrharmer.com/

## Expertising bodies (authoritative for authenticity, never for price)

A certificate is what separates a rarity from a forgery in this field.

- Royal Philatelic Society London — https://www.rpsl.org.uk/
- The Philatelic Foundation — https://philatelicfoundation.org/

## Trade press and societies (context only)

- Linn's Stamp News — https://www.linns.com/
- American Philatelic Society — https://stamps.org/ — beyond its role as trade press, its learning-center/article archive is a usable educational source in its own right, not just its trade-body status.

## Museums, foundations and archives (context, stories, photography — never price)

These are for narrative, provenance and photography, not realised prices. Several block plain
HTTP fetch tools — see the fetch-method note below before citing them.

**National museums (highest authority; curator-written articles, high-res photography)**

- The Postal Museum (UK) — https://www.postalmuseum.org/ — holds the Royal Mail Archive
  (1636–present) and the national philatelic collection. Its `/blogs/stamps/` and
  `/collections/highlights/` sections carry curator articles (e.g. "The first ever stamp: the
  Penny Black") with photography of rarities like the Penny Black plates. A plain HTTP fetch
  returns 403 on both the blog index and article pages — same pattern as David Feldman,
  Cherrystone and Heinrich Köhler below — but a real browser session (e.g. the Claude Browser
  pane) loads it cleanly with no challenge. Use that route, not manual copy-paste.
- Smithsonian National Postal Museum — https://postalmuseum.si.edu/ — the US equivalent, holding
  around 16 million items. Its former standalone site "Arago" (a dedicated storytelling database
  with curator essays) has been folded into the main site — `arago.si.edu` now redirects to
  `postalmuseum.si.edu/search-the-collection`. This one is a harder block: even a real browser
  session hits an active Cloudflare "Request Verification" challenge screen, not just a UA
  filter. Do not attempt to solve it. Treat this source as citable only from material you already
  have independent knowledge of, or ask the user to check the page themselves.

**Nonprofit and educational foundations (solid, fetch-accessible)**

- Postal History Foundation — https://postalhistoryfoundation.org/slusser-library/philatelic-articles/
  — confirmed accessible. A running library of well-illustrated articles (postal routes, UPU
  history, regional postal history) with genuine photographs of covers, postmarks and stamps.
  Non-commercial complement to the auction houses for narrative and context.

**Archival/reference (authoritative for provenance, lower on story content)**

- British Library Philatelic Collections — the UK's national philatelic collection (Tapling,
  Langmead). Useful for provenance claims, but its nominal hub URL (bl.uk/philatelycollectionshub)
  404s, and the live pages found (vll-minos.bl.uk) are older finding-aid style pages rather than
  article-and-photo content — lower priority here than for a provenance check.

## Verification notes for stamps

**Catalogue value is NOT market value.** This is the field's defining trap.
Stanley Gibbons, Scott and Michel catalogue prices routinely sit far above what
a stamp actually fetches, and they are a pricing convention, not a record of
sale. Never present a catalogue figure as a price realised, and never write
"worth £X" on the strength of one. If you cite a catalogue number, cite it as an
identifier (SG 1, Scott 1), which is what it is genuinely useful for.

**Condition vocabulary is technical and non-negotiable.** Centering, perforation
count, gum condition (unmounted mint, mounted mint, no gum), cancellation type
and margins each move the price substantially. Reproduce the lot's own wording.
"Fine used" and "superb unmounted mint" are not interchangeable descriptions of
the same stamp.

**Certificates.** For any significant rarity, state whether the lot carried a
certificate and from whom. An uncertificated example of a famous rarity is a
different proposition, and the great classic rarities are also the most forged
items in collecting.

**Reprints, proofs, essays and facsimiles** are not the issued stamp. Read the
lot description carefully: many are sold openly as such and are worth a fraction
of the real thing.

**Covers and postal history.** A stamp on cover is priced on the whole item —
route, cancellation, rarity of usage — not on the catalogue value of the stamp.
Do not extract a stamp price from a cover sale.

## Access, as at 19 August 2026

David Feldman, Cherrystone and Heinrich Köhler returned 403 to automated
requests. The BPA Expertising site did not resolve at all and is therefore not
listed above. All others responded normally.

## Access, as at 2 September 2026

The Postal Museum (UK) and the Smithsonian National Postal Museum both returned
403 to a plain HTTP fetch, on both their landing pages and specific article
pages. Retried with a real browser session (Claude Browser pane): The Postal
Museum (UK) loaded normally with no challenge — use a browser-based fetch for
this source, not the plain HTTP tool. The Smithsonian site instead served an
active Cloudflare "Just a moment... / Request Verification" challenge even to
the browser session — this is genuine bot-detection, not a simple UA filter,
and was not attempted to be solved; treat the Smithsonian site as unreachable
by automated means for now. The British Library's
`bl.uk/philatelycollectionshub` hub URL 404'd. Postal History Foundation
responded normally to a plain fetch.
