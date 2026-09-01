# Praxis-Leitfaden: Zähleranbindung & 15-Minuten-Messwertübermittlung (Punkt 3.3)

Dieser Leitfaden beschreibt detailliert, wie Zählerdaten (OBIS `1.8.0` Bezug und `2.8.0` Einspeisung) von Messstellenbetreibern (MSB), Smart-Meter-Gateways (iMSys) und Sub-Metern im 15-Minuten-Raster an Sharegy übermittelt werden.

---

## 🧭 Die 3 Wege zur Zählerübermittlung in der Praxis

Je nach Ausgangslage vor Ort gibt es in Deutschland drei praxiserprobte Wege:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               3 WEGE DER ZÄHLERANBINDUNG                                │
├────────────────────────────┬────────────────────────────┬───────────────────────────────┤
│ WEG A: Lokale Gateways &   │ WEG B: Wettbewerblicher    │ WEG C: Grundzuständiger       │
│ Sub-Metering (Kundennetz)  │ Messstellenbetreiber (wMSB)│ Messstellenbetreiber (gMSB)   │
├────────────────────────────┼────────────────────────────┼───────────────────────────────┤
│ • Shelly Pro 3EM / Modbus  │ • z. B. inexogy, Solandeo, │ • z. B. BonnNetz, Rheinische  │
│ • Optische IR-Leseköpfe    │   Discovergy               │   NETZGesellschaft, Westnetz  │
│ • Übermittlung: Push-HTTP  │ • Übermittlung: Cloud-API  │ • Übermittlung: Lokale HAN-   │
│   direkt vom Gebäude       │   Webhook (MSB -> Sharegy) │   Schnittstelle am iMSys      │
│ • 🚀 Sofort einsatzbereit  │ • ⚡ Voll digital          │ • 📜 Nach BSI TR-03109-1      │
└────────────────────────────┴────────────────────────────┴───────────────────────────────┘
```

---

## 🛠️ Detaillierte Vorgehensweise für die 3 Wege

---

### Weg A: Lokale Gateways & IR-Leseköpfe (Schnellster & günstigster Weg)
*Ideal für: Mehrfamilienhäuser, private Quartiere, WEGs und Kundenanlagen (§ 42b EnWG)*

1. **Hardware vor Ort:**
   * Jeder Haushalt in Deutschland besitzt bereits eine moderne Messeinrichtung (mME, digitaler Zähler mit Display).
   * Auf die optische D0/SML-Schnittstelle wird ein magnetischer **Infrarot-Lesekopf** (z. B. Hichi IR mit Tasmota/WiFi, ca. 20–25 €) aufgesetzt.
   * *Alternativ:* Fest installierte Hutschienen-Zähler (z. B. Shelly Pro 3EM, Eastron SDM630 mit Modbus).
2. **Datenabruf:**
   * Der IR-Lesekopf liest den SML-Datenstrom des Zählers im Sekundentakt lokal aus.
3. **Pushtakt an Sharegy:**
   * Das Gerät oder ein kleiner lokaler Controller (z. B. ESP32 oder Home Assistant) puffert die 15-Minuten-Werte und sendet alle 15 Minuten einen HTTPS-POST an Sharegy:
   ```bash
   POST https://api.sharegy.de/api/v1/ingest/meters/
   Header: Authorization: Bearer <COMMUNITY_API_KEY>
   ```

---

### Weg B: Wettbewerblicher Messstellenbetreiber (wMSB) – z. B. inexogy / Solandeo
*Ideal für: Offizielles bundesweites Energy Sharing über das öffentliche Netz*

1. **Beauftragung des wMSB:**
   * Der Anlagenbetreiber oder die Community beauftragt einen wettbewerblichen MSB (z. B. Solandeo, inexogy, Discovergy).
   * Der wMSB tauscht die alten Zähler gegen eichrechtskonforme Smart-Meter-Gateways (iMSys) mit eigener LTE-Mobilfunkanbindung aus.
2. **Datenauslesung durch den wMSB:**
   * Der wMSB liest die Gateways über seinen zertifizierten Backend-Server (BSI-konform) alle 15 Minuten aus.
3. **Automatische Weiterleitung an Sharegy:**
   * Der wMSB richtet einen **automatischen Webhook / API-Push** ein, der die 15-Minuten-Werte direkt als JSON an Sharegy übermittelt.
   * *Alternativ:* Sharegy pollt die REST-API des wMSB alle 15 Minuten.

---

### Weg C: Grundzuständiger Messstellenbetreiber (gMSB, z. B. BonnNetz)
*Ideal für: Haushalte, die bereits ein iMSys vom lokalen Netzbetreiber erhalten haben*

1. **Freischaltung der HAN-Schnittstelle:**
   * Gesetzlich hat jeder Anschlussnutzer nach § 61 MsbG das Recht, die Daten aus seinem Smart-Meter-Gateway (SMGW) lokal über die **HAN-Schnittstelle (Home Area Network / Ethernet/WLAN)** auszulesen.
2. **Lokaler Connect-Agent:**
   * Ein leichtgewichtiger Sharegy-Connect-Dienst (z. B. als Home-Assistant-Plugin, Docker-Container oder Python-Script) verbindet sich lokal mit dem Gateway.
3. **Übermittlung an Sharegy:**
   * Der Connect-Agent sendet die signierten 15-Minuten-Datensätze an den Sharegy Ingestion-Endpoint.

---

## 📡 Einheitliches Schnittstellenformat für Sharegy (API-Spezifikation)

Egal welcher der 3 Wege genutzt wird – an Sharegy wird immer dasselbe schlanke JSON-Format übermittelt:

### `POST /api/v1/ingest/meters/`
```json
{
  "community_id": "bonn-nord-sonne",
  "timestamp": "2026-09-01T14:15:00+02:00",
  "readings": [
    {
      "meter_serial": "1EMH0012345678",
      "ts_start": "2026-09-01T14:00:00+02:00",
      "ts_end": "2026-09-01T14:15:00+02:00",
      "obis": "1.8.0",
      "value_kwh": 0.420,
      "unit": "kWh"
    },
    {
      "meter_serial": "1EMH0012345678",
      "ts_start": "2026-09-01T14:00:00+02:00",
      "ts_end": "2026-09-01T14:15:00+02:00",
      "obis": "2.8.0",
      "value_kwh": 1.250,
      "unit": "kWh"
    }
  ]
}
```

---

## 🛡️ Was Sharegy automatisch übernimmt:
1. **Deduplizierung & Plausibilität:** Erkennt Doppelübertragungen, fehlerhafte Negativwerte und Ausreißer.
2. **Late-Arrivals-Pufferung:** Fällt das Internet für 24 Stunden aus, werden nachgelieferte Werte rückwirkend in die Bilanzen eingerechnet (`recalculate_late_slot`).
3. **Tenant-Sicherheit:** Nur autorisierte Zähler der jeweiligen Community werden akzeptiert.
