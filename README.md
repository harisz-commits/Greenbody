# Greenbody.de – statische Website

Die frühere WordPress-Seite **greenbody.de** als schnelle, statische Website – ohne WordPress, ohne Datenbank, ohne Plugins.
Alle Artikel, Ratgeber und Bilder wurden übernommen, das Design wurde modernisiert.

## Was ist wo?

| Ordner | Inhalt |
|---|---|
| `content/` | Alle 13 Artikel/Ratgeber als HTML – **hier Texte bearbeiten** |
| `pages/` | Impressum & Datenschutz (**Platzhalter bitte ausfüllen!**) |
| `assets/img/` | Alle Bilder (als WebP, max. 1600 px) |
| `assets/style.css`, `assets/main.js` | Design & kleine Skripte |
| `tools/build.py` | Baut die fertige Website nach `site/` |
| `tools/import_wordpress.py` | Einmaliger Import aus WordPress (schon erledigt) |
| `wordpress-export/` | Rohdaten-Backup der alten WordPress-Seite |

## Lokal ansehen

Nur Python 3 nötig, keine weiteren Pakete:

```bash
python3 tools/build.py
python3 -m http.server -d site 8000
# -> http://localhost:8000
```

## Artikel bearbeiten oder neu anlegen

Jede Datei in `content/` beginnt mit einem Kopf:

```
---
title: Die Ketose
url: /ketose/
type: ratgeber          # ratgeber oder artikel
category: Keto & Low Carb   # Ernährung | Keto & Low Carb | Fitness | Schlaf
date: 2021-05-17
updated: 2021-05-26
image: ketones-glucose.webp
description: Kurzbeschreibung für Google (ca. 150 Zeichen)
---
<p>Text …</p>
```

Neuer Artikel = neue Datei nach diesem Muster, Bild nach `assets/img/` legen. Überschriften `<h2 id="...">` erscheinen automatisch im Inhaltsverzeichnis.

## Veröffentlichen mit GitHub Pages (kostenlos)

1. Branch nach `main` mergen.
2. GitHub → *Settings → Pages → Source:* **GitHub Actions** wählen. Bei jedem Push wird die Seite automatisch gebaut.
3. *Settings → Pages → Custom domain:* `greenbody.de` eintragen, „Enforce HTTPS“ aktivieren.
4. Beim Domain-Anbieter die DNS-Einträge umstellen:
   - `A`-Records für `greenbody.de`: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - `CNAME` für `www`: `<dein-github-name>.github.io`
5. Erst wenn die neue Seite unter greenbody.de läuft, WordPress abschalten.

Alternativ lässt sich der Ordner `site/` bei jedem beliebigen Webhoster hochladen.

## Was sich gegenüber WordPress geändert hat

- Alle Adressen sind gleich geblieben (`/c/…/`, `/ketose/` …) – Google-Rankings und Links bleiben erhalten. Alte Archivseiten (`/category/c/`, `/feed/`) leiten weiter.
- Neues Design mit Themenseiten (Ernährung, Keto & Low Carb, Fitness, Schlaf), Inhaltsverzeichnis, Lesezeit, ähnlichen Artikeln, Dark Mode.
- Amazon-Vergleichstabellen: statisch übernommen. Die Live-Preise des AAWP-Plugins wurden entfernt (wären sofort veraltet); die Affiliate-Links funktionieren weiter. Produktbilder werden von Amazon geladen.
- YouTube-Videos laden erst nach Klick (datenschutzfreundlich).
- Keine Cookies, kein Tracking, keine externen Schriften.
- Kommentare gibt es auf einer statischen Seite nicht mehr.
- Die leere „Sample Page“ wurde nicht übernommen.
