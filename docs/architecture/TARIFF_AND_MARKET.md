# 💶 Stromtarife, EPEX Spot Börsenpreise & Tibber-Integration

Sharegy ermöglicht die exakte monetäre Bewertung von Stromkosten und PV-Einsparungen über flexible Tarifmodelle und direkte API-Zähleranbindung.

---

## ⚡ 1. Tarifmodelle

Über die Seite **💶 Strompreise & Tarife** (`/app/tariff`) konfiguriert der Nutzer sein Abrechnungsmodell:

### A. Dynamischer Börsenstromtarif (z. B. Tibber, Rabot Charge, Ostrom)
- **Preisbasis**: Stündliche oder 15-minütige EPEX Spot Day-Ahead Börsenstrompreise.
- **Formel**:
  $$\text{Bruttopreis (ct/kWh)} = (P_\text{spot} + \sum \text{Nebenkosten}_\text{netto}) \times (1 + \frac{\text{MwSt}\%}{100})$$
- **Nebenkosten in Deutschland**:
  - Netzentgelte: ~9,50 ct/kWh
  - Stromsteuer: 2,05 ct/kWh
  - Konzessionsabgabe: 1,66 ct/kWh
  - Umlagen (KWK, §19, Offshore): ~1,57 ct/kWh
  - **Feste Nebenkosten gesamt**: ~14,78 ct/kWh netto (~17,59 ct/kWh brutto).

### B. Klassischer Festpreis-Tarif
- Konstanter Brutto-Arbeitspreis rund um die Uhr (z. B. 32,00 ct/kWh).

---

## 🔌 2. Tibber API-Integration

Sharegy kommuniziert direkt mit der Tibber GraphQL API (`https://api.tibber.com/v1-beta/gql`):
- **Token-Validierung & Home-Discovery**:
  - Endpoint `POST /api/market/tariff/tibber-homes/`
  - Ruft registrierte Adressen und Zähler-IDs live ab (`viewer { homes { id appNickname address } }`).
- **Live-Streaming**:
  - Über `integrations/live_engine.py` können Live-Messwerte des Tibber Pulse in Echtzeit gestreamt werden.
