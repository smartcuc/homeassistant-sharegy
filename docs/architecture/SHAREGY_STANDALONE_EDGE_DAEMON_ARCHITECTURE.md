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

## 🛠️ 5. Realistische Hardware-Optionen & Bezugsquellen (Deutschland / DACH)

> [!NOTE]
> **Transparenz-Hinweis zur Preisgestaltung:**  
> Reine OEM-Nacktplatinen (Bare Boards) aus China (wie Orange Pi oder reine Compute-Module-Baseboards) werben oft mit 20–30 $ Herstellerpreisen. Im **deutschen Einzelhandel (Amazon.de, Reichelt, BerryBase, eBay)** kommen jedoch Gehäuse, Hutschienen-Adapter, Netzteile, Steuern und Händlermargen hinzu.  
> Nachfolgend sind ausschließlich **in Deutschland sofort lieferbare, realistische Gesamtlösungen** aufgeführt.

### 5.1. Die 4 praxiserprobten Hardware-Pfade im deutschen Markt

| Kategorie | Konkretes Produkt / Setup | Realer Endkundenpreis (DE) | Bezugsquelle | Formfaktor & Besonderheiten |
|---|---|---|---|---|
| **🥇 1. Der unzerstörbare x86 Mini-PC** *(Geheimtipp für Prosumer)* | **Fujitsu Futro S740 / HP T630** *(Refurbished)* | **ca. 35 – 55 €** *(komplett mit Netzteil & Gehäuse)* | eBay.de, Refurbished-Händler | Intel Quad-Core x86_64, 4–8 GB RAM, nativer Gigabit-LAN-Port, robuster Dauerläufer (4–5 W), passive Kühlung |
| **🥈 2. Der direkt lieferbare SBC** *(Amazon Prime)* | **Libre Computer "Le Potato" (AML-S905X-CC)** | **ca. 39 – 45 €** *(Board)* / ca. **55 €** *(mit Netzteil/Gehäuse)* | Amazon.de, BerryBase | ARM64 Quad-Core, 2 GB RAM, 100M LAN, 4x USB. Vollständiger Raspberry-Pi-Formfaktor, sofort ab deutschem Lager lieferbar |
| **🥉 3. Der Zählerschrank-Standard** *(Klassiker)* | **Raspberry Pi 4 (2 GB)** + **DIN-Rail Hutschienengehäuse** | **ca. 65 – 85 €** *(Komplettset)* | BerryBase, Reichelt, Welectron | Echter Raspberry Pi mit riesiger Community, passives Aluminium-Hutschienengehäuse für 4 TE im Verteiler |
| **⚡ 4. Plug & Play Zähler-Lesekopf** *(Für eHZ Stromzähler)* | **BitShake SmartMeterReader / Hichi WiFi** | **ca. 35 – 42 €** *(fertig mit Tasmota)* | Amazon.de, eBay.de | Magnetischer IR-Kopf mit ESP32/ESP8266. Liest SML/m-Bus Zählerdaten optisch aus und sendet per MQTT/HTTP |
| **🏢 5. Industrie-All-in-One** *(B2B / Elektriker-Zertifiziert)* | **Seeed EdgeBox-RPI-200 / Kunbus RevPi** | **ca. 280 – 450 €** | Antratek, Conrad, Reichelt | Vollständig CE/Industrie-zertifiziertes DIN-Rail-Gerät mit integriertem galvanisch getrenntem RS485, CAN & USV-Puffer |

---

### 5.2. Detail-Empfehlung: Warum der "Refurbished Thin Client" (Futro S740) oft die beste Wahl ist

Für private Prosumer und Betreiber, die keinen Raspberry Pi zur Hand haben, ist ein gebrauchter Industrie-Thin-Client (z.B. **Fujitsu Futro S740** mit Intel Celeron J4105 / J4005) die wirtschaftlichste und stabilste Lösung:
* **Komplettgerät:** Kommt ab Werk im Metallgehäuse mit 230V-Netzteil, 16–64 GB SSD und 4–8 GB DDR4-RAM (kein SD-Karten-Verschleiß!).
* **Preis:** Auf eBay permanent für **35 bis 50 €** aus Firmen-Leasingrückläufen verfügbar.
* **Leistungsaufnahme:** Zieht im Idle nur **3,5 bis 4,5 Watt** (ca. 12–15 € Stromkosten pro Jahr).
* **Betriebssystem:** Normales Debian/Ubuntu Linux x86_64 – das Sharegy Go-Binary läuft darauf mit 0,1% CPU-Last.

---

### 5.3. RS485-Schnittstellen-Adapter für Wechselrichter & Speicher

Um Wechselrichter (SMA, SolarEdge, Sungrow, Fronius) oder Stromzähler (SDM630, Janitza) per Modbus RTU anzuschließen:
* **DSD TECH SH-U10 USB-zu-RS485 Konverter (mit FTDI-Chip):** ca. **12 – 15 €** auf Amazon.de.
* **Waveshare USB to RS485 (mit galvanischer Trennung / Überspannungsschutz):** ca. **18 – 22 €** auf Amazon.de / BerryBase.

---

### 5.4. Betriebskosten & Amortisation im Dauerbetrieb (24/7)

| Setup | Dauerleistung | Verbrauch / Jahr | Stromkosten / Jahr (bei 0,35 €/kWh) |
|---|---|---|---|
| **SBC (Le Potato / Pi 4)** | ~1,8 – 2,5 W | ~16 – 22 kWh | **ca. 5,60 € – 7,70 €** |
| **Thin Client (Futro S740)** | ~3,8 – 4,5 W | ~33 – 39 kWh | **ca. 11,50 € – 13,60 €** |
| **Industrie DIN-Rail Box** | ~2,2 – 3,0 W | ~19 – 26 kWh | **ca. 6,65 € – 9,10 €** |

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

