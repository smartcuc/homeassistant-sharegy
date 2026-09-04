# Sharegy UI/UX Live-Audit & Optimierungskatalog

> **Datum**: 04. September 2026  
> **Status**: Abgeschlossen (Live-Inspektion via Playwright Headless Browser)  
> **Scope**: Alle 27+ öffentlichen und internen Routen (`https://sharegy.de/`)

---

## 1. Executive Summary & Vorgehen

Die gesamte Web-Plattform wurde im Live-Betrieb automatisiert per Playwright Chromium-Headless-Runner abgefahren. Dabei wurden Full-Page-Screenshots aller öffentlichen Seiten sowie aller authentifizierten App-Seiten (unter Nutzung des Demo-User-Kontexts) erfasst und visuelle Überlappungen, Button-Duplikate, Informationshierarchien und Browser-Konsolen-Fehler systematisch erfasst.

---

## 2. Detaillierte Befunde nach Seiten

### 2.1. Dashboard (`/app/dashboard`)
* **Omi-Check Readiness-Score & Status**:
  * *Befund*: Alle 4 Kernsäulen zeigen `AKTIV ✓`, der Header-Badge meldet jedoch `70% Bereit`. Dies führt zu Verwirrung.
  * *Befund*: Bei Geräten ohne spezifischen Fehlercode wird `Störung: Gerätestörung PV Dachanlage 10 kWp meldet eine Störung (Code None)` ausgegeben.
  * *Empfehlung*: Score bei 4 aktiven Kernsäulen auf 100% setzen. Optionales Sub-Metering als getrennten Bonus ausweisen. `(Code None)` komplett unterdrücken, wenn kein Fehlercode vorliegt.
* **Echtzeit-Status Kacheln**:
  * *Befund*: Die Watt-Zahlenwerte (z. B. `1 731 00 W`, `1 953 00 W`) überlappen mit den Labels (`Bedarf`, `Erzeugung`, `Bezug`, `Laden`).
  * *Empfehlung*: Kachelhöhe und Zeilenabstände (Typography) anpassen, sodass Werte sauber unterhalb der Überschrift stehen.
* **Toggle-Buttons (Etage & Räume)**:
  * *Befund*: Am unteren rechten Rand wurden beide Filter-Toggles fälschlicherweise als `[Etagen & Räume]` betitelt (da beide denselben Lokalisierungs-Key nutzten).
  * *Lösung/Korrektur*: Präzise Einzeltitel zugeordnet: Der linke Button heißt `[🏢 Etage]` und der rechte Button heißt `[🚪 Räume]`.
* **Sidebar Badge-Overflow**:
  * *Befund*: Der `Störung`-Badge beim Menüpunkt *Installations- & Systemstatus* ragt über die Seitenleiste hinaus.
  * *Empfehlung*: Badge-Positionierung flexibel / gekürzt einbinden (`inline-flex`, kompakte Größe).

---

### 2.2. Geräteübersicht (`/app/devices`)
* **Filterleiste (Toggles für Etage & Räume)**:
  * *Befund*: Rechts neben den Status-Filter-Pills wurden beide Toggles ebenfalls mit `[Etagen & Räume]` angezeigt.
  * *Lösung/Korrektur*: Differenzierte Beschriftung: Linker Button `[🏢 Etage]`, rechter Button `[🚪 Räume]`.
* **Header-Actionbar**:
  * *Befund*: Die Buttons `[Papierkorb]`, `[Gerät entfernen]` und `[+ Gerät hinzufügen]` stehen unstrukturiert nebeneinander.
  * *Empfehlung*: Primäraktion `[+ Gerät hinzufügen]` hervorheben, Destruktiv- und Verwaltungsaktionen in ein Menü oder sekundäre Button-Gruppe bündeln.

---

### 2.3. Energiebilanz & Analyse (`/app/energy`)
* **Header-Leiste & Aktionen**:
  * *Befund*: Der Button `[📊 Erfolge teilen]` bricht unter der Datums-Auswahlleiste um und klebt an der Einleitung.
  * *Empfehlung*: `Erfolge teilen` rechtsbündig in die Filter-/Zeitraum-Toolbar integrieren.
* **Live-Energiefluss Kacheln**:
  * *Befund*: Die vier Live-Kacheln (*Photovoltaik*, *Hausverbrauch*, *Batterie*, *Netzeinspeisung*) haben am unteren Rand ein knappes Padding, sodass Labels an den Card-Rahmen stoßen.
  * *Empfehlung*: Innenabstände (`padding-bottom`) vereinheitlichen.

---

### 2.4. Solar-Prognose & Messwert-Explorer (`/app/solarforecast`, `/app/metrics`)
* **Status**: ECharts-Rendering läuft fehlerfrei und flüssig (keine `getRawIndex`-Crashes mehr).
* **Messwert-Explorer Responsive-Verbesserung**:
  * *Befund*: Filter-Pills (*Wirkleistung*, *Zählerstand*, *Netzspannung*, *Stromstärke*, *Temperatur*) brechen bei kleineren Auflösungen mehrzeilig um.
  * *Empfehlung*: Horizontale Scrollleiste (`overflow-x-auto whitespace-nowrap`) für mobile Ansichten aktivieren.

---

### 2.5. Community & Tenant Management (`/app/communities`, `/app/tenant`)
* **Empty States**:
  * *Befund*: Leermeldungen wie *„Keine aktive Energy Community“* oder *„Keine Energiegemeinschaften gefunden“* sind sehr minimalistisch und bieten wenig Führung.
  * *Empfehlung*: Moderne Empty-State-Cards mit anschaulichen Icons und klaren Call-to-Actions (z. B. `[Community gründen]`, `[Einladungscode eingeben]`, `[Demodaten laden]`).

---

### 2.6. Support & Admin-Portal (`/app/support`, `/app/admin/tracking`)
* **API-Berechtigungen & Konsole**:
  * *Befund*: Wenn ein regulärer Nicht-Admin-Benutzer die Routen aufruft, erzeugen geschützte Endpunkte HTTP 403- / 404-Fehler in der Konsole (`/api/admin/tracking/`, `/api/support/agent-tickets/`).
  * *Empfehlung*: In den React-Komponenten vor dem Absetzen der Requests prüfen, ob `user.is_staff` / entsprechende Rollen vorliegen; andernfalls freundliche Hinweiskarte statt Fehlertoast rendern.

---

### 2.7. Öffentliche Seiten & Cookie-Banner
* **Cookie-Banner**:
  * *Befund*: Das Cookie-Banner verdeckt im Ersteindruck ca. 40% des sichtbaren Bildschirms.
  * *Empfehlung*: Schlankeres Banner am unteren Bildschirmrand (Floating Bar) mit klarer *Alle akzeptieren*- und *Nur essenzielle*-Hierarchie.

---

## 3. Priorisierter Maßnahmen- & Umsetzungsplan

| Paket | Dringlichkeit | Modul / Bereich | Konkrete Maßnahmen |
|:---|:---:|:---|:---|
| **P1** | 🔴 Hoch | **Dashboard & Omi-Check** | • Score-Berechnung auf 100% bei 4 aktiven Kernsäulen anpassen<br>• Textüberlappungen in den 4 Echtzeit-Kacheln beheben<br>• `(Code None)` in Fehlertexten unterdrücken<br>• Button-Labels auf `[🏢 Etage]` und `[🚪 Räume]` korrigieren (erledigt)<br>• Sidebar-Störungsbadge layouttechnisch anpassen |
| **P2** | 🟡 Mittel | **Geräteübersicht** | • Button-Labels auf `[🏢 Etage]` und `[🚪 Räume]` korrigieren (erledigt)<br>• Header-Buttons (`Papierkorb`, `Entfernen`) gruppieren |
| **P3** | 🟡 Mittel | **Energiebilanz** | • `[Erfolge teilen]`-Button in Toolbar ausrichten<br>• Kachel-Paddings für Live-Fluss optimieren |
| **P4** | 🟢 Normal | **Empty States & Rollen-Guards** | • Onboarding-CTAs für Community- & Tenant-Leerelemente<br>• Staff-API-Calls clientseitig an Rollen binden zur Vermeidung von 403-Logs |

---

## 4. Test- & Verifikations-Setup

Die automatisierte UI-Inspektion kann jederzeit über folgendes Skript im Frontend ausgeführt werden:
```powershell
node frontend/test_ui_capture.mjs
# bzw. vollständige 27-Routen-Crawling:
node frontend/inspect_all_ui.mjs
```
Alle Screenshots werden als PNG-Dateien in der Artefakt-Ablage gespeichert.
