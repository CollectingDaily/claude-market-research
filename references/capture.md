# Reading walled pages without paying for them twice

Load this when `walled.tsv` or a researcher's `walled-<part>.tsv` has lines in it. It is rung 2 of `blocked-sources.md`, the user's own Google Chrome, done so the page text goes from the browser to disk and only a one-line receipt comes back. The in-app browser is not used for walled pages (the user's instruction, 7 October 2026): it has none of their logins.

**Never** read a page with `get_page_text` or `javascript_tool` and then type its text into a file. In the comics run that was twenty Heritage pages paid for once as input and again as output, and carried by every later request. It is also how a capture stops being the page: a retyped page is a transcription.

## Why it works this way

A page cannot POST to a server on 127.0.0.1: Chrome's Local Network Access blocks it, which is why the first attempt failed. The in-app browser has no second window to `postMessage` to either. A top-level navigation is not blocked. So the page's own script puts its text in the URL fragment and sends the tab to `capture_server.py`. The fragment never leaves the machine (browsers do not send it to any server), and the receiver, being local, saves it with a same-origin request. Tested 2 October 2026 on comics.ha.com in the in-app browser and in the user's own Chrome.

## Start the receiver once per report

```bash
python3 ~/.claude/skills/claude-market-research/scripts/capture_server.py --workings "$W"   # run_in_background
cat "$W/.capture-token"
```

It writes each page in `attest.py`'s exact format into `$W/attested/`, so `check_attested.py` and `check_log.py` check it unchanged. It refuses a payload without the token, under 200 characters, or that is an interstitial ("Just a moment", "Verifying you are human"). Stop it when the browser work is done.

## The two snippets

Replace `TOKEN`, `REQUESTED` (snippet A: the URL as the capture list gives it, or the GOOGLE line itself, copied exactly; a redirect then still matches the page to its line), the method (`user-chrome`) and the wall (a few words: `ha.com 403 to a fetch`, `price behind sign-in`, `cloudflare`).

**A. This page, as rendered.** For pages built by JavaScript, and for signed-in prices in their Chrome:

```js
const K={t:'TOKEN',m:'user-chrome',w:'WALL',r:'REQUESTED'};
const items=[{url:location.href,requested:K.r,text:document.title+'\n'+document.body.innerText,method:K.m,wall:K.w}];
setTimeout(()=>location.href='http://127.0.0.1:8766/#pfc='+encodeURIComponent(JSON.stringify({token:K.t,items})),50);
'sending '+items[0].text.length
```

**B. A list of pages on the same site, fetched from one open page.** For server-rendered pages such as Heritage press releases and lot pages: one tab, one call, any number of pages.

```js
const K={t:'TOKEN',m:'user-chrome',w:'WALL'}, U=['/c/press-release.zx?releaseId=5455','/c/press-release.zx?releaseId=5404'];
const items=[];
for (const u of U){const a=new URL(u,location.href).href; const r=await fetch(a,{credentials:'include'}); const d=new DOMParser().parseFromString(await r.text(),'text/html'); d.querySelectorAll('script,style,noscript,svg').forEach(e=>e.remove()); d.querySelectorAll('p,div,li,h1,h2,h3,h4,tr,br').forEach(e=>e.append('\n')); items.push({url:a,final:r.url,status:r.status,text:d.title+'\n'+d.body.textContent,method:K.m,wall:K.w});}
setTimeout(()=>location.href='http://127.0.0.1:8766/#pfc='+encodeURIComponent(JSON.stringify({token:K.t,items})),50);
'sending '+items.length+' pages, '+items.reduce((n,i)=>n+i.text.length,0)+' chars'
```

Keep a batch under about 40 pages; the fragment carries all of them.

## One browser call per batch

Chain the whole batch in one `browser_batch` and read the receipts at the end:

```
navigate <page>            wait 2     javascript_tool <snippet A or B>     wait 2
navigate <next page>       wait 2     javascript_tool <snippet A>          wait 2
...
navigate http://127.0.0.1:8766/log?last=<n>     get_page_text
```

Each `wait` is the `computer` tool's `wait` action (`{"name": "computer", "input": {"action": "wait", "duration": 3, "tabId": …}}`): a javascript sleep after the snippet is cut off when the snippet sends the tab to the receiver, and navigating to the receiver yourself cuts off the save. Run it in their Chrome with `mcp__claude-in-chrome__browser_batch`, `tabId` on every step (`tabs_context_mcp` first, then a tab of your own). A navigate to a URL that redirects can cut a script off; the wait before the snippet prevents it. Close the tab when the batch is done, except a tab left on a blocked page: the user signs in there.

## Reading the receipts

```
saved attested/comics-ha-com-c-press-release-zx-releaseid-5455-689ff580.txt  10,267 chars  | Superman and Batman Debut Issues ...  | redirected to https://...
```

- **saved**: read it with `find_figures.py "$W/attested" --terms "..."`, then write the log block with `- Access: assisted (<method>, <wall>)` and `- Attested: <the path as printed>`. The URL in the block is the one in the capture's header.
- **REFUSED an error page**: a Cloudflare or server error (520, 503, too many requests) came back instead of the page. Nothing is saved and nothing is asked: `next_step.py` tries the page again. Before 29 October 2026 the receiver saved such a page over the real capture.
- **PRICE HIDDEN**: a real page with the sold price behind a sign-in. The receiver writes the page to `briefs/blocked.tsv` itself and marks the capture `Hidden:`, so it is asked about and never read as the page. Their login to that house has lapsed, even when the site greets them by name: Heritage shows "Welcome <name> (Sign-In | Not me)" for a remembered user whose login has ended. Phase 1 checks this before research starts; if it lapses mid-run, pause and ask them to sign in again, in one line, at that moment (`SKILL.md`, "Run it end to end. Ask only when a page is blocked."), then re-run the capture when they say it is done and carry on with the report. Drop the figure only if they tell you to. Seen on 2 and 7 October 2026.
- **REFUSED not the page**: an interstitial (a CAPTCHA, a verification slider, "verify you are human"). Pause and ask the user at once, in one line, to clear it in their Chrome (the page, and what to do), then re-run the capture when they say it is done and carry on with the report. Never attest an interstitial, and never drop the figure without asking.

What you never do does not change (`blocked-sources.md`): never solve a check, never type a credential, never wander their signed-in session. The snippets only read.
