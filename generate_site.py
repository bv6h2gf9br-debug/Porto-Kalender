#!/usr/bin/env python3
"""
Erzeugt den Adventskalender: 48 Tagesseiten (29.8. - 15.10.), zufällige URLs,
QR-Codes zum Ausdrucken und ein privates Manifest.

WICHTIG: Vor dem finalen Ausdrucken der QR-Codes GITHUB_USERNAME und
REPO_NAME unten anpassen und das Skript erneut laufen lassen, sonst
zeigen die QR-Codes auf eine Platzhalter-URL!
"""
import csv
import datetime
import qrcode
import random
import string
from pathlib import Path

# ---- HIER ANPASSEN --------------------------------------------------
GITHUB_USERNAME = "bv6h2gf9br-debug"
REPO_NAME = "Porto-Kalender"
START_DATE = datetime.date(2026, 8, 29)
END_DATE = datetime.date(2026, 10, 15)
# -----------------------------------------------------------------------

BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"
QR_DIR = BASE_DIR / "qr-codes"
TEMPLATE = (BASE_DIR / "template.html").read_text(encoding="utf-8")

MONTHS_DE = ["Jan","Feb","Mär","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"]

def slug(n=6):
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(n))

def load_existing_slugs():
    """Liest manifest.csv, falls vorhanden, damit bestehende URLs und
    bereits hochgeladene Fotos/Videos beim erneuten Ausführen erhalten
    bleiben. Rückgabe: {tag_nummer: slug}"""
    manifest_path = BASE_DIR / "manifest.csv"
    existing = {}
    if manifest_path.exists():
        with open(manifest_path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                existing[int(row["tag"])] = row["slug"]
    return existing

def build():
    random.seed()  # echter Zufall (nur für NEUE Tage relevant)
    dates = []
    d = START_DATE
    while d <= END_DATE:
        dates.append(d)
        d += datetime.timedelta(days=1)
    total = len(dates)

    existing_slugs = load_existing_slugs()
    is_update_run = bool(existing_slugs)

    DOCS_DIR.mkdir(exist_ok=True)
    QR_DIR.mkdir(exist_ok=True)  # wird NICHT gelöscht, nur ergänzt/überschrieben

    base_url = f"https://{GITHUB_USERNAME}.github.io/{REPO_NAME}"
    manifest_rows = []

    for i, day_date in enumerate(dates, start=1):
        # bestehenden Slug wiederverwenden, falls schon einmal generiert -
        # sonst bricht die schon gedruckte/geklebte QR-Code-URL
        day_slug = existing_slugs.get(i) or f"t{i:02d}-{slug()}"
        folder = DOCS_DIR / day_slug
        folder.mkdir(parents=True, exist_ok=True)
        # Hinweis: hier wird NUR index.html geschrieben/überschrieben.
        # photo.jpg / video.mp4 / caption.txt / ort.txt bleiben unangetastet.

        days_left = (END_DATE - day_date).days
        if days_left > 0:
            headline = f"Noch {days_left} {'Tag' if days_left == 1 else 'Tage'}"
        else:
            headline = "Heute geht's los!"

        html = (TEMPLATE
                .replace("{{DAY}}", str(i))
                .replace("{{TOTAL}}", str(total))
                .replace("{{DAYS_LEFT}}", str(days_left))
                .replace("{{HEADLINE}}", headline))
        (folder / "index.html").write_text(html, encoding="utf-8")

        url = f"{base_url}/{day_slug}/"
        img = qrcode.make(url, border=2)
        img.save(QR_DIR / f"tag{i:02d}_{day_date.isoformat()}.png")

        manifest_rows.append({
            "tag": i,
            "datum": day_date.isoformat(),
            "slug": day_slug,
            "url": url,
        })

    with open(BASE_DIR / "manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["tag", "datum", "slug", "url"])
        w.writeheader()
        w.writerows(manifest_rows)

    modus = "aktualisiert (bestehende URLs & Uploads erhalten)" if is_update_run else "neu erzeugt"
    print(f"{total} Tagesseiten {modus} ({START_DATE} bis {END_DATE}).")
    print(f"Basis-URL: {base_url}")
    if GITHUB_USERNAME == "DEIN-GITHUB-USERNAME":
        print("\n⚠️  ACHTUNG: GITHUB_USERNAME ist noch nicht gesetzt!")
        print("    Die QR-Codes zeigen aktuell auf eine Platzhalter-URL.")
        print("    Trage oben deinen echten GitHub-Nutzernamen ein und führe")
        print("    das Skript erneut aus, BEVOR du die QR-Codes ausdruckst.")

if __name__ == "__main__":
    build()
