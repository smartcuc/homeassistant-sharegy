# 📱 Firebase Cloud Messaging (FCM) Setup & Installationsanleitung

Diese Anleitung führt dich Schritt für Schritt durch die einmalige Einrichtung von **Firebase Cloud Messaging (FCM)** für Sharegy.

> [!NOTE]
> **Kosten**: Firebase Cloud Messaging ist im *Spark Free Tier* von Google zu **100 % kostenlos (0,00 €)** für unbegrenzt viele Push-Nachrichten an Android und iOS.

---

## 🛠️ Schritt 1: Kostenloses Firebase-Projekt erstellen

1. Öffne die **[Firebase Console](https://console.firebase.google.com/)** in deinem Browser und melde dich mit deinem Google-Konto an.
2. Klicke auf **„Projekt hinzufügen“** (Add project).
3. Gib deinem Projekt einen Namen (z. B. `Sharegy` oder `Sharegy-Push`).
4. *(Optional)* Google Analytics aktivieren oder deaktivieren und auf **„Projekt erstellen“** klicken.
5. Nach ca. 20 Sekunden ist dein Firebase-Projekt einsatzbereit.

---

## 🔑 Schritt 2: Service-Account Privatschlüssel (JSON) herunterladen

1. Klicke in der Firebase Console oben links neben *Projektübersicht* auf das **Zahnrad-Symbol ⚙️** $\rightarrow$ **Projekteinstellungen**.
2. Wechsle auf den Reiter **„Dienstkonten“** (Service accounts).
3. Stelle sicher, dass *Firebase Admin SDK* und *Python* ausgewählt sind.
4. Klicke ganz unten auf die Schaltfläche **„Neuen privaten Schlüssel generieren“** (Generate new private key) und bestätige den Dialog.
5. Dein Browser lädt nun eine Datei herunter (z. B. `sharegy-firebase-adminsdk-xxxx.json`).

---

## 📁 Schritt 3: Datei auf dem Server hinterlegen & `.env` konfigurieren

### Option A: Als Datei im Projekt ablegen (Empfohlen)

1. Benenne die heruntergeladene Datei um in:
   ```bash
   firebase_credentials.json
   ```
2. Lade die Datei in den `config/`-Ordner deines Projekts hoch:
   - **Auf dem Produktionsserver (Raspberry Pi / Linux)**:
     ```bash
     mkdir -p /var/www/sharegy/green/config
     # Datei hier ablegen: /var/www/sharegy/green/config/firebase_credentials.json
     chmod 600 /var/www/sharegy/green/config/firebase_credentials.json
     ```
   - **Lokal unter Windows**:
     ```
     c:\Users\Public\Dev\eswes\config\firebase_credentials.json
     ```
3. Öffne deine `.env`-Datei auf dem Server / lokal und trage den Pfad ein:
   ```env
   FIREBASE_CREDENTIALS_PATH=/var/www/sharegy/green/config/firebase_credentials.json
   ```

---

### Option B: Als einzeilige Umgebungsvariable (z. B. für Docker / Cloud-Hosting)

Öffne die `.json`-Datei im Texteditor, kopiere den gesamten Inhalt als einzeiligen String und füge ihn in `.env` ein:
```env
FIREBASE_CREDENTIALS_JSON={"type": "service_account", "project_id": "sharegy-12345", ...}
```

---

## 🚀 Schritt 4: Server-Dienste neu starten & Testen

1. **Celery Worker & Backend neu starten**:
   ```bash
   # Auf dem Server:
   sudo systemctl restart daphne celery
   ```

2. **Funktionstest ausführen**:
   - In der Web-App unter *Einstellungen* $\rightarrow$ *Benachrichtigungen* auf **„Test-Benachrichtigung senden“** klicken.
   - Alternativ über den API-Endpunkt:
     ```bash
     curl -X POST https://sharegy.cloud/api/notifications/test-push/ \
       -H "Authorization: Bearer <DEIN_TOKEN>"
     ```
   - Im Log siehst du sofort:
     ```log
     [INFO] Firebase Admin initialisiert via Zertifikat: /var/www/sharegy/green/config/firebase_credentials.json
     [INFO] FCM Native Push erfolgreich gesendet an Pixel 8 Pro (Msg-ID: projects/sharegy/messages/...)
     ```

---

## 🛡️ Zusammenfassung & Sicherheit

- Die `firebase_credentials.json` enthält sensible private Schlüssel und darf **niemals in öffentliche Git-Repositories** hochgeladen werden (sie ist in `.gitignore` bereits geschützt).
- Solange keine Firebase-Credentials hinterlegt sind, arbeitet Sharegy automatisch im **Web-Push Modus (W3C VAPID)** weiter, ohne Fehler zu werfen. Sobald die Datei hinterlegt wird, schaltet sich der native Smartphone-Push automatisch und nahtlos aktiv.
