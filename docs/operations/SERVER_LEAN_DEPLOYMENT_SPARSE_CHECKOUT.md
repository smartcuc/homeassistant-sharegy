# ⚡ Sharegy Server Lean Deployment: Git Sparse-Checkout

Dieser Leitfaden beschreibt, wie auf dem Produktionsserver ausschließlich die **laufzeitrelevanten Backend-Verzeichnisse** ausgecheckt werden, um Speicherplatz zu sparen, `git pull` zu beschleunigen und unnötige Verzeichnisse (wie `docs/`, `android/`, `frontend/src/`, `scratch/`) vom Server fernzuhalten.

---

## 1. Was wird auf dem Server benötigt?

| Verzeichnis / Datei | Auf Server benötigt? | Zweck |
| :--- | :---: | :--- |
| `backend/`, `core/`, `accounts/` | ✅ **JA** | Django Core & Business Logik |
| `devices/`, `energy/`, `billing/` | ✅ **JA** | Telemetrie, EMS-Optimierer, Abrechnung |
| `market/`, `notifications/`, `alerts/` | ✅ **JA** | Strompreis-Radar, Push, Hardware-Alarm |
| `support_desk/`, `operations/` | ✅ **JA** | Support Desk & Infrastruktur-Status |
| `templates/` | ✅ **JA** | E-Mail-Templates (HTML & TXT) |
| `scripts/` | ✅ **JA** | Backup & Wartungsskripte |
| `manage.py`, `requirements.txt` | ✅ **JA** | Django Management & Abhängigkeiten |
| `frontend/dist/` | ✅ **JA** | Kompilierte Frontend-Assets für Nginx |
| `frontend/src/`, `node_modules/` | ❌ **NEIN** | Nur für den Build-Prozess nötig |
| `docs/`, `android/`, `scratch/` | ❌ **NEIN** | Dokumentation & Mobile App Source |

---

## 2. Einmalige Einrichtung auf dem Server (Sparse-Checkout)

Führe diese Befehle im Projektverzeichnis auf dem Server aus:

```bash
cd /opt/sharegy/eswes  # bzw. dein lokaler Pfad

# 1. Sparse-Checkout initialisieren
git sparse-checkout init --cone

# 2. Nur die benötigten Verzeichnisse abonnieren
git sparse-checkout set accounts backend billing core devices energy market notifications alerts support_desk operations templates scripts frontend/dist

# 3. Checkout aktualisieren
git checkout main
```

Ab diesem Moment enthält das Verzeichnis auf dem Server **nur noch die definierten Ordner**. Verzeichnisse wie `docs/`, `android/` oder `frontend/src/` werden bei jedem künftigen `git pull` automatisch ignoriert.

---

## 3. Workflow für Updates (`deploy.sh`)

Erstelle auf dem Server ein einfaches Skript `/opt/sharegy/deploy.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 [1/4] Git Pull (Sparse Lean)..."
cd /opt/sharegy/eswes
git pull origin main

echo "🐍 [2/4] Python Migrationen & Collectstatic..."
source /opt/sharegy/venv/bin/activate
python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "🔄 [3/4] Gunicorn / Services neu starten..."
sudo systemctl restart gunicorn
sudo systemctl restart sharegy-worker  # falls Celery/DTS im Einsatz

echo "✅ [4/4] Deployment erfolgreich abgeschlossen!"
```

Ausführbar machen:
```bash
chmod +x /opt/sharegy/deploy.sh
```

---

## 4. Wie aktualisiere ich das Frontend?

Das Frontend wird lokal auf dem Entwicklungs-PC gebaut (`npm run build`) und der erzeugte Ordner `frontend/dist` committet/deployed oder direkt per SCP/Rsync übertragen:

```bash
# Auf dem Dev-PC:
cd frontend
npm run build
```

Nginx auf dem Server liefert statisch direkt aus `/opt/sharegy/eswes/frontend/dist` aus.
