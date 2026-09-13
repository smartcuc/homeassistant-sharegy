# 🌐 [WIP] smartEvo.de Produkt- & Markenintegration: Sharegy & Factofy

**Status:** In Konzeption / Freigegeben  
**Fortschritt:** 🟡 25 %  
**Priorität:** 🔴 Hoch (Ziel: Q4 2026 / Go-To-Market)  
**Lead / Modul:** `branding`, `marketing`, `ui/ux`, `cms`  

---

## 🎯 1. Zielsetzung & Ausgangslage

Strategische und visuelle Integration der beiden Kernprodukte **Sharegy** (Energiemanagement, HEMS & Energy-Sharing) und **Factofy** (Faktenbasierte B2B-Daten- & Monitoring-Plattform) auf der Unternehmens-Website **[www.smartEvo.de](https://www.smartevo.de)**.

### Leitprinzipien:
* **Zero Design-Bruch**: 100 % nahtlose Fortführung des bestehenden smartEvo Design-Systems (Shaper Wayne Corp / SP PageBuilder, Farbschema Cyan `#1CC5D9` & Deep Petrol `#062F32`, Typografie Poppins & Work Sans).
* **Entrümpelung & Schärfung**: Vollständige Entfernung des obsoleten Bereichs *„Bildung / Corona-Schulungsangebote“* und Zusammenfassung redundanter Stadtentwicklungs-Blöcke.
* **Klarer Dreiklang**:
  1. **smartEvo** als etablierte B2B-Dachmarke (Strategie, KRITIS, IT-Sicherheitsgesetz, Smart City).
  2. **Sharegy** als dezentrale Energie-, HEMS- & Mieterstrom-Plattform.
  3. **Factofy** als faktenbasierte Monitoring-, Audit- & Entscheidungsplattform (Nachfolger von smartVAL).

---

## 🎨 2. Design-System & Styleguide-Konformität

| Design-Element | Wert / Spezifikation | Verwendung auf smartEvo.de |
|---|---|---|
| **Primary Accent** | `#1CC5D9` (Electric Cyan / Teal) | CTA-Buttons, Icons, Feature-Highlights, Badges |
| **Dark Primary** | `#062F32` (Deep Petrol Slate) | Dunkle Hero-Hintergründe, Header-Akzente, Primary Cards |
| **Dark Secondary** | `#252A35` / `#171717` (Charcoal) | Footer, Top-Bar, Secondary Cards |
| **Text Primary** | `#FFFFFF` (White) / `#252525` (Off-Black) | Kontraststarke Überschriften & Fließtexte |
| **Headings Font** | `Poppins, sans-serif` | H1–H4 Überschriften, Banner-Texte, Navigation |
| **Body Font** | `Work Sans, sans-serif` | Paragraphen, Leistungsbeschreibungen, Tooltips |

---

## 🏗️ 3. Marken- & Navigations-Architektur

```
                       ┌──────────────────────────────┐
                       │           smartEvo           │
                       │   (Dachmarke & Consulting)   │
                       └──────────────┬───────────────┘
                                      │
            ┌─────────────────────────┴─────────────────────────┐
            ▼                                                   ▼
┌──────────────────────────────┐            ┌──────────────────────────────┐
│           Sharegy            │            │           Factofy            │
│  Die Energie- & Sharing-     │            │   Die faktenbasierte Daten-  │
│  Plattform (HEMS, Solar,     │            │   & Monitoring-Plattform     │
│  § 14a, Mieterstrom, Pro)    │            │   (B2B, Smart City, Audits)  │
└──────────────────────────────┘            └──────────────────────────────┘
```

### Menüstruktur im Header (Desktop & Mobile Drawer):
1. **Home** (`/`)
2. **Sharegy** (`/sharegy` $\rightarrow$ Teaser & Weiterleitung zu `sharegy.de`)
3. **Factofy** (`/factofy` $\rightarrow$ Teaser & Nachfolger von smartVAL)
4. **Kritische Infrastrukturen** (`/dienstleistungen/kritische-infrastrukturen`)
5. **Smart City & Quartiere** (`/dienstleistungen/smart-city`)
6. **Über Uns** (`/ueber-uns`)
7. **Kontakt** (`/kontakt`)

---

## 📄 4. Detaillierter Seitenaufbau (Homepage Sektion für Sektion)

### Sektion 1: Hero Banner (Top of Page)
* **Überschrift (H1)**: `Business re-defined`
* **Sub-Headline (H2)**: *„Premiumlösungen für Unternehmenserfolg, Dekarbonisierung & faktenbasierte Transformation.“*
* **Call-to-Action Buttons (Duo)**:
  * `[⚡ Sharegy entdecken]` (Button: Leuchtendes Cyan `#1CC5D9`, Text: `#062F32`)
  * `[📊 Factofy kennenlernen]` (Button: Outlined Border Weiß / Cyan Hover)

---

### Sektion 2: 3-Spalten-Vorteilsmatrix („Nur das Beste für Ihren Erfolg“)
*Ersetzt die alte Aufteilung Stadtentwicklung / Bildung / Unternehmen:*

1. **⚡ Kachel 1: Sharegy (Energie & HEMS)**
   * *Icon*: Flash / Solar / Energy Flow (`#1CC5D9`)
   * *Text*: *„Dezentrale Energiewende, intelligentes HEMS, dynamische Tarife und lokales Energy-Sharing für Ein- & Mehrfamilienhäuser sowie Gewerbe.“*
   * *Link*: `Zu Sharegy →`
2. **📊 Kachel 2: Factofy (Fakten & Monitoring)**
   * *Icon*: Chart-Line / Data / Analytics (`#1CC5D9`)
   * *Text*: *„Das smarte Cockpit für faktenbasierte Unternehmens- und Liegenschaftsführung. Visualisierung, Trendanalysen und automatisierte Berichte.“*
   * *Link*: `Zu Factofy →`
3. **🔒 Kachel 3: smartEvo Consulting (KRITIS & IT-Sicherheit)**
   * *Icon*: Shield-Check / Server / Lock (`#1CC5D9`)
   * *Text*: *„Ganzheitliche Absicherung und Beratung für Betreiber kritischer Infrastrukturen nach IT-Sicherheitsgesetz & ISO 37120.“*
   * *Link*: `Zu den Dienstleistungen →`

---

### Sektion 3: Factofy Produkt-Spotlight (Ersetzt smartVAL)
* **Layout**: 2-Spaltig (Links: Interaktive Dashboard-Mockup-Grafik / Rechts: Leistungsmerkmale)
* **Titel (H2)**: `Factofy – Fakten statt Bauchgefühl`
* **Text**: *„Verlässliche Entscheidungen auf Basis von Echzeitdaten. Factofy vereint heterogene Datenquellen in einem zentralen Managementsystem – inklusive automatisierter Berechnungen, Trendprognosen und Audit-Reports.“*
* **USPs**:
  * ✅ Live-Visualisierung von KPIs & Betriebsparametern
  * ✅ Automatisierte Auswertungen & Berichterstellung
  * ✅ Nahtlose API- & Sensor-Integration (IoT, Modbus, MQTT)

---

### Sektion 4: Sharegy Produkt-Spotlight (Ersetzt Solarenergie)
* **Layout**: 2-Spaltig (Links: Leistungsmerkmale / Rechts: Sharegy Glassmorphism HEMS App Mockup)
* **Titel (H2)**: `Sharegy – Die vernetzte Energiezukunft`
* **Text**: *„Verbinden Sie Photovoltaik, Speicher, Wärmepumpen und Wallboxen zu einem intelligenten, autarken Gesamtsystem. Mit dynamischen Stromtarifen, § 14a EnWG Sektorkopplung und dezentralem Energy-Sharing.“*
* **USPs**:
  * ✅ Multi-Hersteller-Unterstützung (Sungrow, Growatt, Fronius, SMA, Victron u.v.m.)
  * ✅ Intelligenter Autopilot für Börsenstrom-Tiefstpreise & Peak-Shaving
  * ✅ Mieterstrom & P2P-Sharing für Quartiere und Liegenschaften

---

### Sektion 5: Kritische Infrastrukturen & Smart City
* **Status**: Beibehalten und als Fundament für Großkunden & Stadtwerke positionieren.
* **Inhalt**: IT-Sicherheitsgesetz, BSI-Konformität, ISO 37120 Smart City Zertifizierung.

---

### Sektion 6: Streichliste (Was entfällt)
* ❌ **Bildungswesen-Block** (*„John F. Kennedy Zitat / Es gibt nur eine Sache auf der Welt, die teurer ist als Bildung...“*) $\rightarrow$ **Vollständig entfernen**.
* ❌ **smartVAL Einzelmodul** $\rightarrow$ Geht nahtlos in **Factofy** auf.

---

## 📊 5. Roadmap & Umsetzungsschritte

| Schritt | Maßnahme | Tool / Ort | Status |
|---|---|---|:---:|
| **1. Text- & Bild-Assets** | Erstellung der Screenshots & Mockups für Sharegy & Factofy im smartEvo Cyan-Look | Figma / Photoshop | ⚪ Ausstehend |
| **2. Header-Navigation** | Umbenennung & Verlinkung der Menüpunkte im Joomla MegaMenu | Joomla Backend | ⚪ Ausstehend |
| **3. Home-Layout Update** | Austausch der PageBuilder-Zeilen (Factofy & Sharegy rein, Bildung raus) | SP PageBuilder | ⚪ Ausstehend |
| **4. Landingpages** | Bereitstellung der Sub-Pages `/sharegy` und `/factofy` mit Produktübersicht | SP PageBuilder | ⚪ Ausstehend |
| **5. Cross-Linking** | Verlinkung von Sharegy.de & Factofy.de zurück auf smartEvo UG als Betreiber | Frontend Config | ⚪ Ausstehend |
