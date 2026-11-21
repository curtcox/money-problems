"""Write the QR codes for the production scenes.

Usage: python3 tools/make_qr_svgs.py [output-dir]

Requires the `segno` package (pip install segno); it is the only tool in the repository that
needs a package outside the standard library. Reads qr-links.json, so run tools/qr-links.mjs
first. Codes use error correction level M and a 4-module quiet zone, black on white, which
phone cameras read most reliably from video.

Writes:
  build/qr/<id>.svg and .png        for thumbnails, descriptions and print (gitignored)
  production/qr-matrices.json       committed; rows of "0"/"1" per code without the quiet
                                    zone, which production/common.py draws as vector squares
                                    (Manim's SVG import drops segno's stroked module paths)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

try:
    import segno
except ImportError:
    sys.exit('This script needs segno: pip install segno')


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build' / 'qr'
    out.mkdir(parents=True, exist_ok=True)
    rows = json.loads((ROOT / 'qr-links.json').read_text())
    matrices = {}
    versions = set()
    for row in rows:
        code = segno.make(row['url'], error='m', boost_error=False)
        versions.add(code.version)
        code.save(str(out / f"{row['id']}.svg"), scale=10, border=4, dark='#000000', light='#ffffff')
        code.save(str(out / f"{row['id']}.png"), scale=10, border=4, dark='#000000', light='#ffffff')
        matrices[row['id']] = {'url': row['url'], 'title': row['title'],
                               'rows': [''.join('1' if cell else '0' for cell in line) for line in code.matrix]}
    (ROOT / 'production' / 'qr-matrices.json').write_text(json.dumps(matrices, indent=1) + '\n')
    print(f'Wrote {len(rows)} QR codes (SVG and PNG) to {out} and production/qr-matrices.json; '
          f'versions {sorted(versions)}.')


if __name__ == '__main__':
    main()
