# ⚡ Kurzanleitung: Demo-Daten & Hilfetexte importieren

Diese Kurzanleitung erklärt Schritt für Schritt, wie du die **Demo-Daten** (Haushalte, PV-Erzeugung, Batteriespeicher, 15m-Lastgänge, Tibber-Tarife) und die **Hilfetexte / das Wissensportal (Help Center)** in Sharegy importierst oder aktualisierst.

---

## 🚀 1. Schnellstart (In 1 Minute)

Öffne dein Terminal im Projekt-Hauptverzeichnis (`c:\Users\Public\Dev\eswes`) und führe die folgenden Befehle in deiner virtuellen Umgebung (`venv`) aus:

### 🪟 Windows (PowerShell / CMD):
```powershell
# 1. Virtuelle Umgebung aktivieren (falls noch nicht aktiv)
.\venv\Scripts\Activate.ps1

# 2. Datenbank-Migrationen sicherstellen
.\venv\Scripts\python.exe manage.py migrate

# 3. Hilfesystem & Wissensportal befüllen (DE & EN)
.\venv\Scripts\python.exe manage.py seed_helpcenter

# 4. Vollständige Demo-Umgebung neu aufbauen & mit realistischen Live-Daten befüllen
.\venv\Scripts\python.exe manage.py rebuild_demo
```

### 🐧 Linux / macOS:
```bash
source venv/bin/activate
python manage.py migrate
python manage.py seed_helpcenter
python manage.py rebuild_demo
```

---

## 📚 2. Übersicht der Import- & Seed-Befehle

| Befehl | Zweck & Inhalt | Typische Ausführungszeit |
|---|---|:---:|
| **`python manage.py seed_helpcenter`** | 📖 **Wissensportal & Hilfetexte**: Erstellt/aktualisiert alle 9 Kategorien und 12+ ausführliche Handbuch-Artikel (DE & EN) zu § 14a EnWG, 10 Wechselrichter-Clouds, OCPP-Wallboxen, wMSB & Energy Sharing. | `< 2 Sek.` |
| **`python manage.py rebuild_demo`** | 🏘️ **Gesamte Demo-Welt**: Erstellt Demo-Benutzer, Smart Home, PV-Strings, Batteriespeicher, Wallbox, Spotpreise und generiert realistische 15m-Zeitreihen. | `~ 5–10 Sek.` |
| **`python manage.py seed_device_setup`** | 🔌 **Gerätestandards & Rollen**: Richtet Standard-Gerätekategorien, Rollen und Protokolldefinitionen ein. | `< 2 Sek.` |
| **`python manage.py setup_tibber_dev`** | 💶 **Börsenstrompreise & Tibber**: Lädt aktuelle oder synthetische Day-Ahead EPEX-Spotpreise für dynamische Stromtarife. | `< 3 Sek.` |
| **`python manage.py seed_coupons`** | 🎟️ **Gutschein- & Promocodes**: Befüllt die Datenbank mit Test-Coupons (z. B. `SHAREGY100`, `PRO3M`) für das Abrechnungssystem. | `< 1 Sek.` |

---

## 🔍 3. Was wird konkret importiert?

### A. Hilfesystem (`seed_helpcenter`)
* **9 Hauptkategorien**:
  1. 🚀 Erste Schritte & Grundlagen
  2. ☀️ Erzeuger, Speicher & Wechselrichter
  3. 📈 Solar- & Lastprognose
  4. 🤖 Smart Energy Optimizer & EMS
  5. 🛡️ § 14a EnWG, Steuerbox & Netzdienlichkeit
  6. ⚡ Strompreise & Börsenstrom
  7. 🚨 Alarm- & Notifikationszentrale
  8. 🧾 Abrechnung, Mieterstrom & Energy Sharing
  9. 🔌 Geräte, Schnittstellen & Protokolle
* **Inhalte**: Vollständig zweisprachig (Deutsch & Englisch) mit Formeln, Praxis-Beispielen, Schaltplänen für Steuerboxen und Tabellen für 10 Wechselrichter-Hersteller.

### B. Demo-Daten (`rebuild_demo`)
* **Demo-Account**: Login-Daten werden im Terminal ausgegeben (z. B. `demo@sharegy.de` / `testuser`).
* **Hardware-Setup**:
  - 10.5 kWp Süddach-Photovoltaikanlage
  - 10.0 kWh Hausspeicher (LFP)
  - 11 kW OCPP 1.6-J Wallbox (Easee / openWB Simulation)
  - Wärmepumpe & smarte Haushalts-Großverbraucher
* **Telemetrie**:
  - Live-Leistungen (W), Ströme (A), Spannungen (V) und Ladestände (SoC) für das interaktive Sankey-Diagramm.
  - Revisionssichere 15-Minuten-Zeitreihen (OBIS 1.8.0 / 2.8.0) für das § 42b EnWG Quartiers-Clearing.

---

## 🛠️ 4. Fehlerbehebung & Tipps

> [!TIP]
> **Tipp 1: Hilfetexte aktualisieren ohne Datenverlust**  
> `python manage.py seed_helpcenter` verwendet `update_or_create`. Du kannst den Befehl jederzeit erneut ausführen, um überarbeitete Handbuch-Artikel einzuspielen, ohne deine bestehenden Benutzer- oder Messdaten zu überschreiben.

> [!TIP]
> **Tipp 2: Schneller Reset für Vorführungen / Demos**  
> Wenn du für eine Kundenpräsentation oder einen Investoren-Pitch eine saubere Ausgangslage benötigst, setzt `python manage.py rebuild_demo` alle Zählerstände und Graphen auf einen perfekten, sonnigen Referenztag zurück.
