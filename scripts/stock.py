#!/usr/bin/env python3
"""Pull PFC's live stock for section 9 in one call: listings, stock.tsv and images.

    python3 stock.py "$W" <collection handle> [<collection handle> ...]

For each handle it pages through the store's own listing endpoint,
/collections/<handle>/products.json?limit=250, saves the listing to
$W/stock/<handle>.json, takes the union of the products by product handle,
drops every piece whose first variant is not available (sold), downloads each
remaining piece's first image resized to 600px into $W/stock/, and writes
$W/stock/stock.tsv: title, price as listed, available, product URL, image path.
It prints one summary line, so nothing else enters the session.

Pick the handles from /collections.json for the field (SKILL.md, "Stock for
section 9"): coins alone are spread across six. Never conclude "no stock" from
the global /products.json, which is incomplete.
"""
import json, pathlib, shutil, subprocess, sys

SHOP = 'https://www.paulfrasercollectibles.com'


def get(url):
    r = subprocess.run(['curl', '-s', '--max-time', '60', url], capture_output=True)
    return r.stdout


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    W = pathlib.Path(sys.argv[1]).expanduser()
    out = W / 'stock'
    out.mkdir(parents=True, exist_ok=True)
    products, empty = {}, []
    for h in sys.argv[2:]:
        listing, page = [], 1
        while True:
            try:
                batch = json.loads(get(f'{SHOP}/collections/{h}/products.json?limit=250&page={page}') or b'{}').get('products', [])
            except ValueError:
                sys.exit(f'stock: {h} page {page} did not return JSON; nothing written for it')
            listing += batch
            if len(batch) < 250:
                break
            page += 1
        (out / f'{h}.json').write_text(json.dumps({'products': listing}, indent=1), encoding='utf-8')
        if not listing:
            empty.append(h)
        for p in listing:
            products.setdefault(p['handle'], p)
    rows, sold = [], 0
    for handle, p in products.items():
        v = (p.get('variants') or [{}])[0]
        if not v.get('available'):
            sold += 1
            continue
        img = ''
        src = ((p.get('images') or [{}])[0]).get('src', '')
        if src:
            ext = src.split('?')[0].rsplit('.', 1)[-1].lower()
            path = out / f'{handle}.{ext if ext in ("jpg", "jpeg", "png", "webp") else "jpg"}'
            if not path.exists():
                path.write_bytes(get(src))
                if shutil.which('sips'):          # macOS only: elsewhere the image is kept at its own size
                    subprocess.run(['sips', '-Z', '600', str(path)], capture_output=True)
            img = str(path) if path.exists() and path.stat().st_size > 1000 else ''
        rows.append([p.get('title', '').replace('\t', ' '), v.get('price', ''), 'true', f'{SHOP}/products/{handle}', img])
    rows.sort(key=lambda r: float(r[1] or 0))
    (out / 'stock.tsv').write_text('title\tprice\tavailable\turl\timage\n' + ''.join('\t'.join(r) + '\n' for r in rows),
                                   encoding='utf-8')
    prices = [float(r[1]) for r in rows if r[1]]
    print(f'stock: {len(rows)} available pieces from {len(sys.argv) - 2 - len(empty)} collection(s), {sold} sold dropped'
          + (f', prices {min(prices):,.0f} to {max(prices):,.0f} as listed' if prices else '')
          + (f'; empty: {", ".join(empty)}' if empty else '') + f'; {out}/stock.tsv'
          + f'; {sum(1 for r in rows if not r[4])} without an image')


if __name__ == '__main__':
    main()
