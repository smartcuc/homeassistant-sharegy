# 🎫 Helpdesk & Ticketing Modul — Vollständige Dokumentation

> **Modul:** `support_desk`  
> **Letzte Aktualisierung:** 2026-08-28  
> **Projekte:** Sharegy HEMS · Factofy Digital Twin (Cross-Project)

---

## Inhaltsverzeichnis

1. [Überblick & Architektur](#1-überblick--architektur)
2. [Backend-Konfiguration (Erstinstallation)](#2-backend-konfiguration-erstinstallation)
3. [Django Admin — Was konfiguriert werden muss](#3-django-admin--was-konfiguriert-werden-muss)
4. [API-Referenz](#4-api-referenz)
5. [Frontend-Komponenten](#5-frontend-komponenten)
6. [Authentifizierung & Berechtigungen](#6-authentifizierung--berechtigungen)
7. [Deflection (FAQ-Vorschläge)](#7-deflection-faq-vorschläge)
8. [Canned Responses (Textbausteine)](#8-canned-responses-textbausteine)
9. [Ticket-Nummernschema](#9-ticket-nummernschema)
10. [Factofy-Integration](#10-factofy-integration)
11. [Produktionsbetrieb & Checkliste](#11-produktionsbetrieb--checkliste)

---

## 1. Überblick & Architektur

Das `support_desk`-Modul ist ein universelles Helpdesk- und Ticketsystem, das für **mehrere Projekte gleichzeitig** betrieben werden kann. Sharegy und Factofy teilen sich **ein einziges Backend**, jedoch mit:

- Projektspezifischen **Ticket-Präfixen** (`SHAR-2026-0001`, `FACT-2026-0042`)
- Projektspezifischen **JWT-Secrets** für externe Authentifizierung
- Einem gemeinsamen **Agent Hub** für das Support-Team

### Komponentenübersicht

```
FRONTEND (React)
  Topbar [🛟-Button] ──► SupportDrawer
                             ├── Tab: Neues Ticket (Formular + Deflection)
                             ├── Tab: Meine Tickets (Liste)
                             └── Tab: Wissensportal
                          ↓ Klick auf Ticket
                         TicketChatModal (Thread + Status-Toggle)

  AgentSupportHubPage (/app/support-hub) — nur Staff
    ├── KPI-Grid (Neue/Offene/In Bearbeitung/Gelöst)
    ├── Filter (Projekt · Status · Suche)
    ├── Ticket-Liste (links)
    └── Chat-Thread mit internen Notizen (rechts)

BACKEND (Django) — /api/support/ & /api/help/
  support_desk/api/
    ├── views.py                  (Tickets, Messages, Agent Hub Triage)
    ├── views_help.py             (Wissensportal: Kategorien, Artikel, Feedback)
    ├── urls.py                   (/api/support/)
    └── urls_help.py              (/api/help/)

  support_desk/services/
    ├── ticket_engine.py          (Ticket-Logik, Status-Übergänge, Audit-Log)
    ├── knowledge_engine.py       (FAQ-Deflection & Volltextsuche)
    └── auth_jwt.py               (JWT-Generierung & Verifikation für Factofy)

  support_desk/models.py
    ├── HelpCategory              (Wissensportal Kategorien)
    ├── HelpArticle               (Wissensportal Artikel mit Markdown)
    ├── SupportProjectConfig      (Projekt-Konfiguration)
    ├── Ticket                    (Haupt-Ticket-Entität, UUID-PK)
    ├── TicketMessage             (Nachrichten-Thread)
    ├── TicketAttachment          (Datei-Anhänge)
    ├── CannedResponse            (Textbausteine für Agenten)
    └── TicketActivityLog         (Audit-Log aller Aktionen)
```

---

## 2. Backend-Konfiguration (Erstinstallation)

### 2.1 App & URL (bereits erledigt)

Die App ist in `backend/settings/base.py` unter `INSTALLED_APPS` registriert und in `backend/urls.py` eingebunden:

```python
path("api/support/", include("support_desk.api.urls")),
path("api/help/", include("support_desk.api.urls_help")),
```

### 2.2 Migrations ausführen


```bash
python manage.py makemigrations support_desk
python manage.py migrate
```

> **Nach jeder Model-Änderung wiederholen.**

### 2.3 Media-Uploads konfigurieren (für Ticket-Anhänge)

Anhänge werden unter `support_attachments/YYYY/MM/` gespeichert. Sicherstellen, dass in `settings/base.py` gilt:

```python
MEDIA_URL  = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

Nginx-Block für die Produktion:

```nginx
location /media/ {
    alias /var/www/sharegy/media/;
}
```

### 2.4 SUPPORT_SHARED_SECRET setzen

Der Fallback-Secret für JWT-Signierung wenn keine `SupportProjectConfig` gefunden wird:

```python
# backend/settings/production.py
SUPPORT_SHARED_SECRET = "dein-sehr-sicherer-produktions-secret-min-32-zeichen"
```

> **ACHTUNG:** Den Code-Default `"sharegy-factofy-default-secret-2026"` niemals in der Produktion verwenden!

---

## 3. Django Admin — Was konfiguriert werden muss

### 3.1 ⚡ Projektkonfigurationen anlegen (PFLICHT)

**Pfad:** Admin → Support-Projektkonfigurationen → Hinzufügen

Ohne diese Einträge funktioniert das Ticket-Nummernschema und die JWT-Authentifizierung für Factofy **nicht korrekt**.

#### Eintrag 1 — Sharegy:

| Feld | Wert |
|------|------|
| `project_key` | `sharegy` |
| `name` | `Sharegy HEMS` |
| `secret_key` | *(autogeneriert — Wert notieren!)* |
| `ticket_prefix` | `SHAR` |
| `allowed_categories` | `["hardware", "forecast", "tariff", "billing", "alerts", "general"]` |
| `is_active` | ✅ Ja |

#### Eintrag 2 — Factofy:

| Feld | Wert |
|------|------|
| `project_key` | `factofy` |
| `name` | `Factofy Digital Twin` |
| `secret_key` | *(autogeneriert — **in Factofy als** `SHAREGY_SUPPORT_SECRET` **setzen!**)* |
| `ticket_prefix` | `FACT` |
| `allowed_categories` | `["sensor", "building", "device", "visualization", "billing", "general"]` |
| `is_active` | ✅ Ja |

> Den `secret_key` des Factofy-Eintrags im Django Admin kopieren und in der Factofy-`.env` als `SHAREGY_SUPPORT_SECRET` setzen. Dieser Wert wird verwendet, um JWTs zu signieren und zu verifizieren.

### 3.2 Canned Responses (Textbausteine) anlegen

**Pfad:** Admin → Textbausteine (Canned Responses) → Hinzufügen

Textbausteine sind vordefinierte Antworten für Agenten im Support Hub.

**Empfohlene Startbausteine für Sharegy:**

| `shortcut` | `title` | Inhalt (Kurzform) |
|-----------|---------|-------------------|
| `reboot-inverter` | Wechselrichter neu starten | Anleitung zum Neustart |
| `gateway-sync` | Gateway-Synchronisation | LED-Status und Reset-Anleitung |
| `billing-invoice` | Rechnung anfordern | Zusendung innerhalb 24h |
| `waiting-team` | Warten auf internen Check | "Wir prüfen intern und melden uns..." |
| `ticket-resolved` | Ticket als gelöst markieren | Danksagung + Abschluss |

**Felder:**
- `project_key`: `sharegy`, `factofy`, oder `global` (erscheint in allen Projekten)
- `shortcut`: Eindeutiger Kurzbefehl-Slug
- `category`: Optionale Gruppierung (z. B. `hardware`, `billing`)
- `body_de`: Antworttext Deutsch (**Pflicht**)
- `body_en`: Antworttext Englisch (optional)

### 3.3 Support-Agenten als Staff markieren

**Pfad:** Admin → Benutzer → [Nutzer wählen] → `Mitarbeiter-Status` ✅

Nur Staff-Nutzer haben Zugang zum:
- Agent Support Hub (`/app/support-hub`)
- Internen Notizen
- Status- und Prioritätsänderung aller Tickets
- Ticket-Zuweisung

---

## 4. API-Referenz

Basis-URL: `/api/support/`

### Kunden-Endpunkte

#### `GET /api/support/tickets/`
Tickets des angemeldeten Nutzers abrufen.

**Query-Parameter:** `project_key`, `status`

**Response-Beispiel:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "ticket_number": "SHAR-2026-0001",
    "project_key": "sharegy",
    "subject": "Wechselrichter offline",
    "status": "open",
    "status_display": "Neu / Offen",
    "priority": "high",
    "category": "hardware",
    "message_count": 2,
    "created_at": "2026-08-28T05:00:00Z"
  }
]
```

---

#### `POST /api/support/tickets/`
Neues Ticket erstellen.

**Body (JSON oder multipart/form-data):**
```json
{
  "project_key": "sharegy",
  "subject": "Wechselrichter verbindet sich nicht",
  "category": "hardware",
  "priority": "high",
  "initial_message": "Seit gestern zeigt das Dashboard Offline-Status...",
  "contact_name": "Max Mustermann",
  "contact_email": "max@example.com",
  "context_payload": {
    "route": "/app/devices/123",
    "device_id": "INV-456",
    "url": "https://app.sharegy.de/devices/123",
    "userAgent": "Chrome/126",
    "screen": "1920x1080"
  }
}
```

Anhänge: `attachments[]` als multipart-Felder hinzufügen.

**Response:** `201 Created` mit vollständigem Ticket-Objekt.

---

#### `GET /api/support/tickets/<uuid>/`
Ticket mit vollem Nachrichten-Thread und Anhängen abrufen.

---

#### `PATCH /api/support/tickets/<uuid>/`
Status ändern (Kunde kann z. B. auf `resolved` setzen):
```json
{ "status": "resolved" }
```

**Gültige Status-Werte:**
- `open` — Neu / Offen
- `in_progress` — In Bearbeitung
- `waiting_customer` — Wartet auf Rückmeldung
- `waiting_internal` — Wartet intern
- `resolved` — Gelöst
- `closed` — Geschlossen

---

#### `POST /api/support/tickets/<uuid>/messages/`
Nachricht zum Ticket-Thread hinzufügen:
```json
{ "body": "Das Problem ist leider noch vorhanden..." }
```

Mit Anhang: multipart/form-data mit `body` + `attachments[]`.

---

#### `GET /api/support/deflection/suggest/?q=<query>`
FAQ-Vorschläge aus dem HelpCenter abrufen (Suchbegriff min. 3 Zeichen).

**Response:**
```json
{
  "query": "Wechselrichter offline",
  "suggestions": [
    {
      "id": "...",
      "slug": "wechselrichter-offline-beheben",
      "title_de": "Wechselrichter meldet Offline-Status",
      "summary_de": "Schritt-für-Schritt Anleitung...",
      "category_name": "Hardware & Geräte"
    }
  ]
}
```

---

### Agent-Endpunkte (nur `is_staff = True`)

#### `GET /api/support/agent/tickets/`
Alle Tickets aller Projekte + KPI-Block.

**Query-Parameter:** `project_key` (`all`/`sharegy`/`factofy`), `status`, `priority`, `search`

**Response:**
```json
{
  "kpis": {
    "total": 42, "open": 10, "in_progress": 5,
    "waiting_customer": 8, "resolved": 19,
    "sharegy_count": 30, "factofy_count": 12
  },
  "tickets": [...]
}
```

---

#### `PATCH /api/support/agent/tickets/<uuid>/`
Status, Priorität oder Agenten ändern:
```json
{
  "status": "in_progress",
  "priority": "urgent",
  "assigned_agent_id": 5
}
```

---

#### `POST /api/support/agent/tickets/<uuid>/`
Interne Notiz hinzufügen (nur für das Team sichtbar):
```json
{ "body": "Eskaliert an Entwicklung. Ticket-Nr. JIRA-456." }
```

---

#### `GET /api/support/canned-responses/?project_key=sharegy`
Textbausteine abrufen (projektspezifisch + globale).

---

## 5. Frontend-Komponenten

### SupportDrawer
**Datei:** [`src/features/support/components/SupportDrawer.jsx`](../frontend/src/features/support/components/SupportDrawer.jsx)  
**Eingebunden:** Topbar — 🛟-Button oben rechts  
**Props:** `isOpen`, `onClose`, `defaultContext`

Automatisch mitgesendete Kontextdaten (über `context_payload`):
- Aktuelle Route (`location.pathname`)
- Vollständige URL (`window.location.href`)
- Browser/User-Agent
- Screen-Auflösung
- Beliebige eigene Daten via `defaultContext` (z. B. `device_id`, `building_id`)

### TicketChatModal
**Datei:** [`src/features/support/components/TicketChatModal.jsx`](../frontend/src/features/support/components/TicketChatModal.jsx)

Chat-Thread mit Bubble-Design, Anhängen, aufklappbarer Telemetrie, Status-Toggle.

### AgentSupportHubPage
**Datei:** [`src/features/support/pages/AgentSupportHubPage.jsx`](../frontend/src/features/support/pages/AgentSupportHubPage.jsx)  
**Route:** `/app/support-hub`

Split-View: Ticket-Liste + Detailbereich mit internen Notizen, Textbaustein-Dropdown, Status-/Prioritäts-Dropdown.

---

## 6. Authentifizierung & Berechtigungen

Das System erkennt die Auth-Methode automatisch (Reihenfolge):

1. **Factofy JWT** (`Authorization: Bearer <token>`) → externer Nutzer
2. **Django Session** (Cookie) → eingeloggter Sharegy-Nutzer
3. **Anonym** → Ticket-Erstellung möglich mit `contact_name` / `contact_email`

### Berechtigungsmatrix

| Aktion | Anonym | Sharegy-User | Factofy-JWT | Staff/Agent |
|--------|:------:|:------------:|:-----------:|:-----------:|
| Ticket erstellen | ✅ | ✅ | ✅ | ✅ |
| Eigene Tickets lesen | ❌ | ✅ | ✅ | ✅ alle |
| Nachricht senden | ❌ | ✅ | ✅ | ✅ |
| Interne Notiz | ❌ | ❌ | ❌ | ✅ |
| Eigenen Status ändern | ❌ | ✅ | ✅ | ✅ |
| Alle Tickets verwalten | ❌ | ❌ | ❌ | ✅ |
| Agent Hub nutzen | ❌ | ❌ | ❌ | ✅ |
| Textbausteine verwalten | ❌ | ❌ | ❌ | ✅ |

---

## 7. Deflection (FAQ-Vorschläge)

Während der Nutzer den Betreff eines neuen Tickets eintippt (ab 3 Zeichen, 300 ms Debounce), werden automatisch passende HelpCenter-Artikel gesucht und als klickbare Vorschläge angezeigt.

**Ziel:** Selbstbedienung fördern, Ticket-Volumen reduzieren.

**Funktioniert nur** wenn das `helpcenter`-Modul installiert ist und `HelpArticle`-Objekte mit `is_published=True` existieren. Andernfalls wird kommentarlos `[]` zurückgegeben.

**Voraussetzungen `helpcenter.HelpArticle`:**

```python
class HelpArticle(models.Model):
    title_de      = CharField(...)
    title_en      = CharField(...)
    summary_de    = TextField(...)
    summary_en    = TextField(...)
    slug          = SlugField(unique=True)
    tags          = CharField(...)       # z. B. "wechselrichter, offline, reset"
    is_published  = BooleanField()
    views_count   = IntegerField(default=0)
    category      = ForeignKey(...)     # mit .title_de
```

---

## 8. Canned Responses (Textbausteine)

Vordefinierte Antwort-Snippets für Support-Agenten. Im Agent Hub über ein Dropdown-Menü auswählbar — der Text wird direkt ins Antwortfeld eingefügt.

**`project_key = "global"`** → erscheint in allen Projekten.

Empfehlung: Mindestens 5–10 Bausteine für die häufigsten Szenarien anlegen, bevor das Support-Team startet.

---

## 9. Ticket-Nummernschema

```
Format:   {PREFIX}-{JAHR}-{SEQUENZ 4-stellig}
Beispiel: SHAR-2026-0001
          FACT-2026-0042

- PREFIX:   Aus SupportProjectConfig.ticket_prefix (z. B. SHAR, FACT)
- JAHR:     UTC-Jahr der Ticket-Erstellung
- SEQUENZ:  Jahresbezogen, pro Projekt, automatisch kollisionssicher
```

Die Zählung startet jedes Jahr neu bei `0001`.

---

## 10. Factofy-Integration

Vollständige Anleitung: **[`docs/integrations/FACTOFY_SUPPORT_INTEGRATION_GUIDE.md`](./integrations/FACTOFY_SUPPORT_INTEGRATION_GUIDE.md)**

### Kurzanleitung (4 Schritte):

**Schritt 1 — Secret übertragen:**
Im Django Admin den `secret_key` des `factofy`-Projekts kopieren und in Factofy setzen:
```bash
# Factofy .env
SHAREGY_SUPPORT_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
SHAREGY_SUPPORT_API_URL=https://api.sharegy.de/api/support
```

**Schritt 2 — Next.js Token-Route anlegen** (`/api/support-token`):
```typescript
// Generiert ein JWT für den aktuell eingeloggten Factofy-Nutzer
// Payload: { sub, email, name, project: "factofy", iat, exp }
// Signiert mit SHAREGY_SUPPORT_SECRET via HMAC-SHA256
```

**Schritt 3 — Widget einbinden:**
```jsx
// In Factofy-Layout oder als Floating-Button
import { FactofySupportWidget } from "@/components/support/FactofySupportWidget";

<FactofySupportWidget
  buildingId={currentBuilding?.id}
  assetId={selectedAsset?.id}
/>
```

**Schritt 4 — Testen (Django Shell):**
```python
from support_desk.services.auth_jwt import generate_support_jwt

token = generate_support_jwt(
    project_key="factofy",
    user_id="usr_test_123",
    email="test@factofy.de",
    name="Test Nutzer",
)
print(token)  # Als Authorization: Bearer <token> testen
```

---

## 11. Produktionsbetrieb & Checkliste

### Deployment-Checkliste

**Backend:**
- [ ] `python manage.py migrate` — Migrations angewendet
- [ ] `SUPPORT_SHARED_SECRET` in `settings/production.py` gesetzt (kein Default!)
- [ ] `MEDIA_ROOT` konfiguriert
- [ ] Nginx: `/media/` Alias konfiguriert

**Django Admin:**
- [ ] `SupportProjectConfig` **sharegy** angelegt (Prefix: `SHAR`)
- [ ] `SupportProjectConfig` **factofy** angelegt (Prefix: `FACT`)
- [ ] Mindestens einen Nutzer als Staff/Agent markiert
- [ ] Canned Responses angelegt (empfohlen: 5–10 Bausteine)

**Factofy (wenn aktiviert):**
- [ ] `factofy.secret_key` aus Admin kopiert und in Factofy `.env` gesetzt
- [ ] Next.js Token-Route implementiert und getestet
- [ ] Factofy Widget eingebunden und Ticket-Erstellung getestet

**Frontend (bereits vorhanden ✅):**
- [x] Route `/app/support-hub` in React Router registriert
- [x] `SupportDrawer` in Topbar eingebunden
- [x] Sidebar-Navigation "Support & Tickets" eingetragen

### Monitoring & Audit

Alle Aktionen (Statusänderungen, Nachrichten, Zuweisungen) werden in `TicketActivityLog` protokolliert und sind im Django Admin in der Ticket-Detailansicht als Inline-Tabelle sichtbar.

### SLA-Erweiterung (optional)

Das Modell hat bereits alle Zeitstempel-Felder (`first_response_due`, `first_responded_at`, `resolved_at`, `closed_at`). SLA-Deadlines in `ticket_engine.py → create_ticket()` ergänzen:

```python
# 4h Erstantwort-SLA für Priorität "high" und "urgent"
if priority in ("high", "urgent"):
    ticket.first_response_due = timezone.now() + datetime.timedelta(hours=4)
    ticket.save(update_fields=["first_response_due"])
```
