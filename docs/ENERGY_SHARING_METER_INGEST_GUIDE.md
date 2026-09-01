# Architektur & Leitfaden: Deutsches Energy Sharing & 15-Minuten-Clearing

Dieses Dokument beschreibt die eichrechtskonforme Architektur von Sharegy für Energy Sharing Communities in Deutschland nach dem Messstellenbetriebsgesetz (MsbG) und den Vorgaben der Bundesnetzagentur (BNetzA).

---

## 🏛️ 1. Regulatorisches Fundament in Deutschland (Eichrecht & MsbG)

Im deutschen Stromnetz sind für die offizielle Bilanzierung und Abrechnung von Energy Sharing über das öffentliche Verteilnetz ausschließlich **zertifizierte Smart-Meter-Gateways (iMSys)** des Messstellenbetreibers zugelassen:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                     ZULÄSSIGE ZÄHLERDATENQUELLEN NACH MSBG / BNETZA                     │
├──────────────────────────────────────────┬──────────────────────────────────────────────┤
│ 1. Wettbewerblicher Messstellenbetreiber │ • z. B. inexogy, Solandeo, Discovergy        │
│    (wMSB)                                │ • iMSys sendet 15m-Werte an MSB-Backend      │
│                                          │ • MSB pusht 15m-OBIS-JSON an Sharegy-API     │
├──────────────────────────────────────────┼──────────────────────────────────────────────┤
│ 2. Grundzuständiger Messstellenbetreiber │ • z. B. BonnNetz, Rheinische NETZ, Westnetz  │
│    (gMSB)                                │ • Auslesung der zertifizierten HAN-          │
│                                          │   Schnittstelle am iMSys nach BSI TR-03109-1 │
└──────────────────────────────────────────┴──────────────────────────────────────────────┘
```

> **Wichtig:** Private Sub-Meter oder nicht-eichrechtskonforme Lesegeräte sind für die Abrechnung im öffentlichen Netz rechtlich nicht zulässig. Grundlage sind immer die eichrechtlich gesicherten 15-Minuten-Werte für **OBIS 1.8.0** (Bezug) und **OBIS 2.8.0** (Einspeisung).

---

## 👥 2. Akteure & Rollen im Energy Sharing

* **Producer:** Speist erzeugten Solar-/Windstrom über seinen Zähler (`2.8.0`) in das öffentliche Netz ein.
* **Consumer:** Bezieht Energie aus dem Netz (`1.8.0`), aufgeteilt in Community-Sharing-Strom und Reststrom.
* **Prosumer:** Besitzt Erzeugung und Verbrauch (speist Überschuss ein, bezieht bei Bedarf aus dem Netz).
* **Reststrom-Lieferant:** Liefert und bilanziert die Reststrommenge, die die Community nicht decken kann.
* **Sharegy (Sharing-Dienstleister):** Führt die 15-Minuten-Allokation, das Clearing, die KI-Prognosen und die Abrechnungserstellung durch.

---

## ⚡ 3. 15-Minuten-Bilanzierung & Allokationsschlüssel

In jedem 15-Minuten-Slot (z. B. `14:00 - 14:15 Uhr`) führt die Sharegy-Engine folgendes Clearing durch:

1. **Summe Einspeisung ($\sum 2.8.0$):** Alle Producer & Prosumer der Community speisen z. B. $10\text{ kWh}$ ein.
2. **Summe Bezug ($\sum 1.8.0$):** Alle Consumer & Prosumer beziehen im selben Zeitraum z. B. $15\text{ kWh}$.
3. **Community-Deckung:** $10\text{ kWh}$ werden zu $100\,\%$ als Sharing-Strom im Quartier verrechnet. $5\text{ kWh}$ verbleiben als Netzbezug vom Reststrom-Lieferanten.
4. **Verteilung auf Consumer:**  
   Nach dem hinterlegten Allokationsschlüssel (dynamisch/proportional) wird der Sharing-Strom aufgeteilt:  
   *Beispiel:* Consumer A verbraucht $3\text{ kWh}$ $\rightarrow$ **$1\text{ kWh}$ von Bonn-Sharing ($z\text{ Ct/kWh}$) + $2\text{ kWh}$ vom Restversorger**.
5. **Vergütung:** Der Producer erhält für seine $10\text{ kWh}$ den vereinbarten Vergütungssatz ($z\text{ Ct/kWh}$) gutgeschrieben.

---

## 🧠 4. Prädiktive KI-Intelligenz in Sharegy

Sharegy kombiniert die exakte Abrechnung mit vorausdenkender KI-Steuerung:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 KI-FUNKTIONEN IN SHAREGY                               │
├────────────────────────────────────┬───────────────────────────────────────────────────┤
│ 1. 48h-Community-Verfügbarkeit     │ Wetter- & lastbasierte Prognose des Solarüber-    │
│                                    │ schusses in der Community für die nächsten 48h    │
├────────────────────────────────────┼───────────────────────────────────────────────────┤
│ 2. Lokale dynamische Preissignale  │ Signalisierung günstiger Sharing-Phasen an steuer-│
│                                    │ bare Verbraucher (Wallbox, Heimspeicher, WP)     │
├────────────────────────────────────┼───────────────────────────────────────────────────┤
│ 3. Fahrplan- & Portfolioprognosen  │ Unterstützung von Großverbrauchern und Speichern  │
│                                    │ zur optimalen Lastverschiebung in Sonnenstunden   │
├────────────────────────────────────┼───────────────────────────────────────────────────┤
│ 4. KI-Rechnungserläuterung         │ Verständliche Auswertung für Mitglieder:          │
│                                    │ Autarkiegrad, Ersparnis & Sharing-Nutzung in €/kWh│
└────────────────────────────────────┴───────────────────────────────────────────────────┘
```

---

## 📡 5. Einheitliche Ingest-Schnittstelle für den MSB

```json
{
  "community_id": "bonn-share",
  "timestamp": "2026-09-01T14:15:00+02:00",
  "readings": [
    {
      "meter_serial": "1EMH0012345678",
      "ts_start": "2026-09-01T14:00:00+02:00",
      "ts_end": "2026-09-01T14:15:00+02:00",
      "obis": "1.8.0",
      "value_kwh": 3.000,
      "unit": "kWh"
    },
    {
      "meter_serial": "1EMH0099887766",
      "ts_start": "2026-09-01T14:00:00+02:00",
      "ts_end": "2026-09-01T14:15:00+02:00",
      "obis": "2.8.0",
      "value_kwh": 10.000,
      "unit": "kWh"
    }
  ]
}
```
