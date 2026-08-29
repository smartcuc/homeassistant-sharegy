# Sharegy Cloud Energy Bridge for Home Assistant ⚡🏠

Offizielle native Home Assistant Integration zur unterbrechungsfreien Übertragung aller lokalen Energiedaten an die **Sharegy Cloud**.

---

## Highlights

* **🎯 1-Klick Entity Picker:** Wähle deine Sensoren (Netzbezug, PV, Speicher, Wallbox, Smart Plugs) einfach per Klick in der Home Assistant Oberfläche aus.
* **⚡ Outbound WebSocket (WSS) & REST:** Direkter Stream an `wss://sharegy.de/ws/energy/<TOKEN>/` über Port 443 (keine Portfreigaben nötig).
* **💾 Lokaler SQLite Store & Forward Puffer:** Bei Internetausfall oder Neustarts werden alle Messwerte lokal auf dem Home Assistant gespeichert (bis zu 48h) und lückenlos nachgesendet, sobald die Verbindung wieder steht.
* **🔄 Live-Anpassung (Options Flow):** Sensoren und Einzelverbraucher können jederzeit unter *Einstellungen -> Geräte & Dienste -> Sharegy -> Konfigurieren* geändert werden.

---

## Installation

### Methode 1: Über HACS (Custom Repository) — Empfohlen
1. Öffne **HACS** in deinem Home Assistant.
2. Klicke oben rechts auf das Drei-Punkte-Menü $\rightarrow$ **Benutzerdefinierte Repositories**.
3. Füge die URL `https://github.com/smartcuc/eswes` (Kategorie: *Integration*) hinzu.
4. Klicke auf **Herunterladen** und starte Home Assistant neu.

### Methode 2: Manuelle Installation
1. Kopiere den Ordner `custom_components/sharegy` in das Verzeichnis `config/custom_components/` deines Home Assistant.
2. Starte Home Assistant neu.

---

## Einrichtung

1. Gehe in Home Assistant auf **Einstellungen** $\rightarrow$ **Geräte & Dienste** $\rightarrow$ **Integration hinzufügen**.
2. Suche nach **Sharegy Cloud Energy Bridge**.
3. Trage dein persönliches **Home Token** (aus deiner Sharegy-Oberfläche unter *Schnittstellen*) ein.
4. Wähle deine Sensoren in der Auswahlliste aus $\rightarrow$ Fertig!
