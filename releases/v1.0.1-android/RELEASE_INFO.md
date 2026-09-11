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
| `app-release.aab` / `sharegy-v1.0.1-release.aab` | 4.175.958 B (~4.18 MB) | `1F2BD292EA0C0018B5459804D2501690CE391C03443D297058ECEA20739714DE` |
| `app-release.apk` / `sharegy-v1.0.1-release.apk` | 4.310.739 B (~4.31 MB) | `BD446E0A56F370BAA020F65FA0B6761371C03FE7259DA50A24DBA821208B7DDD` |

---

## ✨ Neue Features & Fehlerbehebungen in v1.0.1
- **Frictionless Mobile App Login (Magic Link & 6-Digit OTP Code)**:
  - **6-stelliger Login-Code**: In der E-Mail wird neben dem Link ein 6-stelliger Einmal-Code prominent dargestellt, der direkt in der Sharegy App eingegeben oder eingefügt werden kann.
  - **Deep-Linking & Custom Scheme (`sharegy://`)**: Direkter Start der Android App beim Klick auf *"In der Sharegy App öffnen"* aus E-Mails oder Browser.
  - **Digital Asset Links (`/.well-known/assetlinks.json`)**: Android App Links Unterstützung mit SHA-256 Signatur-Verifikation.
- **Capacitor Mobile API Base URL Fix**: Automatische Auflösung aller API-Aufrufe (`/api/...`) auf `https://sharegy.de` im Android-WebView. Behebt den Fehler `Unexpected token '<'`, der auftrat, wenn lokale Asset-Server `index.html` anstelle der Backend-API auslieferten.
- **Cross-Platform SVG Flaggen**: Vollständige, gestochen scharfe Vektorflaggen (DE, EN, PL, TR, RU, RO) ohne Abhängigkeit von Betriebssystem-Emoji-Fonts.
- **Admin-Sprachbeschränkung**: `/app/admin/*` und `/admin/*` sind strikt auf Deutsch und Englisch fokussiert mit automatischem Fallback.
- **Tracking & Telemetrie**: Behebung des 400 Bad Request im Event-Tracking und Bereitstellung der 7-Tage-Historie.
- **CORS & SameSite Cookies**: Backend-Unterstützung für `https://localhost`, `capacitor://localhost` und `SameSite=None`.

---

## 📖 Dokumentation & Play Store Leitfaden
Leitfaden zur Veröffentlichung in der Google Play Console:
👉 [docs/PLAY_STORE_RELEASE_AND_ACCOUNT_GUIDE.md](file:///c:/Users/Public/Dev/eswes/docs/PLAY_STORE_RELEASE_AND_ACCOUNT_GUIDE.md)
