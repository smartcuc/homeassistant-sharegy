# 🛠️ Sharegy Optimierungs-, Audit- & Backlog-Masterplan

**Dokument-Status:** Konsolidierter Audit-Status & Entwicklungs-Backlog  
**Stand:** 12. September 2026 (v5.3 / Post-Meilenstein 9)  

---

## 📊 1. Status-Zusammenfassung aller Audit- & Optimierungs-Meilensteine

Alle wesentlichen Härtungs-, Skalierungs- und Feature-Erweiterungen aus den vorangegangenen System-Audits wurden erfolgreich abgeschlossen:

| Meilenstein / Bereich | Vorheriger Status | Aktueller Status (v5.3) | Implementierte Kernkomponenten |
|---|:---:|:---:|---|
| **M1: Core HEMS & Telemetrie-Härtung** | 🟡 In Progress | 🟢 **100% Live** | TimescaleDB Hypertables, Deadband-Filter, $O(1)$ LatestMetric-Snapshots, Decompression-Fix. |
| **M2: Live Flow & Sankey-Engine** | 🟡 In Progress | 🟢 **100% Live** | ECharts/SVG Sankey, Merit-Order Flussverteilung, Restlast-Disaggregation. |
| **M3: Smart Autopilot & Dispatch Hub** | 🟡 In Progress | 🟢 **100% Live** | 4 Autopilot-Modi, BWWP SG-Ready Anti-Cycling Schutz, Live Power Budgeting, Surplus Waterfall. |
| **M4: Spotpreise & Batterie-Arbitrage** | 🟡 In Progress | 🟢 **100% Live** | 7-Tage EPEX Trend, dynamische Tarife, 96h Solar- & Lastprognose mit Random Forest ML. |
| **M5: 6-Sprachen i18n & Globalisierung** | 🔴 Offen | 🟢 **100% Live** | Vollständiges i18n für DE, EN, PL, FR, IT, ES mit automatischem Fallback und Translation-Sync. |
| **M6: UI/UX & Responsive Redesign** | 🔴 Offen | 🟢 **100% Live** | Glassmorphic Dark/Light Mode, Mobile Topbar, Drawer & Bottom-Nav, Zero-Layout-Shift. |
| **M7: Multi-Cloud-Inverter Ökosystem** | 🔴 Offen | 🟢 **100% Live** | Sungrow, Fronius, SMA, SolarEdge, Huawei, Deye, Hoymiles, GoodWe, Kostal, Victron API v2. |
| **M8: Native Android App & Store Ready** | 🔴 Offen | 🟢 **100% Live** | Capacitor 7 Native Shell, Fastlane Release Pipeline, FCM Push, Deep Linking. |
| **M9: B2B Whitelabel & AS4 Mako Hub** | 🔴 Offen | 🟢 **100% Live** | Partner-Flottencockpit, Dynamic Theming Engine, BNetzA EDIFACT MSCONS/UTILMD Generator. |

---

## 🔮 2. Aktives Strategie- & Entwicklungs-Backlog (Dedicated WIP Specs)

Jedes anstehende Feature wird in einer eigenständigen Spezifikation im Ordner `docs/wip/` geführt:

1. 🔌 **[`WIP_DECOUPLED_MONITORING_CLUSTER_AND_REVERSE_RPC.md`](./WIP_DECOUPLED_MONITORING_CLUSTER_AND_REVERSE_RPC.md)**
   * **Ziel**: Physische Ausgliederung des WSS-Ingress- und Reverse-RPC-Gateways auf `mon.sharegy.de` für unterbrechungsfreie Deployments und Zero-Trust Edge-Wartung.
   * **Status & Prio**: 🟡 50 % | 🔴 Hoch (Nächster Sprint)

2. 🏠 **[`WIP_EEBUS_AND_CLOUD_ECOSYSTEM_BRIDGE.md`](./WIP_EEBUS_AND_CLOUD_ECOSYSTEM_BRIDGE.md)**
   * **Ziel**: Anbindung von Wärmepumpen (myVAILLANT, ViCare) und Haushaltsgeräten (BSH Home Connect) über Cloud-APIs und EEBUS SHIP/SPINE Stack.
   * **Status & Prio**: 🟡 40 % | 🔴 Hoch (Q4 2026 / Q1 2027)

3. ⚡ **[`WIP_BNETZA_CLS_SMART_METER_GATEWAY.md`](./WIP_BNETZA_CLS_SMART_METER_GATEWAY.md)**
   * **Ziel**: Gesetzeskonforme Dimm- und Steuerbefehle nach § 14a EnWG direkt über den Controllable Local System (CLS) Kanal des SMGW empfangen.
   * **Status & Prio**: 🟡 40 % | 🔴 Hoch (Q1 / Q2 2027)

4. 🔒 **[`WIP_DYNAMIC_WHITELABEL_SSL_PROVISIONING.md`](./WIP_DYNAMIC_WHITELABEL_SSL_PROVISIONING.md)**
   * **Ziel**: Automatische Let's Encrypt SSL-Zertifikatsausstellung für B2B Custom Domains (CNAME) via Caddy/Traefik On-Demand TLS.
   * **Status & Prio**: 🟡 70 % | 🟡 Mittel (Q4 2026)

5. 📈 **[`WIP_AUTOMATED_FLEXIBILITY_AND_VPP_MARKET_CLEARING.md`](./WIP_AUTOMATED_FLEXIBILITY_AND_VPP_MARKET_CLEARING.md)**
   * **Ziel**: Vollautomatisierte Vermarktung gepoolter Heimspeicher an den aFRR/SRL- und Intraday-Märkten über Aggregatoren mit automatischem Erlös-Clearing.
   * **Status & Prio**: 🟡 60 % | 🟡 Mittel (Q2 / Q3 2027)

6. 📱 **[`WIP_DUAL_APP_ECOSYSTEM_USER_VS_PARTNER.md`](./WIP_DUAL_APP_ECOSYSTEM_USER_VS_PARTNER.md)**
   * **Ziel**: Evaluierung und Roadmap für das Two-App Ökosystem (`Sharegy Home` für Endkunden vs. `Sharegy Pro` für Installateure/Admins).
   * **Status & Prio**: 🟡 50 % | 🟡 Mittel (Q1 2027)

