#!/usr/bin/env python3
"""Baut die statische Website aus content/*.html nach site/.

Aufruf:  python3 tools/build.py
Vorschau: python3 -m http.server -d site 8000   ->  http://localhost:8000

PREVIEW=1 python3 tools/build.py  ->  Testversion fuer eine Vorschau-Domain:
    Suchmaschinen werden ausgesperrt (noindex), damit es keinen doppelten
    Inhalt zur Live-Seite gibt.
"""
import html
import json
import os
import re
import shutil
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
PAGES = ROOT / "pages"
OUT = ROOT / "site"

SITE = {
    "name": "Greenbody",
    "tagline": "Fitness. Ernährung. Gesundheit.",
    "url": "https://greenbody.de",
    "lang": "de",
}

# Reihenfolge = Navigation
TOPICS = {
    "Ernährung": ("ernaehrung", "Proteine, Meal Prep und Lebensmittel, die dich wirklich weiterbringen."),
    "Keto & Low Carb": ("keto-low-carb", "Ketogene Diät, Ketose, Low-Carb-Grundlagen und Rezepte."),
    "Fitness": ("fitness", "Training, Sixpack und die passende Ausrüstung."),
    "Schlaf": ("schlaf", "Besser schlafen, schneller regenerieren."),
}

PREVIEW = os.environ.get("PREVIEW") == "1"

MONTHS = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember"]

e = html.escape


# ---------------------------------------------------------------- Inhalte laden

def parse(path):
    raw = path.read_text()
    m = re.match(r"---\n(.*?)\n---\n", raw, re.S)
    meta = dict(line.split(": ", 1) for line in m.group(1).splitlines() if ": " in line)
    meta["body"] = raw[m.end():]
    meta["slug"] = path.stem
    return meta


def load():
    items = [parse(p) for p in sorted(CONTENT.glob("*.html"))]
    for it in items:
        words = len(re.sub(r"<[^>]+>", " ", it["body"]).split())
        it["minutes"] = max(1, round(words / 200))
        it["toc"] = re.findall(r'<h2[^>]*id="([^"]+)"[^>]*>(.*?)</h2>', it["body"], re.S)
    items.sort(key=lambda i: i["date"], reverse=True)
    return items


def fmt_date(iso):
    d = datetime.strptime(iso, "%Y-%m-%d")
    return f"{d.day}. {MONTHS[d.month - 1]} {d.year}"


def strip(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


# ---------------------------------------------------------------- Bausteine

LOGO = """<svg class="logo__mark" viewBox="0 0 32 32" aria-hidden="true"><path d="M27 4C14 4 5 11 5 21c0 3 1 5 2 7 1-6 5-12 12-15-5 4-8 9-9 15 2 1 4 1 6 1 10 0 13-11 11-25z" fill="currentColor"/></svg>"""


def header(active=""):
    links = "".join(
        f'<a href="/thema/{slug}/"{" aria-current=page" if active == name else ""}>{e(name)}</a>'
        for name, (slug, _) in TOPICS.items()
    )
    return f"""<a class="skip" href="#inhalt">Zum Inhalt springen</a>
<header class="site-header">
  <div class="wrap site-header__inner">
    <a class="logo" href="/">{LOGO}<span>GREEN<b>BODY</b></span></a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="nav" aria-label="Menü öffnen"><span></span></button>
    <nav id="nav" class="nav">{links}<a href="/blog/"{" aria-current=page" if active == "blog" else ""}>Alle Artikel</a></nav>
  </div>
</header>"""


def footer():
    topics = "".join(f'<li><a href="/thema/{s}/">{e(n)}</a></li>' for n, (s, _) in TOPICS.items())
    return f"""<footer class="site-footer">
  <div class="wrap site-footer__grid">
    <div>
      <a class="logo logo--footer" href="/">{LOGO}<span>GREEN<b>BODY</b></span></a>
      <p>Fundiertes Wissen zu Ernährung, Fitness und Schlaf – verständlich erklärt und alltagstauglich.</p>
    </div>
    <div><h2>Themen</h2><ul>{topics}</ul></div>
    <div><h2>Rechtliches</h2><ul><li><a href="/impressum/">Impressum</a></li><li><a href="/datenschutz/">Datenschutz</a></li></ul></div>
  </div>
  <div class="wrap site-footer__bottom">
    <p>© {date.today().year} Greenbody. Die Inhalte ersetzen keine ärztliche Beratung.</p>
    <p>Mit * oder „Amazon“ gekennzeichnete Links sind Affiliate-Links. Als Amazon-Partner verdienen wir an qualifizierten Verkäufen.</p>
  </div>
</footer>"""


def layout(title, body, *, description="", path="/", image="", active="", jsonld=None, noindex=False):
    full_title = title if title == SITE["name"] else f"{title} | {SITE['name']}"
    og_image = f"{SITE['url']}/assets/img/{image}" if image else f"{SITE['url']}/assets/img/og-default.png"
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    return f"""<!doctype html>
<html lang="{SITE['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(description)}">
{'<meta name="robots" content="noindex, nofollow">' if noindex or PREVIEW else ''}
<link rel="canonical" href="{SITE['url']}{path}">
<meta property="og:type" content="{'article' if jsonld and jsonld.get('@type') == 'Article' else 'website'}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{SITE['url']}{path}">
<meta property="og:image" content="{og_image}">
<meta property="og:locale" content="de_DE">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1f5c3a">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="Greenbody" href="/feed.xml">
<link rel="stylesheet" href="/assets/style.css">
<script src="/assets/main.js" defer></script>
{ld}
</head>
<body>
{header(active)}
<main id="inhalt">
{body}
</main>
{footer()}
</body>
</html>
"""


def card(it, big=False):
    img = (f'<img src="/assets/img/{it["image"]}" alt="" loading="lazy" decoding="async" width="900" height="600">'
           if it["image"] else '<div class="card__placeholder"></div>')
    return f"""<article class="card{' card--big' if big else ''}" data-topic="{e(it['category'])}">
  <a class="card__link" href="{it['url']}">
    <div class="card__media">{img}</div>
    <div class="card__body">
      <span class="chip">{e(it['category'])}</span>
      <h3 class="card__title">{e(it['title'])}</h3>
      <p class="card__text">{e(it['description'])}</p>
      <span class="card__meta">{it['minutes']} Min. Lesezeit</span>
    </div>
  </a>
</article>"""


# ---------------------------------------------------------------- Seiten

def page_article(it, items):
    body = it["body"]
    hero = ""
    if it["image"] and f'/assets/img/{it["image"]}' not in body:
        hero = f'<figure class="article__hero"><img src="/assets/img/{it["image"]}" alt="{e(it["title"])}" width="1200" height="800" fetchpriority="high"></figure>'

    toc = ""
    if len(it["toc"]) >= 3:
        entries = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in it["toc"])
        toc = f'<details class="toc" open><summary>Inhalt</summary><ol>{entries}</ol></details>'

    affiliate = ""
    if "amazon." in body or "amzn.to" in body:
        affiliate = ('<p class="notice">Hinweis: Dieser Artikel enthält Affiliate-Links zu Amazon. '
                     'Kaufst du darüber ein, erhalten wir eine kleine Provision – für dich ändert sich am Preis nichts.</p>')

    related = [o for o in items if o["category"] == it["category"] and o is not it][:3]
    if len(related) < 3:
        related += [o for o in items if o is not it and o not in related][: 3 - len(related)]
    topic_slug = TOPICS.get(it["category"], ("", ""))[0]
    updated = (f' · Aktualisiert am <time datetime="{it["updated"]}">{fmt_date(it["updated"])}</time>'
               if it["updated"] != it["date"] else "")

    jsonld = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": it["title"], "description": it["description"],
        "datePublished": it["date"], "dateModified": it["updated"],
        "image": f"{SITE['url']}/assets/img/{it['image']}" if it["image"] else None,
        "author": {"@type": "Organization", "name": "Greenbody"},
        "publisher": {"@type": "Organization", "name": "Greenbody"},
        "mainEntityOfPage": f"{SITE['url']}{it['url']}",
    }

    content = f"""<article class="article">
  <header class="article__header wrap wrap--text">
    <nav class="crumbs" aria-label="Brotkrümel"><a href="/">Start</a> › <a href="/thema/{topic_slug}/">{e(it['category'])}</a></nav>
    <h1>{e(it['title'])}</h1>
    <p class="article__meta"><time datetime="{it['date']}">{fmt_date(it['date'])}</time>{updated} · {it['minutes']} Min. Lesezeit</p>
  </header>
  <div class="wrap wrap--text">
    {hero}
    {toc}
    <div class="prose">
{body}
    </div>
    {affiliate}
  </div>
</article>
<section class="related wrap">
  <h2 class="section-title">Das könnte dich auch interessieren</h2>
  <div class="grid">{''.join(card(r) for r in related)}</div>
</section>"""
    return layout(it["title"], content, description=it["description"], path=it["url"],
                  image=it["image"], active=it["category"], jsonld=jsonld)


def page_home(items):
    guides = [i for i in items if i["type"] == "ratgeber"]
    featured = next(i for i in items if i["slug"] == "die-ketogene-diaet")
    topics = "".join(
        f'<a class="topic" href="/thema/{slug}/"><span class="topic__name">{e(name)}</span>'
        f'<span class="topic__text">{e(text)}</span>'
        f'<span class="topic__count">{sum(1 for i in items if i["category"] == name)} Beiträge</span></a>'
        for name, (slug, text) in TOPICS.items()
    )
    body = f"""<section class="hero">
  <div class="wrap hero__inner">
    <div class="hero__copy">
      <p class="eyebrow">{SITE['tagline']}</p>
      <h1>Gesünder leben – mit Wissen, das du wirklich umsetzen kannst.</h1>
      <p class="hero__lead">Ratgeber zu Keto &amp; Low Carb, Proteinen, Training und erholsamem Schlaf. Ohne Mythen, ohne Hype.</p>
      <div class="hero__actions"><a class="btn" href="{featured['url']}">Keto-Guide lesen</a><a class="btn btn--ghost" href="/blog/">Alle Artikel</a></div>
    </div>
    <a class="hero__feature" href="{featured['url']}">
      <img src="/assets/img/{featured['image']}" alt="" width="1200" height="800" fetchpriority="high">
      <span class="hero__badge">Beliebtester Ratgeber</span>
    </a>
  </div>
</section>
<section class="wrap section">
  <h2 class="section-title">Themen</h2>
  <div class="topics">{topics}</div>
</section>
<section class="wrap section">
  <h2 class="section-title">Ratgeber &amp; Guides</h2>
  <div class="grid grid--feature">{''.join(card(g, big=(n == 0)) for n, g in enumerate(guides))}</div>
</section>
<section class="wrap section">
  <div class="section-head"><h2 class="section-title">Neu im Blog</h2><a href="/blog/">Alle Artikel →</a></div>
  <div class="grid">{''.join(card(i) for i in items if i['type'] == 'artikel')}</div>
</section>"""
    jsonld = {"@context": "https://schema.org", "@type": "WebSite", "name": SITE["name"], "url": SITE["url"]}
    return layout(SITE["name"], body, description=f"Greenbody – {SITE['tagline']} Ratgeber zu Keto, Low Carb, Proteinen, Fitness und Schlaf.",
                  path="/", jsonld=jsonld)


def page_list(title, intro, items, path, active, filters=False):
    chips = ""
    if filters:
        chips = '<div class="filters" role="toolbar" aria-label="Nach Thema filtern"><button class="is-active" data-filter="">Alle</button>' + \
            "".join(f'<button data-filter="{e(n)}">{e(n)}</button>' for n in TOPICS) + "</div>"
    body = f"""<section class="wrap section page-head">
  <h1>{e(title)}</h1>
  <p class="page-head__lead">{e(intro)}</p>
  {chips}
</section>
<section class="wrap section section--tight"><div class="grid" id="list">{''.join(card(i) for i in items)}</div></section>"""
    return layout(title, body, description=intro, path=path, active=active)


def page_static(slug):
    it = parse(PAGES / f"{slug}.html")
    body = f"""<article class="article"><header class="article__header wrap wrap--text"><h1>{e(it['title'])}</h1></header>
<div class="wrap wrap--text"><div class="prose">{it['body']}</div></div></article>"""
    return layout(it["title"], body, description=it.get("description", ""), path=f"/{slug}/", noindex=True)


def redirect(target):
    return f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Weiterleitung</title>
<link rel="canonical" href="{SITE['url']}{target}"><meta http-equiv="refresh" content="0; url={target}"><meta name="robots" content="noindex"></head>
<body><p>Diese Seite ist umgezogen: <a href="{target}">{target}</a></p></body></html>"""


# ---------------------------------------------------------------- Build

# Fuer Hostinger (Apache/LiteSpeed)
HTACCESS = """ErrorDocument 404 /404.html
DirectoryIndex index.html

RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType image/webp "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType image/svg+xml "access plus 1 year"
  ExpiresByType text/css "access plus 1 week"
  ExpiresByType application/javascript "access plus 1 week"
  ExpiresByType text/html "access plus 10 minutes"
</IfModule>

<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css application/javascript image/svg+xml application/xml text/xml
</IfModule>
"""

def write(path, text):
    f = OUT / path.lstrip("/")
    if path.endswith("/"):
        f = f / "index.html"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "assets", OUT / "assets")
    items = load()

    write("/", page_home(items))
    for it in items:
        write(it["url"], page_article(it, items))
    write("/blog/", page_list("Alle Artikel", "Alle Beiträge zu Ernährung, Keto & Low Carb, Fitness und Schlaf.",
                              items, "/blog/", "blog", filters=True))
    for name, (slug, text) in TOPICS.items():
        write(f"/thema/{slug}/", page_list(name, text, [i for i in items if i["category"] == name],
                                           f"/thema/{slug}/", name))
    for slug in ("impressum", "datenschutz"):
        write(f"/{slug}/", page_static(slug))

    # alte WordPress-Adressen weiterleiten
    write("/category/c/", redirect("/blog/"))
    write("/c/", redirect("/blog/"))
    write("/author/admin/", redirect("/"))
    write("/feed/", redirect("/feed.xml"))

    write("/404.html", layout("Seite nicht gefunden", """<section class="wrap section page-head">
<h1>Seite nicht gefunden</h1><p class="page-head__lead">Diese Seite gibt es (nicht mehr). Vielleicht hilft dir einer dieser Wege weiter:</p>
<p><a class="btn" href="/">Zur Startseite</a> <a class="btn btn--ghost" href="/blog/">Alle Artikel</a></p></section>""",
                              description="Seite nicht gefunden", path="/404.html", noindex=True))

    urls = ["/", "/blog/"] + [f"/thema/{s}/" for s, _ in TOPICS.values()] + [i["url"] for i in items]
    lastmod = {i["url"]: i["updated"] for i in items}
    write("/sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
          "".join(f"  <url><loc>{SITE['url']}{u}</loc>{f'<lastmod>{lastmod[u]}</lastmod>' if u in lastmod else ''}</url>\n" for u in urls) +
          "</urlset>\n")
    if PREVIEW:
        write("/robots.txt", "User-agent: *\nDisallow: /\n")
    else:
        write("/robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE['url']}/sitemap.xml\n")
    write("/.htaccess", HTACCESS)

    rss = "".join(f"""  <item><title>{e(i['title'])}</title><link>{SITE['url']}{i['url']}</link><guid>{SITE['url']}{i['url']}</guid>
    <pubDate>{datetime.strptime(i['date'], '%Y-%m-%d').strftime('%a, %d %b %Y 00:00:00 +0000')}</pubDate><description>{e(i['description'])}</description></item>
""" for i in items)
    write("/feed.xml", f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Greenbody</title><link>{SITE['url']}/</link><description>{SITE['tagline']}</description><language>de</language>
{rss}</channel></rss>
""")
    print(f"✓ {len(items)} Artikel + Startseite, Blog, {len(TOPICS)} Themen, Impressum, Datenschutz -> {OUT.relative_to(ROOT)}/"
          + (" (Vorschau-Modus: noindex)" if PREVIEW else ""))


if __name__ == "__main__":
    main()
