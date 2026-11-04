# Sources: coins and precious metals

Read `sources-major-houses.md` and `sources-press.md` alongside this file.
Heritage Auctions, in the majors file, runs one of the largest coin departments
in the world; its numismatic arm is `coins.ha.com`.

## Primary authorised sources — specialist numismatic houses

Realised prices only, verified by fetching the lot or results page.

`✓` fetches normally. `⚠` refuses an automated request but loads in a browser
session with no challenge. `⚠⚠` puts up an active challenge and needs the
operator present. Measured 22 September 2026.

**A rung is a property of the page you are citing, not of the domain.** Noonans'
homepage loads unattended and its results archive does not. Test the page that
carries the figure.

**United States**

- ✓ Stack's Bowers Galleries — https://stacksbowers.com/ ⚠ — America's oldest
  coin auctioneer. Its `sell-consign/world-record-prices/` page is the single
  best published record of numismatic records and is worth reading first.
- ⚠ Heritage Auctions, rare coins — https://coins.ha.com/ — realised prices
  need a free Heritage account; the press releases are public and carry records.
- ⚠⚠ GreatCollections — https://www.greatcollections.com/
- ⚠ David Lawrence Rare Coins (DLRC) — https://www.davidlawrence.com/ — a
  JavaScript application: empty to a plain fetch, fine in a browser.
  `dlrcauctions.com` redirects here.

**United Kingdom**

- ✓ Spink — https://www.spink.com/
- ✓ Baldwin's — https://www.baldwin.co.uk/
- ⚠⚠ Noonans Mayfair — https://www.noonans.co.uk/ — formerly Dix Noonan Webb.
  The homepage loads in a browser, but `/archive/`, which is where the prices
  are, serves a Cloudflare challenge. Treat it as needing the operator.
- ✓ Sovereign Rarities — https://www.sovr.co.uk/
- ✓ Morton & Eden — https://www.mortonandeden.com/
- ✓ Heritage Coins — https://www.heritagecoins.co.uk/ — a UK dealer in
  sovereigns and collectable coins. **Not** Heritage Auctions; do not conflate
  the two in a citation.

**Europe and ancients**

- ⚠ Künker — https://www.kuenker.de/en
- ✓ Numismatica Ars Classica (NAC) — https://www.arsclassicacoins.com/
- ✓ Classical Numismatic Group (CNG) — https://www.cngcoins.com/ — Greek, Roman
  and British.
- ✓ Atlas Numismatics — https://www.atlasnumismatics.com/

## Grading and census (authoritative for grade, never for price)

- ⚠ PCGS — https://www.pcgs.com/ — its Auction Prices Realized index,
  `pcgs.com/auctionprices`, aggregates realised prices across houses and loads
  in a browser. Treat that index as an aggregator, not as a grader's opinion:
  find the sale there, then verify it on the selling house's own page.
- ✓ NGC — https://www.ngccoin.com/

## Aggregators and archives (context only, NEVER a realised price on their own)

They index other houses' sales and their records go stale. Use them to find a
sale, then verify it on the selling house's own page.

- ⚠ NumisBids — https://www.numisbids.com/
- ⚠ Sixbid — https://www.sixbid.com/

## Mints and institutions (context, history, photography — never price)

- ⚠ The Royal Mint — https://www.royalmint.com/
- The United States Mint, the British Museum and the Smithsonian's numismatic
  collection are usable for history and photography on the same terms.

## Trade press (context only)

- ✓ Coin World — https://www.coinworld.com/
- ✓ Numismatic News — https://www.numismaticnews.net/
- ✓ COINage — https://www.coinagemag.com/

## Do not use

- **`legendauctions.com`** — the domain has lapsed and now serves a Danish
  casino site. Legend Rare Coin Auctions is a real house; that address is no
  longer it. Do not restore this link without confirming the current domain.
- **`goldbergcoins.com`** — does not resolve. Ira & Larry Goldberg is a real
  house; find the working domain before citing it.
- **`romanumismatics.com`** — returned `522`, origin down on 22 September 2026.
  Not a block. Retry before writing it off.

## Verification notes for coins

**Grade is the price, and the service matters.** PCGS and NGC both use the
70-point Sheldon scale, and a point either side of the market's break point can
double a value. Always give the number, the service and any qualifier, exactly
as the lot states them.

**A "details" grade is not the same coin.** Cleaned, polished, scratched,
tooled, whizzed or repaired examples are slabbed with a details or genuine
designation rather than a straight numeric grade, and sell far below a
straight-graded coin of the same nominal condition. Reproduce the designation.
Cleaning is the commonest value-destroying fault in the field and the easiest
one to leave out of a price comparison.

**CAC and pedigree.** A CAC sticker carries a premium. So does a named pedigree
— Eliasberg, Pogue, Garrett, Norweb, Bruun — which is usually part of the lot
title and part of the price. Keep it.

**Bullion value is a floor, not a price.** A gold coin is worth its metal
whatever else is true. For modern issues and common-date sovereigns the metal is
most of the value, and quoting a numismatic premium on one is misleading. Say
which you mean.

**Mintage is not survival.** 445,500 1933 double eagles were struck and 13 are
known. Quote the surviving population, name the census, and give the date you
checked it, or leave the number out.

**Hammer versus price realised.** As everywhere: say which, take both from the
same page, never compare one house's hammer against another's premium-inclusive
total.

**Proof, mint state and circulation strikes** are different objects. PR/PF and
MS prefixes are part of the grade, not decoration.

**Currency.** This field sells in more currencies than most. Künker and NAC
publish in euros, Swiss houses in francs, Hong Kong sales in HKD. Stack's Bowers
publishes its Scandinavian record at €1,200,000 and gives no dollar figure at
all. Convert, disclose the conversion, and never let a third currency stand in
for sterling or the dollar.

## Access, as at 22 September 2026

Every source above was reached. Spink, Baldwin's, Heritage Coins, Sovereign
Rarities, Morton & Eden, NAC, CNG, Atlas, NGC and all three trade titles
answered a plain fetch. PCGS, Stack's Bowers, Heritage coins, Künker,
NumisBids, Sixbid, DLRC and the Royal Mint refused an automated request and
loaded in a browser session with nothing asked of anyone. GreatCollections
served an active "Verifying Website Traffic" challenge twice, and Noonans serves
one on its results archive though not on its homepage; both need the operator,
and neither challenge is to be solved by the skill. The ladder for a page that
will not open: a plain fetch, then the in-app browser, then the user's own
Chrome, where their logins are (the workspace `CLAUDE.md`). A challenge is never
solved and a credential is never typed; if the page still will not open, the
figure does not go in.

## Note on this file, 22 September 2026

Rewritten. The previous version carried a STRICT MANDATE naming twelve
authorised price sources, of which five were music and entertainment houses —
Julien's, Tracks, GottaHaveRockAndRoll, Omega Auctions and WyCo Vintage, whose
own title tag reads "Vintage Band T-Shirts & Concert Tees". It had been copied
from the music memorabilia list and never rewritten. The real coin houses sat in
a single "context only" bucket that also held a grader and three magazines, so
Spink, Baldwin's, Stack's Bowers and Heritage Coins were barred from carrying a
price. Spink was simultaneously a primary authorised source in
`sources-stamps.md`. Published articles in the corpus had been citing Spink,
PCGS, GreatCollections and Stack's Bowers regardless, so this file documents the
standard already in use rather than imposing a new one.
