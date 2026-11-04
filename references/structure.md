# Section structure

Dan's structure, sent 15 September 2026, for the movie memorabilia report. He has said the first one becomes the template for the series, so treat this as versioned: if he revises it, edit this file rather than the skill.

Audience, in Dan's words: "A relatively new person to the particular collecting area, excited by it, wants to learn more and collect good pieces, and might potentially like to make money from it in the future."

Keep investment sections in. Do not lead with them.

## 1. The Lowdown
- Brief overview
- Demographics: number of collectors, geographic spread, age range, gender split

## 2. Trends
- What is popular, props, clothing, autographs, and why. Auction price examples throughout.
- Who is popular, and why
- Who and what is falling out of favour

## 3. Getting started
- Glossary: screen-used vs screen-matched vs production-made vs replica; hero prop vs stunt prop; COA
- How to spot a fake: what to check, reputable authenticators
- Where to buy safely: auction houses vs dealers vs eBay and private sellers, and red flags
- Budget entry points: what is realistically collectible for your money
- Care, storage and display: light damage, humidity, framing
- Common beginner mistakes: overpaying, poor provenance, unknowingly buying reproductions

## 4. Upcoming market catalysts
Anniversaries and events that bring new collectors in. **List each event once.** A set released for an anniversary and the anniversary itself are one row.

## 5. The 10 most collectible movie stars

Ranked on auction performance. **Every entry must stand alone.** Name the film, the
object and the figure, even where an earlier section already did: readers skip
about, and an entry that leans on prior knowledge fails for most of them.

## 6. The 10 most valuable movie props ever sold

"Valuable", not "expensive". **Cross-check this list against every figure in the
document**. A lightsaber quoted at £2.7m in
section 2 was once missing from a top 10 whose bottom entries were £2.6m and
£2.5m, so the two tables disagreed about the market. Where something is excluded
on purpose, say why: poster art and a gala dress are not film props.

## 7. The expert view
Ghostwritten quote from Paul.

## 8. Investing in movie memorabilia
- Price indices, for example an extract from the PFC40 Autograph Index
- Examples of pieces that have sold twice
- Why invest

**The sold-twice examples carry a hard verification standard. See `sold-twice.md`.**
Both legs must name the **same lot**, with the link stated by an auction house, not
inferred. Eight such pairs were supplied in September 2026 and six were wrong, every
one of them a real recent result bolted onto an earlier sale of a different object.

## 9. Stock for sale
**Include this section only if PFC holds live stock in the category.** No stock, no section: leave it out and renumber what follows. Do not substitute a category we do stock, and do not write a section about valuations, grading advice or buying in other categories in its place. The stock check is the procedure in SKILL.md, "Stock for section 9".

A variety of interesting pieces from the relevant collection, **with images**. Dan
asked for images explicitly; a list of titles and prices is not this section.

- Pull live from the Shopify endpoint, `/collections/<handle>/products.json?limit=250`,
  never from an older report.
- **Check `variants[0].available` on every item and drop anything sold.** Four pieces
  in the movie collection had sold between one report and the next, including a
  &pound;25,000 Monroe photograph. Listing a sold piece in a lead magnet is worse than
  omitting it.
- Take the first image from each product, resize to about 600px, and embed it. Show a
  spread of prices, not only the top end: section 3 has just told the reader what
  &pound;200 buys, and this section has to prove it.
- Give each piece one line saying why it is interesting, and quote the price as listed
  with the date you pulled it.

## 10. Why buy from Paul Fraser Collectibles
**Include this section only if PFC sells in the category or has real expertise in it.** If we have nothing to sell and no expertise (trading cards and Pokémon, as at October 2026), leave it out. It sells our guarantee, returns and valuations, and a reader finishing a report on a field where we hold neither will ask what is being offered. Source: https://www.paulfrasercollectibles.com/pages/about-Paul-Fraser-Collectibles

## 11. Have a question?
Book a call. Always included, and renumbered to follow the last section kept. Where section 10 is omitted, do not write "speak to someone who handles this material every day" or any other claim of expertise in the field: just "Call or email us: the details are below."

---

# Adapting this to other categories

The series covers movie memorabilia, trading cards and Pokémon. Sections 1, 2, 4, 7, 8 and 11 carry across unchanged. Sections 9 and 10 are conditional on stock and expertise (below).

Three need category-specific treatment:

- **Section 3's glossary** is category-specific. Movies: screen-used, screen-matched, hero, stunt. Cards: grading scales, population reports, slabs, shadowless, 1st edition, error cards. Pokémon: the same plus Japanese and English printings, promos, trophy cards.
- **Section 5** is "most collectible movie stars" for film. For cards it is players or franchises; for Pokémon, characters or sets.
- **Sections 9 and 10** depend on PFC holding stock in the category, or having real expertise in it. The movie memorabilia collection has 71 pieces. **There is no trading card or Pokémon stock**, checked across the full 2,211-product catalogue, and no expertise in either, so for those two reports **sections 9 and 10 are left out** and the contact section is renumbered 9. The client's instruction, 5 October 2026: if we have nothing to sell and no expertise, those sections are not included. Re-run the stock check each time, because stock changes.
