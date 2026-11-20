"""VA Pinoy Life static blog builder.
Usage: python build.py   -> writes ./docs (GitHub Pages folder)
"""
import html
import json
import re
import shutil
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
POSTS = ROOT / "posts"
STATIC = ROOT / "static"
OUT = ROOT / "docs"
SITE = "VA Pinoy Life"
BASE_URL = "https://fcagomoc143-cloud.github.io/va-pinoy-life"

CATS = {
    "Pang-beginner": {"slug": "beginner", "blurb": "Magsimula dito kung bago ka sa VA work.", "art": "start"},
    "Tools at skills": {"slug": "tools", "blurb": "Mga app at skills na hinahanap ng clients.", "art": "tools"},
    "Pera at career": {"slug": "pera", "blurb": "Rate, bayad, tax at paglago ng career.", "art": "money"},
}


def art(kind, seed=0):
    """Bespoke inline SVG per category; seed shifts shapes so each post differs."""
    s = seed % 7
    if kind == "start":
        return f'''<svg viewBox="0 0 320 200" preserveAspectRatio="xMidYMid slice" role="img" aria-hidden="true"><rect width="320" height="200" fill="#0F2A6B"/>
<circle cx="{230 - s*6}" cy="70" r="{38 + s*2}" fill="#FFC93C"/>
<path d="M0 160 Q80 {110 + s*4} 160 150 T320 140 V200 H0Z" fill="#1E4BB8"/>
<rect x="{48 + s*4}" y="96" width="92" height="60" rx="6" fill="#F5F7FB"/><rect x="58" y="106" width="72" height="38" rx="3" fill="#0F2A6B"/>
<rect x="34" y="156" width="120" height="8" rx="4" fill="#F5F7FB"/></svg>'''
    if kind == "tools":
        return f'''<svg viewBox="0 0 320 200" preserveAspectRatio="xMidYMid slice" role="img" aria-hidden="true"><rect width="320" height="200" fill="#FFC93C"/>
<rect x="{30 + s*5}" y="34" width="120" height="132" rx="10" fill="#0F2A6B"/>
<rect x="46" y="54" width="{70 + s*3}" height="10" rx="5" fill="#FFC93C"/><rect x="46" y="76" width="88" height="10" rx="5" fill="#F5F7FB"/><rect x="46" y="98" width="60" height="10" rx="5" fill="#F5F7FB"/>
<circle cx="{232 - s*4}" cy="100" r="54" fill="#D7263D"/><path d="M{208 - s*4} 100 l16 16 l30 -34" stroke="#F5F7FB" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'''
    return f'''<svg viewBox="0 0 320 200" preserveAspectRatio="xMidYMid slice" role="img" aria-hidden="true"><rect width="320" height="200" fill="#D7263D"/>
<rect x="40" y="{120 - s*3}" width="40" height="{60 + s*3}" fill="#FFC93C"/><rect x="100" y="{90 - s*3}" width="40" height="{90 + s*3}" fill="#FFC93C"/><rect x="160" y="{60 - s*3}" width="40" height="{120 + s*3}" fill="#FFC93C"/>
<circle cx="258" cy="{70 + s*4}" r="34" fill="#F5F7FB"/><text x="258" y="{82 + s*4}" font-size="34" font-weight="800" text-anchor="middle" fill="#0F2A6B" font-family="Bricolage Grotesque, sans-serif">₱</text>
<rect x="24" y="180" width="272" height="6" fill="#0F2A6B"/></svg>'''


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
    body = m.group(2)
    # drop a leading H1 duplicate of the title
    body = re.sub(r"^\s*#\s+.*\n", "", body, count=1) if body.lstrip().startswith("# ") else body
    body = re.sub(r"^(\s*)[-*] \[[ xX]\] ", r"\1- ☐ ", body, flags=re.M)
    meta["html"] = markdown.markdown(body, extensions=["tables", "sane_lists"])
    words = len(re.findall(r"\w+", body))
    meta["mins"] = max(2, round(words / 200))
    if meta.get("category") not in CATS:
        meta["category"] = "Pang-beginner"
    return meta


def page(title, desc, body, depth=0, canonical=""):
    p = "../" * depth
    return f'''<!doctype html>
<html lang="fil">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<link rel="canonical" href="{BASE_URL}/{canonical}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{p}style.css">
<link rel="icon" href="{p}favicon.svg">
</head>
<body>
<header class="top"><a class="brand" href="{p}index.html">VA <span>Pinoy</span> Life</a>
<nav><a href="{p}index.html#beginner">Simula</a><a href="{p}index.html#tools">Tools</a><a href="{p}index.html#pera">Pera</a><a href="{p}resume-template.html">Free resume</a><a href="{p}about.html">About</a></nav></header>
{body}
<footer class="foot"><div><a class="brand" href="{p}index.html">VA <span>Pinoy</span> Life</a><p>Totoong tips para sa Pinoy VA, galing sa isang EA na nagtatrabaho para sa CEO sa Canada.</p></div>
<p class="small">Ang ilang links ay maaaring affiliate links. Walang dagdag na bayad sa'yo. Hindi ito financial o tax advice.</p></footer>
<script>
const h=document.querySelector('.top');addEventListener('scroll',()=>h.classList.toggle('scrolled',scrollY>8),{{passive:true}});
</script>
</body></html>'''


def card(p, depth=0, big=False):
    c = CATS[p["category"]]
    cls = "lead" if big else "item"
    return f'''<a class="{cls}" href="{'../'*depth}posts/{p['slug']}.html">
<figure>{art(c['art'], p['order'])}</figure>
<div><h3>{html.escape(p['title'])}</h3><p>{html.escape(p.get('description',''))}</p><p class="small">{p['category']} · {p['mins']} min basa</p></div></a>'''


def build():
    OUT.mkdir(exist_ok=True)
    for f in OUT.iterdir():  # clear contents, keep folder (a dev server may hold it)
        shutil.rmtree(f) if f.is_dir() else f.unlink()
    (OUT / "posts").mkdir(parents=True)
    for f in STATIC.iterdir():
        shutil.copy(f, OUT / f.name)
    posts = sorted((parse(f) for f in POSTS.glob("*.md")), key=lambda x: x["order"])
    if not posts:
        raise SystemExit("no posts")

    # post pages
    for i, p in enumerate(posts):
        prev_p = posts[i - 1] if i > 0 else None
        next_p = posts[i + 1] if i + 1 < len(posts) else None
        c = CATS[p["category"]]
        nav = '<nav class="pn">'
        if prev_p:
            nav += f'<a href="{prev_p["slug"]}.html"><span class="small">Nakaraan</span>{html.escape(prev_p["title"])}</a>'
        else:
            nav += "<span></span>"
        if next_p:
            nav += f'<a class="r" href="{next_p["slug"]}.html"><span class="small">Susunod</span>{html.escape(next_p["title"])}</a>'
        nav += "</nav>"
        body = f'''<main class="post">
<div class="post-head"><p class="small"><a href="../index.html#{c['slug']}">{p['category']}</a> · {p['mins']} min basa</p>
<h1>{html.escape(p['title'])}</h1><p class="dek">{html.escape(p.get('description',''))}</p></div>
<figure class="post-art">{art(c['art'], p['order'])}</figure>
<article class="prose">{p['html']}</article>
<aside class="cta"><h2>Libreng VA resume template</h2><p>I-print o i-save bilang PDF. Ready na para sa Upwork at OnlineJobs.ph.</p><a class="btn" href="../resume-template.html">Kunin ang template</a></aside>
{nav}</main>'''
        (OUT / "posts" / f"{p['slug']}.html").write_text(
            page(f"{p['title']} | {SITE}", p.get("description", ""), body, 1, f"posts/{p['slug']}.html"), encoding="utf-8")

    # index
    lead = posts[0]
    sections = ""
    for name, c in CATS.items():
        items = [p for p in posts if p["category"] == name]
        if not items:
            continue
        sections += f'''<section class="cat" id="{c['slug']}"><div class="cat-head"><h2>{name}</h2><p>{c['blurb']}</p></div>
<div class="list">{''.join(card(p) for p in items)}</div></section>'''
    body = f'''<main>
<section class="mast"><h1>Maging VA na may <em>totoong</em> kita.</h1>
<p class="dek">Step-by-step na gabay sa Taglish para sa Pinoy na gustong magtrabaho online para sa clients abroad.</p></section>
<section class="hero-post">{card(lead, big=True)}</section>
{sections}
<section class="freebie"><div><h2>Libreng VA resume template</h2><p>Ang format na ginagamit ko para makapasok bilang EA. Palitan lang ang laman, i-print o i-save bilang PDF.</p><a class="btn" href="resume-template.html">Buksan ang template</a></div>
<figure>{art('tools', 3)}</figure></section>
</main>'''
    (OUT / "index.html").write_text(page(f"{SITE} | Gabay para sa Pinoy Virtual Assistant",
        "Taglish na gabay para maging Virtual Assistant: paano magsimula, tools, rate, bayad at tax.", body, 0, ""), encoding="utf-8")

    # about
    about = '''<main class="post"><div class="post-head"><h1>Tungkol sa VA Pinoy Life</h1>
<p class="dek">Isinulat ng isang Pinoy Executive Assistant na remote na nagtatrabaho para sa isang CEO sa Canada.</p></div>
<article class="prose"><p>Nagsimula rin ako sa wala: walang experience, walang client, at hindi sigurado kung saan magsisimula. Ngayon, araw-araw kong hawak ang inbox, calendar, travel at projects ng isang busy na CEO.</p>
<p>Ginawa ko ang blog na ito para hindi mo na pagdaanan ang trial and error na pinagdaanan ko. Lahat ng nandito ay galing sa totoong trabaho.</p>
<h2>Ano ang makukuha mo dito</h2><ul><li>Step-by-step na gabay kung paano magsimula bilang VA</li><li>Mga tools na talagang ginagamit sa trabaho</li><li>Totoong usapan tungkol sa rate, bayad at tax</li></ul>
<h2>Paalala</h2><p>Ang ilang links ay affiliate links. Kapag bumili ka gamit ang mga ito, maaaring kumita ako ng maliit na komisyon nang walang dagdag na bayad sa'yo. Hindi ito financial o tax advice. Kumonsulta sa BIR o accountant para sa sarili mong sitwasyon.</p></article></main>'''
    (OUT / "about.html").write_text(page(f"About | {SITE}", "Tungkol sa VA Pinoy Life.", about, 0, "about.html"), encoding="utf-8")

    # sitemap + robots
    urls = ["", "about.html", "resume-template.html"] + [f"posts/{p['slug']}.html" for p in posts]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"<url><loc>{BASE_URL}/{u}</loc></url>\n" for u in urls) + "</urlset>\n"
    (OUT / "sitemap.xml").write_text(sm, encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUT / "posts.json").write_text(json.dumps([{k: p[k] for k in ("title", "slug", "category", "order")} for p in posts], ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"built {len(posts)} posts -> {OUT}")


if __name__ == "__main__":
    build()
