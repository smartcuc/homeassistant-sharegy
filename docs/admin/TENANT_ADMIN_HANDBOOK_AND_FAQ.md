# 🏢 Sharegy Tenant-Admin Handbuch & Leitfaden für Liegenschafts- & Quartiersverwalter

**Zielgruppe**: Vermieter, WEG-Beiräte, Hausverwaltungen, Energiegenossenschafts-Vorstände (EEGs) und Liegenschafts-Administratoren.  
**Version**: 5.2 (Produktionsstand September 2026)  
**Dashboard-Bereich**: [`/app/tenant`](file:///c:/Users/Public/Dev/eswes/frontend/src/pages/TenantDashboard.jsx) & [`https://sharegy.de/app/tenant`](https://sharegy.de/app/tenant)

---

## 🏛️ 1. Einführung: Deine Rolle als Tenant-Admin

Als **Tenant-Admin (Liegenschafts- oder Quartiers-Administrator)** hast du die volle Kontrolle über die energiewirtschaftliche Verwaltung deines Gebäudes oder deiner Nachbarschaftsgemeinschaft. 

Sharegy ermöglicht es dir:
1. **Gemeinsame Solarenergie nach § 42b EnWG (Gemeinschaftliche Gebäudeversorgung / Mieterstrom)** 15-minutengenau auf die Wohnungen aufzuteilen.
2. **Den Virtuellen Summenzähler** am Netzanschlusspunkt (NAP) in Echtzeit zu überwachen.
3. **Rechtssichere Monatsabrechnungen und PDF-Nachweise** für Mieter und Miteigentümer mit einem Klick zu generieren.
4. **Exportdateien (Excel, CSV für DATEV, XML für Hausverwaltungssoftware)** für die Buchhaltung bereitzustellen.
5. **Smart Meter und wMSB-Gateways** den jeweiligen Wohneinheiten zuzuweisen.
6. **Netzdienliche Flexibilitäten (§ 14a EnWG & VPP)** gebündelt für Netzbetreiber bereitzustellen.

---

## 📑 2. Die 6 Funktionsbereiche im Tenant-Dashboard

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   TENANT-ADMIN COCKPIT (/app/tenant)                            │
├───────────────┬──────────────────────┬───────────────┬──────────────┬──────────────┬─────────────┤
│ ⚡ Cockpit    │ 🏢 Virtueller Zähler │ 🔌 VPP Kraftw.│ 💰 Tarife &  │ 👥 Mitglieder│ ⚡ wMSB Hub │
│ & Bilanzen    │ & NAP-Saldierung     │ & Flex-Pool   │   Abrechnung │ & Rollen     │ & Zähler    │
└───────────────┴──────────────────────┴───────────────┴──────────────┴──────────────┴─────────────┘
```

---

### 1. ⚡ Cockpit & Bilanzen (Tages- & Monatsüberblick)
* **Produziert (2.8.0)**: Gesamte Solar-Erzeugung der Dach-Photovoltaikanlage im gewählten Zeitraum (Heute / Dieser Monat).
* **Verbraucht (1.8.0)**: Aggregierter Gesamtstrombedarf aller angeschlossenen Wohneinheiten.
* **Geteilt (Sharing)**: Die im Gebäude direkt zeitgleich verbrauchte Solarenergie.
* **Autarkiegrad (%)**: Anteil des Bedarfs, der direkt durch die eigene Solaranlage gedeckt wurde.
* **Zugekauft (Reststrom)**: Vom Reststromversorger aus dem öffentlichen Netz bezogene Energie.
* **Finanzielle Ersparnis (€)**: Gegenüber dem regulären Netzbezugspreis eingesparter Betrag für die Gemeinschaft.

---

### 2. 🏢 Virtueller Summenzähler & NAP-Saldierung
Der **Virtuelle Summenzähler** ersetzt teure physikalische Summenzähler-Schränke durch eine eichrechtskonforme mathematische 15-Minuten-Saldierung am Netzanschlusspunkt (NAP).

#### 🧮 Die 3 Aufteilungsmodelle (§ 42b EnWG):
1. **Dynamisch (zeitgleich) - Empfohlen für maximale Fairness**:
   * In jedem 15-Minuten-Intervall wird die erzeugte Solarenergie exakt im Verhältnis des zeitgleichen Verbrauchs der Parteien aufgeteilt.
   * Wer mittags viel verbraucht (z.B. E-Auto lädt oder kocht), erhält automatisch mehr günstigen Solarstrom zugeteilt.
2. **Statisch (nach Miteigentumsanteilen / MEA-Schlüssel)**:
   * Feste prozentuale Zuteilung der Solarenergie je Wohneinheit (z.B. Wohnung 1 = 25 %, Wohnung 2 = 18 %).
   * Geeignet für WEGs mit vertraglich fixierten Eigentumsquoten.
3. **Hybrid (Eigenbedarf-Vorrang + Restüberschuss-Sharing)**:
   * Jede Partei hat ein Basiskontingent; ungenutzte Überschüsse fließen dynamisch an bedürftige Nachbarn.

#### 📊 15-Minuten-Zeitreihen-Tabelle:
* Zeigt für alle 96 Viertelstunden des Tages Erzeugung, Mieterbedarf, geteilte Energie und den resultierenden NAP-Saldo (Einspeisung / Netzbezug).

---

### 3. 🔌 VPP Kraftwerk & Flexibilitäts-Pool
Hier siehst du das gebündelte Flexibilitätspotenzial aller steuerbaren Anlagen im Gebäude:
* **Positive Regelleistung (+kW)**: Entladepotenzial aus Batteriespeichern bei Stromknappheit im Netz.
* **Negative Regelleistung (-kW)**: Ladepotenzial der Speicher und Dimmbarkeit flexibler Lasten bei Netzüberlastung.
* **§ 14a EnWG SteuVE-Modul**: Dimmbare Wallboxen und Wärmepumpen zur Sicherung des pauschalen Netzentgelt-Rabatts (~160 € pro Anlage/Jahr).
* **Redispatch 2.0 / Connect+ 96-Viertelstunden-Fahrplan**: Visualisierung der standardisierten Fahrplandaten (`PT15M`) für den Netzbetreiber.

---

### 4. 💰 Tarife & Abrechnungen (Monatliches PDF-Clearing)
In diesem Bereich verwaltest du die Strompreise und erstellst die Abrechnungen für die Mieter.

#### 🛠️ Tarif-Einstellungen:
* **Solar-Cent-Preis (z. B. 16,00 ct/kWh)**: Preis, den Mieter für den bezogenen Solarstrom vom Dach zahlen.
* **Reststrom-Preis (z. B. 32,00 ct/kWh)**: Durchgeleiteter Preis für Netzstrom vom externen Restversorger.
* **Grundgebühr (z. B. 8,50 € / Monat)**: Messstellen- und Verwaltungsumlage je Partei.

#### 📄 Monatsabrechnung anstoßen:
1. Klicke auf **"Monatliche Abrechnung & PDFs generieren"**.
2. Das System saldiert alle 15-Minuten-Intervalle des Vormonats für jede Partei centgenau.
3. Für jede Wohneinheit wird ein **separater, rechtssicherer PDF-Abrechnungsnachweis** erzeugt.
4. **Exporte für die Hausverwaltung**:
   * 📊 **Excel (.xlsx)**: Tabellarische Gesamtabrechnung mit Zählerständen, Verbräuchen und Summen.
   * 📁 **CSV**: DATEV-kompatible Buchungsliste (Semikolon-getrennt, UTF-8 BOM).
   * 📜 **XML**: Standardisiertes Datenformat für Immobilien- und Hausverwaltungssoftware (z.B. Haufe PowerHaus, DOMUS, Wodis).

---

### 5. 👥 Mitglieder & Rollenverwaltung
Hier verwaltest du die Nachbarn und delegierst Aufgaben:

| Rolle | Symbol | Berechtigung |
| :--- | :---: | :--- |
| **Admin** | 🏛️ | Volle Rechte (Tarife ändern, Abrechnungen auslösen, Zähler zuweisen, Mitglieder löschen). |
| **Energy-Userverwaltung** | 👥 | Kann neue Mieter einladen, Verträge zuordnen und Adressdaten pflegen. |
| **Auditor / Kassenprüfer** | 📊 | Lesezugriff auf alle Abrechnungen, Rohzeitreihen und Exporte zur Rechnungsprüfung. |
| **Helpdesk** | 🛟 | Kann Support-Tickets und Zählerfragen von Mietern bearbeiten. |
| **Mitglied** | ⚡ | Normaler Mieter/Eigentümer (sieht nur die eigene Wohnung und den eigenen PDF-Nachweis). |

---

### 6. ⚡ wMSB Smart Meter Hub & Zählerzuordnung
* Verwaltet die Anbindung an wettbewerbliche Messstellenbetreiber (Discovergy, inexogy, Solandeo).
* **Zählerzuweisung**: Verknüpft Zählernummer (1.8.0 / 2.8.0) und OBIS-IDs mit der entsprechenden Wohnungsnummer (z. B. "Top 3 - Familie Müller").
* **Sub-Meter-Status**: Prüft, ob Zählerdaten lückenlos empfangen werden (Grüner Live-Indikator).

---

## ❓ Häufig gestellte Fragen (Tenant-Admin FAQ)

### F1: Was passiert, wenn ein Mieter keinen Smart Meter hat?
> **Antwort**: Für das Energy Sharing nach § 42b EnWG ist ein registrierender 15-Minuten-Zähler (Smart Meter / iMSys oder wMSB-Submeter) gesetzlich erforderlich. Für Parteien ohne Smart Meter kann der Zählerstand manuell über das wMSB-Portal nacherfasst werden (Standard-Lastprofil H0).

### F2: Kann ein Mieter die Verbrauchsdaten seiner Nachbarn sehen?
> **Antwort**: **Nein, niemals.** Sharegy trennt die Zugriffe über ein striktes Multi-Tenant RBAC-System. Normale Mieter sehen ausschließlich den eigenen Verbrauch, den eigenen Solar-Anteil und die anonymisierte Gesamtbilanz des Gebäudes (z. B. "Gesamterzeugung 850 kWh").

### F3: Wer haftet für die Reststromversorgung, wenn die Sonne nicht scheint?
> **Antwort**: Der im Gemeinschaftsvertrag hinterlegte Reststromversorger (Vollversorger des Hauptanschlusses). Sharegy saldiert die Reststrommengen präzise, sodass der Vermieter den Netzbezug 1:1 auf die Mieter umlegen kann.

### F4: Wie funktioniert die Zuteilung bei dynamischen Stromtarifen?
> **Antwort**: Wenn die Gemeinschaft einen dynamischen Börsenstromtarif (z.B. Tibber) für den Reststrom nutzt, berechnet Sharegy den Reststromanteil in jedem 15-Minuten-Intervall mit dem exakten Börsenpreis der jeweiligen Stunde.
