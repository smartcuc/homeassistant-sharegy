# 👥 Benutzer- & Rechteverwaltung (Enterprise Multi-Tenant RBAC)

> **Dokument:** `RBAC_AND_USER_MANAGEMENT_GUIDE.md`  
> **Modul:** `accounts` & `core`  
> **Gültig ab:** Version 2.0 (2026-08)  
> **Projekte:** Sharegy HEMS · Sharegy Energy Communities · Factofy Integration  

---

## Inhaltsverzeichnis

1. [Überblick & 2-Ebenen-Architektur](#1-überblick--2-ebenen-architektur)
2. [Ebene 1: Sharegy EMS Plattform (Global / Staff)](#2-ebene-1-sharegy-ems-plattform-global--staff)
3. [Ebene 2: Sharegy Energy Community / Tenant (Lokal)](#3-ebene-2-sharegy-energy-community--tenant-lokal)
4. [Rechte- & Berechtigungsmatrix](#4-rechte--berechtigungsmatrix)
5. [Verwaltungsorte: Wo wird was konfiguriert?](#5-verwaltungsorte-wo-wird-was-konfiguriert)
6. [Schritt-für-Schritt Anleitungen](#6-schritt-für-schritt-anleitungen)
7. [Zusammenspiel mit dem Support- & Ticketsystem](#7-zusammenspiel-mit-dem-support--ticketsystem)
8. [Audit-Log & Revisionssicherheit](#8-audit-log--revisionssicherheit)

---

## 1. Überblick & 2-Ebenen-Architektur

Sharegy trennt die Benutzer- und Rechteverwaltung in zwei logische Schichten:

```
┌────────────────────────────────────────────────────────────────────────┐
│ EBENE 1: Globale Sharegy EMS Plattform (Django Admin / Backoffice)     │
│  - Systemadmin          - Finanzen & Billing                           │
│  - Global User-Admin    - Plattform Helpdesk                           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ hostet & überwacht
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ EBENE 2: Lokale Energy Communities / Tenants (Frontend /app/tenant)    │
│  - Energy-Admin (Quartiersbetreiber)                                   │
│  - Energy-Userverwaltung (Mitgliederbetreuer)                          │
│  - Energy-Helpdesk (1st-Level Support vor Ort)                        │
│  - Kassenprüfer / Auditor (Read-Only)                                  │
│  - Community-Mitglied (Consumer / Producer / Prosumer)                │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Ebene 1: Sharegy EMS Plattform (Global / Staff)

Diese Rollen gelten **systemweit** und werden direkt auf dem Benutzer-Modell (`User.platform_role`) hinterlegt.

| Rolle | Key im Code | Hauptaufgaben | Zugriff |
|---|---|---|---|
| 👑 **Systemadmin** | `system_admin` | Technische Infrastruktur, API-Keys, Django Admin, Systemgesundheit, Migrationen, alle Tenants. | Voller Systemzugriff (`is_superuser = True` oder `is_platform_admin = True`) |
| 💳 **Finanzen & Billing** | `finance` | Stripe-Zahlungsströme, Rechnungs- und Auszahlungsläufe, Plattform-Tarife, SEPA-Batches, Einnahmen-Reportings. | Zugriff auf Billing- und Finanz-APIs |
| 👥 **Userverwaltung (Global)** | `user_admin` | Globales Identity Management, Freischaltung neuer Energy Communities, Zuweisung von Energy-Admins. | Globale Benutzer- & Tenant-Verwaltung |
| 🛟 **Plattform Helpdesk** | `helpdesk` | Bearbeitung aller System- und Hardwaretickets im Support Hub (`/app/support-hub`), Wissensportal-Redaktion. | Ticket-Triage über alle Projekte hinweg |
| 👤 **Endkunde / Standard** | `none` | Standard EMS-Nutzer ohne Plattformbefugnisse. | Eigene EMS-Daten |

---

## 3. Ebene 2: Sharegy Energy Community / Tenant (Lokal)

Diese Rollen gelten **ausschließlich innerhalb einer spezifischen Energy Community** und werden über `TenantMembership.role` vergeben.

| Rolle | Key im Code | Befugnisse & Aufgaben |
|---|---|---|
| 🏛️ **Energy-Admin** | `admin` | **Quartiersbetreiber:** Voller Zugriff auf die Community-Konfiguration, Tarife, Einladungen und Rollenvergabe. |
| 👥 **Energy-Userverwaltung** | `user_admin` | **Mitgliederverwaltung:** Lädt Nachbarn/Mieter ein, weist Standardrollen zu und pflegt die Mitgliederliste. |
| 🛟 **Energy-Helpdesk** | `helpdesk` | **1st-Level Support vor Ort:** Beantwortet lokale Fragen von Community-Mitgliedern (z. B. Solarstrom-Zuteilung im Haus). |
| 📊 **Kassenprüfer / Auditor** | `auditor` | **Read-Only:** Prüft Monatsbilanzen, Quartiers-Abrechnungsberichte und Audit-Logs ohne Bearbeitungsrechte. |
| ⚡ **Community-Mitglied** | `member` | **Endnutzer:** Sieht persönliche Verbrauchs-, Erzeugungs- und Abrechnungsdaten (Consumer, Producer, Prosumer). |

---

## 4. Rechte- & Berechtigungsmatrix

Die Berechtigungsprüfung erfolgt zentral über `accounts/permissions.py`:

| Permission-Key | Bedeutung | `admin` | `user_admin` | `helpdesk` | `auditor` | `member` |
|---|---|:---:|:---:|:---:|:---:|:---:|
| `manage_community` | Quartierseinstellungen & Tarife bearbeiten | ✅ | ❌ | ❌ | ❌ | ❌ |
| `manage_members` | Mitgliederrollen ändern & entfernen | ✅ | ✅ *(eingeschränkt)* | ❌ | ❌ | ❌ |
| `manage_invites` | Neue Einladungslinks erstellen | ✅ | ✅ *(eingeschränkt)* | ❌ | ❌ | ❌ |
| `manage_tickets` | Lokale Community-Tickets beantworten | ✅ | ❌ | ✅ | ❌ | ❌ |
| `view_reports` | Quartiersbilanzen & Abrechnungsreports | ✅ | ❌ | ❌ | ✅ | ❌ |
| `view_audit_log` | Revisionssicheres Aktivitätsprotokoll | ✅ | ❌ | ❌ | ✅ | ❌ |
| `edit_data` | Zählerkonfigurationen anpassen | ✅ | ❌ | ❌ | ❌ | ❌ |
| `view_data` | Eigene Verbrauchs- & Zählerdaten lesen | ✅ | ✅ | ✅ | ✅ | ✅ |

### Rollenhierarchie & Schutzregeln
- Die **Energy-Userverwaltung** (`user_admin`) darf Einladungen für `member`, `helpdesk` und `auditor` erstellen.
- Die **Energy-Userverwaltung** darf **keine neuen Energy-Admins** ernennen und den bestehenden Energy-Admin **nicht entfernen**.
- Nur der **Energy-Admin** (oder Plattform Systemadmin) kann die Rolle `admin` vergeben.

---

## 5. Verwaltungsorte: Wo wird was konfiguriert?

### A. Django Admin Backend (`https://sharegy.de/admin/`)
* **Zielgruppe:** Sharegy Betreiberteam & Systemadministratoren
* **Bereiche:**
  1. `Accounts ➔ Users`: Zuweisung von `platform_role` (`system_admin`, `finance`, `user_admin`, `helpdesk`).
  2. `Core ➔ Tenants`: Anlegen neuer Energy Communities (Name, Slug, Branding, Geodaten).
  3. `Accounts ➔ Tenant memberships`: Initiale Zuweisung des `Energy-Admin` zu einer Community.

### B. Frontend Tenant-Dashboard (`https://sharegy.de/app/tenant`)
* **Zielgruppe:** Energy-Admins & Energy-Userverwaltung
* **Bereiche:**
  1. **Einladungslinks-Generator:** Erstellen von Links mit vorausgewählter Rolle (`⚡ Mitglied`, `👥 Userverwaltung`, `🛟 Helpdesk`, `📊 Auditor`, `🏛️ Admin`).
  2. **Mitglieder-Tabelle:** Live-Änderung der Rolle über ein Dropdown-Menü oder Entfernen eines Mitglieds.
  3. **Audit-Log:** Historie aller Rollenänderungen und Einladungen.

---

## 6. Schritt-für-Schritt Anleitungen

### 6.1 Wie lege ich eine neue Energy Community an und mache einen Nutzer zum Admin?
1. Öffne `https://sharegy.de/admin/`.
2. Gehe auf **Core ➔ Tenants ➔ Tenant hinzufügen**.
3. Gib den Namen ein (z. B. *"Quartier Sonnengarten"*). Der Slug wird automatisch erzeugt.
4. Gehe auf **Accounts ➔ Tenant memberships ➔ Mitgliedschaft hinzufügen**.
5. Wähle den gewünschten Benutzer und die neu angelegte Community aus.
6. Setze die Rolle auf **`Energy Admin` (`admin`)** und speichere.
7. Der Nutzer hat ab sofort vollen Zugriff auf `https://sharegy.de/app/tenant`.

### 6.2 Wie lade ich als Energy-Admin neue Nachbarn oder Helfer ein?
1. Melde dich in der App an und navigiere zu `https://sharegy.de/app/tenant`.
2. Klicke im Bereich *„Einladungslinks“* auf die gewünschte Schaltfläche:
   - `⚡ Mitglied einladen` ➔ Für reguläre Mieter / Wohnungseigentümer
   - `👥 Userverwaltung` ➔ Für einen Beirat, der das Onboarding unterstützt
   - `🛟 Helpdesk` ➔ Für den Hausmeister oder lokalen Support-Ansprechpartner
   - `📊 Auditor / Beirat` ➔ Für den Kassenprüfer der Gemeinschaft
3. Klicke auf **„Link kopieren“** und sende den Link per E-Mail oder Messenger an die Person.
4. Sobald die Person den Link öffnet und sich registriert/anmeldet, wird sie automatisch mit der gewählten Rolle der Community hinzugefügt.

---

## 7. Zusammenspiel mit dem Support- & Ticketsystem

Das Berechtigungssystem steuert automatisch die Support-Funktionen im **Support Desk (`support_desk`)**:

| Rolle | Ticket-Erstellung | ITIL-Prioritätsauswahl | Ticket-Triage & Bearbeitung |
|---|:---:|:---:|---|
| **Anonymer Gast** | ❌ (Login-Pflicht) | ❌ | ❌ |
| **Free-EMS Nutzer** | ✅ | 🔒 Fixiert auf `low` | ❌ |
| **EMS Pro Nutzer** | ✅ | ✅ `low`, `medium`, `high` | ❌ |
| **Energy Community Rollen** (`admin`, `user_admin`, `helpdesk`) | ✅ | ✅ `low`, `medium`, `high`, `urgent` | ✅ Lokaler 1st-Level Support für die eigene Community |
| **Plattform Helpdesk & Staff** | ✅ | ✅ `low`, `medium`, `high`, `urgent` | ✅ Globaler Support Hub für alle Projekte (`/app/support-hub`) |

---

## 8. Audit-Log & Revisionssicherheit

Jede administrative Aktion im Quartier wird im `AuditLog`-Modell (`accounts.models.AuditLog`) protokolliert:

- `invite_created`: Ein neuer Einladungslink wurde generiert (inkl. Rolle).
- `role_updated`: Einem Mitglied wurde eine neue Rolle zugewiesen (wer, welches Mitglied, alte/neue Rolle).
- `member_removed`: Ein Mitglied wurde aus der Community entfernt.
- `invite_deactivated`: Ein aktiver Einladungslink wurde gesperrt.

Das Audit-Log kann direkt im Tenant-Dashboard von **Energy-Admins** und **Kassenprüfern / Auditoren** eingesehen werden.
