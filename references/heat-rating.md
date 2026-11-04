# The heat rating: one to three stars

Every report carries a star rating for the field, out of three. It replaces the
`STRONG BUY` block that used to sit in the sidebar.

**The stars measure how active the market is right now. They are not advice to
buy or sell.** That distinction is the whole point of the change and it has to
survive into the document: a reader who takes three stars as "buy" has been
misled, and the report is a marketing communication going to people new to the
field who may act on it.

## Why the buy rating went

`STRONG BUY` was never computed. It appeared five times in this skill, twice
inside `{{ }}` placeholders in the template, and nothing anywhere defined a
criterion, a threshold or a second rating. No `HOLD`, no `SELL`, no downgrade
condition. All four reports in the series carried it, and a separate run of the
skill produced a bare `BUY` instead, which proved the value was not fixed but
undefined. An undefined rating is worse than a fixed one: the same category can
come out differently on two runs with nothing behind either.

A heat reading is honest in a way a buy rating was not. It describes the market
instead of instructing the reader, it is expected to change between reports, and
it serves a seller as much as a buyer.

## What the stars mean

| | Name | Meaning |
| --- | --- | --- |
| ★★★ | **Moving** | Records being reset, house totals up, most of what is offered selling, new money visibly arriving. Material is easy to sell and easy to find buyers for, and it is the easiest moment to overpay. |
| ★★ | **Steady** | The market trades reliably and prices are firm, and some signals are up, but not all four. Normal conditions, and where most fields sit most of the time. |
| ★ | **Quiet** | Records standing for years, totals flat or falling, material slow to clear. Hard to sell quickly, and the best conditions a patient buyer gets. |

Neither end is good or bad. Three stars is a seller's moment and a buyer's risk.
One star is the reverse. Say so in the explainer box rather than leaving the
reader to assume.

## The four signals

Each scores 1 or 0. Each needs a dated fact with an item number in
`sources-log.md` behind it. **A signal you did not research scores 0 and is
disclosed as not researched, never as absent.**

**1. Record recency.** Has the field's record been set or broken within 24
months of the report date? A record reset is the clearest public evidence of a
market in motion. Name the lot, the house and the date.

**2. House direction.** A named house's latest published annual total, or a
department total, against the prior year. Rising counts. A house calling its own
year a record counts. Stack's Bowers closing 2025 at $325m, up 18% on a prior
record year, is this signal exactly.

**3. Clearance.** A recent named sale documented as fully or near-fully sold.
Baldwin's "every single lot found a new home" is this signal exactly. A
sell-through percentage published by the house also counts.

**4. New demand.** A documented new cohort, geography or channel, with a source.
Baldwin's American buyers travelling to London for British tokens is this signal.
A forward-looking catalyst is **not**: a game released next year may bring new
collectors, but it has not brought them yet. That belongs in section 4.

## Bands

Count the signals you **researched**, and the signals that came back
**positive**. Both numbers matter.

    positives   4        ★★★
                2 or 3   ★★
                0 or 1   ★

**A rating needs at least 3 of the 4 signals researched.** Below that the rating
is withheld: the report says which signals are outstanding and carries no stars
until they are done. Render a withheld rating with **all three stars unlit**,
never with the positive count lit, or a withheld two reads as a confident one.

That rule exists because a zero has two meanings and only one of them is cold. A
signal that was looked for and came back empty is evidence. A signal nobody
looked for is not, and banding them together lets a hot market print one star
because the research was thin. The Pokémon report scored a single researched
signal, which under a naive count would have rated the field Quiet seven months
after it set the world record for any trading card. That is a broken scale, not
a cold market.

Three stars requires all four positive. If three stars is easy to reach, the
scale is worthless, which is the failure the buy rating already demonstrated.

## The trap this was nearly built on

Scored off the evidence logs as they stood, numismatics outranked Pokémon. That
is not because coins are hotter. It is because the coins report happened to
research annual totals and clearance, and the Pokémon report did not.

**A heat score computed from whatever is already in the log measures the
researcher's thoroughness, not the market's temperature.** So the four signals
are a required research step in phase 3, not an extraction at write-up time. Go
and look for each one. Record what you found, and record plainly when you looked
and found nothing.

## Writing it up

For the person writing the report. The research document carries each signal, its items and reading, the two counts and the band the rule gives; the rest of this section is how a report shows them.

**The Steady line in the sidebar key reads "Trades reliably and prices are firm, but not every signal is up."** It used to say "nothing has stepped up recently", which cannot describe a band that includes three positives: the Pokémon report printed it beside a verdict saying records were being reset.

**Section 8 carries the count, as the sentence "N of the four signals came back
positive" or as the marker `<!-- heat: N of 4 signals positive -->`.** The report's build check reads that sentence, works out the band, and
refuses to build if the sidebar's lit stars, its name, or the verdict disagree
with it, or if the sentence is missing. The Pokémon report carried three stars,
Moving, with one signal researched and no count stated anywhere, and passed
every gate the skill then had.

- The rating is **dated**: "as at 22 September 2026". It is expected to change.
- The sidebar carries the stars, the one-word name, and the explainer box.
- **The signals go in the investing section as a short table**: Signal | What we found | Reading
  (Up, Flat or Down). One row per signal that was found, each with its dated fact. No
  methodology and no account of how we looked. A signal that was researched and came back
  empty counts as 0 in the rating but gets no row and no sentence in the report; it is
  recorded in `sources-log.md` and the handover (it was cut from the Pokémon report on
  the client's instruction, 5 October 2026).
- **The count is a marker, not a sentence.** The build check reads either the old
  sentence or `<!-- heat: N of 4 signals positive -->` in the section 8 block, so the
  arithmetic stays checkable without the reader seeing it.
- **If every row reads Up but the rating is Steady**, add one plain sentence saying what
  is missing, in the reader's words ("a Moving market also shows most of what is offered
  finding a buyer, and no auction house publishes that"). Never use "clearance" or
  "sales clearing" in the report.
- **Open decision (client, 5 October 2026):** whether a price index (for example Card
  Ladder) may replace the Clearance signal, since a sell-through rate is rarely
  published. Until decided, Clearance stays a required lookup and the bands above stand.
- Where a signal was not researched, say so in that list. It is a fact about what
  we know, exactly like `not stated` on a price.
- The field's cooling segment still gets its paragraph in section 2. The star is
  for the field; the prose carries the nuance.

## Never

- Never raise a star to match an expectation, including the client's. If the
  evidence supports two, the answer is two, and the fix is more research rather
  than a better mood.
- Never write the stars as a recommendation. No "we recommend", no "strong buy",
  no "we urge swift action" attached to the rating.
- Never carry a rating forward from an earlier report. Re-derive it every time.
