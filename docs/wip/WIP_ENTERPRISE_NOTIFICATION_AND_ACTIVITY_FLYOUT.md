# 🔔 [WIP] Enterprise Notification & Activity Flyout (Topbar-Glocke)

**Dokument-Status:** In Konzeption / Spezifikation  
**Fortschritt:** 🟡 20 %  
**Priorität:** 🔴 Hoch (Operator- & Dispatcher UX)  
**Lead / Modul:** `frontend/src/components/layout/`, `alerts`, `energy`  

---

## 🎯 1. Problemstellung & Motivation

Aktuell öffnet ein Klick auf das Benachrichtigungs-Icon in der Kopfzeile ein zentriertes, modales Dialogfenster.
Im kontinuierlichen Leitstellen- und Betriebsalltag ist ein **reaktives Topbar-Dropdown-Flyout** deutlich ergonomischer:
* Kein Verdecken des aktuellen Arbeitskontexts.
* Strukturierte Aufteilung in 4 getrennte Ereignis-Kategorien.
* 1-Klick-Aktionen zur schnellen Abarbeitung von Warnungen.

---

## 🖥️ 2. UI-Layout & Tab-Struktur

```
                                                 [ 🔔 (3) ▼ ] [ Avatar ]
                                              ┌─────────────────────────┐
                                              │ 🔔 Benachrichtigungen   │
┌─────────────────────────────────────────────┴─────────────────────────┤
│ [ 🚨 Störungen (1) ] [ ⚡ VPP / Netz (2) ] [ 📄 IBN / Doku ] [ 👥 System ] │
├───────────────────────────────────────────────────────────────────────┤
│ 🚨 Wechselrichter Ost-Dach Offline                                    │
│    Liegenschaft Sonnenblick • vor 4 Min.                              │
│    [ Direkt zur Anlage ]   [ Als gelesen markieren ]                  │
├───────────────────────────────────────────────────────────────────────┤
│ ⚡ § 14a EnWG Dimm-Befehl aktiv (4,2 kW)                             │
│    VNB Signal erhalten • Soll: 4,2 kW • Dauer: bis 15:30 Uhr          │
│    [ Dispatch-Log öffnen ]                                            │
├───────────────────────────────────────────────────────────────────────┤
│ ⚡ VPP Regelleistung erbracht (aFRR +8,4 kW)                          │
│    Pool Nord • Erlös: +3,42 € • vor 18 Min.                           │
├───────────────────────────────────────────────────────────────────────┤
│  ✓ Alle als gelesen markieren           ⚙️ Benachrichtigungs-Settings │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 📊 3. Kategorien & Filter-Logik

| Tab-Kategorie | Enthaltene Ereignisse | Auslöser / Backend-Modell |
|---|---|---|
| **🚨 Störungen & Alarme** | Wechselrichter offline, Phasen-Schieflast, Überlastung, Batterie-Tiefentladung | `AlertEvent` (`severity='critical' \| 'warning'`) |
| **⚡ VPP / Netz-Aktionen** | § 14a EnWG Dimm-Befehle, Regelleistungsabrufe (aFRR/FCR), Lastabwurf | `EnWG14aDimmingAuditLog`, `VPPAssetDispatch` |
| **📄 IBN & Dokumente** | Neue IBN-Protokolle, monatliche DATEV-/MSCONS-Exporte, Abrechnungsbelege | `CoreDocument`, `HandoverProtocol` |
| **👥 System-Events** | Neue Benutzer-Einladungen, Rollenänderungen, Sicherheits-Audits | `AuditLogEntry`, `TenantMember` |

---

## 🛠️ 4. Technische Komponenten & Umsetzungsschritte

1. **`frontend/src/components/layout/NotificationFlyout.jsx`**:
   - Reaktives Floating-Popover mit Click-Outside Listener und Escape-Handling.
   - Live-Badge mit unread Counter auf dem Glocken-Icon.
2. **Backend API-Endpunkte**:
   - `GET /api/alerts/recent/?tab=vpp&unread_only=true` (aggregiert Live-Ereignisse)
   - `POST /api/alerts/mark-all-read/` (Quittierung)
   - `POST /api/alerts/{id}/dismiss/`
3. **Optimistisches UI-Update via TanStack Query**:
   - Sofortiges Ausblenden von Badges beim Anklicken ohne Layout-Ruckeln.
