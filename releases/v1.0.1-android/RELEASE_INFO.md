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
| `app-release.aab` / `sharegy-v1.0.1-release.aab` | 4.176.398 B (~4.18 MB) | `E912A509280A4220E3A1EDE2A5E8A0FF6EBB336CB52FC5C6D3E5D361F6227A29` |
| `app-release.apk` / `sharegy-v1.0.1-release.apk` | 4.311.227 B (~4.31 MB) | `0B92E3556EF02FD67A1EC7E087F0D37D2C4E3C03947F9F64430B51CA20790FEC` |

---

## ✨ Neue Features & Fehlerbehebungen in v1.0.1
- **Intelligente Magic-Link & Code-Erkennung (Web vs. App)**:
  - **Browser / Web-Anforderung**: Sendet die klassische, saubere und minimalistische Magic-Link-E-Mail mit einem einzigen prominenten Login-Button (*„⚡ Jetzt bei Sharegy einloggen“*) ohne störende App-Codes oder Buttons.
  - **Smartphone App-Anforderung**: Sendet eine speziell für die mobile App optimierte E-Mail mit großem 6-stelligen Login-Code (*zum schnellen Eintippen in der App*) und direktem Deep-Link-Button (*„📱 In der Sharegy App öffnen“*).
  - **Automatische Client-Erkennung**: Das Backend und Frontend erkennen über native Plattform-Flags (`client: "app" | "web"`) und Header automatisch die Quelle der Anfrage.
- **Mobile Responsive Layout & Topbar Fix**:
  - **Topbar User-Menü / Profil sichtbar**: Der Live-Ticker wird auf Smartphone-Bildschirmen kompakt ausgeblendet bzw. auf Tablets/Desktop verlagert, Abstände wurden mobiloptimiert, sodass Profil und Benachrichtigungs-Glocke auf keinem Bildschirm mehr rechts abgeschnitten werden.
  - **Smart Energy Optimizer Timeline Overflow Fix**: Das Verlaufsdiagramm im Smart Energy Optimizer bricht auf Smartphones nicht mehr rechts über die Kachelkante hinaus, sondern ist mit butterweichem horizontalem Scrollen und responsiven Mindestbreiten sauber gekapselt.
  - **Transparenz bei Festpreis-Tarifen im Börsenpreis-Modal**: Nutzer mit fixen Stromtarifen (flache Endpreis-Linie) sehen nun einen erklärenden Hinweis mit direkter Wechselmöglichkeit zu dynamischen Tarifen.
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
