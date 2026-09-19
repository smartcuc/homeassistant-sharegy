# 🪝 [WIP] Outbox-Pattern Webhook-Dispatcher für ERP & CRM

**Dokument-Status:** In Konzeption / Spezifikation  
**Fortschritt:** 🟡 15 %  
**Priorität:** 🔴 Hoch (B2B Stadtwerke- & Verwalter-Integration)  
**Lead / Modul:** `core/webhooks`, `billing`, `vpp`, `core/tasks`  

---

## 🎯 1. Problemstellung & Motivation

Stadtwerke, Messstellenbetreiber und Immobilienverwaltungen nutzen eigene ERP- und CRM-Systeme (SAP, DATEV Unternehmen online, Salesforce, Aareon).
Bei relevanten Plattform-Ereignissen müssen diese Systeme in Echtzeit benachrichtigt werden.
Ein **transaktionaler Outbox-Pattern Webhook-Dispatcher**:
* Verhindert Datenverlust (ACID-Garantie: Fachdaten und Webhook-Event werden in derselben DB-Transaktion gespeichert).
* Ist vollständig entkoppelt von externen Netzwerk-Latenzen oder vorübergehenden API-Ausfällen beim Partner.
* Bietet kryptografische Signierung via HMAC-SHA256 zur Absicherung vor Manipulation.

---

## 🏗️ 2. Architektur: Transaktionales Outbox-Pattern

```
┌─────────────────────────────────────────────────────────────┐
│              Sharegy Fachlogik (z. B. Billing)              │
├─────────────────────────────────────────────────────────────┤
│ 1. Transaktion öffnen (atomic)                              │
│ 2. Rechnung / 15m-Messung persistieren                      │
│ 3. `WebhookEvent` in DB-Tabelle schreiben                   │
│ 4. Transaktion committen                                    │
└──────────────────────────────┬──────────────────────────────┘
                               │ (ACID garantiert in DB)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               PostgreSQL: `core_webhookevent`               │
│ • status: 'pending'                                         │
│ • payload: JSON                                             │
│ • endpoint_url: https://partner.de/api/webhook             │
│ • secret: hmac_token                                        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼ (Celery Worker Dispatcher alle 2s)
┌─────────────────────────────────────────────────────────────┐
│                 Celery Outbox Dispatcher                    │
├─────────────────────────────────────────────────────────────┤
│ • Signiert Payload mit HMAC-SHA256 (`X-Sharegy-Signature`)  │
│ • Sendet HTTPS POST Request (Timeout: 5s)                   │
│ • Bei 2xx: status -> 'delivered'                            │
│ • Bei 4xx/5xx: Exponential Backoff (1m, 5m, 30m, 2h, 24h)   │
│ • Nach 5 Fehlschlägen: status -> 'dead_letter' & Alarmierung│
└──────────────────────────────┬──────────────────────────────┘
                               │ (HTTPS POST mit HMAC)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             B2B-Partner ERP / CRM Endpoint                  │
│             (z. B. SAP / DATEV / Salesforce)                │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 3. Unterstützte Webhook-Events & Payload-Matrix

| Event-Identifier | Auslösendes Modul | Typischer Payload-Inhalt | Anwendungsfall |
|---|---|---|---|
| `meter.reading.created` | `metering` / `energy` | Zähler-ID, Timestamp (UTC), 15m-kWh Zählerstand, PTB-Prüfstatus | Automatische Übernahme in SAP / Abrechnungssoftware |
| `invoice.issued` | `billing` | Rechnungs-Nr., Brutto-/Nettobetrag, Mandanten-ID, PDF-URL | DATEV- / Finanzbuchhaltungs-Buchungsstapel |
| `vpp.dispatch.triggered` | `vpp` | Signal-Typ (aFRR/§14a), Soll-Leistung (kW), Gültigkeitsfenster | Netzleitstellen-Synchronisation & VNB-Audit |
| `handover.completed` | `support_desk` / `devices` | Liegenschafts-ID, Seriennummern der Geräte, IBN-PDF Hash | CRM-Kundenakte des PV-Installateurs |

---

## 🔒 4. Sicherheit: HMAC-SHA256 Signatur-Verfahren

Jeder Webhook-Request enthält den Header `X-Sharegy-Signature`:
$$\text{Signature} = \text{HMAC-SHA256}(\text{Payload}_{\text{JSON}}, \text{Secret}_{\text{Webhook}})$$

Der Empfänger kann die Authentizität verifizieren:
```python
import hmac, hashlib

def verify_webhook(raw_payload_bytes, received_signature, secret_key):
    expected = hmac.new(secret_key.encode(), raw_payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", received_signature)
```

---

## 🛠️ 5. Technische Komponenten & Umsetzungsschritte

1. **Datenbank-Modelle (`core/models_webhook.py`)**:
   - `WebhookEndpoint`: Ziel-URL, Events-Filter, HMAC-Secret, Active-Flag, Tenant-Relation.
   - `WebhookDelivery`: Protokolliert Timestamp, HTTP-Statuscode, Reaktionszeit, Request/Response Payload.
2. **Celery Worker Task (`core/tasks_webhook.py`)**:
   - `dispatch_pending_webhooks()`: Verarbeitet Batches mit Retry-Backoff.
3. **Frontend Partner-Verwaltung (`frontend/src/pages/admin/WebhooksAdminPage.jsx`)**:
   - Webhook-Endpunkte anlegen, HMAC-Secret kopieren, Test-Event abfeuern und Delivery-Logs inspizieren.
