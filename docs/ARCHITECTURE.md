# 🏛️ System-Architektur & Technologie-Stack

Sharegy basiert auf einer hochgradig performanten, asynchronen **Dual-Core-Architektur**:
1. **Säule 1: Home Energy Management System (EMS Free & Pro)** — Hochfrequente IoT-Telemetrie (1–15s), Echtzeit-Energiefluss, Visualisierung & automatische Laststeuerung für Privathaushalte.
2. **Säule 2: Energy Sharing Communities (ESC)** — Viertelstündliche iMSys-Zähler-Bilanzierung, lokale Peer-to-Peer Stromallokation & Quartiersabrechnung.

---

## 📐 Architektur-Diagramm

```
                           ┌──────────────────────────────────────────────┐
                           │               Frontend (React)               │
                           │  Vite • TailwindCSS • ECharts • React Query  │
                           └──────────────────────┬───────────────────────┘
                                                  │ REST API / WebSockets
                                                  ▼
                           ┌──────────────────────────────────────────────┐
                           │            Backend (Django ASGI)             │
                           │   Django REST Framework • Django Channels    │
                           └──────────────┬───────────────────────────────┘
                                          │
            ┌─────────────────────────────┼─────────────────────────────┐
            ▼                             ▼                             ▼
  ┌───────────────────┐         ┌───────────────────┐         ┌───────────────────┐
  │   Ingestion &     │         │   PostgreSQL /    │         │   Background &    │
  │   Live-Cache      │         │   TimescaleDB     │         │   Forecasting     │
  ├───────────────────┤         ├───────────────────┤         ├───────────────────┤
  │ • MQTT Broker     │         │ • Hypertables     │         │ • Celery Worker   │
  │ • Redis Pub/Sub   │         │ • Snapshot-Tables │         │ • Celery Beat     │
  │ • Deadband-Filter │         │ • Time-Series     │         │ • Open-Meteo 96h  │
  │ • OTel Receiver   │         │ • Composite PKeys │         │ • Random Forest ML│
  └───────────────────┘         └───────────────────┘         └───────────────────┘
```

---

## 🛠️ Technologie-Stack

### Backend
- **Framework**: Django 5.x / Python 3.12 (ASGI & WSGI).
- **API Layer**: Django REST Framework (DRF) mit Token- & Session-Authentifizierung.
- **Echtzeit**: Django Channels 4.x, WebSockets & Daphne ASGI Server.
- **Async & Worker**: Celery mit Redis als Broker & Result Backend.
- **Datenbank**: PostgreSQL 16 mit **TimescaleDB**-Erweiterung für Zeitreihen-Optimierung.
- **Caching**: Redis (Echtzeit-Telemetrie, Deadband-Cache, WebSockets Channel-Layer).

### Frontend
- **Framework**: React 18 / 19 mit Vite 6.x / Rolldown.
- **Routing**: React Router DOM (verschachtelte modulare Routen mit Auth-Guards).
- **State Management**: TanStack React Query v5 (Server-State, Caching & automatische Cache-Invalidierung).
- **Internationalisierung (i18n)**: `i18next` & `react-i18next` mit nativer Multi-Language Unterstützung (🇩🇪 Deutsch, 🇬🇧 English, 🇵🇱 Polski).
- **Charts & Visualisierung**: Apache ECharts via `echarts-for-react` (Sankey-Diagramm, Live-Sparklines, Spotpreis-Heatmaps).
- **Styling**: Tailwind CSS & dynamischer ThemeProvider.

### IoT & Ingestion
- **MQTT**: Paho MQTT Consumer Daemon (`core/management/commands/mqtt_consume.py`).
- **APIs**: OpenTelemetry OTLP/HTTP Metrics Receiver, Tibber GraphQL Client, SMARD / Energy-Charts Börsenpreis-Fetcher.
