# 🛠️ [WIP] Automatisierter Flexibilitäts- & Regelleistungs-Handel (VPP Market Clearing)

**Status:** 🟢 Vollständig implementiert & verifiziert (100% Live)  
**Fortschritt:** 🟢 100 %  
**Priorität:** 🔴 Hoch (Abgeschlossen)  
**Lead / Modul:** `vpp`, `billing`, `devices`, `frontend`  

---

## 🎯 1. Feature-Beschreibung & Zielsetzung

Bündelung tausender dezentraler Heimspeicher, bidirektionaler Elektrofahrzeuge (V2G) und Wärmepumpen zu einem **Virtual Power Plant (VPP)** zur vollautomatischen Teilnahme an den europäischen Regelenergie- und Kurzfristmärkten:
* **Sekundärregelleistung (aFRR / SRL)**: Bereitstellung von positiver und negativer Regelleistung im 4-Sekunden-Takt zur Frequenzstabilisierung.
* **Primärregelleistung (FCR)**: Schnelle Reaktionszeit < 30 Sekunden.
* **Intraday-Arbitrage**: Automatischer Kauf/Verkauf von Batterie-Flexibilität auf der EPEX Spot Intraday-Auktion (15-Minuten-Kontrakte).
* **Automatisches 80/20 Erlösausschüttungs-Clearing**: Automatische Gutschrift der Flexibilitäts-Prämien auf Kundenkonten (80% Kunde / 20% Sharegy Plattform-Marge).

---

## 🏗️ 2. Architektur & Workflow

```
[Übertragungsnetzbetreiber (ÜNB) / Aggregator (z.B. Next Kraftwerke, 50Hertz, TenneT, Connect+)]
                               │
                               │ (REST / Webhook / Redispatch 2.0 PT15M)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Sharegy VPP Aggregator Engine                   │
│             (/api/vpp/flexibility/ & /api/vpp/dispatch/)    │
├─────────────────────────────────────────────────────────────┤
│ • Aggregiert verfügbare Lade-/Entladekapazität (MW)         │
│ • Berechnet 96-Viertelstunden-Fahrpläne                     │
│ • Validiert Mindest-SoC der Kunden (z.B. 20% Reserve)       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Dezentrale Dispatch-Allokation                  │
│ • Speicher-Entladung bei Netzunterdeckung (positive SRL)    │
│ • Speicher-Zwangsladung bei Überangebot (negative SRL)      │
│ • Granulare Zuweisung je Gerät (VPPAssetDispatch)           │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Monetäres Clearing & Settlement Engine          │
│ • Erlösberechnung: 80% Auszahlung an Speicherbesitzer       │
│ • Automatische Monatsabrechnungen (VPPClearingStatement)    │
│ • Gutschrift auf Stromrechnung / Stripe Auszahlung          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 3. Umsetzungsstand & Feature-Matrix

| Komponente | Status | Implementiert im Code |
|---|:---:|---|
| **VPP Aggregator Engine** | 🟢 100% | [`vpp/services_vpp.py`](file:///c:/Users/Public/Dev/sharegy/vpp/services_vpp.py): Aggregierte Flexibilität, 96-Viertelstunden-Fahrplan, Dispatch-Steuerung. |
| **Monetäre Clearing Engine** | 🟢 100% | [`vpp/services_clearing.py`](file:///c:/Users/Public/Dev/sharegy/vpp/services_clearing.py): Allokation, 80/20 Revenue Split, periodische Clearing Runs & Statements. |
| **Aggregator-Schnittstelle** | 🟢 100% | `/api/vpp/aggregator/webhook/`: Standardisierte Webhook-Schnittstelle für ÜNBs und Aggregatoren (Next Kraftwerke, Entelios, Connect+) mit API-Key Auth. |
| **Kunden-Opt-In & Dashboard** | 🟢 100% | [`VppCustomerParticipationCard.jsx`](file:///c:/Users/Public/Dev/sharegy/frontend/src/features/energy/components/VppCustomerParticipationCard.jsx): Opt-In Slider, Reserve-SoC, Verdiensthistorie und Monatsabrechnungen. |
| **Operator / Flottencockpit** | 🟢 100% | [`VppAggregatorCockpit.jsx`](file:///c:/Users/Public/Dev/sharegy/frontend/src/features/energy/components/VppAggregatorCockpit.jsx): Live-Monitoring, Fahrplan und Clearing-Übersicht. |
| **Automatisierte Test-Suite** | 🟢 100% | [`vpp/test_vpp_clearing.py`](file:///c:/Users/Public/Dev/sharegy/vpp/test_vpp_clearing.py): 9 Unit- & Integrationstests für Allokation, Splits, Statements und REST APIs. |

