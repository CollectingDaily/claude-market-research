# Sources: toys

Agreed with the user on 30 September 2026. Read `sources-major-houses.md` and
`sources-press.md` alongside it, exactly as for any other field.

**Scope.** Toys means playthings: action figures, diecast, tinplate and
clockwork, trains, teddy bears and soft toys, dolls, construction toys such as
LEGO and Meccano, and board games. Sealed video games and trading cards are out:
cards and Pokémon have their own file (`sources-trading-cards.md`), and Heritage
sells video games through a separate department.

A realised price must come from a page you have fetched in this session. Press
is context only.

## Primary authorised sources: realised prices

- **Hake's Auctions**, https://hakes.com/. Pop culture and vintage toys, and
  the deepest archive of Kenner *Star Wars* results. Also on the comics list.
- **Vectis**, https://www.vectis.co.uk/. UK specialist: diecast, tinplate,
  trains, TV and film toys, dolls and bears.
- **Morphy Auctions**, https://www.morphyauctions.com/. Toys, mechanical banks,
  advertising.
- **Bertoia Auctions**, https://www.bertoiaauctions.com/. Antique toys,
  mechanical banks, tinplate.
- **Theriault's**, https://www.theriaults.com/. Antique and collectable dolls.
- **LCG Auctions**, https://lcgauctions.com/. Graded action figures.
- **Goldin**, https://goldin.co/. Mainly cards; cite it only for toy lots.

## Majors

Heritage Auctions (`ha.com`), Christie's, Sotheby's, Bonhams, Phillips and
Julien's, all from `sources-major-houses.md`. Heritage runs a toys and
collectibles department. Christie's and Bonhams sold teddy bears and dolls
through dedicated sales for decades, so their older results are the record for
bears.

## Our own articles

Our own articles are never sources. Toy articles often quote valuations, not sales: never put a valuation in a ranking of prices realised.

## Grading (authoritative for a grade, never for a price)

- AFA, Action Figure Authority, https://www.toygrader.com/
- CAS, Collector Archive Services
- UKG, UK Graders

## Demographics and market size

These are not price sources. Trade bodies and market data firms may be cited for
collector numbers and market size: Circana for toy sales, The Toy Association and
the British Toy & Hobby Association. The press list covers
reporting of their figures.

## Verification notes for toys

**Carded, boxed and loose are three markets.** A *Star Wars* figure on its
original card, the same figure loose, and the same figure loose with every
accessory are different objects at very different prices. Say which, as the lot
does, and name the card back (12-back, 20-back and so on) where the lot gives
it.

**A grade is only a grade with the grader named.** AFA, CAS and UKG use
different scales. Reproduce the lot's wording: "AFA 85", not "graded 85".

**Prototype, production and reproduction.** A factory prototype, a production
piece and a later reissue or reproduction are separate markets. Kenner prototypes
and hand-painted samples are where the records are. Reissues are routinely
listed as originals.

**Hammer versus total.** Vectis's department highlights say "Hammer Price", but
its lot pages hide prices behind a login, and its news stories, which are the
readable record, state their basis story by story: "*Inclusive of Buyers
Premium", "including commission", a bare asterisk, or nothing. Record what each
story says. LCG ("Prices Shown Include Buyer's Premium"), Morphy's lot pages
("Final prices include buyers premium"), Bonhams ("inc. premium") and Theriault's
state totals. Morphy's own press releases often run exactly 2.5% above its lot
pages for the same lot: use the lot page. Heritage's releases rarely say which.
Never put a hammer and a total in the same column without saying which is which.

**Euros are the record for German sales.** Steiff and Märklin records set in
Germany are published in euros. Keep the euro figure and add both sterling and
dollars.

**Private sales are not auction records.** The 1963 G.I. Joe prototype went to
Stephen Geppi privately, through Heritage, after failing to reach its reserve.
Say "private sale" wherever it appears.

## Access, as measured on 30 September 2026

- **Vectis** reads with a browser user agent, but answers verify_sources.py's own
  agent with HTTP 202 and an empty body. Read each cited story in the browser
  pane.
- **Hake's** moved platform in 2026. Every pre-2026 lot page returns 404 and past
  results are not on the new site; only Wayback copies survive, which are not
  cited. Current lots read normally.
- **Bertoia**: the sell-your-antique category pages read, except the banks page,
  which is served gzip-compressed regardless of the request and must be read in
  the browser. Results releases are PDFs, which neither checker reads.
  bid.bertoiaauctions.com is a JavaScript shell.
- **Goldin**: a JavaScript shell; the lot page reads in the user's Chrome, but
  the price shows "$0 Winning Bid" unless signed in to Goldin, which the user is
  not. Guinness World Records publishes the record figures.
- **LCG**: 403 to a fetch; reads fully in the user's Chrome, price included.
- **Heritage**: 403; press releases read in the user's Chrome. Lot prices need
  the Heritage login, which was signed out in the user's Chrome on this date.
- **Christie's**: the lot page reads, but the price realised sits only in the
  page's embedded data; read it with the browser's DOM.
- **Theriault's**: a JavaScript shell; reads in a browser.
- **Morphy** (www and auctions.), **Bonhams**, **Sotheby's catalogue text** and
  **Guinness** read with a plain fetch. Sotheby's realised prices need a login.
Re-test the page that carries the figure, not the front door.
