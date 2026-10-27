#!/usr/bin/env python3
"""Generate README.md — a gallery of all desktop stills, then all mobile stills."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
arts = json.loads((ROOT / "arts.json").read_text())

def esc(s): return s.replace("→", "&rarr;")

head = """# frontend-art

**25 generative pixel-art animations — 100 frontends.**

Each piece is one continuous, *resolution-independent* scene drawn on a `<canvas>` and sampled onto a **pixel-box grid**. A single pixel-box parameter (`6 / 10 / 16 / 24 px`) re-samples the *same* motion coarser or finer, so each animation ships at four pixel sizes — 25 &times; 4 = **100 frontends**. Every piece has a landscape **desktop** layout, a full-bleed portrait **mobile** layout, and a **website** hero treatment.

Art &amp; code by **Nikhil Kulkarni**.

### Run it
Open any `art/<slug>.html` in a browser. Query params:

| param | values | effect |
| --- | --- | --- |
| `px` | `6` `10` `16` `24` | pixel-box size (default `10`) |
| `view` | `mobile` | full-bleed portrait layout |
| `site` | `1` | website hero-text overlay |

Example: `art/koi.html?px=16&view=mobile&site=1`

> Stills below are the `10px` build. Videos aren't committed (stored only if need be); regenerate with the capture script.

---

## Gallery · desktop
"""

def cell_desktop(a):
    s = a["slug"]
    return (f'<td width="50%" valign="top"><a href="art/{s}.html">'
            f'<img src="media/{s}/{s}_10px_desktop.png" width="100%"></a><br>'
            f'<b>{a["n"]:02d} &middot; {a["name"]}</b><br><sub>{esc(a["persp"])}</sub></td>')

def cell_mobile(a):
    s = a["slug"]
    return (f'<td width="25%" valign="top"><a href="art/{s}.html?view=mobile">'
            f'<img src="media/{s}/{s}_10px_mobile.png" width="100%"></a><br>'
            f'<b>{a["n"]:02d} &middot; {a["name"]}</b></td>')

def grid(cells, per):
    out = ["<table>"]
    for i in range(0, len(cells), per):
        out.append("<tr>" + "".join(cells[i:i+per]) + "</tr>")
    out.append("</table>")
    return "\n".join(out)

body = [head, grid([cell_desktop(a) for a in arts], 2),
        "\n## Gallery · mobile\n", grid([cell_mobile(a) for a in arts], 4),
        "\n---\n\n<sub>Rendered headless in Chromium (Playwright). Desktop 1280&times;800 @2&times;, mobile 390&times;844 @3&times;.</sub>\n"]
(ROOT / "README.md").write_text("\n".join(body))
print("README.md written")
