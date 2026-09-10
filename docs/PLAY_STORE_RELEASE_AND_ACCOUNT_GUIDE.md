# 📱 Sharegy Android Play Store Release & Developer Account Guide

**Stand**: September 2026 (App-Version `1.0.0`, Build Code `1`)  
**Status**: Release Bundle (.aab) & Release APK (.apk) kompiliert, optimiert & signiert.  
**Package-ID**: `de.sharegy.app`  

---

## 📦 1. Gespeicherte Release-Artefakte (v1.0.0)

Die fertigen Binärdateien wurden nach dem erfolgreichen Gradle-Build dauerhaft gesichert:

| Datei | Pfad | Größe | SHA-256 Prüfsumme | Zweck |
| :--- | :--- | :--- | :--- | :--- |
| **`app-release.aab`** | [`releases/v1.0.0-android/app-release.aab`](file:///c:/Users/Public/Dev/eswes/releases/v1.0.0-android/app-release.aab) | **4.105.395 Bytes (~4.1 MB)** | `9AA19185B8E4FC6622CC17A51253BC4800D601DF953ADDA9DEA1CA0E11FD0DE9` | **Google Play Console Upload** (Offizielles Store-Bundle) |
| **`app-release.apk`** | [`releases/v1.0.0-android/app-release.apk`](file:///c:/Users/Public/Dev/eswes/releases/v1.0.0-android/app-release.apk) | **4.240.364 Bytes (~4.2 MB)** | `A7F52AF310E73F87F8AB973B13A4766274364EA3271C1911CC30B6E82A37A295` | Direkte Installation / Sideloading auf Test-Smartphones |

*(Zusätzlicher Build-Pfad: [`frontend/android/app/build/outputs/bundle/release/app-release.aab`](file:///c:/Users/Public/Dev/eswes/frontend/android/app/build/outputs/bundle/release/app-release.aab))*

---

## 🔐 2. Keystore & Signatur-Spezifikationen

- **Keystore-Datei**: `frontend/android/app/sharegy-release-key.jks` *(lokal gesichert, git-geschützt)*
- **Key-Alias**: `sharegy`
- **Algorithmus**: RSA 2048-Bit, SHA256withRSA
- **Gültigkeit**: 10.000 Tage (bis 2054)
- **Konfigurations-Datei**: `frontend/android/key.properties` *(wird vom Build-Skript eingelesen, nicht im Repository)*
- **Vorlagedatei**: [`frontend/android/key.properties.example`](file:///c:/Users/Public/Dev/eswes/frontend/android/key.properties.example)

---

## 🏢 3. Entscheidungshilfe: Welcher Google Play Developer Account?

Google unterscheidet seit Ende 2023 strikt zwischen zwei Konto-Arten für Entwickler:

```
                       ┌─────────────────────────────────────────────────┐
                       │      Google Play Console Entwicklerkonto        │
                       └────────────────────────┬────────────────────────┘
                                                │
                 ┌──────────────────────────────┴──────────────────────────────┐
                 ▼                                                             ▼
   ┌───────────────────────────┐                                 ┌───────────────────────────┐
   │    ORGANISATIONS-KONTO    │                                 │     PERSÖNLICHES KONTO    │
   │   (Firma / UG / GmbH /    │                                 │  (Privatperson / Einzel-  │
   │    e.V. / Gewerbe)        │                                 │   unternehmer ohne DUNS)  │
   ├───────────────────────────┤                                 ├───────────────────────────┤
   │ ⭐ EMPFOHLEN FÜR SHAREGY   │                                 │ ⚠️ NUR FÜR HOBBY/PROTOTYP │
   ├───────────────────────────┤                                 ├───────────────────────────┤
   │ ✅ Kein 20-Tester-Zwang   │                                 │ ❌ MUSS 20 Tester für mind│
   │    (Direkte Freigabe)     │                                 │    14 Tage nachweisen!    │
   │ ✅ Firmenname im Store    │                                 │ ❌ Klarname des Inhabers  │
   │    ("Sharegy Energy Inc") │                                 │    öffentlich im Store    │
   │ ✅ Mehrere Team-Mitglieder│                                 │ ❌ Nur 1 Login-Konto      │
   │    & Rollenverwaltung     │                                 │                           │
   │ ✅ Gewerbliche Haftungs-  │                                 │ ❌ Private Haftung        │
   │    trennung               │                                 │                           │
   │ ℹ️ Benötigt D-U-N-S Nr.   │                                 │ ℹ️ Personalausweis-Check  │
   │    (kostenlos bei D&B)    │                                 │                           │
   │ 💰 Einmalig 25 $          │                                 │ 💰 Einmalig 25 $          │
   └───────────────────────────┘                                 └───────────────────────────┘
```

### Detaillierter Vergleich

| Kriterium | 🏢 Organisationskonto (Empfohlen) | 👤 Privates / Persönliches Konto |
| :--- | :--- | :--- |
| **Geeignet für** | Unternehmen, Startups, GmbH, UG, GbR, e.V., eingetragene Kaufleute | Privatpersonen, Hobby-Entwickler, Studenten |
| **Freigabeprozess (Produktion)** | **Sofortige Überprüfung & direkte Veröffentlichung möglich** | **Zwingend: Mindestens 20 Tester müssen 14 Tage lang die Closed-Beta testen**, bevor die App für die Öffentlichkeit freigeschaltet werden darf. |
| **Name im Play Store** | Offizieller Unternehmensname (z. B. *Sharegy Technologies*) | Vor- und Nachname der Privatperson |
| **Öffentliche Kontaktdaten** | Firmenadresse & offizielle Support-E-Mail | Adresse & Name öffentlich im Store einsehbar |
| **Zugriffsverwaltung** | Beliebig viele Team-Accounts mit granularer Rechtevergabe (Admin, Release-Manager, Support) | Nur der primäre Google-Account |
| **Voraussetzungen** | 1. D-U-N-S Nummer (kostenlos)<br>2. Gewerbenachweis / Handelsregisterauszug<br>3. Offizielle Firmen-Website & Firmen-E-Mail | Personalausweis / Reisepass |
| **Kosten** | Einmalig 25 USD Registrierungsgebühr | Einmalig 25 USD Registrierungsgebühr |

### 🎯 Klare Empfehlung für Sharegy:
> **Wählt unbedingt ein Organisationskonto (Organisation / Business Account).**  
> **Gründe:**
> 1. Bei einem privaten Konto blockiert Google die Store-Veröffentlichung, bis 20 Personen die App 14 Tage lang aktiv in einem geschlossenen Test installiert haben. Beim Firmenkonto entfällt dieser Zwang.
> 2. Sharegy ist eine professionelle EMS & Energy Sharing Plattform mit Abo-Modellen (Stripe) und B2B-Kunden (Stadtwerke, Quartiere, Bürgerenergie). Ein Firmen-Branding schafft das notwendige Vertrauen.

---

## 📝 4. Schritt-für-Schritt: Organisationskonto anlegen

### Schritt 1: D-U-N-S Nummer prüfen / kostenlos beantragen
Google nutzt das Dun & Bradstreet (D&B) Register zur Verifizierung von Unternehmen.
1. Auf **[dnb.com/de-de/duns-nummer.html](https://www.dnb.com/de-de/duns-nummer.html)** prüfen, ob das Unternehmen bereits eine D-U-N-S Nummer hat.
2. Falls noch nicht vorhanden: Kostenlose Erstellung beantragen (Dauer: i. d. R. 2–5 Werktage).

### Schritt 2: Google Developer Account registrieren
1. Mit dem Google-Konto des Unternehmens bei der **[Google Play Console](https://play.google.com/console/signup)** anmelden.
2. Kontotyp **„Organisation oder Unternehmen“** auswählen.
3. D-U-N-S Nummer, offiziellen Firmennamen und Handelsregister-Daten eingeben.
4. Einmalige Registrierungsgebühr von 25 $ per Kreditkarte bezahlen.
5. Identitätsprüfung abschließen (Hochladen von Gewerbeanmeldung / Handelsregisterauszug).

---

## 🚀 5. Upload-Anleitung für das fertige Release-Bundle

Sobald der Account freigeschaltet ist:

1. In der **Google Play Console** auf **App erstellen** klicken:
   - **App-Name**: `Sharegy - Smart Energy Management`
   - **Standardsprache**: Deutsch (Deutschland) - `de-DE`
   - **App oder Spiel**: App
   - **Kostenlos / Kostenpflichtig**: Kostenlos *(Monetarisierung läuft über In-App-Services/Stripe)*
2. Unter **Release > Produktion** auf **Neues Release erstellen** klicken.
3. Die gesicherte Datei hochladen:
   📁 [`releases/v1.0.0-android/app-release.aab`](file:///c:/Users/Public/Dev/eswes/releases/v1.0.0-android/app-release.aab)
4. **Versionsname**: `1.0.0`
5. **Versionshinweise (Release Notes de-DE)**:
   ```text
   Willkommen bei Sharegy v1.0.0!
   - Echtzeit-Monitoring für PV, Batteriespeicher, Wärmepumpe & Wallbox
   - Omi-Check & 6-Säulen-Energie-Profil mit personalisierten Sparpotenzialen
   - EPEX Spotmarkt-Preise & intelligente dynamische Tarifsteuerung
   - Energy Sharing Community Dashboard für Quartiere & Mieterstrom
   - Mehrsprachigkeit (6 Sprachen) & haptisches Feedback
   ```
6. **Datensicherheit (Data Safety Form)**:
   - Standortdaten: Optional (für standortbezogene Solarprognosen)
   - E-Mail-Adresse: Für Benutzerkonto & Authentifizierung
   - App-Interaktionen / Absturzberichte: Für Fehlerbehebung
7. Auf **Release überprüfen** und **Veröffentlichung starten** klicken.
