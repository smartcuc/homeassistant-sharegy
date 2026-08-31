# 📱 Schritt-für-Schritt Anleitung: Android Studio einrichten & Sharegy App starten

Diese Anleitung führt dich Schritt für Schritt durch die Installation von **Android Studio**, das Einrichten eines virtuellen Test-Smartphones (Emulator) oder echten Android-Handys und den Start der **Sharegy Android App**.

---

## 📥 Schritt 1: Android Studio herunterladen & installieren

1. **Download**:
   * Gehe auf die offizielle Website: 👉 **[https://developer.android.com/studio](https://developer.android.com/studio)**
   * Klicke auf **„Download Android Studio“** (die aktuelle Version, z. B. *Quail / Ladybug*).
2. **Installation unter Windows**:
   * Starte die heruntergeladene `.exe`-Datei.
   * Wähle im Setup-Assistenten die Standardoptionen (inkl. **Android Virtual Device**).
   * Klicke auf **Next** und schließe die Installation ab.
3. **Erster Start & SDK-Download**:
   * Öffne Android Studio nach der Installation.
   * Wähle beim Setup-Typ **„Standard“** aus.
   * Android Studio lädt nun automatisch das aktuelle **Android SDK**, die **Platform-Tools** und den **Emulator** herunter (ca. 1–2 GB).
   * Klicke nach Abschluss auf **Finish**.

---

## 🚀 Schritt 2: Sharegy Android-Projekt öffnen

1. Öffne ein Terminal (PowerShell oder Eingabeaufforderung) in deinem Projektverzeichnis:
   ```bash
   cd c:\Users\Public\Dev\eswes\frontend
   ```
2. Führe den Befehl zum automatischen Öffnen in Android Studio aus:
   ```bash
   npm run cap:open
   ```
3. **Android Studio öffnet sich automatisch** und lädt das native Projekt unter `frontend/android/`.
4. Beim ersten Öffnen synchronisiert Android Studio im Hintergrund die Gradle-Abhängigkeiten (unten rechts siehst du einen blauen Ladebalken *„Gradle build model...“*). Das dauert beim ersten Mal etwa 1–2 Minuten.

---

## 📲 Schritt 3: Test-Gerät auswählen

Du hast zwei einfache Möglichkeiten, die App zu testen:

### Option A: Virtuelles Android-Smartphone (Emulator am PC)
1. Klicke in Android Studio oben rechts in der Symbolleiste auf den **Device Manager** (Handy-Symbol mit kleinem Android-Kopf) oder im Menü auf **Tools → Device Manager**.
2. Klicke auf **Create Device** (oder **+**).
3. Wähle ein Smartphone-Modell aus (z. B. **Pixel 8** oder **Pixel 9 Pro**) und klicke auf **Next**.
4. Wähle die empfohlene Android-Systemversion (z. B. **VanillaIceCream / Android 15** oder **UpsideDownCake / Android 14**) und klicke auf den kleinen Download-Pfeil daneben.
5. Nach dem Download auf **Next** und **Finish** klicken.
6. Der Emulator ist nun eingerichtet!

### Option B: Eigenes Android-Handy per USB anschließen
1. Aktiviere auf deinem Android-Smartphone die Entwickleroptionen:
   * Gehe zu **Einstellungen → Telefoninfo / Über das Telefon**.
   * Tippe **7-mal schnell auf die „Build-Nummer“**, bis die Meldung *„Sie sind jetzt ein Entwickler!“* erscheint.
2. Gehe zu **Einstellungen → System → Entwickleroptionen** und aktiviere **USB-Debugging**.
3. Verbinde dein Handy per USB-Kabel mit dem PC.
4. Auf dem Handy-Display erscheint die Frage: *„USB-Debugging zulassen?“* $\rightarrow$ Setze das Häkchen bei *„Von diesem Computer immer erlauben“* und tippe auf **Zulassen**.
5. Dein Smartphone erscheint nun oben in Android Studio automatisch in der Geräteliste!

---

## ▶️ Schritt 4: Sharegy App starten & testen

1. Wähle oben in der Symbolleiste dein Zielgerät aus (dein angeschlossenes Handy oder den virtuellen Pixel-Emulator).
2. Klicke auf das grüne **▶️ Play-Symbol (Run 'app')** (Tastenkombination: `Shift + F10`).
3. Android Studio kompiliert das Projekt, startet den Emulator bzw. dein Handy und öffnet die **Sharegy App**! 🎉
4. Du siehst sofort den dunklen Splashscreen und das fertige Energie-Dashboard.

---

## 🔄 Schritt 5: Zukünftige Änderungen übertragen

Wenn du Änderungen am React-Frontend, neuen Seiten oder Übersetzungen vornimmst, führst du einfach im `frontend`-Ordner aus:

```bash
npm run cap:sync
```

Danach klickst du in Android Studio einfach wieder auf **▶️ Play** – die Änderungen sind sofort in der App aktiv!

---

## 📦 Schritt 6: Installierbare APK für Freunde & Familie erstellen

Wenn du die App als `.apk`-Datei weitergeben möchtest:

1. Klicke in Android Studio im oberen Menü auf:  
   **Build → Build Bundle(s) / APK(s) → Build APK(s)**
2. Nach wenigen Sekunden erscheint unten rechts ein Pop-up mit dem Link **„locate“**.
3. Klicke auf **locate** – Windows öffnet den Ordner mit der fertigen Datei:  
   `app-debug.apk`
4. Diese Datei kannst du per Messenger, E-Mail oder USB auf jedes Android-Handy übertragen und durch Antippen sofort installieren! 🚀
