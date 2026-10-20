#!/usr/bin/env python3
"""Einmaliger Import: WordPress-REST-Export (wordpress-export/*.json) -> content/*.html

Bereinigt das WordPress-HTML (Plugins, Inline-Styles, srcset ...), biegt Bild-URLs
auf die lokalen WebP-Dateien in assets/img/ um und schreibt pro Artikel eine
editierbare HTML-Datei mit Front-Matter-Kopf.

Aufruf:  python3 tools/import_wordpress.py
"""
import base64
import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup, Comment

ROOT = Path(__file__).resolve().parent.parent
EXPORT = ROOT / "wordpress-export"
CONTENT = ROOT / "content"
IMG_DIR = ROOT / "assets" / "img"

SKIP = {"sample-page"}

# Themen-Zuordnung (neu, die alte Seite hatte nur die Kategorie "Blog")
CATEGORY = {
    "besser-schlafen-die-besten-tipps": "Schlaf",
    "mittagsschlaefchen-gefaellig": "Schlaf",
    "der-ultimative-sixpack-guide": "Fitness",
    "die-besten-fitness-uhren-im-test": "Fitness",
    "welches-ist-das-richtige-protein": "Ernährung",
    "die-11-besten-veganen-proteinquellen": "Ernährung",
    "7-lebensmittel-die-muede-machen": "Ernährung",
    "7-regeln-fuer-erfolgreiches-meal-prep": "Ernährung",
    "ketose": "Keto & Low Carb",
    "die-ketogene-diaet": "Keto & Low Carb",
    "welches-gemuese-bei-der-ketogenen-diaet": "Keto & Low Carb",
    "die-low-carb-diaet": "Keto & Low Carb",
    "low-carb-pfannkuchen-mit-spinat-und-ricotta": "Keto & Low Carb",
}

# Titelbild fuer Seiten ohne "featured image" in WordPress
FALLBACK_IMAGE = {
    "ketose": "ketones-glucose",
    "die-besten-fitness-uhren-im-test": "die-beste-fitness-uhr-laufen-fahrrad-rad",
    "welches-gemuese-bei-der-ketogenen-diaet": "keto-gemuese-Kopie",
    "die-ketogene-diaet": "die_ketogene_diaet",
    "low-carb-pfannkuchen-mit-spinat-und-ricotta": "rezept-pfannkuchen-spinat-kaese",
}


def local_image(url):
    """WordPress-Upload-URL -> /assets/img/<name>.webp (falls vorhanden)."""
    if "wp-content/uploads" not in url:
        return None
    name = Path(urlparse(url).path).stem
    name = re.sub(r"-\d+x\d+$", "", name)
    name = re.sub(r"-scaled$", "", name)
    name = name.replace("logo_white", "logo-white")
    if (IMG_DIR / f"{name}.webp").exists():
        return name
    print(f"  ! Bild fehlt lokal: {url}")
    return None


def image_size(name):
    from PIL import Image

    with Image.open(IMG_DIR / f"{name}.webp") as im:
        return im.size


def text(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def description(excerpt):
    t = text(excerpt)
    t = re.sub(r"\s*(\[…\]|\[&hellip;\]|…|Read More.*)$", "", t)
    t = re.sub(r"\s+", " ", t)
    if len(t) > 158:
        t = t[:155].rsplit(" ", 1)[0] + " …"
    return t


def slugify(s):
    s = s.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60]


def clean(body):
    soup = BeautifulSoup(body, "html.parser")

    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    for t in soup.find_all(["script", "style", "noscript"]):
        t.decompose()

    # --- Amazon-Vergleichstabellen (Plugin AAWP) ---
    for t in soup.select(".aawp-tb--mobile"):
        t.decompose()
    for row in soup.select(".aawp-tb__row"):
        # Preise waren live von Amazon - statisch waeren sie sofort veraltet
        if row.select_one(".aawp-tb__data--type-price"):
            row.decompose()
    for img in soup.select("img[src*='aawp/public/image.php']"):
        q = parse_qs(urlparse(img["src"]).query).get("url", [""])[0]
        try:
            img["src"] = base64.urlsafe_b64decode(q + "=" * (-len(q) % 4)).decode()
        except Exception:
            img.decompose()

    # --- Rezept-Plugin (WP Recipe Maker) ---
    for a in soup.select("a[href*='wprm_print'], a[href*='pinterest.com']"):
        a.decompose()
    for t in soup.select(".wprm-spacer, #recipe, .wprm-template-chic-buttons"):
        t.decompose()

    # --- YouTube: Zwei-Klick-Loesung statt direktem iframe (DSGVO) ---
    for iframe in soup.find_all("iframe"):
        m = re.search(r"youtube\.com/embed/([\w-]+)", iframe.get("src", ""))
        if not m:
            iframe.decompose()
            continue
        title = iframe.get("title") or "YouTube-Video"
        facade = soup.new_tag("div", attrs={"class": "yt", "data-id": m.group(1)})
        btn = soup.new_tag("button", attrs={"type": "button", "class": "yt__btn"})
        btn.string = f"▶ Video abspielen: {title}"
        note = soup.new_tag("p", attrs={"class": "yt__note"})
        note.string = "Beim Abspielen wird eine Verbindung zu YouTube (Google) hergestellt."
        facade.append(btn)
        facade.append(note)
        wrapper = iframe.find_parent(class_="wp-block-embed__wrapper") or iframe
        wrapper.replace_with(facade)

    # --- Bilder ---
    for img in soup.find_all("img"):
        src = img.get("src", "")
        name = local_image(src)
        for attr in ("srcset", "sizes", "style", "class", "loading", "width", "height"):
            img.attrs.pop(attr, None)
        if name:
            img["src"] = f"/assets/img/{name}.webp"
            w, h = image_size(name)
            img["width"], img["height"] = str(w), str(h)
        img["loading"] = "lazy"
        img["decoding"] = "async"
        img["alt"] = img.get("alt", "")

    # --- Links ---
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith(("https://greenbody.de", "http://greenbody.de")):
            path = urlparse(href).path or "/"
            if path.startswith(("/wp-admin", "/wp-login")):
                a.unwrap()
                continue
            a["href"] = path + (("#" + urlparse(href).fragment) if urlparse(href).fragment else "")
            a.attrs.pop("target", None)
            a.attrs.pop("rel", None)
        elif href.startswith("http"):
            host = urlparse(href).netloc
            sponsored = "amazon." in host or "amzn.to" in host
            a["target"] = "_blank"
            a["rel"] = "sponsored nofollow noopener" if sponsored else "noopener"

    # --- Aufraeumen ---
    for t in soup.find_all(True):
        for attr in list(t.attrs):
            if attr == "style" or attr.startswith("data-") and attr != "data-id":
                del t[attr]
    for p in soup.find_all("p"):
        if not p.get_text(strip=True) and not p.find(["img", "iframe", "br"]):
            p.decompose()

    # Anker fuer das Inhaltsverzeichnis
    seen = set()
    for h in soup.find_all(["h2", "h3"]):
        if h.find_parent(class_=re.compile("aawp|wprm")):
            continue
        hid = slugify(h.get_text()) or "abschnitt"
        while hid in seen:
            hid += "-2"
        seen.add(hid)
        h["id"] = hid

    out = str(soup)
    out = re.sub(r"\n\s*\n+", "\n\n", out)
    out = re.sub(r"[ \t]+\n", "\n", out)
    return out.strip() + "\n"


def main():
    media = {}
    CONTENT.mkdir(exist_ok=True)
    count = 0
    for kind in ("posts", "pages"):
        for p in json.loads((EXPORT / f"{kind}.json").read_text()):
            slug = p["slug"]
            if slug in SKIP:
                continue
            url = urlparse(p["link"]).path
            image = FALLBACK_IMAGE.get(slug)
            body = p["content"]["rendered"]
            if p["featured_media"]:
                # Titelbild = erstes Bild mit passender Media-ID im Export
                media_name = {
                    96: "besser-schlafen-die-besten-tipps", 63: "der-ultimative-sixpack-guide",
                    60: "proteinpulver", 51: "lebensmittel-die-muede-machen",
                    39: "vegane-proteinquellen", 36: "vorteile-von-mittagsschlaf",
                    23: "erfolgreiches-meal-prep", 69: "low-carb-diaet",
                }
                image = media_name.get(p["featured_media"], image)
            meta = {
                "title": text(p["title"]["rendered"]),
                "url": url,
                "type": "artikel" if kind == "posts" else "ratgeber",
                "category": CATEGORY.get(slug, "Allgemein"),
                "date": p["date"][:10],
                "updated": p["modified"][:10],
                "image": f"{image}.webp" if image else "",
                "description": description(p["excerpt"]["rendered"]),
            }
            head = "---\n" + "".join(f"{k}: {v}\n" for k, v in meta.items()) + "---\n"
            (CONTENT / f"{slug}.html").write_text(head + clean(body))
            count += 1
            print(f"✓ {url}")
    print(f"{count} Seiten importiert.")


if __name__ == "__main__":
    main()
