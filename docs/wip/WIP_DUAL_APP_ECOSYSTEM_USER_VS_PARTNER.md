# 🛠️ [WIP] Dual-App Android-Ökosystem (Consumer App vs. Partner & Liegenschafts-Pro App)

**Status:** In Konzeption / Strategische Evaluierung  
**Fortschritt:** 🟡 50 %  
**Priorität:** 🟡 Mittel (Ziel: Q1 2027)  
**Lead / Modul:** `mobile`, `frontend`, `accounts`  

---

## 🎯 1. Strategische Motivation

Mit der Einführung des **Installateurs- & Flotten-Cockpits** und der **Liegenschafts-Administration (WEGs / Hausverwaltungen)** stellt sich die Frage nach der optimalen Mobile-App-Strategie:

### Die 2 Zielgruppen mit stark unterschiedlichen Bedürfnissen:
1. **Endanwender & Mieter (Consumer)**:
   * **Fokus**: Maximale Einfachheit, schlankes Design, Live-Energiefluss, Solarprognose, Wallbox-Quickboost, Monatsersparnis.
   * **Ziel**: Schnelles Laden, minimale kognitive Last, Zero-B2B-Clutter.
2. **Installateure, Hausverwalter & Tenant-Admins (Pro / B2B)**:
   * **Fokus**: Flottenübersicht, Multiliegenschafts-Verwaltung, Zuweisung von Zählpunkten, 1-Klick-Inbetriebnahme, Fernwartung, AS4-Übertragungsprotokolle.
   * **Ziel**: Produktivitäts-Werkzeug für den Arbeitsalltag vor Ort beim Kunden.

---

## 📱 2. Vergleich der Ansätze

| Kriterium | Option A: Einheitliche All-in-One App (RBAC-gesteuert) | Option B: Zwei getrennte Play-Store-Apps |
|---|---|---|
| **App 1 (Consumer)** | `Sharegy` (Endanwender, Mieter, Haushalte) | `Sharegy Home` (`de.sharegy.app`) |
| **App 2 (B2B Pro)** | Identische App (zeigt Pro-Tabs nur bei Admin/Partner-Rolle) | `Sharegy Pro & Partner` (`de.sharegy.pro`) |
| **Download-Größe** | ~14 MB (Vollständig) | ~8 MB (Home) / ~12 MB (Pro) |
| **Play Store Positionierung** | Gemischte Zielgruppenansprache | Glasklare Trennung in B2C & B2B Keywords |
| **Wartungsaufwand** | 🟢 **Sehr gering** (Eine Codebase, ein Build) | 🟡 Zwei Play-Store-Einträge, 2 Builds |
| **Empfehlung** | **Phase 1 (Jetzt)**: Einheitliche App mit dynamischem RBAC-Switching | **Phase 2 (Skalierung)**: Eigener Store-Release für Partner |

---

## 🏗️ 3. Architektur der Implementierung (Phase 1 vs. Phase 2)

### Phase 1: Dynamisches UI-Switching in der bestehenden App (Bereits Live ✅)
* Wenn ein Benutzer sich anmeldet, prüft [`AppShell.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/components/AppShell.jsx) die Rollen `isStaffOrAdmin` und `hasCommunityAdminAccess` sowie `PartnerMembership`.
* Normale Nutzer sehen ausschließlich das aufgeräumte Home-Dashboard.
* Installateure sehen zusätzlich das **Flotten-Cockpit (`/app/partner`)** und Hausverwalter den **Liegenschafts-Hub (`/app/tenant`)**.

### Phase 2: Getrennter Build für `Sharegy Pro` (Geplant für Q1 2027)
* Ein zweites Capacitor-Target `frontend/android-pro/` mit eigenem App-Icon (Dunkles Gold/Schwarz Pro-Branding), eigenem Package-Namen `de.sharegy.pro` und direktem Start im Flotten-Cockpit.

---

## 🚀 4. Nächste Umsetzungsschritte

1. **Sprint 1**: Optimierung des mobilen Tabs-Switchers im Partner-Dashboard für Smartphones.
2. **Sprint 2**: Evaluierung der Google Play Store Richtlinien für eigenständige B2B-Begleit-Apps.
3. **Sprint 3**: Bereitstellung von Fastlane-Lanes für `bundleProRelease`.
