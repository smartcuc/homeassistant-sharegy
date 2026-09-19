# ⚡ Sharegy Local Edge Daemon (SLED): Systemarchitektur & Technologie-Entscheidung

**Stand:** 19. September 2026 (v5.4 / Enterprise & Edge Roadmap)  
**Status:** Geplante Standalone-Edge-Architektur (Target: 2027)  
**Dokument-ID:** `docs/architecture/SHAREGY_STANDALONE_EDGE_DAEMON_ARCHITECTURE.md`

---

## 🎯 1. Executive Summary & Zielsetzung

Der **Sharegy Local Edge Daemon (SLED)** ist ein autarkes, hochperformantes und ausfallsicheres Software-Binary für Vor-Ort-Hardware (z.B. Raspberry Pi, DIN-Hutschienen-Gateways, OpenWrt-Router, Industrie-Box-PCs oder BNetzA-zertifizierte Steuerbox-Rechner).

### Warum braucht Sharegy einen dedizierten Edge-Daemon?
* **Bestehende Situation:** Für Smart-Home-Power-User (ca. 95% der heutigen Erstanwender) ist die lokale Resilienz durch das offizielle **Home Assistant Add-on** und den **ioBroker Adapter** bereits gelöst.
* **Das Massenmarkt-Problem:** Endkunden ohne bestehenden Smart-Home-Server, B2B-Wohnungsgesellschaften und PV-Installateure benötigen eine **Plug-and-Play "Blackbox"** (Hutschienen-Modul oder vorkonfigurierter Dongle), die:
  1. Ohne fremde Softwareplattformen (kein HA/ioBroker) sofort nach dem Einstecken bootet.
  2. Bei totalem Internet-Ausfall **über Monate hinweg 100% autark** PV-Überschuss, Batteriespeicher und Wallbox regelt.
  3. Gesetzliche Vorgaben nach **§ 14a EnWG (Netzbetreiber-Drosselung)** und **BNetzA CLS-Steuerbox-Quittierung** mit harter Echtzeit-Garantie (< 1 Sekunde) lokal umsetzt.
  4. Telemetriedaten lokal puffert und bei wiederkehrender Verbindung verlustfrei an `sharegy.de` synchronisiert.

---

## 🔬 2. Technologie-Vergleich & Rationale: Warum Go/Rust und NICHT Python oder Node.js/TS?

Die Wahl der Programmiersprache auf Edge- und Embedded-Geräten entscheidet über Wartungskosten, Ausfallraten (MTBF), Hardware-Stückkosten und Kundenzufriedenheit.

### 2.1. Die Vier-Sprachen-Vergleichsmatrix

| Kriterium | 🐍 Python (CPython) | 🟨 Node.js / TypeScript | 🔷 Go (Golang) | 🦀 Rust |
|---|---|---|---|---|
| **RAM-Verbrauch (Baseline)** | 50 MB – 120 MB | 60 MB – 150 MB | **8 MB – 20 MB** | **2 MB – 8 MB** |
| **Startzeit / Boot-Dauer** | 2.500 ms – 5.000 ms | 1.500 ms – 3.000 ms | **30 ms – 80 ms** | **5 ms – 20 ms** |
| **Laufzeit-Umgebung (Runtime)** | Interpreter + Virtualenv + Shared Libs | V8-Engine + Node-Binary + `node_modules` | **Keine (Statisches Single-Binary)** | **Keine (Statisches Single-Binary)** |
| **Echtzeit-Verhalten & Jitter** | Schlecht (GIL + Dynamic GC Pausen) | Mäßig (V8 Garbage Collector Spikes) | **Sehr gut (< 1ms GC Latency)** | **Perfekt (Deterministisch, kein GC)** |
| **Cross-Compilation** | Komplex (OS-spezifische C-Extensions) | Fehleranfällig bei Native C++ Bindings | **Hervorragend (`GOARCH=arm` out-of-the-box)** | **Hervorragend (LLVM Cross-Targets)** |
| **Langzeit-Stabilität (MTBF > 5 Jahre)** | Risiko von Memory Leaks & Bit-Rot | GC Fragmentierung & Event-Loop Lag | **Extrem hoch (Kompakt & robust)** | **Unübertroffen (Memory- & Thread-Safe)** |
| **Hardware-Kosten pro Einheit** | Benötigt mind. 1 GB RAM Hardware | Benötigt mind. 512 MB RAM Hardware | **Läuft auf 64 MB / 128 MB RAM (5 € Chips)** | **Läuft auf 16 MB / 32 MB RAM (2 € Chips)** |

---

### 2.2. Warum scheiden Python und JavaScript/TypeScript für den Edge-Daemon aus?

#### ❌ 1. Das Problem mit Python auf Embedded-Hardware:
1. **Riesiger Memory-Footprint:** Python reserviert beim Import gängiger Bibliotheken (`requests`, `pydantic`, `pymodbus`, `cryptography`) sofort 60–100 MB RAM. Auf preiswerten Industrie-Gateways (z.B. 256 MB RAM) führt dies bei Daten-Bursts schnell zum Linux Out-Of-Memory (OOM) Killer.
2. **Dependency- und Versionshölle:** Auf Kunden-Hardware sind unterschiedliche Linux-Distributionen (Debian 10/11/12, Alpine, OpenWrt, Yocto) mit verschiedenen Python-Versionen installiert. Fehlende C-Libraries (z.B. `libffi`, `openssl-dev`) führen beim Kunden zu Installationsabbrüchen.
3. **Global Interpreter Lock (GIL) & Trägheit:** Modbus-Polling über serielle RS485-Schnittstellen erfordert präzise Taktung. Python-Interpreter-Pausen führen zu Timeouts und Paketverlusten auf dem Bus.

#### ❌ 2. Das Problem mit Node.js / TypeScript auf Embedded-Hardware:
1. **Die `node_modules`-Last:** Tausende kleine Dateien belasten langsame Flash-Speicher (eMMC/SD-Karten) und führen zu Dateisystem-Korruption bei Stromausfall.
2. **Native Bindings für Hardware:** Serielle Schnittstellen (`node-serialport`) oder RAW-Sockets kompilieren native C++-Bindings gegen die lokale `node-gyp` Umgebung. Ein Node.js-Update bricht regelmäßig die Hardware-Treiber.
3. **V8 Engine Garbage Collection:** Spontane GC-Läufe blockieren den Event-Loop für 50–200 ms, was die gesetzliche § 14a EnWG Echtzeit-Quittierung unzuverlässig macht.

---

### 2.3. Die Stärken von Go und Rust: Warum sie die perfekte Wahl sind

#### 🔷 Die Vorteile von Go (Golang) – *Der Pragmatische Allrounder*:
* **Ein einziges statisches Binary:** `CGO_ENABLED=0 go build` erzeugt eine einzige 12-MB-Datei, die absolut null Abhängigkeiten zu System-Bibliotheken hat. Läuft auf jedem Linux-Kernel ab 2012.
* **Geniale Concurrency:** Go-`goroutines` erlauben es, hunderte Modbus-Geräte, MQTT-Broker, lokale WebSockets und Cloud-Sync parallel mit minimalstem CPU-Aufwand zu betreiben.
* **Rasante Entwicklungsgeschwindigkeit:** Go lässt sich extrem schnell lesen, warten und erweitern.

#### 🦀 Die Vorteile von Rust – *Das Absolute Sicherheits- & Performance-Maximum*:
* **Kein Garbage Collector:** Speicher wird zur Kompilierzeit deterministisch freigegeben. Null Latenz-Spikes.
* **Garantierte Speichersicherheit:** Keine Pufferüberläufe, keine Null-Pointer-Crashes, keine Data-Races.
* **Microcontroller-Fähigkeit:** Rust läuft im Gegensatz zu Go auch direkt "Bare-Metal" auf Mikrocontrollern (z.B. ESP32, STM32) ohne Linux-Betriebssystem.

---

### 💡 2.4. Das finale Architektur-Urteil: Go als Host-Daemon mit optionalem Rust-Core

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SHAREGY EDGE ARCHITEKTUR-ENTSCHEIDUNG                │
├─────────────────────────────────────────────────────────────────────────┤
│  • Primäre Sprache: GO (Golang 1.23+)                                  │
│    -> Schnelle Umsetzbarkeit, exzellente Standardbibliothek (HTTP, WSS) │
│    -> Statisches Single-Binary für Linux (ARM64, ARMv7, x86_64, MIPS)   │
│    -> Footprint: ~14 MB RAM, < 0.5% CPU auf Raspberry Pi Zero 2W       │
│                                                                         │
│  • Spezifische Low-Level-Module (Optional in RUST via C-ABI/Wasm):      │
│    -> ISO 15118-20 V2G Protokoll-Parser                                 │
│    -> BNetzA FNN Steuerbox Kryptographie & CLS-Kanal                    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🏛️ 3. Gesamtsystem-Architektur des Sharegy Local Edge Daemon (SLED)

```mermaid
flowchart TB
    subgraph Local_Hardware ["Lokale Kunden-Hardware (Zählerschrank / LAN)"]
        subgraph Physical_IO ["Hardware- & Protokoll-Treiber"]
            RS485["RS485 / Modbus RTU\n(Zähler, Batterie)"]
            ModbusTCP["Ethernet / Modbus TCP\n(SMA, Fronius, Sungrow)"]
            OCPP["Wallbox (OCPP 1.6J/2.0.1)\n(Easee, go-e, Keba)"]
            Steuerbox["FNN CLS Steuerbox\n(§ 14a EnWG Relais / EEBUS)"]
        end

        subgraph SLED_Core ["Sharegy Local Edge Daemon (Go Binary)"]
            Engine["⚡ Autonomous EMS Rule Engine\n(Lokale Optimierung & Netzdrossel)"]
            Poller["🔄 Modbus & Telemetrie Poller\n(1-Sekunden-Zyklus + Deadband)"]
            RingBuffer["💾 Embedded SQLite / BadgerDB\n(30 Tage Ringspeicher Offline-Puffer)"]
            WebUI["🖥️ Local Zero-Conf Web UI\n(Port 8080 für Installateur)"]
        end
    end

    subgraph Sharegy_Cloud ["Sharegy Cloud Plattform (mon.sharegy.de)"]
        CloudWSS["🌐 WSS Sync & Reverse RPC Gateway\n(mTLS verschlüsselt)"]
        TimescaleDB["📈 TimescaleDB Ingestion"]
        MarketEngine["💰 Dynamic Tariffs & VPP Clearing"]
    end

    RS485 --> Poller
    ModbusTCP --> Poller
    OCPP <--> Engine
    Steuerbox --> Engine

    Poller --> Engine
    Engine --> RingBuffer
    Engine --> WebUI

    RingBuffer <-->|mTLS WebSocket Sync\n(Auto-Replay bei Reconnect)| CloudWSS
    CloudWSS --> TimescaleDB
    MarketEngine -.->|96h Tarif- & Fahrplan-Push| RingBuffer
```

---

## ⚙️ 4. Die 5 Kern-Module des Edge-Daemons

### 4.1. Modul 1: Ultra-Fast Hardware-Poller (Sub-Sekunden-Takt)
* Fragt lokale Smart Meter, Wechselrichter und Batteriespeicher über Modbus TCP/RTU im 1.000 ms Takt ab.
* Verwendet **Deadband-Filterung**: Nur Werte mit einer Änderung von > 0,5% oder nach Ablauf von 15 Sekunden werden verarbeitet, um CPU und Flash-Speicher zu schonen.

### 4.2. Modul 2: Lokale Autonome Rule Engine (Zero-Cloud-Dependency)
* Läuft vollständig autark ohne Internetverbindung.
* **Kernregeln:**
  1. **PV-Überschuss-Maximierung:** Batterie vorrangig laden, Wallbox stufenlos dynamisch nachführen (1p/3p Phasenumschaltung).
  2. **§ 14a EnWG Drosselschutz:** Empfängt das Signal der Netzbetreiber-Steuerbox und drosselt Wallbox/Wärmepumpe innerhalb von **< 800 Millisekunden** auf maximal 4,2 kW.
  3. **Notstrom- & Reserve-Puffer:** Hält einen konfigurierbaren Mindest-SOC der Batterie bei Unwetterwarnung oder Stromausfall.

### 4.3. Modul 3: Offline-Puffer & Ringspeicher (Zero Data-Loss)
* Speichert Telemetrie in einer integrierten, extrem leichten **SQLite**- oder **BadgerDB**-Instanz (reines Go, kein separater Datenbank-Server).
* Puffert bis zu **30 Tage hochauflösende 15-Minuten- und 1-Minuten-Lastgänge** lokal auf dem Flash-Speicher.
* Sobald die Internetverbindung wiederhergestellt ist, synchronisiert das Modul die Lücken chronologisch mit der Cloud (Auto-Replay mit Kompression).

### 4.4. Modul 4: Encrypted Cloud-Sync & Reverse-RPC
* Hält eine dauerhafte, mit **Mutual TLS (mTLS)** gesicherte WebSocket-Verbindung zu `wss://mon.sharegy.de/edge/sync`.
* Empfängt einmal täglich den **96-Stunden-Fahrplan** (dynamische Strompreise von Tibber/EPEX Spot + Solar-Ertragsprognose) von der Cloud.
* Ermöglicht Fernwartung und Firmware-Updates über sichere Reverse-RPCs, ohne dass der Kunde Ports im Router öffnen muss (NAT-Traversal).

### 4.5. Modul 5: Local Installateur Web-UI (Zero-Configuration)
* Stellt auf Port `8080` (oder via mDNS `http://sharegy.local`) eine lokale, blitzschnelle Web-Oberfläche bereit.
* Ermöglicht dem Elektriker/Installateur die Inbetriebnahme im Zählerschrank via Smartphone-WLAN – selbst im Neubau ohne aktiven Internetanschluss.

---

## 🛠️ 5. Professionelle Hardware-Lösungen für den Zählerschrank (DIN-Hutschiene)

> [!IMPORTANT]
> **Fokus auf fabrikneue, installationsfertige Zählerschrank-Hardware:**  
> Für einen professionellen Rollout (B2B, Elektro-Fachbetriebe und qualitätsbewusste Endkunden) kommen Bastellösungen oder Gebrauchtgeräte nicht infrage.  
> Die nachfolgenden **3 Neugeräte-Optionen** sind exakt für die **35-mm-DIN-Hutschiene im Zählerschrank (2 bis 4 TE)** konzipiert, besitzen alle erforderlichen Industrie-Schnittstellen (RS485, RJ45-LAN, Weitbereichs-Spannungseingang) und sind über deutsche Distributoren (BerryBase, Welectron, Reichelt, Amazon.de) sofort lieferbar.

---

### 5.1. Die 3 offiziellen Neugeräte-Standards im Überblick

| Setup | Kern-Komponenten | Formfaktor | Schnittstellen | Reale Gesamtkosten (Neu) | Bezugsquellen (DE) |
|---|---|---|---|---|---|
| **🥇 1. Der Waveshare Industrial CM4 DIN-Controller** *(Top-Standard)* | Waveshare CM4 Industrial Baseboard + Raspberry Pi CM4 (2 GB) + Metall-Hutschienengehäuse | **4 TE Hutschiene (DIN-Rail)** | 1x RS485 (galv. isoliert), 1x RJ45 Gigabit-LAN, 1x CAN-Bus, 1x RTC DS3231, 7–36V DC Eingang | **ca. 85 – 105 €** *(komplett neu)* | BerryBase, Welectron, Reichelt |
| **🥈 2. Der Raspberry Pi 4 Industrie-Hutschienen-Kit** | Raspberry Pi 4 (2 GB) + KKSB/Joy-IT Aluminium-Hutschienengehäuse + Waveshare USB-RS485 | **4 TE Hutschiene (DIN-Rail)** | 1x RJ45 Gigabit-LAN, 1x RS485 (isoliert via USB), 4x USB, 5V DC Eingang | **ca. 90 – 105 €** *(komplett neu)* | Reichelt, BerryBase, Amazon.de |
| **⚡ 3. Die reine Zählerschrank-Aktorik (DIN-Rail)** | **Shelly PRO 3EM / Shelly PRO Serie** | **1 – 3 TE Hutschiene** | 1x RJ45 LAN, 1x WiFi, 3x Stromwandler (120A), 230V AC direkt | **ca. 89 – 110 €** *(fertiges Produkt)* | Reichelt, Amazon.de, Shelly Shop |

---

### 5.2. Detail-BOM & Komponentenliste: Das Waveshare CM4 Industrial Gateway

Dieses Setup ist das **ideale "Sharegy Box" Referenzdesign** für Elektriker und Installateure:

```
┌────────────────────────────────────────────────────────────────────────┐
│        SHAREGY BOX: WAVESHARE CM4 INDUSTRIAL DIN-RAIL GATEWAY          │
├──────────────────────────────┬──────────────────────────┬──────────────┤
│ Komponente                   │ Modell / Spezifikation   │ Richtpreis   │
├──────────────────────────────┼──────────────────────────┼──────────────┤
│ 1. Trägerplatine (Baseboard) │ Waveshare CM4-IO-WIRELESS│ ca. 38 – 42 €│
│                              │ -BASE (SKU 20286 / 21303)│              │
│                              │ Inkl. RS485, CAN, RTC,   │              │
│                              │ Hutschienen-Clip & Klemmen│             │
│ 2. Rechenmodul (Compute Mod.)│ Raspberry Pi CM4 Lite    │ ca. 39 – 45 €│
│                              │ (2 GB RAM, Quad-Core A72)│              │
│ 3. Industrie-MicroSD / Flash │ SanDisk Industrial 16 GB │ ca. 8 – 10 € │
│                              │ (High-Endurance / pSLC)  │              │
│ 4. Zählerschrank-Stromvers.  │ MeanWell HDR-15-12       │ ca. 12 – 14 €│
│                              │ (12V / 1.25A Hutschiene) │              │
├──────────────────────────────┴──────────────────────────┼──────────────┤
│ GESAMT-STÜCKKOSTEN (Fabrikneues B2B-Produkt)            │ ca. 97 – 111 €│
└─────────────────────────────────────────────────────────┴──────────────┘
```

#### Warum Installateure und Kunden diese Waveshare-Lösung schätzen:
1. **Galvanisch isolierter RS485-Anschluss:** Der Schraubklemmen-Block ist optisch und galvanisch vom Rechenmodul getrennt. Eventuelle Überspannungen auf dem Buskabel zum Wechselrichter oder Speicher können das Board nicht zerstören.
2. **7–36V Weitbereichseingang:** Kann direkt an jedes vorhandene 12V- oder 24V-Hutschienennetzteil im Verteiler angeschlossen werden (keine wackeligen USB-Steckernetzteile).
3. **Integrierte DS3231 Echtzeituhr (RTC):** Garantiert sekundengenaue Tarifierung und § 14a EnWG Protokollierung selbst nach einem Netzausfall ohne NTP-Verbindung.
4. **Statisches Go-Binary:** Läuft als `systemd`-Dienst mit < 15 MB RAM und < 1% CPU-Last.

---

### 5.3. Ergänzung: Optische Zählerauslesung (m-Bus / SML am eHZ)

Für Kunden, deren Wechselrichter keine freie RS485-Klemme hat und deren Stromzähler optisch ausgelesen werden soll:
* **BitShake SmartMeterReader / Hichi WiFi (Fabrikneu):** ca. **35 – 39 €** auf Amazon.de / eBay.
* Wird magnetisch auf die Info-Schnittstelle des elektronischen Haushaltszählers (eHZ) gesetzt und liefert 1-Sekunden-Leistungswerte direkt per LAN/WLAN an das Gateway.

---

### 5.4. Dauerbetriebskosten & Energieeffizienz

| Kennzahl | Wert (Waveshare CM4 Industrial Gateway) |
|---|---|
| **Dauerleistung im Betrieb** | **ca. 1,8 bis 2,4 Watt** |
| **Jahresenergieverbrauch (8.760 h)** | **ca. 15,8 bis 21,0 kWh / Jahr** |
| **Jährliche Stromkosten (bei 0,35 €/kWh)** | **nur ca. 5,50 € bis 7,35 € pro Jahr** |
| **Wärmeentwicklung** | Minimal, rein passive Kühlung über das Metallgehäuse (kein Lüfter) |

---

## 📊 6. Ressourcen- & Performance-Ziele

| Parameter | Zielwert (Raspberry Pi Zero 2W / Industrie-Gateway) |
|---|---|
| **Binary-Größe** | < 18 MB (Statisches Go-Binary, komprimiert mit UPX: ~7 MB) |
| **RAM-Nutzung (Idle / Betrieb)** | 12 MB bis max. 25 MB RAM |
| **CPU-Last** | < 1,5% auf Single-Core ARMv7 1.0 GHz |
| **Flash-Schreibzyklen (Wear-Leveling)** | Batch-Writes alle 60 Sekunden (schont SD-Karten & eMMC) |
| **Kaltstart bis Regelbereitschaft** | < 1,2 Sekunden nach Stromzufuhr |

---

## 🗺️ 7. Roadmap & Implementierungs-Phasen

1. **Phase 1 (2026 – Jetzt):**
   - Cloud-first Architektur + Vor-Ort-Resilienz via **Home Assistant Integration** und **ioBroker Adapter** (`iobroker.sharegy`).
2. **Phase 2 (Q1–Q2 2027):**
   - Entwicklung des Core Go-Daemons (`sharegy-edge-core`), Modbus-Treiber-Suite (SunSpec, SMA, Sungrow, Fronius, Deye) und SQLite-Ringspeicher.
3. **Phase 3 (Q3 2027):**
   - BNetzA CLS / FNN Steuerbox-Zertifizierung und § 14a EnWG Hardware-Hutschienen-Paket für Installateure.
4. **Phase 4 (Q4 2027):**
   - Fertiges Sharegy OS Image (minimales Alpine/Buildroot Linux) für Hutschienen-Gateways.

---

## 📄 8. Verankerung im System
* Dokument ist dauerhaft archiviert unter [`docs/architecture/SHAREGY_STANDALONE_EDGE_DAEMON_ARCHITECTURE.md`](./SHAREGY_STANDALONE_EDGE_DAEMON_ARCHITECTURE.md).
* Referenziert im zentralen Dokumentations-Index [`docs/README.md`](../README.md).

