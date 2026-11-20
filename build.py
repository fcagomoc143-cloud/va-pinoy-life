"""VA Pinoy Life static blog builder (80/20 visual format).

python build.py          -> build ./docs
python build.py --check  -> per-post 80/20 report (prose words, visual blocks)

Visual blocks inside posts (each line inside a block = one item, fields split by " | "):
  :::cards    emoji | title | short line            -> icon card grid
  :::steps    emoji | step title                    -> step flow with arrows
  :::stats    big value | label                     -> big number tiles
  :::vs       left title | right title  (1st line), then left | right per row
  :::check    item                                  -> checklist tiles
  :::tip      emoji one-liner                       -> highlight callout
  :::bars     label | 0-100 | value text            -> bar chart
Plain markdown tables are also allowed.
"""
import html
import json
import re
import shutil
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
POSTS = ROOT / "posts"
STATIC = ROOT / "static"
OUT = ROOT / "docs"
SITE = "VA Pinoy Life"
BASE_URL = "https://vapinoylife.netlify.app"
MAX_PROSE = 220
MIN_BLOCKS = 5

CATS = {
    "Pang-beginner": {"slug": "beginner", "short": "Simula", "icon": "🌱", "bg": "#262359", "fg": "#FFFFFF", "blob": "#363275", "dot": "#F7941D"},
    "Tools at skills": {"slug": "tools", "short": "Tools", "icon": "🧰", "bg": "#F1F0F7", "fg": "#262359", "blob": "#E2E0EE", "dot": "#F7941D"},
    "Pera at career": {"slug": "pera", "short": "Pera", "icon": "💸", "bg": "#F7941D", "fg": "#262359", "blob": "#FB8C00", "dot": "#262359"},
}
E = html.escape
IMG_SRC = STATIC / "img"


def optimize_images():
    """PNG from gen_images.py -> 1400px JPG for the web (PNG originals stay out of docs)."""
    try:
        from PIL import Image
    except ImportError:
        return
    for png in IMG_SRC.glob("*.png"):
        jpg = png.with_suffix(".jpg")
        if not jpg.exists() or jpg.stat().st_mtime < png.stat().st_mtime:
            im = Image.open(png).convert("RGB")
            im.thumbnail((1400, 1400))
            im.save(jpg, "JPEG", quality=82, optimize=True, progressive=True)


def pic(key, depth=0, alt="", eager=False):
    if (IMG_SRC / f"{key}.jpg").exists():
        load = 'fetchpriority="high"' if eager else 'loading="lazy"'
        return f'<img src="{'../' * depth}img/{key}.jpg" alt="{E(alt)}" {load} decoding="async">'
    return ""


def art(cat, icon, seed=0, label=""):
    """Big-emoji poster tile, shapes shift by seed so every post looks different."""
    c = CATS[cat]
    s = seed % 6
    cx, cy, r = 70 + s * 36, 40 + (s % 3) * 50, 70 + s * 6
    return f'''<svg viewBox="0 0 320 200" preserveAspectRatio="xMidYMid slice" role="img" aria-label="{E(label)}">
<rect width="320" height="200" fill="{c['bg']}"/><circle cx="{cx}" cy="{cy}" r="{r}" fill="{c['blob']}"/>
<circle cx="{292 - s*6}" cy="{174 - s}" r="{14 + s*2}" fill="{c['dot']}"/><rect x="{18 + s*8}" y="168" width="{60 + s*10}" height="10" rx="5" fill="{c['dot']}" opacity=".9"/>
<text x="160" y="128" font-size="92" text-anchor="middle">{icon}</text></svg>'''


def fields(line, n):
    parts = [p.strip() for p in line.split("|")]
    return (parts + [""] * n)[:n]


def inline(t):
    return markdown.markdown(t).removeprefix("<p>").removesuffix("</p>")


def render_block(kind, lines):
    lines = [l.strip().lstrip("-* ").strip() for l in lines if l.strip()]
    if kind == "cards":
        items = "".join(f'<li><span class="ic">{E(a)}</span><b>{inline(b)}</b><span>{inline(c)}</span></li>' for a, b, c in (fields(l, 3) for l in lines))
        return f'<ul class="v-cards">{items}</ul>'
    if kind == "steps":
        items = "".join(f'<li><span class="n">{i}</span><span class="ic">{E(a)}</span><b>{inline(b)}</b></li>' for i, (a, b) in enumerate((fields(l, 2) for l in lines), 1))
        return f'<ol class="v-steps">{items}</ol>'
    if kind == "stats":
        items = "".join(f'<li><b>{E(a)}</b><span>{inline(b)}</span></li>' for a, b in (fields(l, 2) for l in lines))
        return f'<ul class="v-stats">{items}</ul>'
    if kind == "vs":
        head, rows = fields(lines[0], 2), [fields(l, 2) for l in lines[1:]]
        col = lambda i: "".join(f"<li>{inline(r[i])}</li>" for r in rows if r[i])
        return f'<div class="v-vs"><div><h4>{inline(head[0])}</h4><ul>{col(0)}</ul></div><span class="vs">vs</span><div><h4>{inline(head[1])}</h4><ul>{col(1)}</ul></div></div>'
    if kind == "check":
        items = "".join(f"<li>{inline(l)}</li>" for l in lines)
        return f'<ul class="v-check">{items}</ul>'
    if kind == "tip":
        return f'<p class="v-tip">{inline(" ".join(lines))}</p>'
    if kind == "bars":
        items = ""
        for a, b, c in (fields(l, 3) for l in lines):
            pct = max(4, min(100, int(re.sub(r"\D", "", b) or 50)))
            items += f'<li><span>{inline(a)}</span><i style="--w:{pct}%"></i><b>{inline(c)}</b></li>'
        return f'<ul class="v-bars">{items}</ul>'
    return "\n".join(lines)


BLOCK_RE = re.compile(r"^:::(\w+)[ \t]*\n(.*?)^:::[ \t]*$", re.M | re.S)


def parse(path):
    raw = path.read_text(encoding="utf-8").lstrip("\ufeff")
    m = re.match(r"---\s*\n(.*?)\n---\s*\n(.*)", raw, re.S)
    if not m:
        raise ValueError(f"no front matter: {path}")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    meta["slug"] = meta.get("slug") or path.stem
    meta["order"] = int(re.sub(r"\D", "", meta.get("order", "99")) or 99)
    if meta.get("category") not in CATS:
        meta["category"] = "Pang-beginner"
    meta["icon"] = meta.get("icon") or CATS[meta["category"]]["icon"]
    body = m.group(2)
    if body.lstrip().startswith("# "):
        body = re.sub(r"^\s*#\s+.*\n", "", body, count=1)
    body = re.sub(r"^(\s*)[-*] \[[ xX]\] ", r"\1- ", body, flags=re.M)

    blocks = []

    def sub(mm):
        blocks.append(render_block(mm.group(1).lower(), mm.group(2).splitlines()))
        return f"\n\nBLOCKTOKEN{len(blocks) - 1}\n\n"

    rest = BLOCK_RE.sub(sub, body)
    tables = len(re.findall(r"^\|[ :-]+\|", rest, re.M))
    prose = "\n".join(l for l in rest.splitlines() if not l.lstrip().startswith("|") and "BLOCKTOKEN" not in l)
    meta["prose_words"] = len(re.findall(r"\w+", prose))
    meta["blocks"] = len(blocks) + tables
    out = markdown.markdown(rest, extensions=["tables", "sane_lists"])
    for i, b in enumerate(blocks):
        out = out.replace(f"<p>BLOCKTOKEN{i}</p>", b)
    meta["html"] = out
    meta["mins"] = max(1, round((meta["prose_words"] + 15 * meta["blocks"]) / 200))
    return meta


def page(title, desc, body, depth=0, canonical=""):
    p = "../" * depth
    nav = "".join(f'<a href="{p}index.html#{c["slug"]}">{c["icon"]} {c["short"]}</a>' for c in CATS.values())
    return f'''<!doctype html>
<html lang="fil">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<link rel="canonical" href="{BASE_URL}/{canonical}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{p}style.css">
<link rel="icon" href="{p}favicon.svg">
</head>
<body>
<header class="top"><a class="brand" href="{p}index.html">VA <span>Pinoy</span> Life</a>
<nav>{nav}<a href="{p}resume-template.html">📄 Free resume</a><a href="{p}about.html">👋 About</a></nav></header>
{body}
<footer class="foot"><a class="brand" href="{p}index.html">VA <span>Pinoy</span> Life</a>
<p class="small">Gawa ng Pinoy EA · Ang ilang links ay affiliate · Hindi financial o tax advice</p></footer>
<script>const h=document.querySelector('.top');addEventListener('scroll',()=>h.classList.toggle('scrolled',scrollY>8),{{passive:true}});</script>
</body></html>'''


def tile(p, depth=0, big=False):
    """Text card: anime art lives only in the hero at the top of each page."""
    c = CATS[p["category"]]
    return f'''<a class="card-link" href="{'../'*depth}posts/{p['slug']}.html" style="--cat:{c['dot'] if c['bg'] == '#F1F0F7' else c['bg']}">
<span class="num">{p['order']:02d}</span><h3>{E(p['title'])}</h3><span class="meta">{p['category']} · {p['mins']} min</span></a>'''


def build():
    optimize_images()
    OUT.mkdir(exist_ok=True)
    for f in OUT.iterdir():
        shutil.rmtree(f) if f.is_dir() else f.unlink()
    (OUT / "posts").mkdir(parents=True)
    for f in STATIC.iterdir():
        if f.is_dir():
            shutil.copytree(f, OUT / f.name, ignore=shutil.ignore_patterns("*.png", "test-*"))
        else:
            shutil.copy(f, OUT / f.name)
    posts = sorted((parse(f) for f in POSTS.glob("*.md")), key=lambda x: x["order"])

    for i, p in enumerate(posts):
        c = CATS[p["category"]]
        prev_p = posts[i - 1] if i > 0 else None
        next_p = posts[i + 1] if i + 1 < len(posts) else None
        pn = '<nav class="pn">'
        pn += f'<a href="{prev_p["slug"]}.html"><span class="ic">⬅️</span>{E(prev_p["title"])}</a>' if prev_p else "<span></span>"
        pn += f'<a class="r" href="{next_p["slug"]}.html">{E(next_p["title"])}<span class="ic">➡️</span></a>' if next_p else ""
        pn += "</nav>"
        related = [q for q in posts if q["category"] == p["category"] and q is not p][:3]
        body = f'''<main class="post">
<section class="post-hero" style="--hbg:{c['bg']};--hfg:{c['fg']}">
<figure>{pic(p['slug'], 1, p['title'], eager=True) or art(p['category'], p['icon'], p['order'], p['title'])}</figure>
<div><p class="small"><a href="../index.html#{c['slug']}">{c['icon']} {p['category']}</a> · ⏱️ {p['mins']} min</p><h1>{E(p['title'])}</h1></div></section>
<article class="prose">{p['html']}</article>
<aside class="cta"><span class="big">📄</span><div><h2>Libreng VA resume</h2><a class="btn" href="../resume-template.html">Kunin ngayon</a></div></aside>
<section class="related"><h2>Basahin din</h2><div class="tiles">{''.join(tile(q, 1) for q in related)}</div></section>
{pn}</main>'''
        (OUT / "posts" / f"{p['slug']}.html").write_text(
            page(f"{p['title']} | {SITE}", p.get("description", ""), body, 1, f"posts/{p['slug']}.html"), encoding="utf-8")

    sections = ""
    for name, c in CATS.items():
        items = [p for p in posts if p["category"] == name]
        sections += f'''<section class="cat" id="{c['slug']}"><h2><span class="ic">{c['icon']}</span>{name}</h2>
<div class="tiles">{''.join(tile(p) for p in items)}</div></section>'''
    body = f'''<main>
<section class="mast"><div class="mast-text"><h1>Maging VA na may <em>totoong</em> kita.</h1>
<ol class="v-steps home"><li><span class="n">1</span><b>Matuto</b></li><li><span class="n">2</span><b>Mag-skill up</b></li><li><span class="n">3</span><b>Mag-apply</b></li><li><span class="n">4</span><b>Kumita</b></li></ol></div>{('<figure class="mast-art">' + pic('home', 0, 'Pinoy VA na nagtatrabaho sa gabi', eager=True) + '</figure>') if pic('home') else ''}</section>
{sections}
<section class="freebie"><span class="big">📄</span><div><h2>Libreng VA resume template</h2><a class="btn" href="resume-template.html">Buksan</a></div></section>
</main>'''
    (OUT / "index.html").write_text(page(f"{SITE} | Gabay para sa Pinoy Virtual Assistant",
        "Taglish na gabay para maging Virtual Assistant: paano magsimula, tools, rate, bayad at tax.", body), encoding="utf-8")

    about = '''<main class="post about">
<header class="about-head">''' + (('<figure class="about-art">' + pic('about', 0, 'Si Mia, ang Pinoy EA sa likod ng blog', eager=True) + '</figure>') if pic('about') else '') + '''<h1>Tungkol sa VA Pinoy Life</h1>
<p class="dek">Isinulat ng isang Pinoy Executive Assistant na remote na nagtatrabaho para sa isang CEO sa Canada.</p></header>
<article class="prose about-body">
<p>Hi! Ako ang nasa likod ng VA Pinoy Life. Araw-araw, mula dito sa Pilipinas, hawak ko ang inbox, calendar, travel at mga project ng isang busy na CEO sa Canada. Gising ako habang tulog ang karamihan, at ang trabaho ko ay siguraduhing maayos ang araw ng boss ko bago pa siya magising.</p>
<p>Pero hindi ako nagsimula dito. Gaya ng marami sa inyo, nagsimula ako nang walang malinaw na direksyon. Hindi ko alam kung saan maghahanap ng legit na trabaho, magkano ang dapat kong singilin, o paano makipag-usap sa client na iba ang kultura at time zone. Maraming trial and error. May mga job post na scam pala. May mga buwan na kulang ang kita. At madalas, wala akong mapagtanungan.</p>
<h2>Bakit ko ginawa ang blog na ito</h2>
<p>Ginawa ko ang VA Pinoy Life para hindi mo na pagdaanan ang lahat ng iyon. Ang gusto ko, may isang lugar na diretso, totoo at nasa wikang madaling intindihin, kung saan makikita mo ang buong daan: mula sa pagiging beginner, hanggang sa pagkakaroon ng long-term client na nagtitiwala sa'yo.</p>
<p>Lahat ng nandito ay galing sa totoong trabaho. Ang mga tools na binabanggit ko, ginagamit ko talaga araw-araw. Ang mga tips tungkol sa calendar, email at travel booking, natutunan ko sa paggawa mismo, minsan sa pagkakamali.</p>
<h2>Ano ang makikita mo dito</h2>
<p><strong>Pang-beginner</strong> na gabay kung paano magsimula, gumawa ng resume at pumasa sa interview. <strong>Tools at skills</strong> na hinahanap ng mga client abroad. At <strong>pera at career</strong>: rate, paraan ng pagtanggap ng bayad, tax, at paano lumago mula part-time hanggang full-time.</p>
<p>May libreng <a href="resume-template.html">VA resume template</a> din na pwede mong i-edit at i-save bilang PDF.</p>
<h2>Isang paalala</h2>
<p>Ang ilang links sa blog na ito ay affiliate links. Kapag bumili ka gamit ang mga ito, maaaring kumita ako ng maliit na komisyon nang walang dagdag na bayad sa'yo. Inirerekomenda ko lang ang mga bagay na ginagamit ko o pinagkakatiwalaan ko. Hindi ito financial o tax advice, kaya kumonsulta sa BIR o sa isang accountant para sa sarili mong sitwasyon.</p>
<p>Salamat sa pagbisita. Kung nandito ka dahil gusto mong magbago ang buhay mo sa pamamagitan ng remote work, nasa tamang lugar ka. Kaya mo 'yan.</p>
<p class="sign">Ang iyong kapwa Pinoy EA</p>
</article></main>'''
    (OUT / "about.html").write_text(page(f"About | {SITE}", "Tungkol sa VA Pinoy Life.", about, 0, "about.html"), encoding="utf-8")

    urls = ["", "about.html", "resume-template.html"] + [f"posts/{p['slug']}.html" for p in posts]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"<url><loc>{BASE_URL}/{u}</loc></url>\n" for u in urls) + "</urlset>\n"
    (OUT / "sitemap.xml").write_text(sm, encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUT / "posts.json").write_text(json.dumps([{k: p[k] for k in ("title", "slug", "category", "order", "prose_words", "blocks")} for p in posts], ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"built {len(posts)} posts -> {OUT}")


def check(files=None):
    paths = [Path(f) for f in files] if files else sorted(POSTS.glob("*.md"))
    bad = 0
    for f in paths:
        p = parse(f)
        ok = p["prose_words"] <= MAX_PROSE and p["blocks"] >= MIN_BLOCKS and "—" not in f.read_text(encoding="utf-8")
        bad += not ok
        print(f"{'OK  ' if ok else 'FAIL'} {f.name}: prose={p['prose_words']} (max {MAX_PROSE}), visual blocks={p['blocks']} (min {MIN_BLOCKS})")
    print("ALL PASS" if not bad else f"{bad} FAIL")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check([a for a in sys.argv[1:] if a != "--check"])
    else:
        build()
