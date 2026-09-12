# 📱 Native Android App: Entwicklungs-, Build- & Release-Guide

**App-Name**: Sharegy  
**Package-ID**: `de.sharegy.app`  
**Framework**: Capacitor 7 / React / Vite / Tailwind CSS  
**Target-SDK**: Android 15 (API 35) | **Min-SDK**: Android 7.0 (API 24)  
**Stand**: 12. September 2026 (v5.3 / Play Store Ready)  

---

## 🏗️ 1. Architektur & Projektstruktur

Das native Android-Projekt liegt direkt im Frontend-Verzeichnis unter `frontend/android/`:

```
frontend/
  ├── capacitor.config.json    # Capacitor-Konfiguration (App ID, Splashscreen, Statusbar, FCM)
  ├── android/                 # Natives Android Studio Gradle-Projekt
  │    ├── app/
  │    │    ├── src/main/
  │    │    │    ├── AndroidManifest.xml   # Berechtigungen & Deep Links (https://sharegy.de/t/*)
  │    │    │    ├── java/de/sharegy/app/  # MainActivity.java
  │    │    │    └── res/                  # App-Icons, Mipmaps & Styles
  │    │    └── build.gradle               # App-Level Build (minSdk 24, targetSdk 35)
  │    ├── build.gradle                    # Project-Level Gradle
  │    └── gradlew / gradlew.bat           # Gradle Wrapper
  └── src/utils/nativeBridge.js # Status Bar, Splash Screen, Back-Button, Haptics & FCM
```

---

## 💻 2. Lokale Entwicklungsumgebung & Setup

### A. Voraussetzungen
1. **Node.js (LTS 20 oder 22)**: [nodejs.org](https://nodejs.org)
2. **Java JDK 17 oder 21** (z. B. Eclipse Temurin): [adoptium.net](https://adoptium.net)
   * `JAVA_HOME` Umgebungsvariable setzen.
3. **Android Studio**: [developer.android.com/studio](https://developer.android.com/studio)
   * Im SDK Manager (Tools -> SDK Manager): **Android SDK Platform 35** und **Android SDK Build-Tools 35** installieren.

### B. Initialisierung & Synchronisation
```bash
# 1. In das Frontend wechseln
cd frontend

# 2. Abhängigkeiten installieren
npm install

# 3. Web-Bundle bauen und in Android synchronisieren
npm run cap:sync
```

---

## 🚀 3. Starten & Testen (Emulator & Echtes Smartphone)

### Option A: Android Studio GUI
1. Starte **Android Studio** und öffne den Ordner `frontend/android`.
2. Warte, bis der Gradle-Sync abgeschlossen ist.
3. Wähle oben im Dropdown ein virtuelles Device (AVD Emulator) oder dein angeschlossenes Android-Smartphone (USB-Debugging aktiviert) aus.
4. Klicke auf das grüne **Play-Symbol** (Run).

### Option B: Terminal-Befehle
```bash
# Android Studio direkt aus dem Projekt öffnen:
npm run cap:open

# Live-Reload für die Entwicklung:
npm run cap:run
```

---

## 📦 4. Release Build & Signierung (Google Play Store)

### A. Release Android App Bundle (.aab) erzeugen
```bash
cd frontend/android
./gradlew bundleRelease
```
Das fertige Bundle liegt unter:  
`frontend/android/app/build/outputs/bundle/release/app-release.aab`

### B. Keystore & Signierung
Für Produktiv-Releases wird der Keystore in `frontend/android/keystore/sharegy-release.jks` hinterlegt und über `gradle.properties` bzw. Umgebungsvariablen eingebunden:
```properties
RELEASE_STORE_FILE=keystore/sharegy-release.jks
RELEASE_STORE_PASSWORD=***
RELEASE_KEY_ALIAS=sharegy-key
RELEASE_KEY_PASSWORD=***
```

---

## 🔔 5. Native Integrationen

1. **Firebase Cloud Messaging (FCM)**: Push-Nachrichten für Alarme, negative Strompreise und monatliche Einsparungs-Recaps (Details in [`docs/mobile/NOTIFICATIONS_AND_MOBILE_PUSH.md`](file:///c:/Users/Public/Dev/eswes/docs/mobile/NOTIFICATIONS_AND_MOBILE_PUSH.md)).
2. **Deep Linking**: Öffnen von Einladungs-Links (`https://sharegy.de/t/invitation-token`) direkt in der App.
3. **Hardware Back-Button**: Intelligentes Navigieren im React-Router ohne unbeabsichtigtes Schließen der App.
4. **Haptisches Feedback & Status Bar**: Dynamische Anpassung an Dark/Light Mode.

---

## 🛒 6. Google Play Store Release
Für das Veröffentlichen im Google Play Store (D-U-N-S Verifikation, Datenschutzangaben, 20-Tester-Phase) siehe den vollständigen Leitfaden in [`docs/mobile/PLAY_STORE_RELEASE_AND_ACCOUNT_GUIDE.md`](file:///c:/Users/Public/Dev/eswes/docs/mobile/PLAY_STORE_RELEASE_AND_ACCOUNT_GUIDE.md).
