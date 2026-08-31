# 📲 Mobile Push & Notification Engine (Systemdokumentation)

**Modul**: `notifications/` & `frontend/public/sw.js`  
**Standard**: W3C Web-Push API (RFC 8291, RFC 8292) / VAPID (Voluntary Application Server Identification)  
**Status**: Produktiv (v3.3)  
**Task-Referenz**: Task 2.21 (Roadmap) / Task 5.9 (Optimization Plan)

---

## 1. Architektur & Funktionsweise

Die Sharegy **Mobile Push & Notification Engine** ermöglicht den latenzfreien Echtzeit-Versand von Sicherheits- und Effizienz-Benachrichtigungen direkt auf den Sperrbildschirm von Smartphones (Apple iOS Safari 16.4+, Google Android Chrome/Firefox) und Desktop-Browsern (Firefox, Chrome, Edge, Safari) – **auch wenn die Sharegy-App vollständig geschlossen ist**.

```
  ┌─────────────────────────┐
  │   Alert Watchdogs &     │ (z. B. Speicher-Notreserve,
  │   Anomalie-Erkennung    │  1 kW Dauerlast-Leckage, PV-Ausfall)
  └────────────┬────────────┘
               │
               ▼
  ┌─────────────────────────┐
  │   alerts/services.py    │ ──> dispatch_alert_push(event)
  └────────────┬────────────┘
               │
               ▼
  ┌─────────────────────────┐
  │ notifications/services  │ ──> Prüft Ruhezeiten (Quiet Hours),
  │ (Push Dispatcher)       │     Notfall-Overrides & Kategorie-Filter
  └────────────┬────────────┘
               │
      ┌────────┴────────┐
      ▼                 ▼
 ┌───────────┐    ┌───────────┐
 │ Mozilla   │    │ Google    │ (W3C Web-Push Endpoints via ECDSA VAPID JWT)
 │ Push (FF) │    │ FCM / APNs│
 └─────┬─────┘    └─────┬─────┘
       │                │
       ▼                ▼
 ┌───────────────────────────┐
 │  Native OS Lockscreen     │ (iOS / Android / Windows Notification Center)
 │  via Service Worker sw.js │
 └───────────────────────────┘
```

---

## 2. Datenmodelle (`notifications/models.py`)

### `DeviceSubscription`
Speichert die kryptografischen Verbindungsparameter für jedes angemeldete Gerät eines Nutzers:
* `user`: Referenz auf den Sharegy-Benutzer.
* `endpoint`: Eindeutige Push-Service-URL (z. B. `https://updates.push.services.mozilla.com/wpush/v2/...` oder `https://fcm.googleapis.com/fcm/send/...`).
* `p256dh_key`: Öffentlicher Diffie-Hellman-Schlüssel des Clients zur Ende-zu-Ende-Verschlüsselung der Payload.
* `auth_key`: Authentifizierungs-Geheimnis des Clients (RFC 8291).
* `device_type`: `web_push`, `ios_native`, `android_native`.
* `device_name`: Ableitung aus dem User-Agent (z. B. *„Apple iPhone“*, *„Android Smartphone“*, *„Firefox auf PC“*).
* `is_active`: Boolean. Wird automatisch auf `False` gesetzt, wenn der Push-Provider einen `404 Not Found` oder `410 Gone` zurückgibt (Auto-Deaktivierung bei deinstallierten/abgemeldeten Browsern).
* `last_used_at`: Zeitstempel der letzten erfolgreichen Zustellung.

### `NotificationPreference`
Verwaltet globale Ruhezeiten und Kategorie-Filter je Benutzer:
* `push_enabled`: Globaler Hauptschalter für Push-Benachrichtigungen.
* `quiet_hours_enabled`: Aktiviert konfigurierbare Ruhezeiten (z. B. 22:00 bis 07:00 Uhr).
* `quiet_hours_start` & `quiet_hours_end`: Beginn und Ende der Nachtruhe (unterstützt tagesübergreifende Intervalle).
* `allow_critical_in_quiet_hours`: Notfall-Override (z. B. bei kritischem Batterieschutz oder Brandgefahr).
* `notify_battery`, `notify_leakage`, `notify_pv`, `notify_prices`, `notify_device_status`: Granulare Toggles für spezifische Alarmtypen.

---

## 3. Kryptografie & VAPID Konfiguration

Der Server identifiziert sich gegenüber den Push-Diensten (Mozilla, Apple, Google) über ein asymmetrisches **NIST P-256 (secp256r1) Elliptic-Curve** Schlüsselpaar:

* **Settings (`backend/settings/base.py`)**:
  * `VAPID_PUBLIC_KEY`: 65-Byte unkomprimierter Punkt auf der Kurve (Base64URL-kodiert). Wird an den Browser übermittelt (`GET /api/notifications/vapid-key/`).
  * `VAPID_PRIVATE_KEY`: Privater Schlüssel im PEM-Format (PKCS#8).
  * `VAPID_ADMIN_EMAIL`: Kontakt-E-Mail (`mailto:support@sharegy.cloud`) im `sub`-Claim des VAPID-JWT.

---

## 4. API Endpunkte (`notifications/api/urls.py`)

| Methode | Endpunkt | Berechtigung | Beschreibung |
|---|---|---|---|
| `GET` | `/api/notifications/vapid-key/` | `IsAuthenticated` | Liefert den öffentlichen VAPID-Schlüssel für die Browser-Registrierung. |
| `POST` | `/api/notifications/subscribe/` | `IsAuthenticated` | Registriert ein neues Geräte-Abonnement (`endpoint`, `keys`, `device_name`). |
| `POST` | `/api/notifications/unsubscribe/` | `IsAuthenticated` | Deaktiviert das Geräte-Abonnement für das aktuelle Gerät. |
| `GET` | `/api/notifications/preferences/` | `IsAuthenticated` | Liefert die Ruhezeiten, Kategoriefilter und die Anzahl aktiver Geräte. |
| `POST` | `/api/notifications/preferences/` | `IsAuthenticated` | Aktualisiert die Benachrichtigungseinstellungen. |
| `POST` | `/api/notifications/test-push/` | `IsAuthenticated` | Versendet eine sofortige Test-Push-Nachricht an alle aktiven Geräte des Nutzers. |

---

## 5. Service Worker & Frontend-Integration

* **Service Worker (`frontend/public/sw.js`)**:
  * Lauscht im Hintergrund auf das native `push`-Event.
  * Zeigt die Benachrichtigung mit Sharegy-Branding, Icon, Badge und Vibrationsmuster an.
  * Beim Klick (`notificationclick`) wird die Benachrichtigung geschlossen, ein bestehender Sharegy-Tab fokussiert oder ein neues Fenster mit `/app/alerts` geöffnet.
* **Subscription Manager (`frontend/src/utils/pushManager.js`)**:
  * Führt die 1-Klick Permission-Abfrage durch (`Notification.requestPermission()`).
  * Konvertiert den Base64URL VAPID-Key in ein `Uint8Array` (`applicationServerKey`).
  * Meldet das Abonnement idempotent am Django-Backend an.
* **UI-Komponenten**:
  * [`PushNotificationSettings.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/alerts/components/PushNotificationSettings.jsx): Vollständige Konfigurationsoberfläche mit Live-Status (`🟢 Aktiv`), Ruhezeiten-Uhrzeitfeldern, Kategorie-Toggles und `⚡ Test-Push`-Button.
  * Integriert in **`👤 /app/profile`** und **`🚨 /app/alerts`**.
