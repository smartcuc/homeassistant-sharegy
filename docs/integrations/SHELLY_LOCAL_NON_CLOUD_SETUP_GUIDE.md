# 🔌 Shelly ohne Cloud einrichten: Vollständige Schritt-für-Schritt Anleitung

> **Kosten sparen & maximale Datensouveränität:**  
> Du benötigst **kein kostenpflichtiges Shelly Cloud-Abo** und musst deine Messdaten nicht über fremde Server leiten. Sharegy unterstützt die direkte, lokale und verschlüsselte Anbindung deiner Shelly-Geräte – **100% kostenlos, extrem schnell (< 50 ms Latenz) und ausfallsicher.**

---

## 🎯 Warum die lokale / Non-Cloud Anbindung besser ist

| Kriterium | Lokale Sharegy Anbindung (WSS / RPC) | Shelly Cloud (Standard / Abo) |
| :--- | :--- | :--- |
| **Monatliche Kosten** | **0,00 € dauerhaft kostenlos** | Bis zu 3,99 € / Monat (Premium) |
| **Latenz & Reaktionszeit** | **Echtzeit (< 50 ms)** | 2 – 15 Sekunden Verzögerung |
| **Datenschutz** | **100% privat**, direkte Ende-zu-Ende-Verbindung | Daten liegen auf Drittanbieter-Servern |
| **Ausfallsicherheit** | Funktioniert auch bei Cloud-Störungen | Abhängig von externer Cloud-Verfügbarkeit |
| **Smart-Charging & Arbitrage** | Sofortige PV-Überschussregelung | Trägere Regelung durch Polling-Intervalle |

---

## 🚀 Methode 1 (Empfohlen): Outbound-WebSocket (WSS)

Diese Methode ist der modernste, sicherste und einfachste Weg für alle **Shelly Gen2, Gen3 und Pro** Geräte (z. B. *Shelly Plus 1PM, Shelly Pro 3EM, Shelly Plus Plug S, Shelly Mini Gen3, Shelly Pro 4PM*).

### Voraussetzungen:
- Das Shelly-Gerät ist mit deinem WLAN/LAN verbunden.
- Du kennst die IP-Adresse des Shelly (steht in der Fritz!Box / deinem Router oder in der Shelly App).
- Dein persönlicher Sharegy Home-Token (zu finden in Sharegy unter **Schnittstellen** $\rightarrow$ **1. Outbound-WebSocket**).

---

### Schritt-für-Schritt Anleitung:

#### 1. Shelly-Weboberfläche im Browser aufrufen
Öffne einen Browser (Chrome, Firefox, Safari oder Edge) und gib die IP-Adresse deines Shelly ein:
```text
http://192.168.178.XX   (Ersetze XX durch die IP deines Shelly)
```

#### 2. WebSocket-Menü öffnen
1. Klicke im Menü links oder oben auf **Settings** (bzw. **Einstellungen** / Zahnrad-Symbol).
2. Scrolle zum Bereich **Outbound WebSocket** (bei manchen Modellen unter *Network / Connectivity*).

#### 3. Sharegy Server-URL eintragen
1. Setze das Häkchen bei **Enable** (Aktivieren).
2. Wähle als Verbindungstyp **SSL/TLS (WSS)**.
3. Trage deine persönliche Sharegy WebSocket-URL ein:
   ```text
   wss://sharegy.de/ws/energy/<DEIN_SHAREGY_TOKEN>/
   ```
   *(Ersetze `<DEIN_SHAREGY_TOKEN>` durch den Token aus deinem Sharegy Account)*.
4. Klicke unten auf **Save Settings** (Einstellungen speichern).

#### 4. Fertig!
Der Shelly baut innerhalb von 2 Sekunden eine sichere, ausgehende Verbindung zu Sharegy auf.
- In Sharegy erscheint das Gerät sofort unter **Geräte** und im **Dashboard**.
- **Keine Portweiterleitung am Router (NAT) erforderlich**, da die Verbindung vom Shelly aus initiiert wird (Outbound).

---

## 🛠️ Methode 2: Lokales Netzwerk (LAN / WLAN RPC)

Wenn du den Shelly ausschließlich im lokalen Subnetz ohne ausgehende Internet-Verbindung betreiben möchtest:

### 1. Feste IP-Adresse im Router vergeben
Stelle in deiner Fritz!Box oder deinem DHCP-Server ein:  
`Diesem Netzwerkgerät immer die gleiche IPv4-Adresse zuweisen`.

### 2. Lokaler Abruf & Steuerung
Sharegy oder dein lokaler Server können den Shelly direkt über REST/RPC ansprechen:
- **Status abfragen:**  
  `GET http://192.168.178.XX/rpc/Shelly.GetStatus`
- **Relais schalten (Ein):**  
  `GET http://192.168.178.XX/rpc/Switch.Set?id=0&on=true`
- **Relais schalten (Aus):**  
  `GET http://192.168.178.XX/rpc/Switch.Set?id=0&on=false`

---

## 📡 Methode 3: Lokales MQTT

Für fortgeschrittene Nutzer mit eigenem MQTT-Broker (z. B. Mosquitto auf Raspberry Pi, Synology NAS oder Home Assistant):

1. Öffne die Shelly Weboberfläche $\rightarrow$ **Settings** $\rightarrow$ **MQTT**.
2. Aktiviere **Enable MQTT**.
3. Gib deine Broker-Daten ein:
   - **Server:** `192.168.178.YY:1883` (oder `mqtt.sharegy.de:1883`)
   - **User / Client ID:** Dein Benutzername / Device-Name
   - **Passwort:** Dein MQTT-Passwort
4. Speichere die Einstellungen. Telemetrie wird nun direkt im Sekundentakt auf das Topic `shellies/<device_id>/status` übertragen.

---

## 📻 Methode 4: Ältere Shelly-Geräte der 1. Generation (Gen1)

Für ältere Modelle (z. B. *Shelly 1, Shelly 1PM Gen1, Shelly Plug S Gen1, Shelly EM*):

1. Rufe die Weboberfläche des Shelly auf.
2. Gehe auf **Internet & Security** $\rightarrow$ **Advanced - Developer Settings**.
3. Aktiviere **CoIoT (CoAP)**.
4. Trage unter **CoIoT peer** die Zieladresse ein (z. B. `192.168.178.10:5683` oder `mcast`).
5. Starte das Gerät einmalig über **Reboot** neu.

---

## ❓ Häufige Fragen (FAQ)

### Kostet die Anbindung über Sharegy etwas?
**Nein.** Die Anbindung deiner Shelly-Geräte über WebSocket oder MQTT ist in Sharegy kostenfrei enthalten. Du sparst dir das Shelly Cloud Premium Abo.

### Funktioniert die PV-Überschusssteuerung und SG-Ready auch ohne Cloud?
**Ja, sogar deutlich schneller!** Da die Messwerte über Outbound-WebSocket in Echtzeit vorliegen, kann Sharegy deine Wärmepumpe, Brauchwasserwärmepumpe oder Wallbox ohne Verzögerung regeln.

### Was passiert bei einem Internetausfall?
Der Shelly misst intern weiter. Sobald die Internetverbindung wieder steht, baut der Shelly die WebSocket-Verbindung automatisch innerhalb von Sekundenbruchteilen wieder auf.

---

*Stand: September 2026 · Sharegy Dokumentation*
