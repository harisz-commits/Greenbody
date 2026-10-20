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

## Veröffentlichen auf Hostinger

GitHub baut die Seite bei jedem Push automatisch (`.github/workflows/deploy.yml`) und legt die fertigen Dateien auf einen eigenen Branch:

| Branch | Wofür | Suchmaschinen |
|---|---|---|
| `hostinger-preview` | Testversion zum Arbeiten (Vorschau-Domain) | gesperrt (noindex) |
| `hostinger-live` | echte Seite für greenbody.de – nur per Hand: *Actions → Website für Hostinger bauen → Run workflow → live* | erlaubt |

### Vorschau einrichten (einmalig)

1. **Vorschau-Domain anlegen** – eine von beiden:
   - hPanel → *Domains → Subdomains*: z. B. `neu.greenbody.de` (geht, wenn die Domain bei Hostinger liegt) **oder** eine Subdomain einer anderen Domain, die du bei Hostinger hast.
   - oder hPanel → *Website hinzufügen → „Temporäre Domain verwenden“* (kostenlose `….hostingersite.com`-Adresse).
2. hPanel → die Vorschau-Website → *Erweitert → Git*:
   - Repository: `https://github.com/harisz-commits/Greenbody.git`
   - Branch: `hostinger-preview`
   - Verzeichnis: leer lassen (= Hauptordner der Subdomain). Der Ordner muss leer sein – vorher z. B. die `default.php` löschen.
   - Da das Repo privat ist: den angezeigten SSH-Schlüssel bei GitHub unter *Repo → Settings → Deploy keys* eintragen und die SSH-Adresse `git@github.com:harisz-commits/Greenbody.git` verwenden.
3. *Auto-Deployment* einschalten und die angezeigte Webhook-URL bei GitHub unter *Repo → Settings → Webhooks* eintragen. Dann ist jede Änderung nach ca. 1 Minute online.

Wichtig: Die Seite muss im **Hauptordner einer (Sub-)Domain** liegen, nicht in einem Unterordner wie `deinedomain.de/greenbody/` – sonst stimmen die Pfade zu Bildern und CSS nicht.

### Später live gehen

1. Workflow einmal mit „live“ starten → Branch `hostinger-live` entsteht.
2. In hPanel bei der Website **greenbody.de** WordPress sichern/entfernen und Git auf Branch `hostinger-live` einrichten (wie oben).

## Was sich gegenüber WordPress geändert hat

- Alle Adressen sind gleich geblieben (`/c/…/`, `/ketose/` …) – Google-Rankings und Links bleiben erhalten. Alte Archivseiten (`/category/c/`, `/feed/`) leiten weiter.
- Neues Design mit Themenseiten (Ernährung, Keto & Low Carb, Fitness, Schlaf), Inhaltsverzeichnis, Lesezeit, ähnlichen Artikeln, Dark Mode.
- Amazon-Vergleichstabellen: statisch übernommen. Die Live-Preise des AAWP-Plugins wurden entfernt (wären sofort veraltet); die Affiliate-Links funktionieren weiter. Produktbilder werden von Amazon geladen.
- YouTube-Videos laden erst nach Klick (datenschutzfreundlich).
- Keine Cookies, kein Tracking, keine externen Schriften.
- Kommentare gibt es auf einer statischen Seite nicht mehr.
- Die leere „Sample Page“ wurde nicht übernommen.
