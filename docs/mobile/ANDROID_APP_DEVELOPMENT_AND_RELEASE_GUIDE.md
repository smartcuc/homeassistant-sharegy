# 📱 Native Android Apps: Entwicklungs-, Build- & Release-Guide

**Projekt**: Sharegy Mobile Ecosystem  
**Architektur**: Dual-Flavor Native Builds (Home & Pro)  
**Framework**: Capacitor 8 / React 19 / Vite / Tailwind CSS  
**Target-SDK**: Android 15/16 (API 35/36) | **Min-SDK**: Android 7.0 (API 24)  
**Stand**: September 2026 (v1.0.2 / Dual Flavor Production Ready)  

---

## 🎯 1. Dual-Flavor Architektur (Home vs. Pro)

Sharegy wird aus einer gemeinsamen Web-/React-Codebasis in zwei eigenständige, dedizierte Android-Apps mit getrennten Bundle-IDs, Splashscreens, Konfigurationen und Zielgruppen ausgeliefert:

| Eigenschaft | 🏠 Sharegy Home | 🏢 Sharegy Pro |
| :--- | :--- | :--- |
| **Zielgruppe** | Privathaushalte, Mieterstrom, PV-Heimspeicher | Gewerbe, Industrie, Großverbraucher, § 14a EnWG |
| **Package-ID (AppId)** | `de.sharegy.app` | `de.sharegy.pro` |
| **App-Name** | **Sharegy Home** | **Sharegy Pro** |
| **Natives Verzeichnis** | `frontend/android-home/` | `frontend/android-pro/` |
| **Capacitor-Config** | `frontend/capacitor.home.json` | `frontend/capacitor.pro.json` |
| **Vite Build-Modus** | Standard (`vite build`) | Pro Mode (`vite build --mode pro`) |
| **Primäres Theme / Splash** | Dark Slate (`#0F172A`) | Dark Obsidian (`#090D16`) |

---

## 🏗️ 2. Projektstruktur

```
frontend/
  ├── capacitor.home.json       # Flavor-Config für Sharegy Home (de.sharegy.app)
  ├── capacitor.pro.json        # Flavor-Config für Sharegy Pro (de.sharegy.pro)
  ├── capacitor.config.json     # Generiert/übernommen durch Synchronisations-Skript
  │
  ├── scripts/
  │    ├── cap-sync-flavor.js   # Synchronisiert Web-Assets in das Ziel-Verzeichnis
  │    └── cap-open-flavor.js   # Öffnet das jeweilige Projekt in Android Studio
  │
  ├── android-home/             # Natives Android Studio Gradle-Projekt (Sharegy Home)
  │    ├── app/
  │    │    ├── src/main/       # AndroidManifest.xml (de.sharegy.app), Assets, Icons
  │    │    └── build.gradle    # App-Level Build (versionCode, versionName, signingConfigs)
  │    ├── key.properties       # Optionale Keystore-Konfiguration für Release-Signierung
  │    └── gradlew / gradlew.bat
  │
  ├── android-pro/              # Natives Android Studio Gradle-Projekt (Sharegy Pro)
  │    ├── app/
  │    │    ├── src/main/       # AndroidManifest.xml (de.sharegy.pro), Assets, Icons
  │    │    └── build.gradle    # App-Level Build (versionCode, versionName, signingConfigs)
  │    ├── key.properties       # Optionale Keystore-Konfiguration für Release-Signierung
  │    └── gradlew / gradlew.bat
  │
  └── src/utils/nativeBridge.js # Status Bar, Splash Screen, Back-Button, Haptics & FCM
```

---

## 💻 3. Lokale Entwicklungsumgebung & Setup

### A. Voraussetzungen
1. **Node.js (LTS 20 oder 22)**: [nodejs.org](https://nodejs.org)
2. **Java JDK 17 oder 21** (z. B. Eclipse Temurin oder Android Studio Bundled JBR):
   * `JAVA_HOME` Umgebungsvariable setzen (z. B. `C:\Program Files\Android\Android Studio\jbr`).
3. **Android Studio & SDK**:
   * Im SDK Manager: **Android SDK Platform 35/36** und **Build-Tools 35/36** installieren.
   * `ANDROID_HOME` setzen (z. B. `%LOCALAPPDATA%\Android\Sdk`).

### B. Initialisierung & Synchronisation

Alle Aktionen werden aus dem Verzeichnis `frontend/` ausgeführt:

```bash
cd frontend

# Abhängigkeiten installieren
npm install

# --- 🏠 SHAREGY HOME SYNCHRONISIEREN ---
npm run cap:home:sync

# --- 🏢 SHAREGY PRO SYNCHRONISIEREN ---
npm run cap:pro:sync
```

> [!NOTE]
> Das Flavor-Skript (`scripts/cap-sync-flavor.js`) kopiert die entsprechende `capacitor.[flavor].json` nach `capacitor.config.json` und stößt danach `npx cap sync android` für das jeweilige Verzeichnis an.

---

## 🚀 4. Starten & Testen (Emulator & Smartphone)

### Option A: Android Studio GUI
Du kannst das gewünschte Flavor direkt in Android Studio öffnen:

```bash
# Öffnet Sharegy Home in Android Studio:
npm run cap:home:open

# Öffnet Sharegy Pro in Android Studio:
npm run cap:pro:open
```

1. Warte, bis der Gradle-Sync abgeschlossen ist.
2. Wähle oben im Device-Dropdown dein Smartphone (USB-Debugging aktiv) oder einen AVD-Emulator aus.
3. Klicke auf das grüne **Play-Symbol** (Run).

### Option B: Schneller Dev-Build via Gradle CLI
```bash
# Home Debug APK erstellen und installieren:
cd frontend/android-home
./gradlew installDebug

# Pro Debug APK erstellen und installieren:
cd frontend/android-pro
./gradlew installDebug
```

---

## 📦 5. Build & Release Workflows

### A. Release-Pakete via CLI erstellen

#### 1. Sharegy Home (`de.sharegy.app`)
```bash
# 1. Frontend bauen & nach android-home synchronisieren:
cd frontend
npm run cap:home:sync

# 2. Release APK bauen:
cd android-home
./gradlew assembleRelease

# 3. Play Store AAB Bundle bauen:
./gradlew bundleRelease
```

**Erzeugte Artefakte:**
* **Release APK**: `frontend/android-home/app/build/outputs/apk/release/app-release.apk`
* **Release AAB**: `frontend/android-home/app/build/outputs/bundle/release/app-release.aab`

---

#### 2. Sharegy Pro (`de.sharegy.pro`)
```bash
# 1. Frontend mit Pro-Mode bauen & nach android-pro synchronisieren:
cd frontend
npm run cap:pro:sync

# 2. Release APK bauen:
cd android-pro
./gradlew assembleRelease

# 3. Play Store AAB Bundle bauen:
./gradlew bundleRelease
```

**Erzeugte Artefakte:**
* **Release APK**: `frontend/android-pro/app/build/outputs/apk/release/app-release.apk`
* **Release AAB**: `frontend/android-pro/app/build/outputs/bundle/release/app-release.aab`

---

### B. Keystore & Signierung (`key.properties`)

Beide Projekte verfügen über ein automatisches Signierungs-Fallback:
* Wenn **`key.properties`** existiert, wird der Release-Build mit dem hinterlegten Produktions-Keystore signiert.
* Wenn **keine `key.properties`** vorhanden ist, nutzt Gradle automatisch die Debug-Signatur, sodass APKs direkt auf Testgeräten ohne manuelle Signierung installiert werden können.

**Beispiel `key.properties` (in `android-home/` bzw. `android-pro/`):**
```properties
storeFile=../keystore/sharegy-release.jks
storePassword=dein_keystore_passwort
keyAlias=sharegy-key
keyPassword=dein_key_passwort
```

---

### C. Versionierung
Die Versionen werden in der jeweiligen `app/build.gradle` gepflegt:
```groovy
defaultConfig {
    applicationId "de.sharegy.app" // bzw. "de.sharegy.pro"
    minSdkVersion rootProject.ext.minSdkVersion
    targetSdkVersion rootProject.ext.targetSdkVersion
    versionCode 3       // Inkrementelle Ganzzahl für Google Play
    versionName "1.0.2" // SemVer Version für Nutzer
}
```

---

## 🔔 6. Native Features & Bridge-Integration

1. **Native Bridge (`src/utils/nativeBridge.js`)**:
   - Initialisierung von SplashScreen (automatisch nach 1,5s ausgeblendet)
   - Dynamic Status Bar (Dark Backgrounds, Light Icons)
   - Hardware Back-Button Handling für React Router Navigation
   - Haptisches Feedback bei User-Interaktionen
2. **Push Notifications (FCM)**:
   - Benachrichtigungen bei negativen Strompreisen, Einspeisespitzen und Systemalarmen.
3. **Deep Linking**:
   - Direkte Navigation über Einladungs- und Sharing-Links (`https://sharegy.de/t/*`).
4. **Responsive Layouts**:
   - Automatische Erkennung von Smartphone- vs. Tablet-Viewports.
   - Sankey- und Flussdiagramme passen sich dynamisch der Bildschirmbreite an (Querformat auf Smartphones bleibt im kompakten Mobile-Layout; Sidebar aktiviert erst ab Tablet-Auflösung ≥ 1024px).

---

## 🛒 7. Google Play Store Release-Checkliste

1. **Version Code & Name** in `app/build.gradle` inkrementieren.
2. Web-Bundle & Sync durchführen: `npm run cap:home:sync` bzw. `npm run cap:pro:sync`.
3. Release Bundle erstellen: `./gradlew bundleRelease`.
4. Die generierte `.aab`-Datei in der [Google Play Console](https://play.google.com/console) in den internen Test- oder Produktions-Track hochladen.
5. Versionshinweise (Release Notes in DE/EN) hinterlegen und Release freigeben.
