# 🚚 smartEvo / Sharegy / Valofy / moniy – Arbeitsplatz-Umzugsplan & Setup-Guide

**Dokument-ID:** OPS-MIGRATION-2026-001  
**Gültig für:** Umzug auf neue Entwickler-Maschinen (Windows / Linux / macOS)  
**Letzte Aktualisierung:** 15. September 2026  

---

## 1. 📦 Übersicht der Repositories & Systeme

Alle Komponenten und Repositories des smartEvo-Ökosystems:

| Repository / System | GitHub URL | Zweck / Technologie |
| :--- | :--- | :--- |
| **Sharegy** *(ex eswes)* | https://github.com/smartcuc/sharegy.git | Dezentrale Energieplattform (Django, Next.js, Python, PostgreSQL) |
| **smartEvo Web** | https://github.com/smartcuc/smartevo-web.git | Öffentliche Website & Relaunch (Astro 5, Tailwind CSS, Cloudflare Pages) |
| **Valofy** *(ex smartVal)* | https://github.com/smartcuc/valofy.git | Industrielle Rohstoff-, Energie- & Prozessplattform (Architektur & Roadmap) |
| **moniy** *(Monitoring & Gateway)* | https://github.com/smartcuc/moniy.git | Reverse-RPC Gateway, WebSocket-Carrier & 5-Minuten DB-Backup-Vault (Python AsyncIO, Podman, Nginx) |

---

## 2. 🔑 Sensible Konfigurationsdateien (.env) sichern

Folgende .env-Dateien liegen aus Sicherheitsgründen **nicht** im Git und müssen vor der Stilllegung des alten PCs gesichert werden:

* `C:\Users\Public\Dev\eswes\.env` *(bzw. sharegy)*
* `C:\Users\Public\Dev\eswes\.env.prod`
* `C:\Users\Public\Dev\eswes\.env.stg`
* `C:\Users\Public\Dev\eswes\frontend\.env`
* `C:\Users\Public\Dev\eswes\stg\api\.env`
* `C:\Users\Public\Dev\moniy\.env` *(sofern vorhanden)*

> [!TIP]
> **Transfer-Tipp:** Packe diese Dateien in ein passwortgeschütztes ZIP-Archiv oder transferiere sie über deinen Passwort-Manager (z.B. Bitwarden / 1Password) auf den neuen Rechner.

---

## 3. 🤖 Antigravity AI-Skills & Konfiguration mitnehmen

Damit die AI (Antigravity) auf dem neuen Rechner sofort über das gesamte Domänenwissen, dieselben Skills, Customizations und MCP-Server verfügt:

* Sichere das gesamte Konfigurationsverzeichnis:
  📁 **`C:\Users\Ruediger\.gemini\config\`**
* Kopiere es auf dem neuen Rechner an denselben Speicherort:
  📁 `C:\Users\<DeinBenutzername>\.gemini\config\`

---

## 4. ⚡ Automatisierte Schnelleinrichtung auf dem NEUEN Rechner

Führe auf dem neuen PC folgendes Skript in der **PowerShell** (als Administrator oder Standardbenutzer) aus:

```powershell
# ==============================================================================
# 1. ENTWICKLUNGSVERZEICHNIS ANLEGEN
# ==============================================================================
New-Item -ItemType Directory -Path "C:\Users\Public\Dev" -Force
Set-Location "C:\Users\Public\Dev"

# ==============================================================================
# 2. ALLE REPOSITORIES KLONEN
# ==============================================================================
git clone https://github.com/smartcuc/sharegy.git
git clone https://github.com/smartcuc/smartevo-web.git
git clone https://github.com/smartcuc/valofy.git
git clone https://github.com/smartcuc/moniy.git

# ==============================================================================
# 3. SMARTEVO WEB INITIALISIEREN
# ==============================================================================
Set-Location "C:\Users\Public\Dev\smartevo-web"
npm install
npm run build

# ==============================================================================
# 4. SHAREGY (BACKEND & VIRTUAL ENVIRONMENT) INITIALISIEREN
# ==============================================================================
Set-Location "C:\Users\Public\Dev\sharegy"
python -m venv venv
.\venv\Scripts\Activate.ps1
# pip install -r requirements.txt

# ==============================================================================
# 5. MONIY (MONITORING & BACKUP GATEWAY) INITIALISIEREN
# ==============================================================================
Set-Location "C:\Users\Public\Dev\moniy"
python -m venv venv
.\venv\Scripts\Activate.ps1
# pip install -r requirements.txt
if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
}

# ==============================================================================
# 6. .ENV-DATEIEN WIEDERHERSTELLEN
# ==============================================================================
# Kopiere nun deine gesicherten .env-Dateien in C:\Users\Public\Dev\sharegy\ und moniy\
```

---

## 5. 🎯 Starten & Weiterarbeiten

1. Öffne die **Antigravity IDE** auf dem neuen PC.
2. Wähle **File → Open Folder** (oder füge die Workspaces hinzu):
   * `C:\Users\Public\Dev\sharegy` (für die Energieplattform)
   * `C:\Users\Public\Dev\smartevo-web` (für die smartEvo Website)
   * `C:\Users\Public\Dev\moniy` (für das Monitoring-, Gateway- & Backup-System)
   * `C:\Users\Public\Dev\valofy` (für die Re-Engineering Konzeption)
3. Alle Git-Branches, Remote-URLs und Commit-Historien sind sofort einsatzbereit.
