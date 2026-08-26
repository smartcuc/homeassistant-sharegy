# Walkthrough: EMS User SaaS Subscription, Billing & Accounting System + Task 2.2 Query-Optimierung

**Datum:** 26. August 2026  
**Status:** ✅ Vollständig implementiert, getestet & verifiziert

---

## 1. Übersicht & Zielsetzung

In diesem Meilenstein wurde das duale Abrechnungs- und Accounting-Fundament von Sharegy realisiert:

1. **Säule 1 (EMS User SaaS Subscriptions)**:
   - Benutzerprofil-Erweiterung (`UserProfile.billing_name`, Firmenname, USt-IdNr, vollständige Anschrift).
   - Subscription-Lifecycle-Engine (`EMSSubscription` & `EMSInvoice`).
   - Preismodelle: **Free (0 €)**, **Pro (4,99 €/M bzw. 49,99 €/J)**, **Vermieter (14,99 €/M bzw. 149,99 €/J)** mit 17% Jahresrabatt.
   - Automatische Rechnungsgenerierung mit rechtskonformem **ReportLab A4-PDF-Download** (MwSt-Ausweis, Leistungszeitraum, fortlaufende Rechnungsnummer).
   - REST API Endpoints unter `/api/billing/subscription/` für Planwechsel, Adressaktualisierung, Kündigung und PDF-Export.
   - Moderne Frontend-Suite mit Plan-Selector, Rechnungsadresse-Editor, Rechnungsarchiv und Integration in `Sidebar.jsx`, `AppShell.jsx` und `Profile.jsx`.

2. **Säule 2 (Task 2.2 Billing-Balance Berechnung: 24.000+ Queries $\rightarrow$ 1 Query)**:
   - Eliminierung von $24.000+$ sequenziellen Slot- und Zähler-Queries in `compute_balance_range`.
   - Ersatz durch eine einzige aggregierte Django-ORM Abfrage mit bedingten `Sum(..., filter=Q(obis_code__startswith="1.8"))` und `Sum(..., filter=Q(obis_code__startswith="2.8"))`.
   - Atomares Bulk-Upsert über `BalanceSlot.objects.bulk_create(..., update_conflicts=True)`.

---

## 2. Technische Änderungen im Detail

### 2.1 Backend-Architektur (`accounts` & `billing`)

- [`accounts/models.py`](file:///c:/Users/Public/Dev/eswes/accounts/models.py): `billing_name` zu `UserProfile` hinzugefügt (Migration `0011_userprofile_billing_name`).
- [`billing/models.py`](file:///c:/Users/Public/Dev/eswes/billing/models.py): Modelle `EMSSubscription` und `EMSInvoice` erstellt (Migration `0002_emssubscription_emsinvoice_and_more`).
- [`billing/services_subscription.py`](file:///c:/Users/Public/Dev/eswes/billing/services_subscription.py):
  - `get_or_create_subscription(user)`
  - `change_subscription_plan(user, target_plan, payment_method)`
  - `update_billing_address(user, data)`
  - `cancel_subscription(user, at_period_end)` / `reactivate_subscription(user)`
  - `generate_invoice_pdf(invoice)` mit ReportLab (A4-Layout, Kopfzeile, Tabelle, Steuerberechnung 19%, Fußzeile)
  - `seed_demo_invoices(user)`
- [`billing/services_balance.py`](file:///c:/Users/Public/Dev/eswes/billing/services_balance.py):
  - Batch-Aggregation aller Zähler und 15-Minuten-Slots in 1 Query.
- [`billing/api/views.py`](file:///c:/Users/Public/Dev/eswes/billing/api/views.py) & [`billing/urls.py`](file:///c:/Users/Public/Dev/eswes/billing/urls.py):
  - `GET /api/billing/subscription/me/`
  - `POST /api/billing/subscription/update-address/`
  - `POST /api/billing/subscription/change-plan/`
  - `POST /api/billing/subscription/cancel/`
  - `POST /api/billing/subscription/reactivate/`
  - `GET /api/billing/subscription/invoices/<uuid:invoice_id>/pdf/`
  - `POST /api/billing/subscription/seed-demo/`
- [`backend/urls.py`](file:///c:/Users/Public/Dev/eswes/backend/urls.py): `path("billing/", include("billing.urls"))` unter `/api/` eingebunden.

---

### 2.2 Frontend-Komponenten

- [`frontend/src/features/billing/components/SubscriptionPlanCard.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/billing/components/SubscriptionPlanCard.jsx):
  - Monats-/Jahres-Umschalter mit 17% Sparvorteil.
  - Interaktive Tarifkarten für Free, Pro und Vermieter.
  - Live-Statusanzeige (Aktiv, Gekündigt zum Periodenende, Widerrufen).
- [`frontend/src/features/billing/components/BillingAddressCard.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/billing/components/BillingAddressCard.jsx):
  - Privatkunden- und Geschäftskundenmodus (USt-IdNr, Firmenname).
  - Live-Validierung und Speichern mit Rückmeldung.
- [`frontend/src/features/billing/components/InvoicesListCard.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/billing/components/InvoicesListCard.jsx):
  - Tabelle aller Rechnungen mit Status-Badge, Bruttobetrag und Direkt-Download-Link als PDF.
- [`frontend/src/features/billing/pages/BillingPage.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/billing/pages/BillingPage.jsx):
  - Dedizierte Hauptseite unter `/app/billing`.
- [`frontend/src/components/layout/Sidebar.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/components/layout/Sidebar.jsx):
  - Neuer Menüeintrag `💳 Abonnement & Tarife`.
- [`frontend/src/pages/Profile.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/pages/Profile.jsx):
  - Übersichtskarte mit aktuellem Plan-Status und Verlinkung zur Abrechnungsseite.

---

## 3. Verifikation & Testergebnisse

### 3.1 Backend Tests (`billing.tests`, `energy.tests`, `market.tests`)
```text
Creating test database for alias 'default'...
......................
Ran 22 tests in 38.659s

OK
Destroying test database for alias 'default'...
```

### 3.2 Frontend Production Build
```text
> vite build
vite v8.0.16 building client environment for production...
transforming...✓ 1393 modules transformed.
rendering chunks...
dist/index.html                     0.45 kB │ gzip:   0.30 kB
dist/assets/index-BoGi7J79.css    114.52 kB │ gzip:  15.73 kB
dist/assets/index-Djgw8p_Z.js   2,326.27 kB │ gzip: 701.74 kB
✓ built in 10.41s
```
