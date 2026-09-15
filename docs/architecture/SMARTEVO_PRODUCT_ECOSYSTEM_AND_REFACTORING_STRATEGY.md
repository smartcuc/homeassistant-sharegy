# 🏛️ smartEvo Produkt-Ökosystem, Markenarchitektur & Re-Engineering Strategie

**Dokument-ID:** ARCH-STRAT-2026-001  
**Autor:** smartEvo Architektur & Produktstrategie  
**Status:** In Konzeption / Strategische Roadmap  
**Datum:** 15. September 2026  

---

## 1. 🧬 Produkt-Genealogie & Historie: Das smartVal-Erbe

`mermaid
graph TD
    SV["🏭 smartVal (smart Value)<br/><b>Industrial Energy & Resource Intelligence</b><br/>• Rohstoffbilanzen & Verbrauchs-/Produktionsoptimierung<br/>• Optimale Bestellzeitpunkte (Tagespreise & Produktionspläne)<br/>• Druck- & Temperaturkompensationen / Thermodynamik"]
    
    SV -->|"Fokus 1: Dezentrale Energie & Sharing"| SH["⚡ Sharegy<br/><i>EMS, dynamische Tarife, P2P Sharing & § 14a EnWG</i>"]
    SV -->|"Fokus 2: Kommunaler & Urbaner Zwilling"| FF["🌐 Factofy<br/><i>Digital Twin, 17 ISO 37120 Indikatoren & BI</i>"]
    
    SH -.->|"Erprobte Core-Engines & Algorithmen"| RE["🚀 Next-Gen Re-Engineering (Valofy)<br/><b>Industrial Value & Resource Platform</b>"]
    FF -.->|"Moderne Microservices, UI & Data Hub"| RE
`

### 1.1 Ursprung: Was war / ist smartVal?
**smartVal (= smart Value)** war und ist das hochgradig spezialisierte Energie- und Rohstoff-Managementsystem der smartEvo für industrielle Anwendungen:
* **Ganzheitliche Rohstoff- & Stoffstrombilanzierung:** Kontinuierliche Verfolgung und Optimierung von Material- und Massenströmen im Produktionsprozess.
* **Verbrauchs- & Produktionsoptimierung:** Dynamische Abstimmung von Fertigungsplänen mit schwankenden Energiepreisen und Anlagenauslastungen.
* **Optimale Einkaufszeitpunkte für Rohstoffe:** Algorithmische Ermittlung des kostenoptimalen Bestellzeitpunkts auf Basis von Produktionsprognosen, internen Lagerbeständen und volatilen Spot-/Tagespreisen.
* **Physikalische Messwertkorrektur:** Komplexe thermodynamische Berechnungen wie Druck- und Temperaturkompensationen für Gase, Dampf, Druckluft und Fluide.

### 1.2 Entkopplung in zwei spezialisierte SaaS-Säulen:
1. **Sharegy:** Auskopplung der dezentralen Energiemanagement-Logik (EMS), dynamischer Börsenstromtarife, § 14a EnWG Steuerbarkeit und Peer-to-Peer Energy Sharing (50 km regional, ab 2028 überregional).
2. **Factofy:** Auskopplung der sensor- und datenbasierten Monitoring- und Kennzahlensteuerung für Kommunen und Smart Cities auf Basis der 17 ISO 37120 Themenbereiche.

---

## 2. 🚀 Re-Engineering Strategie: "Das Beste aus beiden Welten vereinen"

Um den doppelten Entwicklungsaufwand zu eliminieren, wird die künftige Architektur auf einem modularen **Shared Core Engine (s&f-y Framework)** aufgebaut:

`mermaid
graph TD
    subgraph Shared Core ["🧠 s&f-y Unified Core Engine"]
        TS["Zeitreihen- & Optimierungs-Engine<br/>(Time-Series, Forecasting, Arbitrage)"]
        SM["Smart Meter & IoT Gateway Adapter<br/>(Modbus, LoRaWAN, MQTT, SMGW)"]
        SEC["KRITIS & NIS-2 Security Mesh<br/>(BSI IT-Grundschutz, Role-Based Access)"]
    end
    
    Shared Core --> SH_APP["⚡ Sharegy App (EMS & Sharing)"]
    Shared Core --> FF_APP["🌐 Factofy App (Urban Digital Twin)"]
    Shared Core --> VAL_APP["🏭 Valofy / smartVal (Industrial Resource Intelligence)"]
`

### 2.1 Wiederverwendbare Kernkomponenten:
* **Algorithmischer Kern:** Berechnungsmodelle für Peak-Shaving, flexible Speicherbeladung, Preisprognosen und Massenstrombilanzen.
* **IoT & Schnittstellen-Schicht:** Treiber für SCADA, SPS/PLC, Modbus TCP/RTU, LoRaWAN und FIWARE NGSI-LD.
* **Multimandanten- & Rechte-Isolation:** Vollständig getrennte Mandantenwelten für Stadtwerke, Kommunen, Industriebetriebe und private Gemeinschaften.

---

## 3. ⚖️ Marken- & Namensrechtliche Prüfung (Naming Candidates)

Für das Re-Engineering von smartVal wurden vier Naming-Kandidaten im Kontext der relevanten Nizza-Klassen (**Klasse 9:** Software/EMS/IoT, **Klasse 35:** Geschäftsdaten-/Einkaufsoptimierung, **Klasse 42:** SaaS/Cloud/Engineering) analysiert:

| Kandidat | Linguistischer Ursprung | Nizza-Klassen Risiko (9, 35, 42) | Bewertung & Empfehlung |
| :--- | :--- | :--- | :--- |
| **Valofy** ⭐ | *Value + Factory / Simplify* (s&f-y Brand Family) | **Sehr gering / Weitgehend frei** (Keine marktführende Software-Marke, nur Nischen-/Veranstaltungs-Tool oder Namensfunktionen ValOfY()) | **Top-Favorit:** Schließt die Markenfamilie Sharegy · Factofy · Valofy perfekt ab. |
| **smartVal OS** | *smart Value + Operating System* (Heritage) | **Frei im smartEvo-Eigentum** | **Beste B2B-Enterprise-Alternative** für klassische Industrie-Bestandskunden. |
| **Valugy** | *Value + Energy / Synergy* | **Gering** (Lediglich Holding-Name in CH/LUX, keine Softwareklasse) | Harmonisch mit *Sharegy*, aber etwas zungenbrecherischer als *Valofy*. |
| **Resofy** | *Resource + Optimize / Factory* | **Frei** (Keine relevanten Markenansprüche im IT-Bereich) | Starker Rohstoff-Fokus, aber weniger stark im "Value"-Bezug. |

---

## 4. 🏁 Strategisches Produkt-Trio der smartEvo UG

| Produkt | Domain / Positionierung | Zielgruppe |
| :--- | :--- | :--- |
| **⚡ Sharegy** | Dezentrales EMS, dynamische Tarife & P2P Energy Sharing | Privathaushalte, Liegenschaften, Quartiere & Stadtwerke |
| **🌐 Factofy** | Kommunaler Digitaler Zwilling & 17 ISO 37120 Indikatoren | Städte, Landkreise, Gemeinden & kommunale Betriebe |
| **🏭 Valofy** *(ex smartVal)* | Industrielle Rohstoff-, Energie- & Produktionsoptimierung | Verarbeitendes Gewerbe, Chemie-/Prozessindustrie, KMU |
