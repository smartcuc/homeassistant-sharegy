# 💶 Walkthrough: Stromtarife & Tibber API-Integration

**Datum**: 23. August 2026  
**Bereich**: Frontend (SideNav & Settings), Backend (`market` & `integrations` Apps)  

---

## 🎯 Ziel & Motivation
Der Nutzer sollte seinen individuellen Stromtarif (Börsenstrom vs. Festpreis) hinterlegen können. Zudem sollte eine direkte Integration des persönlichen Tibber-Stromvertrags (API-Token & automatische Zählererkennung) geschaffen werden.

---

## 🛠️ Durchgeführte Implementierungen

### 1. Navigation & Seitenstruktur
- **SideNav ([`Sidebar.jsx`](../../frontend/src/components/layout/Sidebar.jsx))**: Neuer Menüeintrag **💶 Strompreise & Tarife** (`/app/tariff`) unter *⚙️ Einstellungen*.
- **Routing ([`AppShell.jsx`](../../frontend/src/components/AppShell.jsx))**: Dedizierte Seite [`TariffPage.jsx`](../../frontend/src/features/market/pages/TariffPage.jsx) eingebunden.

### 2. Frontend-Komponenten
- **[`HomeTariffSettingsCard.jsx`](../../frontend/src/features/market/components/HomeTariffSettingsCard.jsx)**:
  - **Strombezug**: Umschaltung zwischen *Dynamischer Börsenstromtarif (EPEX Spot)* und *Klassischer Festpreis-Tarif* (mit Eingabefeld in ct/kWh).
  - **Einspeisevergütung & PV-Überschuss**:
    - 🔘 *Feste EEG-Einspeisevergütung* (z. B. 8,20 ct/kWh für Neuanlagen oder bis 28 ct/kWh für Altanlagen nach § 25 EEG).
    - 🔘 *Börsen-Marktwert Solar* (Direktvermarktung & Post-EEG nach EPEX Spot).
    - 🔘 *Keine Vergütung / Nulleinspeisung* (0,00 ct/kWh für Balkonkraftwerke / reine Eigenverbrauchsoptimierung).
  - Transparente Aufklappansicht für feste gesetzliche Nebenkosten (Netzentgelte, Stromsteuer, Konzessionsabgabe, Umlagen, MwSt. = ~17,59 ct/kWh brutto).
- **[`TibberSettingsCard.jsx`](../../frontend/src/features/market/components/TibberSettingsCard.jsx)**:
  - Eingabe des Personal Access Tokens.
  - Button **„🔍 Homes laden“**: Fragt die Tibber-GraphQL-API live ab und befüllt ein Dropdown mit allen registrierten Haushalten/Zählern samt Adresse und ID.
  - Live-Status-Badge (`🟢 Verbunden` / `⚪ Nicht konfiguriert`).

### 3. Backend-API & Services
- **[`market/models_tariff.py`](../../market/models_tariff.py)**:
  - `HomeTariff` um `feed_in_tariff_type` (`static`, `dynamic`, `none`) und `feed_in_tariff_eur_per_kwh` erweitert.
- **[`market/api/views.py`](../../market/api/views.py)**:
  - `GET/POST /api/market/tariff/`: Liest/speichert Bezugs- und Einspeisetarife sowie `user.tibber_token` / `user.tibber_home_id`.
- **[`energy/services/balance.py`](../../energy/services/balance.py)**:
  - Verwendet live die individuellen Tarifeinstellungen des Benutzers.
  - Bei dynamischen Tarifen werden Ersparnis und Einspeiseerlöse stunden-/intervallgenau anhand der EPEX Spot Marktdaten bewertet.
- **[`integrations/services_tibber.py`](../../integrations/services_tibber.py)**:
  - `get_tibber_homes(token)` mit Adressformatierung und Fehlerbehandlung.

---

## ✅ Verifikation
- Frontend Build: `npm run build` $\rightarrow$ **Erfolgreich in 6.14s (0 Fehler)**.
- ESLint: **0 Fehler / 0 Warnungen**.
- Backend Tests: `manage.py test` $\rightarrow$ **13/13 Tests erfolgreich (`OK`)**.
