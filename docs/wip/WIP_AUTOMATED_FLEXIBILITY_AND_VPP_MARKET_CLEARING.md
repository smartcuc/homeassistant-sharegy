# 🛠️ [WIP] Automatisierter Flexibilitäts- & Regelleistungs-Handel (VPP Market Clearing)

**Status:** Teilweise vorbereitet / Phase 2 in Planung  
**Fortschritt:** 🟡 60 %  
**Priorität:** 🟡 Mittel (Ziel: Q2 / Q3 2027)  
**Lead / Modul:** `energy`, `billing`, `market`  

---

## 🎯 1. Feature-Beschreibung & Zielsetzung

Bündelung tausender dezentraler Heimspeicher, bidirektionaler Elektrofahrzeuge (V2G) und Wärmepumpen zu einem **Virtual Power Plant (VPP)** zur vollautomatischen Teilnahme an den europäischen Regelenergie- und Kurzfristmärkten:
* **Sekundärregelleistung (aFRR / SRL)**: Bereitstellung von positiver und negativer Regelleistung im 4-Sekunden-Takt zur Frequenzstabilisierung.
* **Primärregelleistung (FCR)**: Schnelle Reaktionszeit < 30 Sekunden.
* **Intraday-Arbitrage**: Automatischer Kauf/Verkauf von Batterie-Flexibilität auf der EPEX Spot Intraday-Auktion (15-Minuten-Kontrakte).
* **Automatisches Erlösausschüttungs-Clearing**: Gutschrift der Flexibilitäts-Prämien auf den Kunden-Guthabenkonten (`UserBalanceSlot`).

---

## 🏗️ 2. Architektur & Workflow

```
[Übertragungsnetzbetreiber (ÜNB) / Aggregator (z.B. Next Kraftwerke, Entelios)]
                               │
                               │ (REST / Webhook / Redispatch 2.0 PT15M)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Sharegy VPP Aggregator Engine                   │
│             (/api/vpp/flexibility/)                         │
├─────────────────────────────────────────────────────────────┤
│ • Aggregiert verfügbare Lade-/Entladekapazität (MW)         │
│ • Berechnet 96-Viertelstunden-Fahrpläne                     │
│ • Validiert Mindest-SoC der Kunden (z.B. 20% Reserve)       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Dezentrale Dispatch-Verteilung                  │
│ • Speicher-Entladung bei Netzunterdeckung (positive SRL)    │
│ • Speicher-Zwangsladung bei Überangebot (negative SRL)      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Monetäres Clearing & Payout Engine              │
│ • Erlösberechnung: Anteilige Auszahlung an Speicherbesitzer │
│ • Gutschrift auf Stromrechnung / Bankauszahlung via Stripe  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 3. Aktueller Umsetzungsstand & Delta

| Komponente | Status | Implementiert im Code | Noch zu erledigen |
|---|:---:|---|---|
| **VPP Aggregator Engine** | 🟢 100% | `/api/vpp/flexibility/` liefert Live-Flexibilität, 96-Viertelstunden-Fahrplan und Dispatch-Endpunkte. | Anbindung an Produktions-Schnittstellen der Aggregatoren. |
| **VPP Frontend Cockpit** | 🟢 100% | [`VppAggregatorCockpit.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/energy/components/VppAggregatorCockpit.jsx) mit Fahrplan-Chart und Simulator. | Historische Ertrags-Analyse im Kunden-Dashboard. |
| **Aggregator-Kopplung** | 🔴 10% | REST-Spezifikation für aFRR/FCR Schnittstellen. | B2B-Partnerschaftsvertrag mit lizenziertem Flex-Vermarkter. |
| **Erlösausschüttung** | 🟡 50% | `UserBalanceSlot` und `EMSInvoice` in `billing`. | Automatischer Split der Flex-Prämie (z.B. 80% Kunde, 20% Sharegy). |

---

## 🚀 4. Nächste Umsetzungsschritte

1. **Sprint 1**: Pilot-Partnerschaft mit einem zertifizierten Flex-Aggregator (Next Kraftwerke / EnSpire).
2. **Sprint 2**: Implementierung des automatisierten Erlös-Clearing-Jobs (`billing/tasks_vpp_clearing.py`).
3. **Sprint 3**: Endkunden-Opt-In im Dashboard: *„Am Regelleistungsmarkt teilnehmen & bis zu 250 €/Jahr extra verdienen“*.
