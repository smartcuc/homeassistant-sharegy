# 🧪 Geschlossenes Hardware-Paten-Programm & Inverter-Diagnostik (Closed Beta Playbook)

**Dokument-Status:** Verbindlicher Operations- & Test-Leitfaden  
**Stand:** 19. September 2026 (Live v5.4)  
**Lead / Modul:** `devices`, `operations`, `support_desk`  

---

## 🎯 1. Strategischer Hintergrund & Zielsetzung

Dieses Playbook dokumentiert den **geschlossenen, diskreten 1-on-1 Hardware-Verifikations-Prozess** für Wechselrichter- und Speicher-Schnittstellen (Fronius, SMA, SolarEdge, Huawei, Deye, Hoymiles, GoodWe, Kostal, Victron).

### Warum ein geschlossener Prozess statt öffentlicher Foren-Aufrufe?
1. **Kein öffentliches Reputationsrisiko**: Keine chaotischen Foren-Threads mit vagen Fehlermeldungen („geht bei mir nicht“), die man mühsam durchforsten müsste.
2. **Sauberes Kernsystem (Zero Code Pollution)**: Keine temporären Debug-Hacks in der User-Oberfläche.
3. **Objektive Verifikation**: Wir können serverseitig in 3 Sekunden exakt nachvollziehen, ob der Tester Zugangsdaten eingegeben hat, welche Fehlercodes die Hersteller-Cloud geliefert hat und ob Messwerte in TimescaleDB fließen.
4. **Exklusivität & Loyalität**: Ausgewählte Tester fühlen sich als „VIP-Hardware-Paten“, arbeiten gerne mit dem Entwicklerteam zusammen und erhalten als Dankeschön einen lebenslangen Pro-Zugang.

---

## 🏗️ 2. Die 5 Phasen des 1-on-1 Hardware-Paten-Prozesses

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 ABLAUF DES GESCHLOSSENEN HARDWARE-LABORS                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ 1. Diskrete Auswahl & Direktnachricht (1-on-1 per E-Mail / PN)              │
│    • Gezielte Ansprache von 1–2 Personen pro Wechselrichter-Marke           │
│                                                                             │
│ 2. Bereitstellung des Zugangs auf app.sharegy.de                            │
│    • Registrierung / Freischaltung mit VIP-Pro-Status                       │
│                                                                             │
│ 3. Tester führt Onboarding-Wizard durch                                     │
│    • Eingabe der Hersteller-Zugangsdaten (API-Key / OAuth)                  │
│                                                                             │
│ 4. Serverseitige Verifikation via Diagnose-Tool                             │
│    • `python manage.py verify_inverter_telemetry --email=tester@example.com`│
│                                                                             │
│ 5. Diskrete Fehlerbereinigung über internen Support-Desk                    │
│    • Tester meldet Feedback direkt über den Support-Drawer in der App       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ✉️ 3. Vorlage für diskrete 1-on-1 Einladungen (Copy & Paste)

*Diese Nachricht kann privat per E-Mail oder persönlicher Direktnachricht (z. B. im PV-Forum / LinkedIn / WhatsApp) an 1–2 ausgewählte Anlagenbesitzer gesendet werden:*

> **Betreff / Nachricht:**  
> Hallo [Name],  
> ich entwickle mit **Sharegy** (`https://smartevo.de/sharegy`) eine herstellerunabhängige Energiemanagement- und Sharing-Plattform für PV, Speicher und dynamische Tarife.  
> 
> Wir eröffnen aktuell unser geschlossenes Hardware-Labor und suchen für **[Hersteller, z. B. Fronius Symo Gen24 / SMA Tripower / SolarEdge]** genau **eine Referenzanlage** als exklusiven Hardware-Paten.  
> 
> **Was bedeutet das für dich?**
> - Du erhältst vorab Zugang zu unserem neuen Pro-Cockpit (Live-Sankey, 4 Autopilot-Modi, § 14a Netzdrosselung, dynamische Börsentarife).
> - Direkter, persönlicher Draht zu unserem Entwicklerteam bei Fragen oder individuellen Wünschen.
> - Als Dankeschön schalten wir deinen Account **dauerhaft kostenlos auf Sharegy Pro (Lifetime)** frei.
> 
> Alles, was du tun müsstest: Dich kurz einloggen, deinen Wechselrichter über den 1-Klick Setup-Wizard verbinden und uns kurz Bescheid geben, ob die Werte sauber fließen.  
> 
> Hättest du Lust, als Referenz-Pate für [Hersteller] dabei zu sein? Wenn ja, erstelle ich dir direkt deinen persönlichen Zugang.  
> 
> Viele Grüße,  
> [Dein Name]

---

## 🔍 4. Das Diagnose-Werkzeug: `verify_inverter_telemetry`

Um jederzeit objektiv zu prüfen, was der Tester getan hat, existiert der Management-Befehl:

```bash
python manage.py verify_inverter_telemetry --email=<tester-email@example.com>
```

### Parameter:
* `--email=<email>`: Prüft alle Geräte des spezifischen Benutzers.
* `--device-id=<uuid>`: Prüft ein spezifisches Gerät.
* `--hours=6`: Prüffenster für historische Messwerte (Standard: 6 Stunden).

### Beispiel-Ausgabe des Prüfberichts:

```
======================================================================
 🔍 SHAREGY INVERTER & HARDWARE-PATEN DIAGNOSTIC INSPECTOR
======================================================================

👤 Prüfe Beta-Tester: tester-fronius@example.com (ID: 42)
📋 Gefundene Geräte zur Analyse: 1

--- Gerät: Fronius Gen24 Plus (Typ: inverter, Hersteller/Integration: fronius_solarweb) ---
   • Device-ID: dev_8f99a1b2
   • Angelegt am: 2026-09-19 14:30:00 UTC
   • Zugangsdaten hinterlegt: 🟢 JA
   • Letzter Snapshot (`DeviceLatestMetric`): 2026-09-19 14:45:12 UTC (vor 2 Minuten)
     - Leistung (W): 4850.0 W
     - Energie (kWh): 14.80 kWh
     - Spannung (V): 230.5 V
     - Strom (A): 7.02 A
   • Empfangene Zeitreihen-Messpunkte (letzte 6h): 142

   📊 Gesamt-Ergebnis: 🟢 VERIFIED & STREAMING (Tester hat erfolgreich Daten gesendet)
   💡 Diagnose: Schnittstelle funktioniert einwandfrei. Live-Telemetrie fließt stabil in die Datenbank.
======================================================================
```

---

## 🚨 5. Diagnose-Entscheidungsmatrix

| Diagnose-Status | Bedeutung | Ursache & Nächster Schritt |
|---|---|---|
| 🟢 `VERIFIED & STREAMING` | **Erfolg** | Schnittstelle funktioniert fehlerfrei im echten Betrieb. |
| 🟡 `HISTORICAL DATA PRESENT` | **Verbindung unterbrochen** | Daten kamen an, sind aber älter als 60 Min. (z. B. Wechselrichter nachts im Standby oder Token abgelaufen). |
| 🟡 `CONFIGURED BUT NO METRICS` | **Warten auf Ingest** | Zugangsdaten sind da, aber TimescaleDB ist leer. Webhook-URL, Polling-Task oder API-Key Berechtigungen prüfen. |
| 🔴 `NOT CONFIGURED` | **Tester inaktiv** | Tester hat den Account angelegt, aber den Wizard noch nicht abgeschlossen. |

---

## 🎫 6. Diskrete Fehler-Triage über den internen Support-Desk

1. Der Tester meldet Probleme nicht öffentlich, sondern klickt in Sharegy auf das Hilfesymbol (**Support-Drawer**).
2. Das Ticket landet direkt im Django Support-Desk (`/app/support` bzw. Admin-Backend).
3. Wir sehen sofort die Systemumgebung, den Inverter-Typ und den Fehlerbericht und können serverseitig nachbessern, ohne dass Außenstehende davon erfahren.

---

## 📌 7. Zusammenfassung für zukünftige Testläufe

Dieser Prozess garantiert:
- **Null Druck & absolute Diskretion**
- **Volle technische Kontrolle durch das Diagnose-Tool**
- **Schrittweise Validierung aller 10 Wechselrichter-Marken ohne Blamage-Risiko**
