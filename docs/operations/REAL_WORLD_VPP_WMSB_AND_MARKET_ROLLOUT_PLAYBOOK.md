# 🚀 Real-World VPP, wMSB Gateway & Market Rollout Playbook
## Schritt-für-Schritt-Leitfaden zur operativen Inbetriebnahme von VPP, Smart Meter Gateways (SMGW/CLS) und Markt-Akteuren

**Version:** 1.1.0 (Human-Readable & Executive Edition)  
**Ziel:** Konkrete Handlungsanleitung, Ansprechpartner, Anträge, Fragenkataloge und Verträge zur echten Anbindung des Sharegy Virtuellen Kraftwerks (VPP) und Flexibilitäts-Pools an den deutschen Strommarkt.

---

## 🧭 Inhaltsverzeichnis
1. [Strategische Grundsatzentscheidung: Sub-Aggregator vs. Eigener BKV](#1-strategische-grundsatzentscheidung)
2. [Die Akteure & konkrete Ansprechpartner im deutschen Energiemarkt](#2-die-akteure--konkrete-ansprechpartner)
3. [Schritt-für-Schritt-Ablaufplan (Phasen 1 bis 4)](#3-schritt-für-schritt-ablaufplan)
4. [Notwendige Verträge, Anträge & regulatorische Registrierungen](#4-notwendige-vertraege-antraege--registrierungen)
5. [Fragen- & Antwortkatalog für Erstgespräche mit Marktpartnern](#5-fragen--antwortkatalog-fuer-erstgespraeche)
6. [Technische Integrationsarchitektur (Ablauf eines Flexibilitäts-Abrufs)](#6-technische-integrationsarchitektur)
7. [Muster-Anschreiben & Gesprächsleitfäden](#7-muster-anschreiben--gespraechsleitfaeden)
8. [Sofort-Aktionsliste](#8-sofort-aktionsliste)

---

## 1. Strategische Grundsatzentscheidung & Tiefenanalyse: Pfad A (Sub-Aggregator)

Bevor Anträge gestellt oder Verträge verhandelt werden, muss der regulatorische Pfad für Sharegy festgelegt werden:

```
+-----------------------------------------------------------------------------------------+
|                                SHAREGY VPP MARKTEINTRITT                                |
+-----------------------------------------------------------------------------------------+
                                             |
                   +-------------------------+-------------------------+
                   |                                                   |
                   v                                                   v
  +---------------------------------+                 +---------------------------------+
  |    PFAD A: SUB-AGGREGATOR       |                 |      PFAD B: VOLL-VERSORGER     |
  |     (DRINGEND EMPFOHLEN)        |                 |      (EIGENER BKV & wMSB)       |
  +---------------------------------+                 +---------------------------------+
  | * Kooperation mit bestehendem   |                 | * Eigene BNetzA-Versorgerlizenz |
  |   Direktvermarkter / BKV        |                 | * Eigener Bilanzkreis bei 4 ÜNB |
  | * Time-to-Market: 3 bis 6 Monate|                 | * Time-to-Market: 12-18 Monate  |
  | * Keine Millionen-Bürgschaften  |                 | * 24/7 Leitwarte + AS4/EDIFACT  |
  | * Geringes finanzielles Risiko  |                 | * Hohe Bürgschaften & Fixkosten |
  +---------------------------------+                 +---------------------------------+
```

---

### 🔍 1.1 Was bedeutet "Sub-Aggregator" bildlich erklärt?

Um Strom und Flexibilität an der Strombörse (**EPEX Spot**) oder den Übertragungsnetzbetreibern (**Regelleistungsmarkt regelleistung.net**) zu verkaufen, verlangt der deutsche Gesetzgeber extrem hohe regulatorische Hürden:
* Einen **Bilanzkreisvertrag** mit allen 4 deutschen Übertragungsnetzbetreibern (Amprion, TenneT, 50Hertz, TransnetBW).
* **Bankbürgschaften** in Millionenhöhe zur Absicherung von Ausgleichsenergie.
* Eine **24/7 besetzte energiewirtschaftliche Leitwarte** (Fehlschaltungen werden mit existenzbedrohenden Strafen belegt).
* BSI-zertifizierte IT-Sicherheitszertifikate (ISO 27001 auf Basis IT-Grundschutz).

Als **Sub-Aggregator (Pfad A)** umgeht Sharegy diesen gigantischen bürokratischen und finanziellen Aufwand vollständig:
* **Der Master-Aggregator (z. B. Next Kraftwerke oder Statkraft)** besitzt bereits all diese Lizenzen, Bürgschaften, Leitwarten und Börsenzugänge.
* **Sharegy** agiert als der **Spezialist für die dezentralen Prosumer-Assets**: Wir haben die Software auf den Heimspeichern, die Wallbox-Steuerung, das Smartphone-Frontend und die direkte Kundenbeziehung.
* **Die Partnerschaft:** Sharegy bündelt 100, 1.000 oder 10.000 Heimspeicher zu einem **digitalen 5-Megawatt-Paket** und übergibt dieses Paket über eine einzige Programmierschnittstelle (API / OpenADR) an den Master-Aggregator. Der Master-Aggregator bietet das Paket an der Strombörse an und überweist Sharegy monatlich die Erlöse.

---

### 👥 1.2 Die Rollenverteilung in Pfad A: Wer macht was?

```
+───────────────────────────────────────────────────────────────────────────────────────────+
| 1. ENDKUNDE (SPEICHERBESITZER)                                                           |
|    - Stellt freie Batteriekapazität zur Verfügung (z. B. 5 kWh von 10 kWh)                |
|    - Behält immer 20% Mindest-SoC für Eigenbedarf / Notstrom                              |
|    - Erhält 80% des erwirtschafteten Erlöses als "Flex-Bonus" aufs Bankkonto              |
+───────────────────────────────────────────────────────────────────────────────────────────+
                                             ▲
                                             │ Lokale Modbus / WSS Steuerung (Sub-Sekunde)
                                             ▼
+───────────────────────────────────────────────────────────────────────────────────────────+
| 2. SHAREGY (TECHNOLOGIE- & FLOTTEN-AGGREGATOR)                                           |
|    - HEMS Core & KI-Optimizer: Berechnet Wetter- & Lastprognose                           |
|    - Fleet Dispatcher: Steuert die Speicher im Schwarm zielgenau an                       |
|    - Clearing Engine: Verteilt Erlöse transparent (80% Kunde / 20% Plattform)            |
|    - Null Bilanzkreisrisiko: Sharegy haftet NICHT für Marktpreisschwankungen             |
+───────────────────────────────────────────────────────────────────────────────────────────+
                                             ▲
                                             │ Standardisierte OpenADR 2.0b / REST-API
                                             ▼
+───────────────────────────────────────────────────────────────────────────────────────────+
| 3. MASTER-AGGREGATOR / BKV (z. B. NEXT KRAFTWERKE / STATKRAFT)                           |
|    - Bilanzkreisverantwortlicher (BKV) & 24/7 Leitstelle                                 |
|    - Vermarktung an EPEX Spot, Intraday & Regelleistung (aFRR / mFRR)                    |
|    - Rechnet mit den 4 Übertragungsnetzbetreibern (ÜNBs) ab                              |
|    - Schüttet Großhandelserlöse an Sharegy aus                                           |
+───────────────────────────────────────────────────────────────────────────────────────────+
```

---

### 💰 1.3 Das Erlös- & Geldflussmodell (Konkretes Rechenbeispiel)

Wie verdient der Kunde und wie verdient Sharegy Geld?

#### 📈 Beispiel-Szenario: Eine Flotte von 500 Heimspeichern
* **Installierte Speicherkapazität:** 500 Speicher à 10 kWh = **5.000 kWh (5 MWh)**
* **Freigegebene Flexibilität für das VPP:** 50 % der Kapazität = **2.500 kWh (2,5 MWh)**
* **Vermarktungsformen:**
  1. **Spotmarkt-Arbitrage:** Laden bei Negativpreisen / Windüberschuss, Entladen im Abend-Peak.
  2. **Regelleistung (aFRR):** Bereithalten von Sekundärreserve für den Netzbetreiber.

#### 💶 Geldfluss im Monatsabschluss:
1. **Großhandelserlös an der Strombörse:** Der Master-Aggregator erwirtschaftet mit den 2,5 MWh Flexibilität im Monat **12.500 €**.
2. **Master-Aggregator Fee:** Der Partner behält z. B. 10 % für Börsenzugang und Bilanzkreisführung = **1.250 €**.
3. **Auszahlung an Sharegy:** Sharegy erhält die Netto-Erlöse = **11.250 €**.
4. **Automatisches 80/20 Clearing in Sharegy:**
   * **80 % an die 500 Kunden:** `11.250 € * 0,80` = **9.000 €**  
     *(➡️ Jeder Kunde erhält **18,00 € / Monat** bzw. **216 € / Jahr** passiven Flex-Bonus gutgeschrieben).*
   * **20 % Plattform-Marge für Sharegy:** `11.250 € * 0,20` = **2.250 € / Monat**  
     *(➡️ **27.000 € / Jahr** wiederkehrender Plattform-Deckungsbeitrag allein aus dieser 500er Flotte).*

---

### 🔌 1.4 Wie funktioniert die technische Kommunikation zwischen Sharegy und dem Aggregator?

Als Sub-Aggregator muss Sharegy keine eigene Leitstellen-Infrastruktur bauen. Die Kommunikation erfolgt vollautomatisch über Cloud-APIs:

```
[ Master-Aggregator Leitwarte ]
              |
              | 1. Dispatch-Befehl via OpenADR / REST API:
              |    "Bitte Pool um +1,5 MW für 15 Minuten entladen"
              v
[ Sharegy Cloud Fleet Dispatcher ]
              |
              | 2. Schwarm-Aufteilung:
              |    Sharegy prüft alle aktiven Speicher (SoC > 20%)
              |    und weist 300 Speichern je 5 kW Entladeleistung zu.
              v
[ Lokale Heimspeicher der Kunden ]
              |
              | 3. Sekundenschnelle Modbus TCP Regelung
              |    Batterie speist 5 kW ins Haus/Netz ein.
              v
[ Sharegy Telemetrie-Feedback ]
              |
              | 4. Rückmeldung an Aggregator:
              |    "Ist-Einspeisung: 1.492 kW erfolgreich aktiv."
```

* **Standard-Protokoll OpenADR 2.0b:** Der Aggregator agiert als *Virtual Top Node (VTN)*, Sharegy agiert als *Virtual End Node (VEN)*.
* **Latenz:** Dispatch-Befehle werden in unter 2 Sekunden empfangen und an die Heimspeicher via WebSocket verteilt.

---

### 📑 1.5 Vertragsverhandlung mit dem Aggregator: Worauf muss Sharegy achten?

Wenn du mit Next Kraftwerke, Statkraft oder Entelios verhandelst, sind folgende **3 Vertragsklauseln entscheidend**:

1. **Haftungsausschluss bei privatem Kundenausfall (Schwarm-Toleranzband):**
   * *Hintergrund:* Wenn ein privater Kunde sein Internet ausschaltet oder das Auto spontan ansteckt, kann der Speicher nicht entladen werden.
   * *Regelung im Vertrag:* Der Aggregator muss ein **Toleranzband (i. d. R. 10–15 % Überbuchung)** akzeptieren. Sharegy darf **keine Pönalen oder Strafzahlungen** für den Ausfall einzelner privater Heimspeicher zahlen.
2. **Mindest-SoC Schutz (Kundenschutz-Klausel):**
   * Im Vertrag wird festgeschrieben, dass die lokale Eigenversorgung des Haushalts und ein konfigurierbarer **Mindest-Ladezustand (min-SoC, z. B. 20%)** immer Vorrang vor Marktabrufen haben.
3. **Abrechnungs-Intervall & Transparenz:**
   * Der Aggregator muss monatlich eine standardisierte Abrechnung auf 15-Minuten-Basis (`CSV / API`) liefern, damit Sharegy das 80/20-Clearing vollautomatisch verbuchen kann.

---

### ⏱️ 1.6 Der tägliche Ablauf im Regelbetrieb (Automatisierte Kette)

```
[ 1. Tag vorher (Day-Ahead) bis 12:00 Uhr ]
* Sharegy übermittelt aggregierte Verfügbarkeitsprognose für morgen an Aggregator.
* Aggregator platziert Gebote an der Strombörse EPEX Spot / Regelleistung.

[ 2. Erfüllungstag (Echtzeit) ]
* Netzbetreiber oder Börsenfahrplan löst Abruf aus.
* Aggregator sendet Sollwert an Sharegy API.
* Sharegy steuert Speicher sekundenschnell an.
* Telemetrie wird manipulationssicher protokolliert (Audit Trail).

[ 3. Monatsende (Clearing) ]
* Aggregator überweist Sammelbetrag an Sharegy.
* Sharegy Clearing Engine generiert PDF-Abrechnungsbelege für jeden Kunden.
* Flex-Bonus wird den Kundenkonten gutgeschrieben.
```

---

### 💡 1.7 Warum starten 99% aller erfolgreichen HEMS-Unternehmen mit Pfad A?

* **Beispiele aus der Praxis:** Unternehmen wie **sonnen** (sonnenCommunity), **1KOMMA5°** (Heartbeat), **tado°** und **Tibber** haben ihre Flexibilitätsvermarktung alle als Sub-Aggregator mit Partnern wie Next Kraftwerke oder Statkraft gestartet.
* **Fokus auf Kernkompetenz:** Sharegy kann sich zu 100 % auf Software, Benutzererlebnis, Partnerbetriebe (Solarteure) und schnelles Kundenwachstum konzentrieren, während der Partner das energiewirtschaftliche Marktrisiko trägt.

---

## 2. Die Akteure & konkrete Ansprechpartner

| Marktrolle | Funktion im VPP-Ökosystem | Führende Akteure in Deutschland | Zuständige Abteilung & Kontakt |
| :--- | :--- | :--- | :--- |
| **1. Direktvermarkter / VPP-Aggregator** | Vermarktet die Flexibilität an EPEX Spot, Intraday und Regelleistungsmärkten; schüttet Erlöse an Sharegy aus. | • **Next Kraftwerke** (Köln)<br>• **Statkraft** (Düsseldorf)<br>• **Entelios** (München)<br>• **Energy2Market / e2m** (Leipzig)<br>• **sonnen eServices** (Wildpoldsried)<br>• **Lumenaza** (Berlin) | *Business Development / Flexible Assets / Energy Trading Partnerships*<br>E-Mail: `partnerships@...` / `flexibility@...` |
| **2. Wettbewerblicher Messstellenbetreiber (wMSB)** | Installiert Smart Meter Gateways (SMGW), betreibt CLS-Kanäle und liefert 15-Minuten-Lastgänge. | • **Discovergy / inexogy** (Aachen/Heidelberg)<br>• **Solandeo** (Berlin)<br>• **co.met** (Saarbrücken)<br>• **Theben Smart Energy** (Haigerloch)<br>• **PPC** (Mannheim) | *Vertrieb Messwesen / Kooperationen & CLS-Services*<br>E-Mail: `partner@solandeo.com`, `vertrieb@inexogy.com` |
| **3. Verteilnetzbetreiber (VNB)** | Zuständig für § 14a EnWG Netzdrosselung (4,2 kW) und lokales Engpassmanagement (Redispatch 2.0). | Die ca. 880 regionalen VNBs (z. B. **Westnetz**, **Bayernwerk**, **Netze BW**, **Stromnetz Berlin**, **E.DIS**, **Avacon** etc.) | *Einspeiser- & Flexibilitätsmanagement / Netzkundenbetreuung / § 14a Beauftragte* |
| **4. Übertragungsnetzbetreiber (ÜNB)** | Beschafft Frequenz-Regelleistung (FCR, aFRR, mFRR). | **TenneT TSO**, **Amprion**, **50Hertz Transmission**, **TransnetBW** | Gemeinsame Plattform: [regelleistung.net](https://www.regelleistung.net)<br>Connect+ Plattform: [connect-plus.de](https://www.connect-plus.de) |
| **5. Bundesnetzagentur (BNetzA) & Behörden** | Regulatorische Registrierungen, MaStR, Energieversorger-Meldungen. | **Bundesnetzagentur (BNetzA)** (Bonn) | Referat *Netzzugang Strom / Messwesen*<br>[marktstammdatenregister.de](https://www.marktstammdatenregister.de) |
| **6. BDEW / DVGW** | Vergabe von Marktpartner-Codes (BDEW-Codenummer) für Marktkommunikation. | **BDEW Bundesverband der Energie- und Wasserwirtschaft** | [bdew-codes.de](https://www.bdew-codes.de) |

---

## 3. Schritt-für-Schritt Ablaufplan

```
[ Phase 1: Monat 1-2 ] ──> [ Phase 2: Monat 2-3 ] ──> [ Phase 3: Monat 3-4 ] ──> [ Phase 4: Monat 5+ ]
  Partnering & Verträge      Schnittstellen & CLS       Feldtest & PQ-Test         Go-Live & Clearing
```

### 🔹 Phase 1: Partnering & Regulatorik (Monat 1–2)
1. **Aggregator-Gespräche führen:** Kontaktaufnahme mit Next Kraftwerke, Statkraft oder Solandeo bzgl. Sub-Pool-Vermarktung für Heimspeicher und steuerbare Lasten (§ 14a EnWG).
2. **wMSB-Partnerschaft schließen:** Rahmenvereinbarung mit Discovergy/inexogy oder Solandeo für Hardware-Lieferung, Zählertausch und API-Zugriff auf die 15m-Messwerte.
3. **Marktstammdatenregister (MaStR):** Registrierung von Sharegy als Marktakteur (Dienstleister / Aggregator / Softwareplattform).

### 🔹 Phase 2: Technische Schnittstellen-Kopplung (Monat 2–3)
1. **Aggregator-Schnittstelle aktivieren:**
   * Anbindung der Sharegy Cloud an das Dispatching-Gateway des Aggregators via **OpenADR 2.0b**, **IEC 60870-5-104** oder **REST-Webhook**.
   * Testen des Sollwert-Empfangs (+kW Einspeisung, -kW Laden, Ramp-Rate in Sekunden).
2. **CLS-Kanal (Smart Meter Gateway) schalten:**
   * Einrichtung des gesicherten TLS-Proxys zwischen dem SMGW (BSI TR-03109-1) und dem Sharegy HEMS Core.
   * Einbindung von FNN-Steuerbox-Signalen (§ 14a EnWG Dimmung auf 4,2 kW).
3. **Connect+ / Redispatch 2.0:**
   * Test der automatischen Erstellung und Übertragung der 96-Viertelstunden-Fahrpläne (`PT15M`).

### 🔹 Phase 3: Feldtest & Präqualifikation (Monat 3–4)
1. **Pilotflotte ausrollen:** 20 bis 50 Test-Heimspeicher (z. B. Sungrow, SMA, Fronius, Deye) mit aktiver VPP-Einwilligung im Feld aufsetzen.
2. **Abruf-Simulation:** Testen von Lastabwürfen und Schnelllade-Impulsen unter Einhaltung des **20 % Mindest-SoC-Reserveschutzes**.
3. **Doppel-Prüfung (Audit Trail):** Vergleich der Soll-Abrufe mit den gemessenen wMSB-Zählerwerten (Soll vs. Ist).

### 🔹 Phase 4: Kommerzieller Go-Live (Monat 5+)
1. **Freischaltung im Dashboard:** Alle Endkunden können den Flex-Bonus mit 1 Klick im [Smart Energy Optimizer](file:///c:/Users/Public/Dev/sharegy/frontend/src/pages/ControlPage.jsx) aktivieren.
2. **Automatischer Monatsabschluss:** Sharegy zieht die Erlösabrechnung des Aggregators, berechnet den 80/20 Split und stellt Gutschriften bereit.

---

## 4. Notwendige Verträge, Anträge & Registrierungen

### 📑 1. Verträge mit dem Vermarktungs-Partner (BKV / Direktvermarkter)
* **Flexibilitäts-Vermarktungsvertrag (Aggregator Framework Agreement):**
  * *Inhalt:* Bedingungen für die Bereitstellung von Regelleistung (aFRR/mFRR) und Spotmarkt-Flexibilität.
  * *Vergütungsmodell:* Fixe Prämie (€/kW/Monat) oder dynamischer Erlös-Split (z. B. 90/10 Partner zu Sharegy, woraus Sharegy den 80/20 Kundensplit speist).
  * *Pönalen / Haftung:* Ausschluss von Strafzahlungen bei Ausfall einzelner privater Heimspeicher (Schwarm-Toleranzband).
* **Datenschutz- & Auftragsverarbeitungsvertrag (AVV gem. Art. 28 DSGVO):**
  * Übermittlung pseudonymisierter Anlagendaten (Postleitzahl, Netzknoten, Wirkleistung).

### 📑 2. Verträge mit dem Messstellenbetreiber (wMSB)
* **wMSB-Kooperationsvertrag:**
  * Regelung der Zählersetzung beim Kunden (Kosten für Zählertausch i. d. R. gesetzliche Preisobergrenze von 20–50 €/Jahr nach MsbG).
  * API-SLA (Übermittlung der 15m-Lastgänge bis spätestens 04:00 Uhr des Folgetages).
  * CLS-Kanal Nutzungsvereinbarung für Steuerungsimpulse.

### 📑 3. Verträge mit dem Kunden (Endnutzer / Prosumer)
* **VPP-Teilnahmevereinbarung & AGB-Zusatz (im Sharegy Dashboard integriert):**
  * Zustimmung zur netzdienlichen Steuerung des Speichers / der Wallbox.
  * Garantie des Mindest-Ladezustands (20% min-SoC).
  * Auszahlungsmodalitäten des 80 % Flex-Bonus (Gutschrift auf Stromrechnung oder Banküberweisung).

### 📑 4. Regulatorische Meldungen
* **Marktstammdatenregister (MaStR):**
  * Registrierung der Speicher als fernsteuerbare Erzeugungs-/Verbrauchseinheiten mit Verknüpfung zur MaStR-Nummer der PV-Anlage.
* **Meldung an den örtlichen VNB gem. § 14a EnWG:**
  * Übermittlung der SteuVE-Meldung zur Inanspruchnahme des reduzierten Netzentgelts (Modul 1: pauschaler Rabatt ~160 €/Jahr oder Modul 2: prozentuale Reduktion).

---

## 5. Fragen- & Antwortkatalog für Erstgespräche

### 🤝 A. Gespräch mit Direktvermarktern / Aggregatoren (z. B. Next Kraftwerke, Statkraft)

| Typische Frage des Aggregators | Richtige Sharegy-Antwort & Argumentation |
| :--- | :--- |
| *„Welche Asset-Typen poolt ihr und wie groß ist die kumulierte Leistung?“* | *„Wir bündeln private Heimspeicher (3–15 kW / 5–20 kWh), dimmbare Wallboxen (11–22 kW) und Wärmepumpen. Unsere Zielgröße im Pilot-Pool beträgt 2 bis 5 MW schaltbare Leistung mit 0,5C C-Rate.“* |
| *„Wie schnell ist eure Latenz vom Dispatch-Befehl bis zur Reaktion der Batterie?“* | *„Über unsere WebSockets (WSS) und Edge-Controller beträgt die End-to-End Latenz unter 2 Sekunden. Für Sekundärregelleistung (aFRR, 30s) und Redispatch 2.0 (15m) sind wir voll reaktionsfähig.“* |
| *„Wie stellt ihr sicher, dass Kunden-Ausschaltquoten (Default Rate) den Fahrplan nicht gefährden?“* | *„Durch dynamisches Überbuchen (Over-Provisioning) um 15–20 % und kontinuierliche Echtzeit-Telemetry. Fällt ein Speicher lokal aus, kompensieren benachbarte Speicher im Schwarm die Differenz sekundengenau.“* |
| *„Welches Schnittstellen-Protokoll bevorzugt eure Plattform?“* | *„Wir unterstützen OpenADR 2.0b (Virtual End Node / VEN), IEC 60870-5-104 sowie moderne REST Webhooks mit TLS 1.3 und Token-Authentifizierung.“* |
| *„Wie handhabt ihr den Bilanzkreis?“* | *„Wir docken unseren Pool als virtuellen Unter-Bilanzkreis (Sub-Balancing-Group) an euren Master-Bilanzkreis an. Ihr übernehmt das Börsen-Clearing, wir liefern die aggregierten 96-Viertelstunden-Daten.“* |

---

### 🔌 B. Gespräch mit wettbewerblichen Messstellenbetreibern (wMSB)

| Typische Frage des wMSB | Richtige Sharegy-Antwort |
| :--- | :--- |
| *„Welche Smart Meter Gateways (SMGW) setzt ihr voraus?“* | *„Wir sind herstellerunabhängig und kompatibel mit allen BSI-zertifizierten Gateways (PPC, EMH, Theben, Sagemcom), die über einen aktiven CLS-Kanal oder eine HKS-Schnittstelle verfügen.“* |
| *„Wie erfolgt der Zählertausch beim Endkunden?“* | *„Unsere Partner-Fachbetriebe (Elektroinstallateure) können den Einbau übernehmen (sofern beim wMSB als Monteur akkreditiert) oder der wMSB führt den Turnus-Tausch durch.“* |
| *„In welchem Format benötigt ihr die Messwerte?“* | *„Bevorzugt über eine sichere REST-API (JSON) mit 15-Minuten-Lastgängen (`kW` / `kWh`) oder standardisiert per EDIFACT MSCONS / AS4.“* |

---

### 🛡️ C. Gespräch mit dem Verteilnetzbetreiber (VNB)

| Typische Frage des VNB | Richtige Sharegy-Antwort |
| :--- | :--- |
| *„Erfüllt euer System die § 14a EnWG Festlegung BK6-22-300?“* | *„Ja. Sharegy unterstützt sowohl die direkte Dimmung auf 4,2 kW als auch das dynamische Summenleistungs-Modell am NAP. Die Dimmvorgabe wird innerhalb von < 30 Sekunden zuverlässig umgesetzt.“* |
| *„Was passiert bei Ausfall der Internetverbindung?“* | *„Das HEMS verfügt über eine lokale Fail-Safe-Logik: Bleibt der Netzkontakt aus, drosselt das System die steuerbaren Lasten nach Ablauf des Timeouts automatisch auf den sicheren 4,2 kW Grenzwert.“* |

---

## 6. Technische Integrationsarchitektur

Der genaue Ablauf eines Flexibilitäts-Abrufs vom Übertragungsnetzbetreiber bis zur Kundenbatterie:

```
[1. ÜNB (TenneT/Amprion)]
        |
        |  Bedarf: +500 kW Regelleistung (15 min)
        v
[2. VPP-Aggregator / BKV (z. B. Next Kraftwerke)]
        |
        |  OpenADR 2.0b Dispatch-Event (Target: +500 kW)
        v
[3. Sharegy Cloud Fleet Dispatcher]
        |
        |-- Schwarm-Kalkulation: Prüfe aktive Speicher (SoC > 20%, C-Rate <= 0.5C)
        |-- Verteilung auf 100 Kundenspeicher (je 5,0 kW Sollwert)
        |
        +-----------------------------------------------+
        |                                               |
        v (TLS / CLS-Kanal)                             v (TLS / CLS-Kanal)
[4a. Smart Meter Gateway Kunde A]              [4b. Smart Meter Gateway Kunde B]
        |                                               |
        | Modbus TCP (Set: Discharge 5000 W)            | Modbus TCP (Set: Discharge 5000 W)
        v                                               v
[5a. Heimspeicher Kunde A (5 kW)]              [5b. Heimspeicher Kunde B (5 kW)]
        |                                               |
        +───────────────────────┬───────────────────────+
                                |
                                |  1-Sekunden Telemetrie-Push (Ist: +498 kW)
                                v
                [6. Sharegy Aggregated Proof]
                                |
                                |  Erfüllungsnachweis Regelleistung
                                v
                    [7. Aggregator / ÜNB]
                                |
                                |  Monatsabschluss: Erlösgutschrift
                                v
                [8. Sharegy 80/20 Clearing Engine]
                                |
                    +-----------+-----------+
                    |                       |
                    v (80 % Gutschrift)     v (20 % Marge)
              Kunden-Konto            Sharegy Plattform
```

---

## 7. Muster-Anschreiben & Gesprächsleitfäden

### ✉️ Vorlage: Erstkontakt an Direktvermarkter / Aggregatoren

```text
Betreff: Kooperationsanfrage: Flexibilitäts-Aggregator & VPP-Vermarktung für dezentrale Heimspeicher-Flotte (Sharegy)

Sehr geehrte Damen und Herren,
sehr geehrtes Flexibilitäts- & Partnering-Team,

Sharegy betreibt eine modulare Smart Energy Management Plattform (HEMS) für private und gewerbliche Prosumer mit stark wachsender installierter Basis in Deutschland und Österreich.

Wir bündeln Heimspeicher (Sungrow, SMA, Fronius, Deye u. a.), steuerbare Verbrauchseinrichtungen gem. § 14a EnWG sowie dezentrale PV-Anlagen zu einem hochreaktiven, virtuellen Schwarmkraftwerk (VPP). Unsere Plattform unterstützt Sub-Sekunden-Telemetrie, OpenADR 2.0b und standardisierte Dispatching-Schnittstellen.

Für die kommerzielle Vermarktung unseres Flexibilitäts-Pools (Spotmarkt-Arbitrage, aFRR/mFRR und Redispatch 2.0) suchen wir einen erfahrenen Direktvermarktungs- und Bilanzkreispartner (BKV).

Wir möchten Ihnen gerne unser System, die Schnittstellen-Architektur sowie unsere Flotten-Roadmap in einem 30-minütigen Gespräch vorstellen.

Bitte teilen Sie uns mit, welcher Ansprechpartner aus Ihrem Hause für ein kurzes Kennenlernen zur Verfügung steht.

Mit freundlichen Grüßen,
Geschäftsführung Sharegy
Web: https://sharegy.de | E-Mail: kontakt@sharegy.de
```

---

### ✉️ Vorlage: Erstkontakt an wettbewerbliche Messstellenbetreiber (wMSB)

```text
Betreff: Kooperationsanfrage Smart Meter Rollout & CLS-Gateway Integration (Sharegy / wMSB)

Sehr geehrte Damen und Herren,

im Rahmen unseres Rollouts für ganzheitliches Home Energy Management und Mieterstrom gem. § 42b EnWG binden wir Smart Meter Gateways (iMSys) und CLS-Steuerboxen in Mehrfamilienhäusern und Einfamilienhäusern ein.

Wir suchen einen leistungsstarken Messstellenbetreiber-Partner für:
1. Die zuverlässige Zählersetzung und den Rollout von Smart Meter Gateways bei unseren Kunden.
2. Die Bereitstellung von 15-Minuten-Lastgängen via standardisierter REST-API / Cloud-Bridge.
3. Die Nutzung des CLS-Kanals zur netzdienlichen Steuerung nach § 14a EnWG.

Gerne möchten wir die Rahmenbedingungen für eine Kooperationsvereinbarung und technische Schnittstellen mit Ihnen besprechen.

Mit freundlichen Grüßen,
Sharegy Team
```

---

## 8. Sofort-Aktionsliste

1. **Top 3 Aggregatoren anschreiben:** Next Kraftwerke, Statkraft und Solandeo mit dem Muster-Anschreiben kontaktieren.
2. **Marktstammdatenregister:** Stammdaten und Unternehmensprofil von Sharegy als Dienstleister verifizieren.
3. **OpenADR Test-Server aufsetzen:** Die interne Schnittstelle in `backend/vpp/` gegen die Testumgebung des gewählten Aggregators validieren.
4. **Erste 20 Speicherbetreiber vormerken:** Early-Adopter aus der Sharegy-Community für die Pilot-Präqualifikation zusammenstellen.
