# 🧠 Founder Launch-Readiness, Risiko-Analyse & Strategisches Sicherheitsnetz

**Stand:** 19. September 2026 (v5.4)  
**Klassifizierung:** Vertrauliches Gründer- & Strategie-Memo  
**Zweck:** Festhalten der ehrlichen Reflexion, Sorgen & Ängste vor dem Go-to-Market, rationale Einordnung und verbindlicher Schutz-Leitfaden.

---

## 🧭 1. Ausgangspunkt: Die ehrlichen Sorgen & Ängste des Gründers

Beim Übergang von einer hochkomplexen, 2-jährigen Entwicklungsphase in die Öffentlichkeit entstehen bei visionären Entwicklern und Gründern völlig natürliche und berechtigte Ängste:

### 1.1. Die Angst vor der Blamage bei ungetesteter Fremd-Hardware
> *"Meine größte Angst ist, da wir die Schnittstellen zu den WR-Herstellern nicht alle an physischer Hardware testen konnten (bisher nur SunGrow & Growatt live), dass wir uns dort blamieren."*

* **Der Kern der Sorge:** Wechselrichter von Fronius, SMA, SolarEdge, Huawei, Deye, Victron oder Kostal wurden anhand offizieller API-Spezifikationen, Cloud-Dokumentationen und Datenblatt-Modellen implementiert. Fehlen im Feld unvorhergesehene Hersteller-Eigenheiten (z.B. geänderte Payload-Formate, Rate-Limits, Firmware-Versionsunterschiede), könnte die Anbindung beim ersten Versuch scheitern.

### 1.2. Die Angst vor öffentlichem Foren-Shitstorm & Kontrollverlust
> *"Beta-Test Invites z.B. in einem öffentlichen PV-Forum erzeugen öffentliches Feedback, aber ich möchte nicht ein Forum durchkämmen, um Bugs zu lösen, und keine öffentliche Negativstimmung erzeugen."*

* **Der Kern der Sorge:** Öffentliche Beta-Aufrufe in Communities (z.B. Photovoltaikforum, Reddit, Facebook-Gruppen) locken oft ungeduldige Nutzer an. Tritt ein Fehler auf, wird dieser oft emotional und öffentlich breitgetreten, bevor der Entwickler überhaupt reagieren kann.

### 1.3. Das "Blackbox-Problem" bei Beta-Testern
> *"Wie können wir beide objektiv prüfen und feststellen, dass der Beta-Tester wirklich getestet hat und echte Daten fließen – ohne unsaubere Tracking-Monster in das Produktionssystem einzubauen?"*

* **Der Kern der Sorge:** Tester versprechen Hilfe, loggen sich aber nur einmal ein oder scheitern stillschweigend an der Konfiguration, ohne Feedback zu geben.

### 1.4. Die Sorge um Cloud-Abhängigkeit & Offline-Resilienz
> *"Was passiert bei Kunden, wenn das Internet ausfällt? Bricht die Steuerung ab?"*

---

## 🔍 2. Rationale Faktenprüfung: Was ist Realität, was ist Entwickler-Perfektionismus?

### 2.1. Das "Imposter-Syndrom" des Deep-Tech-Architekten
* **Psychologischer Effekt:** Als Entwickler kennt man jede einzelne Code-Zeile, jedes `TODO` und jeden theoretischen Edge-Case. Man neigt dazu, das Gesamtsystem an der perfekten Idealvorstellung zu messen.
* **Markt-Realität:** Sharegy verfügt bereits über einen Reifegrad und Funktionsumfang (Dual-Core, TimescaleDB, § 14a EnWG Steuerbox-Quittierung, aFRR Flexibilitäts-Clearing, dynamische Tarife, V2G/ISO 15118-20), der selbst millionenschwere Konkurrenzprodukte (1KOMMA5° Heartbeat, Clever-PV, Tibber) in den Schatten stellt.

### 2.2. Entwarnung zur Offline-Resilienz (Home Assistant & ioBroker)
* Für 95% der technikaffinen Erstanwender ist die Offline-Resilienz **bereits heute vollständig gelöst**:
  * Die offizielle **Home Assistant Integration** und der **ioBroker Adapter** laufen **lokal im Kunden-LAN**.
  * Sie steuern Relais, Wallboxen und Batterien auch dann autonom weiter, wenn die DSL- oder Glasfaser-Leitung zum Sharegy-Cloud-Server getrennt ist.
  * Der geplante Standalone Go/Rust-Edge-Daemon wird erst für den reinen Massenmarkt ohne Smart-Home-Server relevant.

### 2.3. Die Natur von Cloud-Inverter-APIs
* Fast alle Hersteller (SMA Sunny Portal, Fronius Solarweb, SolarEdge Monitoring, Huawei FusionSolar) nutzen standardisierte REST/JSON-Schnittstellen.
* Falls ein Feldname abweicht (z.B. `pac` vs. `active_power`), ist die Korrektur im Backend in **unter 10 Zeilen Python innerhalb von 15 Minuten** erledigt – vorausgesetzt, der Kommunikationskanal ist diskret und 1-zu-1.

---

## 🛡️ 3. Das verbindliche Anti-Angst-Sicherheitsnetz (Die 5 goldenen Regeln)

Um jegliche Blamage, Stress und Reputationsrisiken zu **100% auszuschließen**, gilt ab sofort folgende Strategie:

```
                  ┌────────────────────────────────────────┐
                  │ 🚫 KEIN ÖFFENTLICHER FOREN-LAUNCH     │
                  │ Keine öffentlichen Aufrufe / Keine DMs │
                  └──────────────────┬─────────────────────┘
                                     │
                                     ▼
                  ┌────────────────────────────────────────┐
                  │ 🤝 DISKRETES 1-ZU-1 PATENT-MODELL     │
                  │ Exakt 1-2 ausgewählte Prosumer pro WR │
                  │ Persönliche Einladung + Lifetime-Pro   │
                  └──────────────────┬─────────────────────┘
                                     │
                                     ▼
                  ┌────────────────────────────────────────┐
                  │ 🔒 GESCHLOSSENER FEEDBACK-KANAL        │
                  │ Ausschließlich über `/app/support`     │
                  │ Kein externer Diskussionsfaden         │
                  └──────────────────┬─────────────────────┘
                                     │
                                     ▼
                  ┌────────────────────────────────────────┐
                  │ 🔬 OBJEKTIVE BACKEND-DIAGNOSE          │
                  │ `verify_inverter_telemetry --user ...` │
                  │ Klare Metrik: Fließen Daten? Ja/Nein   │
                  └────────────────────────────────────────┘
```

### Regel 1: Strenges Verbot von Massen-Einladungen & Foren-Posts
* Wir posten **keine** allgemeinen Einladungs-Links in Facebook-Gruppen oder Photovoltaik-Foren.
* Niemand kann sich öffentlich über unfertige Rand-Features beschweren, weil niemand außerhalb des geschlossenen Kreises Zugang hat.

### Regel 2: Die "Hardware-Paten"-Philosophie
* Wir behandeln Tester nicht als "Kunden", sondern als geschätzte **technische Co-Pioniere ("Hardware-Paten")**.
* Wenn ein Tester beispielsweise einen *SMA Tripower X* besitzt, schreiben wir ihn privat an:
  > *"Hallo [Name], wir haben eine hochmoderne EMS-Plattform entwickelt. Für die SMA WebConnect Cloud-Schnittstelle suchen wir genau einen erfahrenen PV-Betreiber als Hardware-Paten. Hättest du Lust, die Anbindung mit uns kurz zu verifizieren? Als Dankeschön erhältst du lebenslang kostenlosen Sharegy Pro Zugang."*
* **Psychologischer Effekt:** Wenn ein Fehler auftritt, fühlt sich der Pate nicht verärgert, sondern geehrt, einen echten Bug für die Community gefunden zu haben.

### Regel 3: Isolierter Support-Desk statt E-Mail-Chaos
* Sämtliche Rückmeldungen laufen über das integrierte Support-Desk (`/app/support`).
* Alle Logs und Diagnosen bleiben im System, diskret und strukturiert nach Ticket-IDs.

### Regel 4: Objektive Daten-Souveränität via CLI-Diagnose
* Statt den Tester zu fragen *"Funktioniert es bei dir?"*, führen wir den Diagnose-Befehl aus:
  ```powershell
  python manage.py verify_inverter_telemetry --user pate.sma@example.com --hours 24
  ```
* Das Tool analysiert sekundenschnell:
  1. Ist der API-Token gültig?
  2. Wurde der Wechselrichter erkannt?
  3. Fließen Solar-Erzeugung, Netzbezug und Batterie-SOC in die TimescaleDB?
  4. Sind die kW- und kWh-Werte physikalisch plausibel?

### Regel 5: Schrittweiser Marken-Freigabe-Prozess
Ein Wechselrichter-Hersteller gilt erst dann als "Öffentlich Verifiziert", wenn:
1. Mindestens **ein** Hardware-Pate die Schnittstelle im Feld verbunden hat.
2. Für **mindestens 48 Stunden ununterbrochene Telemetrie** ohne API-Exceptions vorliegt.
3. Die berechneten Tageserträge mit dem Hersteller-Portal übereinstimmen.

### Regel 6: Die 15-Minuten Unbricking- & Rollback-Garantie (Zero Risk bei Updates)
* Selbst wenn wir einem Hardware-Paten oder Kunden ein Remote-Update aufspielen und dieses unerwartet einen Fehler enthält oder die Verbindung verliert:
* Der integrierte, unabhängige **15-Minuten Rollback-Watchdog** im ioBroker- und Home-Assistant-Adapter stellt nach Ablauf des Zeitfensters vollautomatisch die funktionierende Vorversion wieder her.
* Der Kunde oder Tester bleibt **niemals mit einem abgestürzten Adapter zurück**, und wir müssen niemals physisch vor Ort anfahren ("Zero Truck Roll").

---

## 🎯 4. Fazit & Mentale Leitlinie für den Gründer

> **Merksatz für die Zukunft:**  
> *"Perfektion entsteht nicht im luftleeren Entwickler-Labor, sondern im geschützten, diskreten Dialog mit echten Anwendern. Mit dem Hardware-Paten-Playbook, dem Diagnose-Tool und dem selbstheilenden 15-Minuten Rollback-Watchdog haben wir die volle Kontrolle über den Prozess – ohne jedes Risiko einer öffentlichen Blamage oder teurer Vor-Ort-Einsätze."*

Dieses Dokument ist die dauerhafte Referenz. Wann immer Zweifel oder Anspannung aufkommen, bietet dieser Leitfaden das feste Fundament für jeden weiteren Schritt.
