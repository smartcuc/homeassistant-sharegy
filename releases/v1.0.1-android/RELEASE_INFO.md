# 📦 Sharegy Release v1.0.1 (Android)

- **Release-Datum**: 11. September 2026
- **Version Name**: `1.0.1`
- **Version Code**: `2`
- **Min SDK**: 24 (Android 7.0+)
- **Target SDK**: 36 (Android 15+)
- **Package Name**: `de.sharegy.app`

---

## 📁 Gesicherte Binärdateien

| Datei | Größe | SHA-256 Prüfsumme |
| :--- | :--- | :--- |
| `app-release.aab` | 4.172.146 B (~4.17 MB) | `F928B6C1ED9EB185A4CD3C4EFAFFE7EC7DAC6C4D147BFB3D6FF15503BE061898` |
| `app-release.apk` | 4.306.991 B (~4.31 MB) | `C4871A245612E0AFCEE7E2CEF470744DC691C53FBFDCFB51EABB470014E535E4` |

---

## ✨ Neue Features & Fehlerbehebungen in v1.0.1
- **Capacitor Mobile API Base URL Fix**: Automatische Auflösung aller API-Aufrufe (`/api/...`) auf `https://sharegy.de` im Android-WebView. Behebt den Fehler `Unexpected token '<'`, der auftrat, wenn lokale Asset-Server `index.html` anstelle der Backend-API auslieferten.
- **Cross-Platform SVG Flaggen**: Vollständige, gestochen scharfe Vektorflaggen (DE, EN, PL, TR, RU, RO) ohne Abhängigkeit von Betriebssystem-Emoji-Fonts.
- **Admin-Sprachbeschränkung**: `/app/admin/*` und `/admin/*` sind strikt auf Deutsch und Englisch fokussiert mit automatischem Fallback.
- **Tracking & Telemetrie**: Behebung des 400 Bad Request im Event-Tracking und Bereitstellung der 7-Tage-Historie.
- **CORS & SameSite Cookies**: Backend-Unterstützung für `https://localhost`, `capacitor://localhost` und `SameSite=None`.

---

## 📖 Dokumentation & Play Store Leitfaden
Leitfaden zur Veröffentlichung in der Google Play Console:
👉 [docs/PLAY_STORE_RELEASE_AND_ACCOUNT_GUIDE.md](file:///c:/Users/Public/Dev/eswes/docs/PLAY_STORE_RELEASE_AND_ACCOUNT_GUIDE.md)
