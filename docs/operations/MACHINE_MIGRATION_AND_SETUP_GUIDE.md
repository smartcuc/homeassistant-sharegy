# 🚚 smartEvo / Sharegy / Valofy – Arbeitsplatz-Umzugsplan & Setup-Guide

**Dokument-ID:** OPS-MIGRATION-2026-001  
**Gültig für:** Umzug auf neue Entwickler-Maschinen (Windows / Linux / macOS)  
**Letzte Aktualisierung:** 15. September 2026  

---

## 1. 📦 Übersicht der Repositories & Status

Alle Repositories der smartEvo-Produktfamilie sind zentral auf GitHub unter der Organisation **smartcuc** versioniert:

| Repository | GitHub URL | Zweck / Technologie |
| :--- | :--- | :--- |
| **Sharegy** *(ex eswes)* | https://github.com/smartcuc/sharegy.git | Dezentrale Energieplattform (Django, Next.js, Python, PostgreSQL) |
| **smartEvo Web** | https://github.com/smartcuc/smartevo-web.git | Öffentliche Website & Relaunch (Astro 5, Tailwind CSS, Cloudflare Pages) |
| **Valofy** *(ex smartVal)* | https://github.com/smartcuc/valofy.git | Industrielle Rohstoff-, Energie- & Prozessplattform (Architektur & Roadmap) |

---

## 2. 🔑 Sensible Konfigurationsdateien (.env) sichern

Folgende .env-Dateien liegen aus Sicherheitsgründen **nicht** im Git und müssen vor der Stilllegung des alten PCs gesichert werden:

* C:\Users\Public\Dev\eswes\.env
* C:\Users\Public\Dev\eswes\.env.prod
* C:\Users\Public\Dev\eswes\.env.stg
* C:\Users\Public\Dev\eswes\frontend\.env
* C:\Users\Public\Dev\eswes\stg\api\.env

> [!TIP]
> **Transfer-Tipp:** Packe diese Dateien in ein passwortgeschütztes ZIP-Archiv oder transferiere sie über deinen Passwort-Manager (z.B. Bitwarden / 1Password) auf den neuen Rechner.

---

## 3. 🤖 Antigravity AI-Skills & Konfiguration mitnehmen

Damit die AI (Antigravity) auf dem neuen Rechner sofort über das gesamte Domänenwissen, dieselben Skills, Customizations und MCP-Server verfügt:

* Sichere das gesamte Konfigurationsverzeichnis:
  📁 **C:\Users\Ruediger\.gemini\config\**
* Kopiere es auf dem neuen Rechner an denselben Speicherort:
  📁 C:\Users\<DeinBenutzername>\.gemini\config\

---

## 4. ⚡ Automatisierte Schnelleinrichtung auf dem NEUEN Rechner

Führe auf dem neuen PC folgendes Skript in der **PowerShell** (als Administrator oder Standardbenutzer) aus:

`powershell
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
# 5. .ENV-DATEIEN WIEDERHERSTELLEN
# ==============================================================================
# Kopiere nun deine gesicherten .env-Dateien in C:\Users\Public\Dev\sharegy\
`

---

## 5. 🎯 Starten & Weiterarbeiten

1. Öffne die **Antigravity IDE** auf dem neuen PC.
2. Wähle **File → Open Folder** und öffne:
   * C:\Users\Public\Dev\sharegy (für die Plattform)
   * C:\Users\Public\Dev\smartevo-web (für die Website)
   * C:\Users\Public\Dev\valofy (für die Re-Engineering Konzeption)
3. Alle Git-Branches, Remote-URLs und Commit-Historien sind sofort einsatzbereit.
