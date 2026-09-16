# 👨‍👩‍👧‍👦 Go-to-Market Playbook: Consumer & Prosumer (B2C & Community)
## Schritt-für-Schritt-Leitfaden zur Nutzerakquise, Aktivierung, Community-Wachstum & Monetarisierung

**Version:** 1.0.0 (B2C Execution Guide)  
**Zielgruppe:** Eigenheimbesitzer mit PV-Anlage & Speicher, Balkonkraftwerk-Nutzer, E-Mobilisten, Wärmepumpenbesitzer und Mieter in Mehrfamilienhäusern.  
**Kernziel:** Von 0 auf 1.000 aktive Haushalte in 6 Monaten durch reibungsfreies Onboarding, virale Sharing-Schleifen und Freemium-zu-Pro Upgrades.

---

## 🧭 Inhaltsverzeichnis
1. [Zielgruppen-Personas & Nutzenversprechen (Value Proposition)](#1-zielgruppen-personas--nutzenversprechen)
2. [Der 120-Sekunden Onboarding-Trichter (0 zu "Aha-Moment")](#2-der-120-sekunden-onboarding-trichter)
3. [Akquise-Kanäle & Wachstums-Hebel](#3-akquise-kanaele--wachstums-hebel)
4. [Virale Sharing- & Referral-Schleifen (Growth Loops)](#4-virale-sharing---referral-schleifen)
5. [Freemium-zu-Pro Conversion Strategie](#5-freemium-zu-pro-conversion-strategie)
6. [Retention & Engagement-Mechanismen](#6-retention--engagement-mechanismen)
7. [Wöchentlicher KPI- & Tracking-Dashboard-Fokus](#7-woechentlicher-kpi---tracking-dashboard-fokus)

---

## 1. Zielgruppen-Personas & Nutzenversprechen

```
+───────────────────────────────────────────────────────────────────────────────────────────+
| DIE 4 CONSUMER-PERSONAS BEI SHAREGY                                                      |
+───────────────────────────────────────────────────────────────────────────────────────────+
```

### 🧑‍💼 Persona 1: Der PV- & Speicher-Prosumer ("Maximierer Markus")
* **Profil:** Eigenheim (Baujahr 1990–2022), 8–15 kWp PV-Anlage, 5–15 kWh Speicher (Sungrow, Fronius, SMA, Deye), Wallbox und evtl. Wärmepumpe.
* **Schmerzpunkt:** Intransparente Hersteller-Apps, schlechte oder fehlende Überschussladung, keine Möglichkeit, von dynamischen Börsenpreisen (Tibber/Awattar) zu profitieren.
* **Sharegy USP:** *"Alle Geräte in einer herstellerunabhängigen Schaltzentrale vereinen, bis zu 350 €/Jahr durch dynamisches Laden sparen und mit dem VPP-Flex-Bonus bares Geld verdienen."*

### 🧑‍💻 Persona 2: Der Balkonkraftwerk- & Tech-Enthusiast ("Smart Home Simon")
* **Profil:** Wohnung oder Reihenhaus, 800W Balkonkraftwerk mit Shelly Plus 1PM oder Home Assistant.
* **Schmerzpunkt:** Weiß nicht, wie viel Solarstrom er tatsächlich selbst verbraucht und wie viel er unvergütet ins Netz verschenkt.
* **Sharegy USP:** *"Verbinde deinen Shelly oder Home Assistant in 60 Sekunden kostenlos. Sieh in Echtzeit deinen Autarkie-Grad und optimiere Waschmaschine & Spülmaschine bei Sonnenschein."*

### 🚗 Persona 3: Der E-Mobilist & Wärmepumpen-Besitzer ("Dynamischer Daniel")
* **Profil:** Fährt Elektroauto (ID.4, Tesla, Hyundai Ioniq 5), lädt zu Hause an Wallbox, will günstige Nachtstrompreise nutzen.
* **Schmerzpunkt:** Teurer Grundversorger-Tarif (34 ct/kWh), manuelle Ladeplanung nervt.
* **Sharegy USP:** *"Automatisiertes Überschuss- & Börsenpreis-Laden. Lade dein Auto nachts für unter 18 ct/kWh oder tagsüber kostenlos mit 100% Sonnenstrom."*

### 🏢 Persona 4: Der Mieter im Mehrfamilienhaus ("Community Clara")
* **Profil:** Mietwohnung in einem Gebäude mit Dach-PV oder Quartiersstrom.
* **Schmerzpunkt:** Hohe Stromrechnung, kein eigener Dachzugang für Solaranlagen.
* **Sharegy USP:** *"Nutze günstigen Solarstrom direkt vom Dach deines Hauses gem. § 42b EnWG. Spare bis zu 30% Stromkosten ohne Zählerumbau mit transparenter Monatsabrechnung per PDF."*

---

## 2. Der 120-Sekunden Onboarding-Trichter

Der größte Hebel für B2C-Wachstum ist ein **hürdenloser Einstieg ohne Kreditkarte und ohne Frust**.

```
[ Schritt 1: 0-15s ] ──> [ Schritt 2: 15-45s ] ──> [ Schritt 3: 45-90s ] ──> [ Schritt 4: 90-120s ]
  Magic Link / Social       Haushalt & PLZ           Gerät verbinden            "Aha-Moment":
  Login (1-Klick)           angeben (Prognose)       (Shelly / Inverter / HA)   Live-Sankey-Flow
```

### Die 4 Onboarding-Schritte im Detail:
1. **Schritt 1 (Registrierung in 15 Sekunden):**
   * Nur E-Mail-Adresse eingeben (oder "Sign in with Apple" / "Google").
   * Sofortiger Magic-Link-Login ohne Passwort-Zwang.
2. **Schritt 2 (Haushalts-Setup in 30 Sekunden):**
   * Postleitzahl eingeben (lädt automatisch lokale Wetter- & Solarprognosen und Netzbetreiberdaten).
   * Auswahl: *Einfamilienhaus*, *Wohnung mit Balkonkraftwerk* oder *Energy Community Beitritt*.
3. **Schritt 3 (1-Klick Geräteanbindung in 45 Sekunden):**
   * **Option A:** Shelly Pro 3EM / Plus 1PM über Outbound WebSocket (WSS Token kopieren).
   * **Option B:** Wechselrichter (Sungrow, SMA, Fronius, Deye) via IP / Modbus TCP.
   * **Option C:** Home Assistant Bridge über HACS 1-Klick Entity Picker.
4. **Schritt 4 (Der "Aha-Moment" nach 90 Sekunden):**
   * Das Dashboard erwacht zum Leben: Der **Live-Sankey-Energiefluss** animiert PV-Erzeugung, Hausverbrauch, Netzbezug und Einspeisung in Echtzeit.
   * Erste KI-Ersparnis-Tipps werden eingeblendet.

---

## 3. Akquise-Kanäle & Wachstums-Hebel

```
+───────────────────────────────────────────────────────────────────────────────────────────+
| DIE 4 KERN-AKQUISE-KANÄLE FÜR B2C                                                         |
+───────────────────────────────────────────────────────────────────────────────────────────+
```

### 📣 Kanal 1: Community-Seeding in Solar- & Smart-Home-Foren (Organic Growth)
* **Plattformen:**
  * [Photovoltaikforum.com](https://www.photovoltaikforum.com) (Größtes deutschsprachiges PV-Forum).
  * Reddit: `r/Finanzen`, `r/Balkonkraftwerk`, `r/de_EDV`, `r/homeassistant`.
  * Facebook-Gruppen (*"Photovoltaik & Speicher Erfahrungen"*, *"Balkonkraftwerk Deutschland"*).
* **Vorgehen (Value-First Content):**
  * Keine plumpe Werbung, sondern nützliche Anleitungen und Vergleiche posten:
    * *„Wie ich meinen Sungrow Speicher ohne Cloud-Zwang mit dynamischen Strompreisen steuere.“*
    * *„Die neue § 14a EnWG Dimm-Regel verständlich erklärt – wie man 160 € Netzentgelt-Rabatt sichert.“*
  * Verlinkung auf die kostenlosen Sharegy Handbuch-Guides (`/app/help`).

### 🎥 Kanal 2: YouTube Tech- & Solar-Creator Kooperationen
* **Ziel-Creator:** YouTuber mit 10k–200k Abonnenten im Bereich Energiewende, Smart Home und Elektromobilität (z. B. *Schlau Energiesparen*, *Der Kanal*, *Dennis Witthus*, *Haus Automation*, *simon42*).
* **Format:** Unboxing & Live-Einrichtung: *„Sharegy HEMS im Test: Schlägt diese kostenlose Software teure Smart-Meter-Systeme?“*
* **Incentive:** Exklusiver Partner-Link mit 3 Monaten kostenlosem Pro-Zugang für Zuschauer.

### 🔍 Kanal 3: SEO-Wissensportal & Long-Tail Ratgeber
* Die Handbuch-Artikel aus dem Sharegy Help Center (`/app/help`) ranken für hochrelevante Suchbegriffe:
  * *„Sungrow SH10RT Modbus Register Map Deutsch“*
  * *„§ 14a EnWG Dimmung 4.2 kW Wallbox einstellen“*
  * *„Gemeinschaftliche Gebäudeversorgung § 42b EnWG Musterabrechnung“*
* Jeder Artikel leitet über Call-to-Action Buttons direkt in die kostenlose Registrierung.

### 🏘️ Kanal 4: Lokale Energiegemeinschaften & WEG-Aushänge
* Bereitstellung von **PDF-Aushangvorlagen** für das Treppenhaus: *„Unser Haus teilt jetzt Solarstrom – Registriere dich hier für günstigen Dachstrom.“*

---

## 4. Virale Sharing- & Referral-Schleifen (Growth Loops)

```
[ Nutzer sieht monatliche Ersparnis ] ──> [ Teilt Social-Proof Grafik ] ──> [ Nachbar meldet sich an ]
                 ▲                                                                   │
                 └────────────────── 1 Monat Pro gratis für beide ───────────────────┘
```

1. **"Share my Solar Flow" Social-Card:**
   * Im Dashboard befindet sich ein 1-Klick-Button **"Ersparnis teilen"**.
   * Erzeugt eine visualisierte Infografik für WhatsApp-Status, Instagram oder LinkedIn:  
     *„Diesen Monat 84 % Autarkie erreicht und 92,40 € Stromkosten gespart mit @Sharegy ☀️🔋“*
2. **Nachbarschafts-Referral ("Bring deinen Nachbarn mit"):**
   * Jeder Nutzer hat einen persönlichen Einladungslink (`sharegy.de/join?ref=MARCUS123`).
   * **Belohnung:** Für jeden geworbenen Haushalt erhalten Werber und Geworbener jeweils **1 Monat Sharegy Pro gratis**.

---

## 5. Freemium-zu-Pro Conversion Strategie

Sharegy monetarisiert über ein faires, transparentes **Freemium-Modell**:

```
+───────────────────────────────────────────+───────────────────────────────────────────+
|               SHAREGY FREE                |                SHAREGY PRO                |
|             (0,00 € dauerhaft)            |       (4,99 € / Monat oder 49 € / Jahr)   |
+───────────────────────────────────────────+───────────────────────────────────────────+
| • Live-Energiefluss (Sankey-Diagramm)     | • Alle Free-Features                      |
| • 1 Wechselrichter + 1 Speicher + 1 Zähler| • Unbegrenzte Geräte, Wallboxen & Relais  |
| • Standard 24h Solarprognose              | • KI-gestützte Hybrid-Prognose (98% Güte) |
| • Basis-Historie (letzte 30 Tage)         | • Lückenloses 10-Jahres-Archiv & DATEV-Exp|
| • Community-Hilfebereich                  | • Automatisches Überschussladen (Wallbox) |
|                                           | • Spotmarkt-Optimierung (Tibber/Awattar)  |
|                                           | • VPP-Flexibilitäts-Bonus (80% Gutschrift)|
+───────────────────────────────────────────+───────────────────────────────────────────+
```

### 🎯 Die 3 stärksten Upgrade-Trigger in der App:
1. **Trigger 1: Zweites Großgerät hinzufügen**  
   * Wenn der Nutzer eine Wallbox oder Wärmepumpe hinzufügen möchte: *„Aktiviere Sharegy Pro für intelligentes Überschussladen und spare bis zu 400 € Ladekosten pro Jahr.“*
2. **Trigger 2: VPP Flexibilitäts-Bonus aktivieren**  
   * Nutzer klickt auf Flex-Bonus: *„Verdiene 15–30 € pro Monat mit deinem Speicher. Im Pro-Plan inklusive.“*
3. **Trigger 3: Monatsbericht mit verpasstem Sparpotenzial**  
   * Der kostenlose Monatsbericht zeigt: *„Diesen Monat hättest du mit dynamischem Börsenladen 38,50 € zusätzlich sparen können. Jetzt Pro testen.“*

---

## 6. Retention & Engagement-Mechanismen

Wie verhindern wir, dass Nutzer die App vergessen oder deinstallieren?

1. **Push-Mitteilung: Solar-Spitzen-Alarm (Daily Nudge)**  
   * *„☀️ Perfektes Solarwetter heute ab 11:30 Uhr! Nutze deinen Überschuss für Waschmaschine oder E-Auto.“*
2. **Wöchentlicher Spar-Digest (Jeden Sonntag um 18:00 Uhr)**  
   * E-Mail & In-App Summary: Autarkiequote der Woche, verhinderte CO₂-Emissionen und eingesparte Euro.
3. **Push-Mitteilung: Negativpreis-Warnung an der Strombörse**  
   * *„⚡ Strompreise heute Nacht bei 0 Cent / negativ! Speicher lädt automatisch günstig aus dem Netz.“*

---

## 7. Wöchentlicher KPI- & Tracking-Dashboard-Fokus

Im Sharegy Admin Tracking Dashboard (`/admin/tracking`) überwachen wir wöchentlich:

| KPI | Zielwert (Benchmark) | Hebel bei Unterschreitung |
| :--- | :--- | :--- |
| **Registration-to-Device-Connected** | $> 65\,\%$ | Onboarding-Assistenten vereinfachen, 1-Klick WSS Prompts |
| **Day-7 Retention** | $> 50\,\%$ | Push-Benachrichtigungen für Solarpeaks aktivieren |
| **Day-30 Retention** | $> 40\,\%$ | Wöchentlichen Spar-Digest optimieren |
| **Free-to-Pro Conversion** | $> 8{,}5\,\%$ | Überschusslade- & VPP-Vorteilsbanner schärfen |
| **NPS (Net Promoter Score)** | $> +60$ | Support-Triage beschleunigen, Handbuch-Lücken schließen |
