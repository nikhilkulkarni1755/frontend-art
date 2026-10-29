#!/usr/bin/env python3
"""Generate README.md — coloring styles, per-piece palette matrix, detail ladder,
UI-with-text, then the natural desktop & mobile galleries."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
arts = json.loads((ROOT / "arts.json").read_text())
PALS = ["anime", "tapestry", "neon", "noir"]
PAL_LABEL = {"anime": "Anime bright", "tapestry": "Japanese tapestry", "neon": "Neon", "noir": "Noir"}
LADDER = [2, 4, 6, 10, 16, 24]
LADDER_SCENES = ["koi", "cheetah-run", "city-flyover"]   # representative detail ladders
by_slug = {a["slug"]: a for a in arts}

def esc(s): return s.replace("→", "&rarr;")
def m(slug, fn): return f"media/{slug}/{fn}"

head = f"""# frontend-art

**25 generative pixel-art animations — rendered 4 ways, from 2px to 24px pixel boxes.**

Each piece is one continuous, *resolution-independent* scene drawn on a `<canvas>` and sampled onto a **pixel-box grid**. The design never changes — a single pixel-box parameter re-samples the *same* motion coarser or finer (**2 / 4 / 6 / 10 / 16 / 24 px**), and a post-process **palette grade** repaints it in four coloring styles without touching the artwork. Every piece also has a full-bleed **mobile** layout, a **website hero**, and a **UI-with-text** treatment to check legibility.

| | |
| --- | --- |
| Scenes | **25** |
| Coloring styles | **4** — anime bright · Japanese tapestry · neon · noir (plus natural) |
| Pixel sizes | **6** — 2 / 4 / 6 / 10 / 16 / 24 px |
| Layouts | desktop · mobile · website hero · UI text |

Art &amp; code by **Nikhil Kulkarni**.

### Run it
Open any `art/<slug>.html` in a browser. Query params:

| param | values | effect |
| --- | --- | --- |
| `px` | `2` `4` `6` `10` `16` `24` | pixel-box size (default `10`) |
| `pal` | `anime` `tapestry` `neon` `noir` | coloring style (default natural) |
| `view` | `mobile` | full-bleed portrait layout |
| `site` | `1` | website hero-text overlay |
| `text` | `1` | sample UI text-boxes over the animation |

Example: `art/koi.html?px=4&pal=neon&text=1`

> Stills below are the `10px` build unless noted. Videos aren't committed (stored only if need be); regenerate with the capture script.

---

## Coloring styles

The same scene, same motion — only the palette grade changes. (Koi Pond, 10px.)

<table><tr>
<td width="20%" valign="top"><a href="art/koi.html"><img src="{m('koi','koi_10px_desktop.png')}" width="100%"></a><br><sub><b>natural</b></sub></td>
<td width="20%" valign="top"><a href="art/koi.html?pal=anime"><img src="{m('koi','koi_anime_10px_desktop.png')}" width="100%"></a><br><sub><b>anime bright</b></sub></td>
<td width="20%" valign="top"><a href="art/koi.html?pal=tapestry"><img src="{m('koi','koi_tapestry_10px_desktop.png')}" width="100%"></a><br><sub><b>japanese tapestry</b></sub></td>
<td width="20%" valign="top"><a href="art/koi.html?pal=neon"><img src="{m('koi','koi_neon_10px_desktop.png')}" width="100%"></a><br><sub><b>neon</b></sub></td>
<td width="20%" valign="top"><a href="art/koi.html?pal=noir"><img src="{m('koi','koi_noir_10px_desktop.png')}" width="100%"></a><br><sub><b>noir</b></sub></td>
</tr></table>

---

## Every piece × 4 palettes

All 25 scenes in each coloring style (10px desktop). Click any frame to open it live.
"""

def palette_matrix():
    rows = ["<table>",
            "<tr><th align=\"left\">piece</th>"
            + "".join(f"<th>{PAL_LABEL[p]}</th>" for p in PALS) + "</tr>"]
    for a in arts:
        s = a["slug"]
        cells = [f'<td valign="top"><b>{a["n"]:02d}</b><br>{a["name"]}<br><sub>{esc(a["persp"])}</sub></td>']
        for p in PALS:
            cells.append(f'<td width="22%" valign="top"><a href="art/{s}.html?pal={p}">'
                         f'<img src="{m(s, f"{s}_{p}_10px_desktop.png")}" width="100%"></a></td>')
        rows.append("<tr>" + "".join(cells) + "</tr>")
    rows.append("</table>")
    return "\n".join(rows)

def detail_ladder():
    out = ["## Detail — how small can a pixel box go",
           "",
           "One scene at every pixel size. At **2px** the grid is fine enough to read almost like a painting; "
           "at **24px** the boxes become the subject. (natural palette, desktop)", ""]
    for s in LADDER_SCENES:
        a = by_slug[s]
        out.append(f"**{a['n']:02d} · {a['name']}** — {esc(a['persp'])}")
        out.append("<table><tr>")
        for px in LADDER:
            out.append(f'<td width="16%" valign="top"><a href="art/{s}.html?px={px}">'
                       f'<img src="{m(s, f"{s}_{px}px_desktop.png")}" width="100%"></a><br>'
                       f'<sub align="center"><b>{px}px</b></sub></td>')
        out.append("</tr></table>")
        out.append("")
    return "\n".join(out)

def ui_text():
    picks = [
        ("koi", "koi_text_desktop.png", "art/koi.html?text=1", "Koi · desktop · natural"),
        ("koi", "koi_text_mobile.png", "art/koi.html?text=1&view=mobile", "Koi · mobile · natural"),
        ("city-flyover", "city-flyover_text_neon_desktop.png", "art/city-flyover.html?text=1&pal=neon", "City Flyover · neon"),
        ("jellyfish", "jellyfish_text_anime_desktop.png", "art/jellyfish.html?text=1&pal=anime", "Jellyfish · anime"),
    ]
    out = ["## UI with text",
           "",
           "Sample text-boxes — a heading card, an email capture, and status chips — over the live animation, "
           "to check how real copy and UI chrome read against each background and palette.", "",
           "<table><tr>"]
    for slug, fn, href, lbl in picks:
        w = "26%" if "mobile" in fn else "32%"
        out.append(f'<td width="{w}" valign="top"><a href="{href}"><img src="{m(slug, fn)}" width="100%"></a>'
                   f'<br><sub>{lbl}</sub></td>')
    out.append("</tr></table>")
    return "\n".join(out)

def cell_desktop(a):
    s = a["slug"]
    return (f'<td width="50%" valign="top"><a href="art/{s}.html">'
            f'<img src="{m(s, f"{s}_10px_desktop.png")}" width="100%"></a><br>'
            f'<b>{a["n"]:02d} &middot; {a["name"]}</b><br><sub>{esc(a["persp"])}</sub></td>')

def cell_mobile(a):
    s = a["slug"]
    return (f'<td width="25%" valign="top"><a href="art/{s}.html?view=mobile">'
            f'<img src="{m(s, f"{s}_10px_mobile.png")}" width="100%"></a><br>'
            f'<b>{a["n"]:02d} &middot; {a["name"]}</b></td>')

def grid(cells, per):
    out = ["<table>"]
    for i in range(0, len(cells), per):
        out.append("<tr>" + "".join(cells[i:i+per]) + "</tr>")
    out.append("</table>")
    return "\n".join(out)

body = [
    head,
    palette_matrix(),
    "\n---\n\n" + detail_ladder(),
    "\n---\n\n" + ui_text(),
    "\n---\n\n## Gallery · desktop\n\nNatural palette, 10px.\n",
    grid([cell_desktop(a) for a in arts], 2),
    "\n## Gallery · mobile\n\nNatural palette, 10px, full-bleed portrait.\n",
    grid([cell_mobile(a) for a in arts], 4),
    "\n---\n\n<sub>Rendered headless in Chromium (Playwright). Desktop 1280&times;800 @2&times;, mobile 390&times;844 @3&times;. "
    "Palette = post-process grade of the sampled colour, so the design is identical across styles.</sub>\n",
]
(ROOT / "README.md").write_text("\n".join(body))
print("README.md written")
