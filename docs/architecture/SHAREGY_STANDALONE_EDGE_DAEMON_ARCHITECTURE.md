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

## 🛠️ 5. Offizieller Hardware-Standard: Die "Sharegy Box" (DIN-Hutschiene)

> [!IMPORTANT]
> **Das offizielle Sharegy Hardware-Referenzdesign v1.0:**  
> Für Vor-Ort-Installationen im Zählerschrank (Reiheneinbau / DIN-Hutschiene) wurde das **Waveshare ESP32-S3-8DI-8Rly-POE-ETH** als primäre All-in-One-Hardware gewählt.  
> Es vereint Rechenkern, 8 isolierte Digitaleingänge (§ 14a Steuerbox), 8 Relaisausgänge (Wärmepumpe/Schütze), isoliertes RS485 (Modbus Zähler/Wechselrichter) und PoE-Ethernet in einem einzigen, installationsfertigen Hutschienengehäuse für **ca. 44 €**.

---

### 5.1. Das All-in-One Referenzgerät im Detail

```
┌────────────────────────────────────────────────────────────────────────┐
│     SHAREGY BOX v1.0: WAVESHARE ESP32-S3-8DI-8RLY-POE-ETH             │
├────────────────────────────────────────────────────────────────────────┤
│ • Prozessor: ESP32-S3 Dual-Core Xtensa LX7 (240 MHz, 8MB Flash)        │
│ • Netzwerk: 1x RJ45 Ethernet MIT PoE (IEEE 802.3af) + 2.4 GHz WiFi/BLE │
│ • Eingänge (§ 14a EnWG): 8x Optokoppler-isolierte Digitaleingänge (DI) │
│ • Ausgänge (Aktorik): 8x Relais (10A / 250V AC) für SG-Ready / Schütze │
│ • Serielle Schnittstelle: 1x galvanisch isoliertes RS485 (Modbus RTU)  │
│ • Spannungsversorgung: PoE (über LAN-Kabel) ODER 7–36V DC Schraubklem. │
│ • Montage: 35-mm DIN-Hutschiene, Klemmen oben und unten                │
│ • Bezugsquelle: Amazon.de [ASIN: B0FBKGGKK3] / BerryBase               │
│ • Stückpreis (Fabrikneu): ca. 44 €                                     │
└────────────────────────────────────────────────────────────────────────┘
```

#### Warum dieses Gerät das perfekte All-in-One-Design ist:
1. **Power over Ethernet (PoE):** Wenn ein PoE-fähiges Netzwerkkabel im Zählerschrank liegt, wird das Gerät über das LAN-Kabel mit Strom versorgt – **kein separates Netzteil nötig!**
2. **Flexible Versorgung als Backup:** Liegt kein PoE vor, lässt es sich an jedes 12V/24V-Hutschienennetzteil (z.B. MeanWell HDR-15-12) anklemmen.
3. **8x Steuerbox-Eingänge (DI):** Liest alle 4 bitcodierten Schaltstufen der FNN-Steuerbox (100%, 60%, 30%, 4,2 kW) in unter 5 Millisekunden ein.
4. **8x Relais-Ausgänge (DO):** Schaltet Wärmepumpen (SG-Ready Boost/Sperre), Heizstäbe oder Wallbox-Freigabeschütze direkt.
5. **Isoliertes RS485:** Liest Energiezähler (SDM630, Janitza) und Wechselrichter ohne teure Zusatz-Dongles aus.

---

### 5.2. Erweiterte B2B-Alternative: Waveshare CM4 Industrial Gateway

Für komplexe Großprojekte (z.B. Mehrparteienhäuser mit 50 Zählern oder lokalem Linux-Serverbedarf) steht als modulare Linux-Alternative das **Waveshare CM4 Industrial Baseboard** (mit Raspberry Pi CM4, ca. 95–110 €) bereit.

---

### 5.3. Ergänzung: Optische Zählerauslesung (m-Bus / SML am eHZ)

Für Kunden mit elektronischem Haushaltszähler (eHZ) ohne freie RS485-Klemmen:
* **BitShake SmartMeterReader / Hichi WiFi (Fabrikneu):** ca. **35 – 39 €** auf Amazon.de / eBay.
* Wird magnetisch auf die Info-Schnittstelle des Zählers geklickt und sendet 1-Sekunden-Leistungswerte direkt per LAN/WLAN an das Sharegy-Gateway.

---

### 5.4. Dauerbetriebskosten & Energieeffizienz

| Kennzahl | Wert (Waveshare ESP32-S3 PoE Controller) |
|---|---|
| **Dauerleistung im Betrieb** | **ca. 0,9 bis 1,6 Watt** |
| **Jahresenergieverbrauch (8.760 h)** | **ca. 7,9 bis 14,0 kWh / Jahr** |
| **Jährliche Stromkosten (bei 0,35 €/kWh)** | **nur ca. 2,75 € bis 4,90 € pro Jahr** |
| **Wärmeentwicklung** | Praktisch nicht spürbar, rein passive Kühlung |

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

