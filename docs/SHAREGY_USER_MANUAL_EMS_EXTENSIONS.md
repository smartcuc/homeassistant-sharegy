# ⚡ Sharegy Prosumer EMS — Anwenderdokumentation & Handbuch der Erweiterungen

Dieses Handbuch dokumentiert alle erweiterten Funktionen des Sharegy Energy Management Systems (EMS) und der Schnittstellen-Architektur. Es richtet sich an Prosumer, Anlagenbetreiber, Installateure und WEG-Verwalter.

---

## 📑 Inhaltsverzeichnis

1. [🚗 Intelligentes EV-Laden & Abfahrtszeit-Planer (Departure Ready Planner)](#1--intelligentes-ev-laden--abfahrtszeit-planer)
2. [📊 Monatlicher Finanz- & ROI-Recap (Monatliche Ersparnis & Umweltbilanz)](#2--monatlicher-finanz---roi-recap)
3. [🌊 Live Surplus-Waterfall Kaskade (Echtzeit-Überschuss-Verteilung)](#3--live-surplus-waterfall-kaskade)
4. [🛡️ § 14a EnWG Netzdienliche Steuerung & Dimm-Konformität](#4-️-14a-enwg-netzdienliche-steuerung--dimm-konformit%C3%A4t)
5. [📡 Vollständige Schnittstellen-Übersicht (1 bis 7)](#5--vollst%C3%A4ndige-schnittstellen-%C3%BCbersicht-1-bis-7)

---

## 1. 🚗 Intelligentes EV-Laden & Abfahrtszeit-Planer

Die Sharegy Wallbox-Steuerung kombiniert PV-Überschussladung, dynamische Börsenstrompreise (EPEX Spot) und intelligente Fahrzeug-Reichweitenprognosen.

```
                  ┌──────────────────────────────────────────────────┐
                  │             Abfahrtszeit-Planer                  │
                  │   Zielzeit: 07:30 Uhr  ·  Ziel-Ladestand: 80%    │
                  └────────────────────────┬─────────────────────────┘
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    ▼                                             ▼
     ┌─────────────────────────────┐               ┌─────────────────────────────┐
     │      ☀️ PV-Überschuss       │               │   🌙 Günstigste Spotstunde  │
     │      (Kosten: 0,00 €)       │               │     (z.B. 02:00–05:00 Uhr)  │
     └─────────────────────────────┘               └─────────────────────────────┘
```

### 🎯 Kernfunktionen & Kennzahlen:
* **km-Reichweitengewinn**: Neben reinen kWh berechnet Sharegy in Echtzeit den realen Reichweitengewinn deines Elektrofahrzeugs (auf Basis des Standard-Flottenverbrauchs von $17\,\text{kWh} / 100\,\text{km}$).
  $$\text{Reichweite}\,(\text{km}) = \frac{E_\text{geladen}\,(\text{kWh})}{17\,\text{kWh}} \times 100$$
* **Fahrzeug-SoC-Schätzung**: Visuelle Batterie-Ladestandsanzeige in Prozent.
* **Abfahrtszeit-Planer**:
  1. Öffne im Dashboard oder unter *Steuerung* die Wallbox-Karte.
  2. Klicke auf **"Abfahrtszeit planen"**.
  3. Lege deine gewünschte Abfahrtszeit (z. B. `07:30 Uhr`) und deinen Ziel-SoC (z. B. `80%`) fest.
  4. Sharegy berechnet automatisch den Ladebedarf und wählt priorisiert die günstigsten Börsenstromstunden der Nacht aus, falls der PV-Ertrag des Vortages nicht ausreichte.
* **1-Klick Quick-Boost**: Mit einem Klick auf *„⚡ 1h Vollladung“* wird das Fahrzeug für 60 Minuten mit maximaler Ladeleistung (bis zu $11\,\text{kW}$ bzw. $22\,\text{kW}$) geladen, unabhängig vom aktuellen Sonnenstand.

---

## 2. 📊 Monatlicher Finanz- & ROI-Recap

Das Finanz-Recap-Modul macht den wirtschaftlichen und ökologischen Mehrwert deiner PV- und EMS-Investition transparent messbar.

### 💶 Berechnungsgrundlagen:
1. **Netto-Sparvorteil (€)**:
   Vergleicht deinen tatsächlichen Netzbezug und Eigenverbrauch mit dem regionalen Grundversorgertarif ($P_\text{Grundversorger} \approx 32{,}0\,\text{ct/kWh}$) abzüglich der entgangenen Einspeisevergütung ($P_\text{Einspeisung} \approx 8{,}2\,\text{ct/kWh}$):
   $$\text{Ersparnis} = E_\text{Eigenverbrauch} \times (P_\text{Grundversorger} - P_\text{Einspeisung}) + \text{Vorteil}_\text{Spotpreis}$$
2. **Autarkiegrad (%)**:
   Anteil deines Gesamtstrombedarfs, der direkt durch eigene Solarenergie und Batteriespeicher gedeckt wurde:
   $$\text{Autarkie} = \left( 1 - \frac{E_\text{Netzbezug}}{E_\text{Gesamtverbrauch}} \right) \times 100\%$$
3. **Eigenverbrauchsquote (%)**:
   Anteil deiner erzeugten Solarenergie, der im eigenen Haus (inkl. E-Auto & Speicher) verbraucht wurde:
   $$\text{Eigenverbrauch} = \frac{E_\text{solar\_direkt} + E_\text{batterieladung}}{E_\text{solar\_gesamt}} \times 100\%$$
4. **CO₂-Einsparung & Baum-Äquivalent**:
   Berechnet anhand des aktuellen deutschen Strommix-Emissionsfaktors ($380\,\text{g CO}_2/\text{kWh}$). Ein ausgewachsener Baum bindet ca. $20\,\text{kg CO}_2$ pro Jahr.
5. **§ 14a EnWG Netzentgelt-Vorteil**:
   Automatische Berücksichtigung der jährlichen Netzentgelt-Pauschale (Modul 1: ca. $160{,}00\,€/\text{Jahr}$).
6. **1-Klick Social Sharing**:
   Über den Button *„Ersparnis teilen“* wird eine visualisierte Grafik für WhatsApp, LinkedIn oder die Hausgemeinschaft generiert.

---

## 3. 🌊 Live Surplus-Waterfall Kaskade

Die Live Surplus-Waterfall Kaskade visualisiert auf einen Blick, wie jeder erzeugte Watt Solarstrom im Haushalt nach dem Merit-Order-Prinzip verteilt wird.

### 📐 Die Kaskaden-Reihenfolge:

```
┌────────────────────────────────────────────────────────┐
│ 1. ☀️ Solarerzeugung (PV-Generatoren & Balkonkraftwerke)│
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ 2. 🏠 Haushalts-Grundlast (Licht, Kühlschrank, IT)      │
└───────────────────────────┬────────────────────────────┘
                            │ (Verbleibender Überschuss)
                            ▼
┌────────────────────────────────────────────────────────┐
│ 3. 🔋 Batteriespeicher (Hausspeicher & DC-Speicher)    │
└───────────────────────────┬────────────────────────────┘
                            │ (Verbleibender Überschuss)
                            ▼
┌────────────────────────────────────────────────────────┐
│ 4. ♨️ Warmwasser-Wärmepumpe (SG-Ready Boost / Heizstab)│
└───────────────────────────┬────────────────────────────┘
                            │ (Verbleibender Überschuss)
                            ▼
┌────────────────────────────────────────────────────────┐
│ 5. 🚗 E-Auto Wallbox (Dynamische Überschussladung)     │
└───────────────────────────┬────────────────────────────┘
                            │ (Verbleibender Überschuss)
                            ▼
┌────────────────────────────────────────────────────────┐
│ 6. 🌐 Netzeinspeisung (Vergüteter Strom ins Netz)      │
└────────────────────────────────────────────────────────┘
```

* **Dynamische Zuteilungsbalken**: Jeder Knoten zeigt in Echtzeit den prozentualen Anteil und die Leistung in Watt an.
* **Status-Badges**: Farbige Indikatoren signalisieren sofort: *„100% Gedeckt“*, *„Lädt mit Überschuss“*, *„Gedrosselt“* oder *„Standby“*.

---

## 4. 🛡️ § 14a EnWG Netzdienliche Steuerung & Dimm-Konformität

Gemäß Festlegung BK6-22-300 der Bundesnetzagentur (BNetzA) müssen steuerbare Verbrauchseinrichtungen (SteuVE mit Netzbezug $> 4{,}2\,\text{kW}$ wie Wallboxen, Wärmepumpen und Batteriespeicher ab Inbetriebnahme 01.01.2024) im Falle einer Netzüberlastung netzdienlich gesteuert werden können.

### 🌟 Die Sharegy § 14a EnWG Lösung:
* **Keine Totalabschaltung**: Sharegy implementiert das **Summenleistungs-Dimm-Modell** (Mindestleistung $4{,}2\,\text{kW}$ je Anlage bzw. gewichtete Summe bei mehreren SteuVE).
* **PV-Kompensation**: Erzeugt deine PV-Anlage Strom, darf deine Wallbox oder Wärmepumpe mit $4{,}2\,\text{kW} + P_\text{PV}$ weiterbetrieben werden!
* **Netzentgelt-Reduktion (Modul 1 & 2)**:
  * **Modul 1**: Pauschale Reduktion des Netzentgelts um ca. **110 € bis 190 € pro Jahr** (bundesweiter Schnitt: **~160 €/a**).
  * **Modul 2**: Prozentuale Netzentgelt-Reduktion um **60%** für separate Zählpunkte.
* **Prüfprotokoll & Nachweis**: Sharegy protokolliert alle Steuersignale revisionssicher.

---

## 5. 📡 Vollständige Schnittstellen-Übersicht (1 bis 7)

Unter **Menü $\rightarrow$ Schnittstellen** (`/app/interfaces`) stehen sieben standardisierte Schnittstellen zur Verfügung:

| Nr. | Schnittstelle | Protokoll / Port | Anwendungsbereich |
| :---: | :--- | :--- | :--- |
| **1.** | **Outbound-WebSocket (Shelly WSS)** | WSS (Port 443 / TLS) | **Empfohlen**: Shelly Plus 1PM, Pro 3EM, Gen3. Funktioniert hinter jeder Fritz!Box ohne Portfreigabe. |
| **2.** | **Shelly Cloud 1-Klick Auto-Discovery** | REST API (Cloud Token) | Automatischer Import aller Shelly-Geräte aus deinem Shelly-Cloud-Konto per Knopfdruck. |
| **3.** | **Sungrow Direkt-Kopplung (SH-Serie)** | iSolarCloud API / OAuth | Hybrid-Wechselrichter (SH5.0RT bis SH25T) und SBR-Speicher. |
| **4.** | **Weitere Wechselrichter-Clouds** | Vendor Cloud APIs | SolarEdge, Fronius Solar.web, Kostal Solar Portal, Growatt ShinePhone. |
| **5.** | **Natives Home Assistant Plugin** | HACS / WebSocket Bridge | 1-Klick Entity Picker mit integriertem **48h Store-and-Forward Offline-Puffer**. |
| **6.** | **MQTT Broker Schnittstelle** | MQTT (TCP Port 1883) | Universeller IoT-Broker für ioBroker, Node-RED, Tasmota, OpenTelemetry (OTel). |
| **7.** | **Smart Meter Gateways & wMSB** | REST / MSCONS / § 42b EnWG | BSI-zertifizierte Smart Meter Gateways (inexogy, Solandeo, Discovergy) für Mieterstrom & Energy Sharing. |

---

## 💡 Support & Hilfe

Bei Fragen oder zur Unterstützung bei der Einrichtung stehen folgende Ressourcen bereit:
- **Integriertes Wissensportal**: Direkt im System unter `/app/help`.
- **Interaktiver Onboarding-Assistent**: Unter `/app/devices` $\rightarrow$ *„Gerät hinzufügen“*.
- **Community & Ticketsystem**: Unter `/app/support`.
