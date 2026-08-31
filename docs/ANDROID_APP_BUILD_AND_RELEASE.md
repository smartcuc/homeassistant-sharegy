# 📱 Native Android App: Build, Testing & Release Guide

**App-Name**: Sharegy  
**Package-ID**: `de.sharegy.app`  
**Framework**: Capacitor 7 / React / Tailwind  
**Status**: Initialisiert & Synchronisiert (v3.3)  
**Task-Referenz**: Task 2.22 (Roadmap) / Task 5.10 (Optimization Plan)

---

## 🏗️ 1. Architektur & Projektstruktur

Das native Android-Projekt liegt direkt im Frontend-Verzeichnis unter `frontend/android/`:

```
frontend/
  ├── capacitor.config.json    # Capacitor-Konfiguration (App ID, Splashscreen, Statusbar)
  ├── android/                 # Natives Android Studio Gradle-Projekt
  │    ├── app/
  │    │    ├── src/main/
  │    │    │    ├── AndroidManifest.xml   # Berechtigungen & Deep Links (https://sharegy.de/t/*)
  │    │    │    ├── java/de/sharegy/app/  # MainActivity.java
  │    │    │    └── res/                  # App-Icons, Mipmaps & Styles
  │    │    └── build.gradle               # App-Level Build-Konfiguration (minSdkVersion 24, targetSdk 35)
  │    ├── build.gradle                    # Project-Level Gradle
  │    └── gradlew / gradlew.bat           # Gradle Wrapper
  └── src/utils/nativeBridge.js # Status Bar, Splash Screen, Back-Button & Haptics
```

---

## ⚡ 2. Entwickler-Workflows

### Frontend-Änderungen in die Android-App übertragen:
Jedes Mal, wenn React-Code oder Designs geändert werden:
```bash
cd frontend
npm run cap:sync
```
*Dieser Befehl baut das Web-Bundle (`vite build`) und kopiert die Assets sowie Plugin-Bindings automatisch in den nativen Android-Ordner.*

---

## 🛠️ 3. APK & App-Bundle (AAB) bauen

### Option A: Über Android Studio (Empfohlen für Debugging & Emulatoren)
1. Öffne das Android-Projekt:
   ```bash
   cd frontend
   npx cap open android
   ```
2. Android Studio startet und lädt die Gradle-Abhängigkeiten.
3. Klicke oben auf **▶️ Run 'app'**, um die App direkt auf deinem per USB angeschlossenen Android-Smartphone oder Emulator auszuführen.

### Option B: Direkt über die Kommandozeile (Debug-APK bauen)
```bash
cd frontend/android
./gradlew assembleDebug      # Unter Windows: gradlew.bat assembleDebug
```
Die fertige APK liegt anschließend unter:  
`frontend/android/app/build/outputs/apk/debug/app-debug.apk`

---

## 🌐 4. Deep-Linking (Magic Links & Alarme)

In `AndroidManifest.xml` ist bereits der standardkonforme Android App-Link Intent-Filter hinterlegt:
* Klickt ein Nutzer in einer E-Mail auf `https://sharegy.de/t/<token>`, fängt Android den Link ab und öffnet die Sharegy App **direkt**, ohne den externen Browser zu starten.
* Klickt ein Nutzer auf eine Push-Benachrichtigung (`/app/alerts`), navigiert die App direkt zur Alarmzentrale.

---

## 🚀 5. Google Play Store Release (AAB)

Für die Veröffentlichung im Play Store:
1. Versionsnummer in `frontend/android/app/build.gradle` inkrementieren (`versionCode` und `versionName`).
2. Release-Bundle erzeugen:
   ```bash
   cd frontend/android
   ./gradlew bundleRelease    # Windows: gradlew.bat bundleRelease
   ```
3. Die signierte Datei unter `frontend/android/app/build/outputs/bundle/release/app-release.aab` in der Google Play Console hochladen.
