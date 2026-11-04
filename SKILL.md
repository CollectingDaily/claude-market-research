---
name: market-research
description: "Research a collecting category for a Paul Fraser Collectibles market report and deliver one markdown research document holding every result, section by section, as a guide for the writer, who writes the report and finds its images by hand. Same sourcing rules, research cards, signed-in Chrome captures and proven evidence log as a full report. Never drafts the report, never sources images and never builds a PDF. Use when asked for market research, the research for a market report, or a research document or research pack for a collecting category; not for a finished, designed report."
---

# Market research

The research behind a Paul Fraser Collectibles market report, delivered as one markdown document that guides the person who writes the report. It is the full PFC market report research: the plan, the task cards, the walled-page captures in the user's own Chrome, the proven evidence log and the stock pull. Then it compiles what was found, section by section, and stops. **No report prose is written, no image is sourced and no PDF is built**: the writer writes the report and finds the images by hand.

## Run it end to end. Ask only when a page is blocked.

The user's standing instruction (24 September 2026): "do the process and deliver, not questions". Every step below is done without stopping for the user, with one exception added on 7 October 2026: a CAPTCHA, a verification check or a lapsed login in their Chrome. The phase 7 checkpoint is an internal check, not a stop. Decide by these rules and report the decisions in the handover:

- **Our own articles: images only, never read.** The user's instruction (13 October 2026): our own articles (`Archive/1 - COLLECTING DAILY`), justcollecting.com, news.justcollecting.com and collectingdaily.com are never used for anything other than images, and are never read. That replaces the 7 October rule, which still let them be read as leads. Not as a source, not as a lead, not for a lot, a house, a date or a ranking. Research every figure, date, grade, house and claim online, on the house's or publisher's own page. This skill takes nothing from them, not even a photograph: images are the writer's. A PFC blog post is never cited. `check_log.py` and `compile_research.py` fail any log or analysis line that cites one of ours, and `fetch_pages.py` refuses their URLs.
- **A page will not open: the user's own Google Chrome**, where their logins already are (`mcp__claude-in-chrome__*`), then a Google `site:<house>` search in their Chrome. The user's instruction (7 October 2026): "YOU MUST USE GOOGLE CHROME WHERE THE CREDENTIALS FOR LOGGING IN ARE ALREADY THERE". The in-app browser is not used for walled pages: it has none of their logins (`references/blocked-sources.md`).
- **Chrome not connected, a CAPTCHA or slider, or a lapsed login: pause and ask.** The user's instructions (7 October 2026): "if you cannot see something due to captcha, ask me", and "it should stop to ask me to connect chrome or to move the slide or login, not to stop the whole process". Stop at that step and say in one line what is blocked and what to do ("Chrome is not connected: open Chrome and click the Claude extension", "Heritage shows a verification slider on <url> in your Chrome: please move it and tell me", "Heritage login has lapsed: click Sign-In on ha.com in Chrome"). Asking is a pause, not the end of the run: when they say it is done, read the page and carry on from that point. Never abandon the research, never skip past the page as if it had been read, and never drop the figure without asking first. Never solve it yourself and never type a credential.
- **Two sources disagree: decide nothing.** Log both, and the research document lists both figures, both items and what kind of page each is, for the person writing to decide. A finished report decides conflicts, because its reader must never see working; a research document is the working.
- **An existing claim turns out wrong** against the house's record (a promotional car listed as a film prop, a dress misidentified): log what the house says, and the conflict.
- **A heat signal is ambiguous:** log it, and the compiler scores it by the letter of `references/heat-rating.md` (a whole-house annual total counts for house direction) and says what is ambiguous.
- **A section needs a count** (three resale pairs, ten in a top ten): meet it with verified entries. Look harder before cutting one. Never pad with an unverified one. What falls short goes on the section's Missing line.
- **Only four things ever justify asking:** a request that could mean two different reports, stock that does not exist for the field, an instruction that would break the sourcing rules in `references/verification.md`, or a page their Chrome shows behind a CAPTCHA, a verification check or a lapsed login. Otherwise, deliver.

**Ten files govern this skill. Every one is read in full, by the agent and at the phase that uses it.**

| File | What it is | Read at |
| --- | --- | --- |
| `references/structure.md` | Dan's section list for the report. His spec, not mine. If he revises it, edit that file rather than this skill. The research document is laid out on it. | main session, phase 1; compiler; reviewer |
| `references/article-structure.md` | What goes inside each section: its job, what it needs before it can be written, and how it fails. The compiler judges coverage against it. | compiler; reviewer |
| `references/verification.md` | The sourcing standard, the evidence log, and the Sources field. | researchers, in full |
| `references/heat-rating.md` | The one-to-three star market heat rating: what the stars mean, the four signals behind them. | main session, phase 1 (the four signals go in plan.md); compiler; reviewer |
| `references/blocked-sources.md` | What to do when a page will not open: straight to the user's own signed-in Chrome, asking them when a CAPTCHA or login blocks it, what you never do, and how an assisted read is recorded. | researchers |
| `references/sold-twice.md` | The verification standard for section 8's resale pairs, and the six that failed it. | researchers (section 8 pairs); compiler; reviewer |
| `references/capture.md` | Reading walled pages in the user's Chrome so the text goes straight to disk and only a receipt comes back. | capturer |
| `references/walled-first.md` | The walled pages the plan lists for the first capturer, so the researchers read them from disk instead of finding them walled. | main session, phase 1; researchers |
| `references/review-brief.md` | The independent review a fresh agent runs before delivery, and what it checks that no script can. **Mandatory.** | the reviewer, phase 9 |

## Keeping the run inside the session limit

### Hard limits (from the art run of 26 to 27 October and the wine run of 28 October 2026; they override anything else in this skill)

The art report finished but cost 67.4M weighted tokens against a 10M target: main session 16.9M (233 requests, mean context 549k), six agents 50.5M (60 to 130 requests each, mean context 234k to 494k). **Cost grows with the square of an agent's length**: every request re-sends everything the agent has read, so one agent making 120 calls costs about four times what five agents making 24 calls cost for the same work. **Resuming an agent reloads its whole context**: twelve resumes in the art run each re-sent 400k to 800k tokens. Accuracy depends on neither.

1. **Task cards, not parts.** plan.md splits research into 8 to 12 cards, each one narrow job (for example "the ten all-time top lots: read each house lot page", "the four heat signals", "budget bands: 12 sold lots"), naming its targets where they can be named, with a cap of 12 log items and its own `research-<card>.log.md`. Each card is a `### <card> (sections …)` heading under `## Cards` in plan.md, which is where `next_step.py` reads them, and where `compile_research.py` reads which sections each card's items were for. Items across all cards stay within what a report prints plus a quarter.
2. **Every agent has a call cap**, finished or not: researcher 25 tool calls, capturer 15, each compiler phase 35, reviewer 40. At the cap it stops and returns what is done and what is not. Unfinished work is never a resume and never a card of the main session's own making: it becomes one of the two gap cards `next_step.py` allows, or goes in the handover.
3. **Never resume an agent.** Not for a follow-up, not for captures, not for review fixes. A follow-up is a fresh agent with a few lines of brief naming only the files it needs. SendMessage has no use in this skill.
4. **The main session does not use the browser.** Walled pages go to a fresh `market-research-capturer` agent (`agents/market-research-capturer.md`), which works the user's Chrome and returns receipts only. If it reports Chrome not connected, a CAPTCHA, a slider or a lapsed login, `next_step.py` prints ASK: the main session puts it to the user in one line, and once they have cleared it runs `next_step.py "$W" --cleared`, which sends those pages again. Only if the capturer cannot use the Chrome tools does the main session capture, and then one browser_batch per site (snippet B wherever pages are server-rendered), never page by page.
5. **The main session plans, launches and relays, nothing else.** It reads SKILL.md, `structure.md`, `heat-rating.md` and `walled-first.md`, greps the allowlists' house headings, runs `stock.py`, writes plan.md, and from then on runs `next_step.py` after every notification and launches what it prints. Agents do the rest: the captures, the log check (the log agent), the analysis (the compiler). It never reads a page, a capture, a log, a brief, the analysis, the research document or the review file, never searches, never debugs a script, and never polls: notifications wake it. On a notification it makes one `next_step.py` call and the launches it prints, or ends the turn on WAIT. Target: about 50 requests, under 150k context.
6. **The compiler runs as fresh agents, one per phase:** compile (the analysis, then the document), and after the review a further fresh compiler in phase fix with only the review file and the analysis.
7. **Decide rankings and their proof before research.** plan.md names each ranking basis and the pages that prove it, and gives those pages a card (for example "best result since <date>" needs the houses' season-results pages). In the art run a ranking basis chosen late forced three extra passes.
8. **PDF sources cannot be checked here** (`fetch_pages.py` saves a source PDF, such as a house's year-end release, as raw bytes, and the gate cannot read it): never use a PDF as a source; find the same fact on an HTML page or leave it out.
9. **`scripts/next_step.py` decides every launch, from plan.md to delivery.** Run `python3 ~/.claude/skills/claude-market-research/scripts/next_step.py "$W" --usage <N>` once plan.md is written (N from item 11), and `next_step.py "$W" --returned <name>` after every agent notification (the name is the description it printed). Launch exactly the agents it prints, with the description and prompt it prints, all in one message, and nothing else. WAIT: do nothing until the next notification. ASK: put its BLOCKED lines to the user at once, one line per site, and run `--cleared` when they say it is done, or `--drop-blocked` if they say to go on without those pages (the research document lists them). HOLD: wait for the user; nothing blocked is read until they answer. The receiver queues a page whose sold price needs their sign-in by itself, and refuses an error page (it is tried again), so the asking never depends on an agent remembering. STOP: tell the user in one line what the last agent returned, and wait. It runs the cards all at once, with a capturer for the plan's `## Walled pages` lines; once every card is back, one capture of every page they queued in `walled-<card>.tsv`, in parts of 24 run one after another; readers, at most 12 captured pages each; the phase 7 checkpoint, where a gap gets `--usage <N> --gap <name> "<sections>" "<what is missing>"` (at most two in the run, none past 25 points of the 5-hour limit) and no gap gets `--usage <N> --close`; then the log agent, the compiler's compile phase, the reviewer, the compiler's fix phase, and DELIVER, each from a brief it writes to `$W/briefs/`. A step whose file is missing afterwards (the log marker, the research document, the review file, the document compiled again after the review) gets one more fresh agent, then STOP; after a STOP, a plain `next_step.py "$W"` carries on once the missing file exists. Research already on disk starts with `--usage <N> --from-logs`, which goes straight to the log agent. It is a script because the rule did not hold: the wine plan of 28 October 2026 said "one capture sweep follows research, then a lean researcher logs the captures", and the main session still launched seven capture agents, eight second-pass readers and three late cards.
10. **The effort level comes from `~/.claude/settings.json` when it sets one.** Its `env` block can hold `CLAUDE_CODE_EFFORT_LEVEL`, and that overrides both the app's effort control and every agent file's `effort:` line. At max the capturer, which only opens and saves pages, thought about 7,000 tokens a step and the researchers about 8,600, and that reasoning stays in each agent's context. The user is on a subscription: the measure is how much of the session a run uses, never money. In phase 1, run `grep -o '"CLAUDE_CODE_EFFORT_LEVEL": *"[a-z]*"' ~/.claude/settings.json`. If it prints a level, tell the user in one line in your first message that every agent will run at that level whatever the app shows, then carry on. Never edit their settings yourself.
11. **Measured against the 5-hour limit.** The market report delivers both PDFs on at most half the 5-hour limit (the user's instruction, 28 October 2026); the research alone must come in under that. Read the limit with `get_usage` (`mcp__ccd_session_mgmt__get_usage`, loaded through ToolSearch) before planning and pass its 5-hour percent to the first `next_step.py` call; read it again at the checkpoint, where `next_step.py` refuses gap cards once the run has used 25 points; and at delivery, where `next_step.py "$W" --usage <N>` prints the points the run used for the handover. If the start reading leaves less than 50 points before the limit, say so in one line with the reset time, and carry on.
12. **Models (the user's decision, 28 October 2026).** Researchers (medium) and the capturer (low) run Haiku 5.5: every figure they log is checked by `check_log.py` against its saved page. The compiler, which writes what is delivered, and the reviewer run Sonnet 5.5 at high effort: no script checks what the analysis says the items show. Each agent file pins its model. Never save session usage by weakening the compiler or the reviewer.

The coins report of 22 October 2026 used the whole session window and did not finish: nine research agents researched twice because the first four could not open Heritage, Stack's Bowers, PCGS or Sotheby's, and the log held 391 items for a report that printed about 100. None of the rules below lowers a standard: every figure is still read on its own page, `check_log.py` still proves every item, and the fresh review stays.

- **The main session orchestrates, at medium effort.** If the session is at high or max effort, say so in one line at the start and carry on while the user switches it: the run does not wait. The app's control cannot lower it while `~/.claude/settings.json` sets a level (Hard limits 10).
- **Walled pages in one pass, through `next_step.py`.** Pages the plan already knows are walled (from `references/walled-first.md` for the field) go under `## Walled pages` in plan.md as bulleted URLs or `GOOGLE site:<domain> <words>` lines, and are captured alongside the cards. Agents read captures from `$W/attested/` and never fetch a walled domain. Anything walled they still need goes to `walled-<card>.tsv`, is captured once every card is back, and is logged by the readers `next_step.py` briefs. Never a second full research pass.
- **A fact budget per card, in plan.md**, matched to what a report prints: about 15 candidates for the top ten, 10 to 12 series for section 5, 20 to 25 priced results for trends, 12 to 15 results across the budget bands, 25 to 30 facts for section 3, 12 to 15 for demographics, indices and catalysts, and each of the four heat signals. Agents stop when their budget is met with verified items. More items is not more accuracy.
- **Research runs in `market-research-researcher` agents**, one per task card (Hard limits 1), all launched together in the background in the first minutes as `next_step.py` prints them, covering every section, the budget bands and the series included, so nothing is added late.
- **The independent review runs in a `market-research-reviewer` agent** (Sonnet, high effort), whatever model the session uses. It writes its findings to `$W/review-<date>.md` and returns only their count; the fix compiler reads the file, so the findings never pass through the main session.
- **Nothing is read whole into the main session that a script can summarise.** Few calls, each doing a lot: chain a step's commands into one Bash call, and print a summary rather than a file.
- **Measure it.** The handover gives the points of the 5-hour limit the run used. `run_cost.py` then shows, per agent, the requests and contexts behind them.
- **Scripts explain themselves.** Do not read a checker's source mid-run.

**Check the agents are installed** at the start, in the same call as phase 1's reads:

```bash
for a in market-research-researcher market-research-compiler market-research-reviewer market-research-capturer; do cmp -s ~/.claude/skills/claude-market-research/agents/$a.md ~/.claude/agents/$a.md || { mkdir -p ~/.claude/agents && cp ~/.claude/skills/claude-market-research/agents/$a.md ~/.claude/agents/; echo "$a installed or updated: a new session may be needed before the Agent tool lists it"; }; done
```

If the Agent tool does not list one of the four agents, a new session is needed: say so to the user in one line and stop, because `general-purpose` would run on the default model (Haiku), and the compiler and the reviewer never run on it (Hard limits 12).

The scripts:

| Path | What it does |
| --- | --- |
| `scripts/next_step.py` | The run's driver (Hard limits 9), plan.md to delivery: reads plan.md, the walled queues, `attested/`, the files each step leaves and its own `briefs/state.json`, and prints the one thing to launch next, with each agent's description and prompt; every brief is written to `$W/briefs/`. |
| `scripts/verify_sources.py` | Checks each logged price and quote against its page; `check_log.py` runs it. |
| `scripts/fetch_pages.py` | Saves any number of pages to `$W/pages/` in one call, with `verify_sources.py`'s own fetcher, so the text saved is the text the gate checks. Queues walled pages in `walled.tsv`. |
| `scripts/find_figures.py` | Reads saved pages the cheap way: only the sentences with figures or named terms, numbered. `--around N` for context; `--quote` and `--price` check a log block exactly as the gates will. |
| `scripts/capture_server.py` | The local receiver for walled pages read in a browser: writes `attest.py`-format captures straight to disk and returns a receipt. `references/capture.md` has the snippets. |
| `scripts/attest.py` | Records a page that could only be read with the user present: the page text, the URL, the wall and who cleared it. |
| `scripts/queue_blocked.py` | Puts a captured lot whose sold price is behind the user's sign-in on the list they are asked about. |
| `scripts/check_attested.py` | Checks the log's assisted reads against those captures, and reports every source that needed the user. |
| `scripts/merge_logs.py` | Joins the researchers' `research-*.log.md` into `sources-log.md`, numbered once, each item marked with the card it came from, without anyone retyping them. |
| `scripts/check_log.py` | Phase 5 in one call: lint, `verify_sources.py` (whole log offline, unattended prices online), quotes for fact items, `check_attested.py` for assisted reads. Prints only failures. |
| `scripts/stock.py` | Section 9's stock in one call: pages each collection's `products.json`, saves the listings, drops sold pieces, downloads and resizes each first image, writes `stock/stock.tsv`, prints one line. |
| `scripts/fx.py` | The ECB daily reference rate, either way. Used only to put a ranking across currencies in order: the research document prints every price as its page states it. |
| `scripts/compile_research.py` | Builds the research document from `sources-log.md` and the compiler's `analysis.md`, copying every item in full, and refuses to write it while the analysis carries a price or percentage that is not in the item named on its line. `--items` prints the log one line per item. |
| `scripts/run_cost.py` | What a run cost and where, from the session transcripts: requests, context at start, mean and peak, per agent. Run it after delivery. |

The skill covers every field with a source list: art, coins, comics, film and entertainment, music, stamps, trading cards, wine and spirits, toys, autographs and historical documents, political memorabilia, sports memorabilia, royal memorabilia, space and aviation, photography, and rare books.

**`references/structure.md` is the section list.** The research document carries all eleven of Dan's sections in order, each named for the field, sections 9 and 10 marked out where plan.md leaves them out.

## Where the files go

`<root>` is the folder the session is working in, unless the user names another.

```
<root>/Market research/<Topic>/
    <Topic> market research.md        the deliverable: the research document
    <Topic> market research.docx      the same, for Word, LibreOffice and Google Docs (when pandoc is installed)
    workings/                         $W
        plan.md                       what each card gathers
        research-<card>.log.md        each researcher's blocks
        sources-log.md                the evidence log (merge_logs.py builds it)
        analysis.md                   the compiler's analysis, the only part written by hand
        pages/                        pages, as text, read with find_figures.py
        attested/                     captures of walled pages
        walled.tsv                    pages a fetch found walled (a record)
        walled-<card>.tsv             pages a researcher needed and could not fetch
        briefs/                       next_step.py's state.json, every agent's brief, blocked.tsv, not-captured.tsv, the markers
        dropped.md                    items the log agent dropped, with URL and reason
        review-<date>.md              the reviewer's findings
        stock/                        the stock listings, product images and stock.tsv
```

## Audience

The research serves Dan's reader, verbatim: *"A relatively new person to the particular collecting area, excited by it, wants to learn more and collect good pieces, and might potentially like to make money from it in the future."* Plan the cards for that reader: the getting-started facts and the budget bands matter as much as the records.

## Sourcing

`references/verification.md` holds the sourcing rules, and they are not advisory.

**Read the field's source file before you search.** The source lists are in `references/sources/` and the routing table is in `references/verification.md`.

Every run reads three: the field's own, `sources-major-houses.md` and `sources-press.md`. Each researcher reads all three in full. The main session greps their house headings for the plan and reads no more.

**You must open and read every page you cite.** A search result is a way to find a candidate URL and nothing else. A 200 status with a Cloudflare interstitial behind it is not a readable page. If you cannot copy the sentence that states the figure, you have not verified it.

**A page that will not open is not automatically `not stated`.** Take it straight to the user's own Google Chrome (`references/blocked-sources.md`), where they are signed in to Heritage, Propstore, Sotheby's and the titles they subscribe to. **Use their Chrome without asking; the in-app browser is not used for walled pages.** If Chrome is not connected, or shows a CAPTCHA, a verification check or a sign-in wall, **pause and ask them** in one line, naming the page and what to do; when they say it is done, read it and carry on from that point. Drop a figure only when they say to, or when the page, once open, does not state it. An assisted read is recorded by `capture_server.py` (`references/capture.md`) in `attest.py`'s format and checked by `check_attested.py`.

Keep an evidence log at `$W/sources-log.md`, in the format `references/verification.md` specifies, then prove it:

```bash
python3 ~/.claude/skills/claude-market-research/scripts/check_log.py "$W/sources-log.md"
```

Nothing is compiled until it exits zero (`briefs/log-ok`). The research document carries no footnotes, so `verify_citations.py` has nothing to check on it (it prints NOTHING CHECKED); `compile_research.py` is the check on the one part written by hand.

## Our own articles: images only, never read

The user's instruction of 13 October 2026: our own published articles (`1 - COLLECTING DAILY` in the vault), justcollecting.com, news.justcollecting.com and collectingdaily.com are never used for anything other than images, and are never read. It replaces the 7 October rule, which still let them be read as leads, and, for this research, the workspace `CLAUDE.md` permission to cite them.

- **Images only, and the images are the writer's.** This skill takes nothing from them. Never read an article's text, never open one in a browser, never fetch one, never search one for a lot, a house, a date, a count, a ranking or a claim.
- **Never cite one, quote one or log one**, for anything. The comics report of 1 October 2026 took Action Comics #1's on-sale date, Spider-Man's first-appearance date and a grader's name from our articles; the Spider-Man date turned out to be the cover month.
- **Searches leave them out.** Every WebSearch passes `blocked_domains: ["news.justcollecting.com", "justcollecting.com", "collectingdaily.com"]`. A result or a link that is one of them is not opened. `fetch_pages.py` refuses their URLs.
- **A PFC blog post is never cited**, as before.

## Stock for section 9

**Section 9 (stock) and section 10 (why buy from us) are in the report only if PFC holds stock in the category or has real expertise in it.** The research says which in plan.md's header, and the research document marks them in or out. Never fill the gap with valuations, grading advice or another category.

`scripts/stock.py "$W" <handle> ...` does it in one call: it saves each listing to `$W/stock/<handle>.json`, drops sold pieces, writes `stock/stock.tsv` (title, price as listed, available, product URL, image path) and downloads each piece's first image, resized to 600px, into `stock/`. It prints one line. The research document prints the whole table, so the person writing can pick a spread of prices.

**Never conclude "no stock" from `/products.json`.** That global feed is incomplete: two coins the client named were in the coin collections and absent from it entirely. List `/collections.json`, pick the handles for the field, and query each one. **Coins are spread across six handles**: `coins-banknotes`, `coins-and-banknotes`, `ancient-coins`, `world-coins-collection`, `rare-british-coins` and `coin-archive`. The movie memorabilia handle is `movie-memorabilia`. A wrong "we hold nothing" deletes a section the client is expecting.

## Phases

`$W` below is `<root>/Market research/<Topic>/workings` (Where the files go). Create it before writing plan.md.

1. **Read the phase 1 files** in the table above in one call, with the agent check and the effort check (Hard limits 10). The field's three source files are read in full by the researchers: the main session greps their house headings for the plan and reads no more. Read the 5-hour limit (Hard limits 11). The Chrome connection and the Heritage login are checked by the first capturer, not by the main session (Hard limits 4): whenever the field uses Heritage, put a sold Heritage lot under `## Walled pages` (https://comics.ha.com/itm/golden-age-1938-1955-/superhero/batman-1-dc-1940-cgc-nm-94-white-pages/a/7239-91027.s); its capture shows `FOR: SIGN-IN` when the login has lapsed. Heritage keeps greeting a remembered user, "Welcome <name> (Sign-In | Not me)", long after the login itself has lapsed, and every sold price stays hidden until they sign in again. A disconnected Chrome or a lapsed login comes back as BLOCKED and `next_step.py` prints ASK: put it to the user in one line. When they say it is done, run `next_step.py "$W" --cleared` and carry on. Never type or fetch a password, and never copy cookies out of Chrome.
2. **Do not read our articles.** Not for leads either (the user's instruction, 13 October 2026). Work out what to look up from the field's source files and from the houses' own sites and results pages.
3. **Plan and launch the research.** Write `$W/plan.md`: per section, the figures it needs and which card gathers them; the four heat signals (`references/heat-rating.md`: recency, house direction, clearance, new demand), each assigned to a card by name, because they are a lookup, not something to extract from whatever you happened to gather, and a signal nobody looked for scores zero and is shown as not researched; the resale pairs to the standard of `sold-twice.md`; and the allowlist houses to work through. Every card needs fresh research from the houses' own pages: nothing is carried over from an earlier report or from our articles. Then run `next_step.py "$W" --usage <N>` and launch what it prints, in one message, in the background (Hard limits 9). Do not research in the main session while they run. Give each card its fact budget, and cover every section in this one launch, the budget bands and the series included. The plan has this shape:

```text
# Plan: <Topic> market research, research date YYYY-MM-DD
Field: <field>. Allowlist: sources-<field>.md, sources-major-houses.md, sources-press.md.
Scope: <the report's scope, one line>. Ranking: <section 5 and section 6 basis, and the pages that prove it>. Sections 9 and 10: <in, or out and why>.
Section 8: PFC40 Autograph Index extract found at <path or URL>, or left out.

## Rules every card follows
<allowlist, price basis, research date, 25 tool calls, 12 log items, walled pages to walled-<card>.tsv>

## Cards (8 to 12). Fresh researcher each, 25 tool calls, 12 log items, log to research-<card>.log.md
### records (sections 5, 6; heat signal 1)
<targets by name, the proof pages, the budget: 10 to 12 series for section 5, about 15 candidates for section 6>
### trends (section 2)
<20 to 25 priced results>
### sold-twice (section 8)
<3 pairs to sold-twice.md, up to 8 candidates>
### budget-bands (section 3)
<12 to 15 results across the bands>
<further cards, 8 to 12 in all, covering sections 1 to 8: section 3's 25 to 30 facts; 12 to 15 facts for demographics, indices and catalysts>

## Heat signals (heat-rating.md), one or two dated items each
1. Record recency: card <name>. A record set or broken within 24 months of the research date.
2. House direction: card <name>. A named house's latest annual or department total against the prior year.
3. Clearance: card <name>. A named recent sale documented as fully or near-fully sold.
4. New demand: card <name>. A documented new cohort, geography or channel.

## Walled pages
- <one URL per line, or a Google site search as GOOGLE site:domain words: pages walled-first.md says are walled for this field, captured alongside the cards>
```

   The first line names the document: `# Plan: <Topic> market research, research date YYYY-MM-DD` gives `<Topic> market research.md`, written beside `$W`. Each card heading's `(sections …)` is how the compiler knows where the card's items belong, so name every section a card serves.
4. **Walled pages** (`references/capture.md`), all through `next_step.py` (Hard limits 9): the plan's `## Walled pages` lines go to a capturer with the cards, and every line of every `walled-<card>.tsv` once all the cards are back, in parts of 24 run one after another. A fresh `market-research-capturer` agent reads them in the user's own Chrome, without asking, never in the in-app browser (Hard limits 4). When their Chrome shows a CAPTCHA, a verification check or a lapsed login, `next_step.py` prints ASK as soon as that capturer is back: put it to them at once in one line (page, and what to do); when they say it is done, run `next_step.py "$W" --cleared` and launch what it prints. The main session logs none of it: the readers `next_step.py` launches log the captures. Pages that could not be captured are in `$W/briefs/not-captured.tsv`, and the research document lists them.
5. **Merge and prove**, by the log agent `next_step.py` launches when research closes: `merge_logs.py --workings "$W" --force`, then `check_log.py "$W/sources-log.md"`, fixing each failure in the research log that holds the item, from its saved page, until it exits zero; what a page does not state is dropped into `$W/dropped.md`. Nothing is compiled until it exits zero (`briefs/log-ok`). Fix a failure in the log, never in the gate.
6. **Pull the stock** for section 9 at planning, in one call: `python3 ~/.claude/skills/claude-market-research/scripts/stock.py "$W" <handle> ...`, with the field's handles from `/collections.json` (Stock for section 9). If there is none and we have no expertise in the field, sections 9 and 10 are out: say so in plan.md's header.
7. **Checkpoint (internal, not a stop).** Per section: what is covered, from where, what is missing. This is where `next_step.py` prints CHECKPOINT. A gap goes to `next_step.py "$W" --gap <name> "<sections>" "<what is missing>"` (at most two in the run), never to research in the main session; with no gap, `next_step.py "$W" --close`. Read the 5-hour limit first and pass it with `--usage`. A page blocked by a CAPTCHA or login has already been put to the user (phase 4); a figure is dropped only if they said to, or the page does not state it.
8. **Compile**: a fresh `market-research-compiler` agent (Sonnet 5.5, high) writes `$W/analysis.md` and runs `compile_research.py "$W"`, which writes the research document (below). The main session neither writes nor reads the brief, the analysis or the document.
9. **Independent review.** A fresh `market-research-reviewer` agent reviews the document against `references/review-brief.md`, with the analysis, the log and the saved pages in front of it and no account of the research, and writes its findings to `$W/review-<date>.md`. Then `next_step.py` launches a fresh compiler in phase fix with that path. It fixes each finding or answers it with the reason it stands, and compiles again. **Mandatory.** Every gate the market report series had passed the Pokémon report, and an outside reader then found a dozen errors in one read.
10. **Deliver** the research document, `<root>/Market research/<Topic>/<Topic> market research.md`, and its `.docx` when pandoc made one. When `next_step.py` prints DELIVER: read the 5-hour limit and run `next_step.py "$W" --usage <N>` for the points the run used, run `run_cost.py`, and write the handover: the document's path; how many items, in which sections, and the sections with something missing; the conflicts left for the writer; the pages not captured or dropped; what the review changed (from the fix compiler's return); the points used.

## The research document

Everything the research found, laid out on Dan's eleven sections so a person can write the report from it, top to bottom, without opening the workings. `compile_research.py` writes it from two things: `sources-log.md`, every item of which it copies in full, exactly as proven, and `analysis.md`, which the compiler writes (its agent file gives the format). Nothing in it is retyped by hand.

- **Frontmatter**: `Title`, `Date researched` (plan.md's research date), `tags` (the first `market_research`, the second the topic, then the analysis's own), and `Sources`: every URL in the log, with its item's title, and each PFC collection listing the stock came from, every item double-quoted so Obsidian reads a list of strings (the script validates it with Ruby's YAML when Ruby is there).
- **The brief**: plan.md's header as written: field, allowlist, scope, ranking basis, sections 9 and 10, section 8's index.
- **Coverage**: one row per section: how many items, and what is missing.
- **Overview**, then **sections 1 to 11**: per section, what it needs (`article-structure.md`) and which items meet each need, the Missing line, then the evidence: every item the section lists, in full, the first time it appears, and a pointer back after that. Each item shows its price as the page states it, with its basis, lot size, house and date; what tells the copy apart; the sentence copied off the page; the researcher's note; and the link to check it, marked where the page shows its price only to someone signed in. Sections 5 and 6 carry the full ranking of every candidate on plan.md's basis. Section 3 carries the budget bands, section 4 the catalysts table, section 8 the indices and the sold-twice pairs, with every rejected pair and the condition it failed. Section 9 carries the live stock table.
- **Heat signals**: each signal, its items and its reading; researched N of 4, positive M; and the band `heat-rating.md`'s arithmetic gives, or withheld. The writer makes the call.
- **Conflicts**: every sale two items disagree on, both figures, both items, what kind of page each is. Decided nowhere.
- **Dropped, not captured and not cleared**, **Other evidence** (any item no section lists), **For the writer**.

**No images.** The writer finds and clears the images by hand.

**Nothing in it is converted, rounded or computed.** Every price is as its page states it, in its own currency, with its basis; percentages, multiples, per-annum rates and conversions are the writer's, at the day's ECB rate. That is the researchers' rule ("never compute a figure") carried to the document, and `compile_research.py` enforces it on the analysis: a price or percentage that is not in the Price or Quote of the item named on its line stops the build.

**It names no skill and no process.** The person writing may be Dan. The document says where each figure came from and that each was checked against its page, and nothing about how the run works.

## Things to check rather than assume

**A tool you have not looked for is not a tool that does not exist.** Before deciding a part of the research cannot be done, read the script table above and the reference file that covers it. If you do drop something the series has always carried, say so at the time rather than letting its absence be the result.

**Anniversary maths.** Dan's example is the 100th anniversary of *The Wizard of Oz*. The film is 1939, so that falls in **2039**. Nearer catalysts exist: *Star Wars* turns fifty in **2027**. Check every anniversary against the release year before it goes in section 4.

**Count an anniversary from the launch, never from the thing that celebrates it.** The Pokémon report dated the trading card game's 30th to 16 September 2026, the release date of the 30th Celebration set. The game launched in Japan in October 1996, so the 30th was still ahead. Log the launch date with its source beside every anniversary.

**The PFC40 Autograph Index.** Section 8 asks for an extract. The 2012 music memorabilia update cites it, so it exists internally. Look for the current data on disk and on paulfrasercollectibles.com (the site has a PFC40 Autograph Index page). If it is not there, say so in plan.md's header and on section 8's Missing line. Never reconstruct it from the fourteen-year-old document.

**Stock for the other two reports.** PFC holds no trading cards and no Pokémon, checked across all 2,211 products, and has no expertise in either. For those two fields sections 9 and 10 are out (the client's instruction, 5 October 2026). Do not research a substitute section on valuations, grading advice or buying across our other categories: the earlier Pokémon report did, and it was cut.
