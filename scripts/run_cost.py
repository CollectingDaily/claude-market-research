#!/usr/bin/env python3
"""What a research run cost, and where: read straight from the session transcripts.

    python3 run_cost.py                 # the most recent market-research session
    python3 run_cost.py <session-id>

For the main session and each of its agents: model, requests, starting and
mean context, and a weighted token total (cache reads at 0.1, cache writes at
1.25, output at 5, all relative to plain input on the same model), with the
share taken by each tool. The context columns are the ones to watch: every
request re-sends the whole context, so a run's cost is roughly its mean context
times its number of requests.

The comics report of 1 October 2026, before this skill's cost rules: main
session 143 requests at a mean context near 350,000 tokens; three Opus research
agents 411 requests at a mean of 217,000; 17.4M weighted in all, 61% of it the
agents, and the run stopped in its build rounds.
"""
import collections, glob, json, os, pathlib, sys

PROJECTS = pathlib.Path('~/.claude/projects').expanduser()
W = dict(inp=1, cr=0.1, cw=1.25, out=5)


def load(path):
    reqs, order, tools = {}, [], {}
    for line in open(path, encoding='utf-8', errors='replace'):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        m = d.get('message') or {}
        if d.get('type') != 'assistant':
            continue
        rid = d.get('requestId') or m.get('id')
        if rid not in reqs:
            reqs[rid] = {'u': {}, 'tool': None, 'model': m.get('model')}
            order.append(rid)
        reqs[rid]['u'] = m.get('usage') or reqs[rid]['u']
        for c in m.get('content') or []:
            if c.get('type') == 'tool_use' and not reqs[rid]['tool']:
                reqs[rid]['tool'] = c['name']
    return [reqs[r] for r in order]


def ctx(u):
    return (u.get('input_tokens', 0) + u.get('cache_read_input_tokens', 0)
            + u.get('cache_creation_input_tokens', 0))


def cost(u):
    return (u.get('input_tokens', 0) * W['inp'] + u.get('cache_read_input_tokens', 0) * W['cr']
            + u.get('cache_creation_input_tokens', 0) * W['cw'] + u.get('output_tokens', 0) * W['out'])


def report(label, reqs):
    reqs = [r for r in reqs if r['model'] and not r['model'].startswith('<')]
    if not reqs:
        return 0
    total = sum(cost(r['u']) for r in reqs)
    cs = [ctx(r['u']) for r in reqs]
    models = collections.Counter(r['model'] for r in reqs)
    print(f"{label}\n  {', '.join(models)}: {len(reqs)} requests, context {cs[0] // 1000}k at start, "
          f"{sum(cs) // len(cs) // 1000}k mean, {max(cs) // 1000}k peak; {total / 1e6:.2f}M weighted")
    by = collections.Counter()
    for r in reqs:
        by[(r['tool'] or '(text)').replace('mcp__Claude_Browser__', 'browser:')
           .replace('mcp__claude-in-chrome__', 'chrome:')] += cost(r['u'])
    print('  ' + ', '.join(f"{k} {100 * v / total:.0f}%" for k, v in by.most_common(5)))
    return total


def main():
    if len(sys.argv) > 1:
        sid = sys.argv[1]
        hits = list(PROJECTS.glob(f'*/{sid}.jsonl'))
    else:
        hits = sorted((p for p in PROJECTS.glob('*/*.jsonl')
                       if 'market-research' in p.read_text(encoding='utf-8', errors='replace')[:200000]),
                      key=os.path.getmtime)[-1:]
    if not hits:
        sys.exit('no such session transcript')
    main_path = hits[-1]
    grand = report(f"main session {main_path.stem}", load(main_path))
    for sub in sorted(glob.glob(str(main_path.with_suffix('')) + '/subagents/*.jsonl')):
        meta = pathlib.Path(sub[:-6] + '.meta.json')
        desc = json.loads(meta.read_text()).get('description', '') if meta.exists() else ''
        grand += report(f"agent: {desc}", load(sub))
    print(f"\nall: {grand / 1e6:.2f}M weighted")


if __name__ == '__main__':
    main()
