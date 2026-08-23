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
  - Umschaltung zwischen *Dynamischer Börsenstromtarif (EPEX Spot)* und *Klassischer Festpreis-Tarif* (mit Eingabefeld in ct/kWh).
  - Transparente Aufklappansicht für feste gesetzliche Nebenkosten (Netzentgelte, Stromsteuer, Konzessionsabgabe, Umlagen, MwSt. = ~17,59 ct/kWh brutto).
- **[`TibberSettingsCard.jsx`](../../frontend/src/features/market/components/TibberSettingsCard.jsx)**:
  - Eingabe des Personal Access Tokens.
  - Button **„🔍 Homes laden“**: Fragt die Tibber-GraphQL-API live ab und befüllt ein Dropdown mit allen registrierten Haushalten/Zählern samt Adresse und ID.
  - Live-Status-Badge (`🟢 Verbunden` / `⚪ Nicht konfiguriert`).

### 3. Backend-API & Services
- **[`market/api/views.py`](../../market/api/views.py)**:
  - `GET/POST /api/market/tariff/`: Liest/speichert `HomeTariff` und `user.tibber_token` / `user.tibber_home_id`.
  - `POST /api/market/tariff/tibber-homes/`: Ruft `get_tibber_homes(token)` auf und validiert das Token.
- **[`market/services_tariff.py`](../../market/services_tariff.py)**:
  - Fallback für automatische Generierung von Standard-`ElectricityPriceConfig` Daten.
- **[`integrations/services_tibber.py`](../../integrations/services_tibber.py)**:
  - `get_tibber_homes(token)` mit Adressformatierung und Fehlerbehandlung.

---

## ✅ Verifikation
- Frontend Build: `npm run build` $ightarrow$ **Erfolgreich in 3.38s (0 Fehler)**.
- ESLint: **0 Fehler / 0 Warnungen**.
- Backend Tests: `manage.py test` $ightarrow$ **15/15 Tests erfolgreich (`OK`)**.
