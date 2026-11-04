# Market research

**Claude researches a collecting market for you, and hands you everything it found, neatly sorted, so you can write the market report yourself.**

<p align="center"><img src="docs/how-it-works.svg" alt="How a market report is made: 1 Claude researches, 2 you write, 3 Claude lays it out, 4 two PDFs" width="100%"></p>

This skill is step 1. It does the research and stops. It never writes the report, never chooses images and never makes a PDF: you do the writing, and the [market-report-layout](https://github.com/CollectingDaily/claude-market-report-layout) skill turns your finished report into the two designed PDFs.

---

## What you get

One document, laid out on the eleven sections of a market report, with everything the research found under the section it belongs to. You get it twice: as a **Word file** (opens in Word, LibreOffice or Google Docs) and as a **Markdown file** (opens in Obsidian).

<p align="center">
  <img src="docs/research-page-1.png" alt="Page 1 of a research document: the brief, the coverage table and the overview" width="45%">
  &nbsp;
  <img src="docs/research-page-3.png" alt="A later page: a table of prices by budget, then each piece of evidence with its price, house, date, quote and link" width="45%">
</p>
<p align="center"><em>A real example: two pages of an autographs research document.</em></p>

**Page 1** tells you what was researched and gives a **coverage table**: for each section of the report, how many pieces of evidence were found and what is still missing.

**Each section** then explains what it needs and which evidence covers it, followed by the evidence itself. Every piece of evidence shows:

- **the price**, exactly as the auction house printed it, and whether it includes the buyer's premium;
- **the auction house and the date**;
- **the sentence copied from the page**, so you can see the proof;
- **a link to check it yourself.** A few auction houses only show prices to people who are signed in: those links say so.

At the end you'll find the **heat signals** (is the market busy or quiet?), any **conflicts** where two sources disagree (both are shown: you decide), PFC's **live stock** for the field, and a list of anything that couldn't be found.

> **Nothing is made up, converted or rounded.** If a figure isn't on the page it links to, it isn't in the document. Prices stay in the currency they were sold in: converting them is part of writing the report.

---

## What happens when you run it

<p align="center"><img src="docs/what-happens.svg" alt="Six steps: you ask, a plan, research, locked pages read in your Chrome, every figure checked, your document" width="100%"></p>

You only take part twice: when you ask, and if a website wants you to sign in. Everything else runs on its own. A full run takes a while and uses a good part of your Claude allowance, so start it when you don't need Claude for much else.

---

## What you need

| | |
| --- | --- |
| 💻 **A Mac** | The skill uses tools that come with macOS. |
| 🤖 **The Claude app**, with its **Code** tab | A paid Claude plan (Pro, Max, Team or Enterprise). Download it from [claude.com](https://code.claude.com/docs/en/desktop-quickstart). |
| 🌐 **Google Chrome** with the **Claude in Chrome** extension | Some auction houses only show prices to people who are signed in. Claude reads those pages in *your* Chrome, where you're already signed in. It never sees or types a password. |
| 📝 **pandoc** *(optional)* | Makes the Word copy of the document. Without it you get the Markdown file only. |

---

## Installing it

1. **Open the Claude app**, click the **Code** tab, choose **Local** and any folder (such as Documents).
2. **Paste this** into the message box and press **Return**:

   ```text
   Install the skill from https://github.com/CollectingDaily/claude-market-research into ~/.claude/skills/claude-market-research
   ```

3. **Click Allow** when Claude asks to download it.
4. **Quit the Claude app completely** (⌘ Q) and open it again. Type **/** in the message box and look for **market-research** in the list. If it's there, you're ready.

New to Claude, or setting up a Mac for the first time? The [Collecting Daily page](https://github.com/CollectingDaily) explains everything step by step, including how to update your skills.

The first time you use it, Claude sets up its research helpers and may ask you to start a new session. Do that, then ask again.

---

## Using it

1. **Open a folder** for your research in the Claude app (Code tab → Local → Select folder).
2. **Make sure Chrome is open**, with the Claude extension switched on.
3. **Ask:** */market-research Research the autographs market*
4. **Keep an eye out for questions.** If a site shows a sign-in page or a "verify you're human" check in your Chrome, Claude stops and asks you to deal with it. Do it in Chrome, tell Claude it's done, and it carries on.
5. **Open your document.** It's in a new folder called **Market research**, inside the folder you chose:

```
Market research/
    Autographs/
        Autographs market research.docx    ← open this in Word or Google Docs
        Autographs market research.md      ← or this one in Obsidian
        workings/                          ← Claude's notes and saved pages (you can ignore these)
```

Then write your report, with your own images and captions, and hand it to **market-report-layout** for the PDFs.

---

## Questions

**Can I trust the figures?**
Every price and quote was checked against the page it came from before the document was made, and a second, independent check reads the whole document again before you get it. Even so, the links are there so you can look for yourself, and you should for anything you lead with.

**Why does it say "not stated"?**
The page didn't say. The document never guesses: "house not stated" means the page gave no auction house.

**Two sources disagree. Which is right?**
The document shows both, with what kind of page each is (the auction house's own record, a magazine, the press). The auction house's own sale record is usually the one to trust, but it's your call.

**Some prices are in dollars, some in pounds.**
Each price is shown as it was sold. Convert them when you write, at the day's exchange rate.

---

<details>
<summary><strong>For the technically minded</strong></summary>

`SKILL.md` is the full procedure. The run is driven by `scripts/next_step.py`, which decides every step from the files on disk: research agents (one per task card, 8 to 12), captures of walled pages in the user's Chrome (`capture_server.py`), readers for the captures, the checkpoint, the log check (`merge_logs.py`, `check_log.py`, which runs `verify_sources.py` and `check_attested.py`), the compiler, which writes `analysis.md`, `compile_research.py`, which builds the document and refuses any price or percentage not in the evidence item it names, the reviewer and a fix pass. The agents are in `agents/` and are copied to `~/.claude/agents/` on the first run. The source lists for every field are in `references/sources/`. Needs Python 3 and curl; pandoc for the `.docx`, styled by `assets/research-reference.docx`.

</details>
