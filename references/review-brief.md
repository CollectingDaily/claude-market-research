# The independent review

Read by the `market-research-reviewer` agent, after the compile phase and before delivery. **Mandatory.**

The research document is what a person writes a market report from, and they will take every line of it as checked. `check_log.py` has proved every item against its saved page, and `compile_research.py` has matched every price and percentage in the analysis to the item named on its line. Neither can tell whether the analysis says what the items show, whether a ranking is in the right order, whether a resale pair is one object, or whether a "missing" need was really missing. Every gate the market report series had passed the Pokémon report, and an outside reader then found a dozen errors in one read. This review is that outside reader, before the writer starts.

## What the reviewer checks

1. **Scope.** Every item sits inside plan.md's stated scope, and the numbered section titles are named for the field.
2. **Section assignment.** Each item serves the section it is listed under. An item missing from the section its card was planned for has a reason in For the writer. Nothing a section needs sits only under Other evidence.
3. **What the analysis says.** Every sentence says what its named item shows: the date, house, grade, copy and basis as the item states them, and the figure under the right item. No figure is computed (a conversion, a percentage, a multiple, a per-annum rate, a per-item share of a lot, a sum or an average) and none is rounded.
4. **Rankings, sections 5 and 6.** The order is right on plan.md's basis. Every item in the log that belongs is in it: scan the `--items` lines for a price above the bottom entry that is missing. One price basis only, the other listed beneath and unranked against it. The same object twice is one row. Each exclusion has its reason. Where currencies cross, the `Rate:` line is fx.py's.
5. **Sold twice, section 8.** Each pair in the table meets all four conditions of `sold-twice.md`: check the house's own words linking the two sales on the saved page of the later one. Each rejected pair is named with the condition it fails.
6. **Heat signals.** Each signal's items show what its Reading says, inside the window `heat-rating.md` gives for it. The researched and positive counts are right, the band is the one the rule gives, and a rating with fewer than three researched is withheld. "Not researched" and "researched, none found" are told apart from the research logs' heads.
7. **Conflicts.** Look in the log for the same sale under two items with a different price, date or house: each one is listed, with both figures and both items, and nothing is decided, averaged or dropped.
8. **Missing lines and coverage.** For each need `article-structure.md` names, look for an item that meets it before accepting it as missing, and check that each need the analysis says is met really is.
9. **Price basis.** Hammer and the total with buyer's premium are never compared in the analysis, and every priced item shows its Basis.
10. **Sources.** No item rests on justcollecting.com, news.justcollecting.com, collectingdaily.com or a PFC blog post.
11. **What was lost.** For the writer names each dropped or uncaptured page that cost a section something.
12. **The page.** British English, plain, one paragraph per line, and nothing names a skill or how the run works: the document may be handed on.

## What is not a finding

A figure printed exactly as its page states it, in its own currency; a conflict listed and not decided; a `not stated` shown as the log has it. Those are the document's rules.
