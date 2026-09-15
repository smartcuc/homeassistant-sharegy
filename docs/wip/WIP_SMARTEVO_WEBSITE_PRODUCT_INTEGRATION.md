# 🌐 smartEvo Produkt- & Markenintegration: Sharegy & Factofy

**Status:** 🟢 Vollständig implementiert & verifiziert (Staging Live auf Cloudflare Pages)  
**Fortschritt:** 🟢 100 % (Frontend & Architektur fertig / Go-Live via DNS-Switch auf smartevo.de vorbereitet)  
**Lead / Modul:** randing, marketing, ui/ux, stro5, cloudflare-pages  
**Repository:** [https://github.com/smartcuc/smartevo-web](https://github.com/smartcuc/smartevo-web)  
**Live Staging URL:** [https://sharegy.eu](https://sharegy.eu)  

---

## 🎯 1. Zielsetzung & Ausgangslage

Strategische, visuelle und technische Migration der Unternehmens-Website **smartEvo** von einem veralteten Joomla-CMS auf ein modernes, ultra-performantes statisches Framework (**Astro 5 + Tailwind CSS**), gehostet auf **Cloudflare Pages**.

### Erreichte Kernziele:
* **Radikale Entrümpelung & Performance**: Ladezeiten unter **800 ms**, Wegfall des obsoleten Bereichs *„Bildung / Corona-Schulungsangebote / JFK-Zitat“*, Eliminierung von Tracking-Bloat und Cookie-Bannern.
* **Klarer Fokus auf das Kerngeschäft**:
  1. **smartEvo**: Etablierte B2B-Dachmarke für Technologie, KRITIS-Sicherheitsberatung und nachhaltige Stadtentwicklung.
  2. **Sharegy**: Dezentrale Energieplattform für EMS, dynamische Börsenstromtarife, § 14a EnWG und **Peer-to-Peer Energy Sharing** (50-km-Radius & Doppel-Ertrag).
  3. **Factofy**: Faktenbasierte Daten- und Digital-Twin-Plattform für Kommunen nach dem **ISO 37120 Standard** (Nachfolger von smartVAL).
  4. **Solarenergie**: Schlüsselfertige PV-Komplettsysteme mit interaktivem Ertragsrechner als Hardware-Fundament.
* **Flache, moderne URL-Architektur**: Vollständige Abschaffung des alten Joomla-Präfixes /dienstleistungen/.

---

## 🎨 2. Design-System & CI-Konformität

| Design-Element | Spezifikation | Verwendung |
|---|---|---|
| **Primary Accent** | #1CC5D9 (Electric Cyan / Teal) | CTA-Buttons, Icons, Feature-Highlights, Badges |
| **Dark Primary** | #062F32 (Deep Petrol Slate) | Dunkle Hero-Hintergründe, Header-Akzente, Primary Cards |
| **Dark Secondary** | #042022 / #0A474D (Deep Teal Dark) | Footer, Sektions-Hintergründe, Contrast Cards |
| **Success / Energy Accent** | #10B981 / #34D399 (Emerald) | Sharegy Plattform-Highlights, Ertrags-Badges |
| **Headings Font** | Poppins, sans-serif (700 / 800) | H1–H4 Überschriften, Brand-Logo, Buttons |
| **Body Font** | Work Sans, sans-serif (400 / 500) | Fließtexte, Leistungsbeschreibungen, Tabellen |
| **Favicon** | Custom Vector SVG (#062F32 Squircle + sE. Monogramm) | Gestochen scharf auf allen Geräten & Apple Touch |

---

## 🏗️ 3. Marken- & Navigations-Architektur

`
                       ┌──────────────────────────────┐
                       │           smartEvo           │
                       │   (Dachmarke & Consulting)   │
                       └──────────────┬───────────────┘
                                      │
            ┌─────────────────────────┴─────────────────────────┐
            ▼                                                   ▼
┌──────────────────────────────┐            ┌──────────────────────────────┐
│           Sharegy            │            │           Factofy            │
│  Die Energie- & Sharing-     │            │   Der Kommunale Digitale     │
│  Plattform (EMS, Börsentarif,│            │   Zwilling & 17 ISO 37120    │
│  § 14a, P2P Energy Sharing)  │            │   Indikatoren (ex smartVAL)  │
└──────────────────────────────┘            └──────────────────────────────┘
`

### Finale Menüstruktur in der TopNav:
1. **Home** (/)
2. **⚡ Sharegy** (/sharegy $\rightarrow$ Interne Produktseite & Link zu sharegy.de)
3. **🌐 Factofy** (/factofy $\rightarrow$ Interne Produktseite & Link zu actofy.de)
4. **🛡️ KRITIS** (/kritische-infrastrukturen $\rightarrow$ NIS-2 & BSI IT-Grundschutz)
5. **🏙️ Stadtentwicklung** (/stadtentwicklung $\rightarrow$ Strategie & ISO 37120)
6. **📡 Smart City** (/smart-city $\rightarrow$ LoRaWAN & Urbane Datenräume)
7. **☀️ Solarenergie** (/solarenergie $\rightarrow$ PV-Pakete & Rechner)
8. **Über Uns** (/ueber-uns)
9. **Erstberatung vereinbaren →** (/kontakt $\rightarrow$ Rechter CTA-Button)

---

## 📄 4. Struktur der 11 statischen Routen

| Route | Inhalt & Highlights | Status |
|---|---|:---:|
| / | Hero mit Real-Image-Overlay, 6 interaktive 3D-FlipCards, Spotlights für Sharegy & Factofy, Partnerlogos | ✅ Live |
| /sharegy | EMS, dynamische Börsentarife, § 14a EnWG und **Energy-Sharing Deep-Dive** mit Doppel-Ertragsmodell | ✅ Live |
| /factofy | 6 Kernmodule für Kommunen, 17 ISO 37120 Themenkatalog, Digitaler Zwilling | ✅ Live |
| /kritische-infrastrukturen | NIS-2 Betreiberpflichten, BSI IT-Grundschutz, IEC 62443 OT-Sicherheit | ✅ Live |
| /stadtentwicklung | Strategische Stadtentwicklungsberatung harmonisiert mit den 17 ISO 37120 Indikatoren | ✅ Live |
| /smart-city | LoRaWAN Funknetzwerke, Sensorik, FIWARE Urbane Datenplattformen | ✅ Live |
| /solarenergie | 3 Komplettpakete (5 / 10 / 20+ kWp), interaktiver Solar- & Ersparnisrechner, Lead-Formular | ✅ Live |
| /ueber-uns | Unternehmensprofil, Wesseling am Rhein, Vision & Werte | ✅ Live |
| /kontakt | Ansprechpartner, optimiertes Dropdown (Sharegy/Factofy oben), Terminanfrage | ✅ Live |
| /impressum | Rechtskonformes Impressum der smartEvo UG (haftungsbeschränkt), Wesseling | ✅ Live |
| /datenschutz | DSGVO-konforme Datenschutzerklärung (cookiefrei, ohne Drittanbieter-Tracker) | ✅ Live |

---

## 🚀 5. Nächster Schritt: Finale Domain-Aufschaltung (Go-Live)

Sobald der offizielle Wechsel der Hauptdomain **smartevo.de** erfolgen soll:
1. In Cloudflare Pages unter *Custom Domains* smartevo.de und www.smartevo.de hinterlegen.
2. DNS-Einträge (CNAME / ALIAS) beim Domain-Registrar auf Cloudflare Pages zeigen lassen.
3. Die Seite schaltet sofort ohne Ausfallzeit auf das neue System um.
