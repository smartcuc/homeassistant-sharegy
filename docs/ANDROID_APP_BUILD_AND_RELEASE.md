# 📱 Native Android App: Build, Testing & Release Guide

**App-Name**: Sharegy  
**Package-ID**: `de.sharegy.app`  
**Framework**: Capacitor 7 / React / Tailwind CSS  
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

## 💻 2. Setup auf einem neuen Rechner (Host-PC)

Wenn du das Projekt auf einen anderen PC (z. B. außerhalb einer VM) kopiert hast, befolge diese Schritte zur Ersteinrichtung:

### A. Voraussetzungen installieren
1. **Node.js (LTS Version 20 oder 22)**: [nodejs.org](https://nodejs.org)
   * Prüfen im Terminal: `node -v` und `npm -v`
2. **Java JDK 17 oder 21** (z. B. Eclipse Temurin): [adoptium.net](https://adoptium.net)
   * Prüfen im Terminal: `javac -version`
3. **Android Studio**: [developer.android.com/studio](https://developer.android.com/studio)
   * Beim ersten Start den Setup-Assistenten ausführen, damit das **Android SDK**, die **SDK Platform-Tools** und die **Build-Tools** (API 34/35) installiert werden.

### B. Projekt initialisieren & synchronisieren
Öffne ein Terminal (PowerShell / CMD) im Projektordner:

```bash
# 1. In das Frontend-Verzeichnis wechseln
cd frontend

# 2. Alle Node-Abhängigkeiten installieren
npm install

# 3. Web-Bundle bauen und in das Android-Projekt synchronisieren
npm run cap:sync
```

> **Was macht `npm run cap:sync`?**  
> Es baut den React-Code (`vite build`) und kopiert die kompilierte Web-App sowie alle nativen Capacitor-Plugins automatisch in das native Android-Projekt (`frontend/android/app/src/main/assets/public`).

---

## ⚡ 3. Entwickler-Workflows & Code-Updates

Jedes Mal, wenn React-Code, Styling oder Übersetzungen geändert werden:
```bash
cd frontend
npm run cap:sync
```

---

## 🛠️ 4. APK bauen & testen

### Option A: Über Android Studio (Empfohlen für Live-Testing & Emulatoren)
1. Öffne das Android-Projekt:
   ```bash
   cd frontend
   npx cap open android
   ```
   *(Oder starte Android Studio manuell und öffne den Ordner `frontend/android`).*
2. Warte kurz, bis die Gradle-Synchronisation (Statusbalken unten) abgeschlossen ist.
3. **Auf echtem Smartphone testen:**
   * Aktiviere auf dem Handy die **Entwickleroptionen** und das **USB-Debugging**.
   * Schließe das Handy per USB-Kabel an den PC an.
   * Wähle dein Gerät oben in der Geräteliste von Android Studio aus.
   * Klicke auf den grünen **▶️ Run 'app'** Button.

---

### Option B: Direkt über die Konsole (Debug-APK bauen)
Falls du schnell eine `.apk`-Datei zum manuellen Installieren benötigst:

```powershell
# In den nativen Android-Ordner wechseln
cd frontend/android

# Debug-APK unter Windows bauen:
.\gradlew.bat assembleDebug

# Unter macOS / Linux:
./gradlew assembleDebug
```

Die fertige APK-Datei liegt anschließend unter:  
📁 `frontend/android/app/build/outputs/apk/debug/app-debug.apk`

---

## 🌐 5. Deep-Linking (Magic Links & Alarme)

In `AndroidManifest.xml` ist bereits der standardkonforme Android App-Link Intent-Filter hinterlegt:
* Klickt ein Nutzer in einer E-Mail auf `https://sharegy.de/t/<token>`, fängt Android den Link ab und öffnet die Sharegy App **direkt**, ohne den externen Browser zu starten.
* Klickt ein Nutzer auf eine Push-Benachrichtigung (`/app/alerts`), navigiert die App direkt zur Alarmzentrale.

---

## 🚀 6. Google Play Store Release (AAB Bundle)

Für die Veröffentlichung im Google Play Store verlangt Google das **Android App Bundle (.aab)** Format:

### Option A: Über Android Studio (Grafisch signieren)
1. Menüleiste: **Build** ➔ **Generate Signed Bundle / APK...**
2. Wähle **Android App Bundle** ➔ **Next**.
3. **Key store path:**
   * Falls du noch keinen Keystore hast: Klicke auf **Create new...**, wähle einen sicheren Speicherort und erstelle deinen Signaturschlüssel (Passwort gut merken & Keystore sichern!).
   * Falls vorhanden: Wähle deinen `.jks` Keystore aus.
4. Wähle als Build-Variante **release**.
5. Klicke auf **Create**.

### Option B: Über die Kommandozeile
1. Versionsnummer in `frontend/android/app/build.gradle` inkrementieren (`versionCode` und `versionName`).
2. Release-Bundle erzeugen:
   ```powershell
   cd frontend/android
   .\gradlew.bat bundleRelease
   ```

### Speicherort der fertigen Play-Store-Datei:
📁 `frontend/android/app/build/outputs/bundle/release/app-release.aab`

Diese `.aab`-Datei kann direkt in der **Google Play Console** hochgeladen werden.

---

## 💡 7. Typische Stolperfallen & Lösungen

* **Fehler: `SDK location not found`:**  
  Erstelle im Ordner `frontend/android/` eine Datei `local.properties` mit dem Pfad zu deinem Android SDK (Pfade mit doppeltem Backslash formatieren):
  ```properties
  sdk.dir=C\:\\Users\\DEIN_BENUTZERNAME\\AppData\\Local\\Android\\Sdk
  ```
* **Fehler: `JAVA_HOME is not set`:**  
  Setze in deinen Windows-Umgebungsvariablen `JAVA_HOME` auf das Installationsverzeichnis deines JDKs (z. B. `C:\Program Files\Eclipse Adoptium\jdk-17...`).
