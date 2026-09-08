# ⚡ Sharegy Platform — Entwickler- & System-Dokumentation

Willkommen in der offiziellen Dokumentation der **Sharegy**-Plattform (Smart Home Energy Management & Community Energy Sharing).

---

## 📚 Dokumentations-Übersicht

| Dokument | Beschreibung |
|---|---|
| 🏛️ **[`ARCHITECTURE.md`](./ARCHITECTURE.md)** | Gesamtsystem-Architektur, Dual-Core Konzept, Tech-Stack & Datenflüsse |
| 🗄️ **[`DATA_MODEL.md`](./DATA_MODEL.md)** | Vollständige Datenmodell-Referenz (EMS, Forecast, Market, Metering, Core) |
| ⚡ **[`EMS_SYSTEM_GUIDE.md`](./EMS_SYSTEM_GUIDE.md)** | Home Energy Management System: Telemetrie, Deadband-Filter, Flow-Engine & Sankey |
| 💶 **[`TARIFF_AND_MARKET.md`](./TARIFF_AND_MARKET.md)** | Stromtarife (Statisch / Dynamisch), EPEX Spot Börsenpreise & Tibber API-Integration |
| ☀️ **[`SOLAR_FORECAST.md`](./SOLAR_FORECAST.md)** | 96h Hybrid-Prognose (Open-Meteo Wetter, Physik-Modell & Random Forest ML) |
| 👥 **[`RBAC_AND_USER_MANAGEMENT_GUIDE.md`](./RBAC_AND_USER_MANAGEMENT_GUIDE.md)** | Multi-Tenant Rollen- & Berechtigungskonzept (Plattform & Energy Communities) |
| 📲 **[`NOTIFICATIONS_AND_MOBILE_PUSH.md`](./NOTIFICATIONS_AND_MOBILE_PUSH.md)** | Mobile Push & Notification Engine (W3C Web-Push, VAPID, Service Worker & Quiet Hours) |
| 🎫 **[`HELPDESK_MODULE_DOCUMENTATION.md`](./HELPDESK_MODULE_DOCUMENTATION.md)** | Support Desk, Ticket-System, ITIL-Prioritäten, Deflection & Factofy-Integration |
| 🚀 **[`OPERATIONS_AND_DEPLOYMENT.md`](./OPERATIONS_AND_DEPLOYMENT.md)** | Deployment Guide (Ubuntu/Pi), Systemd Services, Redis, Celery & Health-Checks |
| 🔍 **[`SHAREGY_CODEBASE_AUDIT_AND_FEATURE_EXPANSION.md`](./SHAREGY_CODEBASE_AUDIT_AND_FEATURE_EXPANSION.md)** | Codebase-Audit, Performancehebel, Bundle-Optimierung & Roadmap für neue strategische Features |
| 🛠️ **[`OPTIMIZATION_PLAN.md`](./OPTIMIZATION_PLAN.md)** | Audit-Ergebnisse, Stabilitäts-Härtung und abgeschlossene Meilensteine |
| 🗺️ **[`SHAREGY_STRATEGIC_ROADMAP.md`](./SHAREGY_STRATEGIC_ROADMAP.md)** | Strategische Produkt-Roadmap (EMS Pro, Smarte Laststeuerung, Energy Sharing) |
| 🎯 **[`SHAREGY_STRATEGIC_EVALUATION_AND_GAP_ANALYSIS.md`](./SHAREGY_STRATEGIC_EVALUATION_AND_GAP_ANALYSIS.md)** | Schonungslose Gesamtevaluation: Stärken, Schwachstellen, Mitbewerber-Vorteile & Masterplan |
| 🏆 **[`SHAREGY_COMPETITOR_BENCHMARK_AND_EVALUATION.md`](./SHAREGY_COMPETITOR_BENCHMARK_AND_EVALUATION.md)** | Detaillierter Mitbewerber-Vergleich (1Komma5°, Tibber, evcc, Exnaton, Clever-PV) & Matrix |
| 💰 **[`SHAREGY_FINANCIAL_VALUATION_AND_DEVELOPMENT_COSTS.md`](./SHAREGY_FINANCIAL_VALUATION_AND_DEVELOPMENT_COSTS.md)** | Finanzielle Bewertung, Substanzwert (Cost-to-Duplicate), SaaS ARR-Multiples & M&A-Wert |
| ⚡ **[`marketing/SHAREGY_FEATURE_CATALOG_AND_MARKETING_MATRIX.md`](./marketing/SHAREGY_FEATURE_CATALOG_AND_MARKETING_MATRIX.md)** | Gesamter Feature-Katalog & Marketing-Leistungsmatrix aller 15 Module |
| 📱 **[`ANDROID_APP_BUILD_AND_RELEASE.md`](./ANDROID_APP_BUILD_AND_RELEASE.md)** | Native Android App (Capacitor 7, Gradle Build, Deep Linking & Play Store Release) |
| 🛠️ **[`ANDROID_STUDIO_SETUP_GUIDE.md`](./ANDROID_STUDIO_SETUP_GUIDE.md)** | Schritt-für-Schritt Anleitung: Android Studio installieren, Emulator einrichten & App starten |
| 📋 **[`walkthroughs/`](./walkthroughs/README.md)** | Detaillierte Meilenstein- und Änderungsprotokolle der Entwicklung |
| 📱 **[`marketing/APP_TEASER.md`](./marketing/APP_TEASER.md)** | App Store Beschreibungen, Teaser-Texte und Marken-Farbkonzepte |


---

## ⚡ Schnellstart (Entwicklungsumgebung)

```bash
# 1. Repository klonen & Virtual Environment
cd eswes
python -m venv venv
.\venv\Scripts\activate  # Linux: source venv/bin/activate
pip install -r requirements.txt

# 2. Datenbank & Migrationen
python manage.py migrate

# 3. Demo-Haushalt initialisieren (Optional)
python manage.py rebuild_demo

# 4. Entwicklungsserver starten
# Terminal 1: Backend
python manage.py runserver 0.0.0.0:8000

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```
