# 📘 Walkthrough: MQTT-Zugangsdaten-Hub, erweiterte SI-Einheiten & Multi-Language (i18n)

**Datum**: 23. August 2026  
**Bereich**: Frontend UX, System-Settings, i18n & API  
**Status**: ✅ Abgeschlossen & Verifiziert  

---

## 🎯 Ziel & Motivation

1. **Zentraler MQTT-Zugangsdaten-Hub**: Nutzer müssen ihre globalen MQTT-Zugangsdaten (Host, Port, Token, Passwort) jederzeit transparent einsehen, kopieren und sicher rotieren können – ohne erst ein Gerät anlegen zu müssen.
2. **Umfassende SI-Einheiten & Multi-Metriken**: Vollständige Unterstützung aller physikalischen Sensor- und Energietypen (Temperatur, Luftdruck, Feuchte, CO2, VOC, Helligkeit, Batterie-SoC, Durchfluss, Wirk-/Blind-/Scheinleistung).
3. **Frontend Multi-Language (i18n)**: Native Mehrsprachigkeit für die Benutzeroberfläche mit Unterstützung für 🇩🇪 Deutsch, 🇬🇧 Englisch und 🇵🇱 Polnisch.

---

## 🛠️ Durchgeführte Änderungen

### 1. 📡 MQTT & Smart Home Schnittstellen-Hub
- **Backend**:
  - [`HomeSerializer`](file:///c:/Users/Public/Dev/eswes/devices/api/serializers.py): Liefert `mqtt_host`, `mqtt_port`, `mqtt_token`, `mqtt_username`, `mqtt_password` an autorisierte Haushaltsinhaber.
  - Endpoint `POST /api/devices/homes/regenerate-mqtt/`: Ermöglicht sichere Passwort-Rotation bei Schlüsselverlust.
- **Frontend**:
  - Neuer Bereich in [`frontend/src/pages/Settings.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/pages/Settings.jsx):
    - Host & Port (`mqtt.sharegy.de:1883`) mit Live-Aktiv-Badge.
    - Maskiertes Passwort mit 👁️ Einblenden- und 📋 Kopierfunktion.
    - Vollbild-QR-Code Modal für mobile Apps.
    - Schnellanleitungen für **ioBroker**, **Home Assistant** und **Shelly**.
  - Neuer Sidebar-Menüpunkt **`📡 MQTT & Schnittstellen`** in [`frontend/src/components/layout/Sidebar.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/components/layout/Sidebar.jsx).

---

### 2. 📊 Erweiterte SI-Einheiten & Multi-Metric Katalog
- [`devices/management/commands/seed_device_setup.py`](file:///c:/Users/Public/Dev/eswes/devices/management/commands/seed_device_setup.py) & `KEY_METADATA` in [`devices/api/views.py`](file:///c:/Users/Public/Dev/eswes/devices/api/views.py) erweitert um:
  - **Elektrisch**: `power` (`W`), `voltage` (`V`), `current` (`A`), `frequency` (`Hz`), `energy` (`kWh`), `reactive_power` (`var`), `apparent_power` (`VA`).
  - **Speicher**: `soc` (`%`), `soh` (`%`).
  - **Umwelt & Klima**: `temperature` (`°C`), `humidity` (`%`), `pressure` (`hPa`), `co2` (`ppm`), `voc` (`ppb`), `illuminance` (`lx`), `solar_radiation` (`W/m²`), `wind_speed` (`m/s`).
  - **Wärme & Durchfluss**: `flow_temperature` (`°C`), `return_temperature` (`°C`), `flow_rate` (`l/h`), `heat_power` (`kW`).

---

### 3. 🌍 Frontend Multi-Language (i18n mit DE, EN, PL)
- **Framework**: `i18next` & `react-i18next` mit `i18next-browser-languagedetector`.
- **Dateistruktur**:
  - [`frontend/src/i18n/index.js`](file:///c:/Users/Public/Dev/eswes/frontend/src/i18n/index.js): Init mit Fallback `de` und LocalStorage-Caching.
  - [`frontend/src/i18n/locales/de.json`](file:///c:/Users/Public/Dev/eswes/frontend/src/i18n/locales/de.json): Deutsche Übersetzung.
  - [`frontend/src/i18n/locales/en.json`](file:///c:/Users/Public/Dev/eswes/frontend/src/i18n/locales/en.json): Englische Übersetzung.
  - [`frontend/src/i18n/locales/pl.json`](file:///c:/Users/Public/Dev/eswes/frontend/src/i18n/locales/pl.json): Polnische Übersetzung.
- **Sprachumschalter**: In den Einstellungen mit Live-Umschaltung in **0 ms** und Backend-Synchronisation.
- **Sidebar-Lokalisierung**: Vollständig dynamisch mit `useTranslation()`.

---

## ✅ Verifikation & Build-Status

1. **Frontend-Build**:
   ```bash
   npm run build
   # ✓ built in 6.91s (0 Fehler)
   ```
2. **Backend-Tests**:
   ```bash
   python manage.py test accounts devices energy market forecast
   # Ran 15 tests in 11.801s -> OK
   ```
3. **Django System-Check**:
   ```bash
   python manage.py check
   # System check identified no issues (0 silenced).
   ```

