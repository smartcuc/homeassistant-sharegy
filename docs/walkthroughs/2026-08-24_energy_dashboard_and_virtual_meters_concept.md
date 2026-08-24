# ⚡ Konzept: Energiebilanz, Virtuelle Zähler & Sub-Metering

Datum: 24. August 2026  
Status: **Architektur- & UI-Spezifikation**

---

## 1. Strategische Differenzierung: Dashboard vs. Energiebilanz

Um eine intuitive und professionelle Benutzererfahrung (Best-in-Class SaaS) zu gewährleisten, sind das Haupt-Dashboard und das Energie-Dashboard scharf nach **Zeithorizont** und **physikalischen Einheiten** getrennt:

| Kriterium | 🏠 Dashboard (`/app/dashboard`) | ⚡ Energie-Dashboard (`/app/energy`) |
| :--- | :--- | :--- |
| **Fokus** | **Echtzeit-Cockpit (Live)** | **Bilanzierung & Verbrauchs-Analyse** |
| **Zeithorizont** | Aktuelle Sekunde / Live-Takt | Zeitraum (*Heute, 7 Tage, 30 Tage, Jahr, Custom*) |
| **Einheiten** | **Watt (W / kW)** — Momentanleistung | **Kilowattstunden (kWh)** & **Euro (€)** — Mengen & Kosten |
| **Kernfrage** | *„Was passiert in diesem Augenblick?“* | *„Wo ist meine Energie hingeflossen und was hat sie gebracht?“* |
| **Visualisierung** | Animierter Live-Fluss (Sankey-Echtzeit) | **Virtuelle Zähler, Verbrauchs-Donut, Stacked-Bar-Bilanzen** |

---

## 2. Architektur der Virtuellen Zähler (Sub-Metering & Disaggregation)

Ein zentrales Problem in vielen Haushalten: Es gibt einen Hauptzähler (z. B. am Netzanschlusspunkt oder Wechselrichter), aber nur einige Geräte (Wallbox, Wärmepumpe, Waschmaschine) sind mit Zwischensteckern oder Smart Metern ausgestattet.

```mermaid
graph TD
    A[Gesamter Hausverbrauch E_total] --> B[🚗 Wallbox (Virtueller Zähler 1)]
    A --> C[♨️ Wärmepumpe (Virtueller Zähler 2)]
    A --> D[🍳 Küche & Großgeräte (Virtueller Zähler 3)]
    A --> E[💡 Restlicher ungemessener Hausverbrauch (Residual-Zähler)]
```

### Die Residual-Formel (Automatischer Rest-Zähler):
$$E_{\text{residual}} = \max\left(0, E_{\text{house\_total}} - \sum_{i=1}^{n} E_{\text{submeter}_i}\right)$$

* **Vorteil**: Die Summe aller Kacheln ergibt immer exakt 100 % des gemessenen Hausverbrauchs – ohne Lücken oder Widersprüche.
* **Solar-Deckungsanteil pro Verbraucher**:  
  Durch Überlagerung des 15-Minuten-Erzeugungsprofils mit dem Lastprofil des Geräts wird berechnet, wie viel Prozent des Verbrauchs aus eigenem Solarstrom gedeckt wurden (z. B. *„Wallbox: 140 kWh geladen — davon 68 % Solarstrom“*).

---

## 3. Die 4 Kern-Module des Energie-Dashboards

### 1. 🧮 Virtuelle Zähler (Sub-Metering Kacheln)
Jeder gemessene Großverbraucher erhält eine eigene Karte mit folgenden Daten:
* **Verbrauch im gewählten Zeitraum** (z. B. `142,5 kWh`).
* **Anteil am Gesamtverbrauch** (z. B. `34 % des Haushaltsstroms`).
* **Solarer Eigenverbrauchsanteil** (z. B. `🟢 68 % PV-Strom / 🔴 32 % Netzstrom`).
* **Kosten des Geräts** (z. B. `28,40 €` statt `45,60 €` ohne PV).

---

### 2. ⚡ Energetische Mengenbilanz (kWh-Flussmatrix)

Die Gesamtbilanz im gewählten Zeitraum gliedert sich in Erzeugung und Verbrauch:

```
☀️ Solar-Erzeugung (z. B. 450 kWh)
 ├── 🏠 Direktverbrauch:  180 kWh (40 %)
 ├── 🔋 Batteriespeicher: 150 kWh (33 %)
 └── 🔌 Netzeinspeisung:  120 kWh (27 %)

🏠 Hausbedarf (z. B. 380 kWh)
 ├── ☀️ Gedeckt durch PV-Direkt:    180 kWh (47 %)
 ├── 🔋 Gedeckt durch Batterie:      140 kWh (37 %)
 └── 🔌 Gedeckt durch Netzbezug:      60 kWh (16 %)
```

* 🛡️ **Autarkiegrad**:
  $$\text{Autarkie} = \frac{E_{\text{PV}\rightarrow\text{Haus}} + E_{\text{Batt}\rightarrow\text{Haus}}}{E_{\text{Haus\_gesamt}}} = \frac{180 + 140}{380} = \mathbf{84{,}2\,\%}$$
* 🔄 **Eigenverbrauchsgrad**:
  $$\text{Eigenverbrauch} = \frac{E_{\text{PV}\rightarrow\text{Haus}} + E_{\text{PV}\rightarrow\text{Batt}}}{E_{\text{PV\_gesamt}}} = \frac{180 + 150}{450} = \mathbf{73{,}3\,\%}$$

---

### 3. 💶 Monetäre Kosten- & Einsparungsbilanz (€)

* **Vermiedener Netzstrombezug (Ersparnis)**:  
  $$(180\text{ kWh Direkt} + 140\text{ kWh Batterie}) \times 0{,}32\text{ €/kWh} = \mathbf{+102{,}40\text{ €}}$$
* **Erzielte Einspeisevergütung**:  
  $$120\text{ kWh Einspeisung} \times 0{,}08\text{ €/kWh} = \mathbf{+9{,}60\text{ €}}$$
* **Verbliebene Netzbezugskosten**:  
  $$60\text{ kWh Netzbezug} \times 0{,}32\text{ €/kWh} = \mathbf{-19{,}20\text{ €}}$$
* **Netto-Finanzvorteil**: $\mathbf{+92{,}80\text{ €}}$ gegenüber reinem Netzbezug.

---

### 4. 📈 Verbrauchs-Disaggregation & Historische Bilanzen
* **Donut-Chart**: Prozentuale Verteilung der Verbraucher (Wallbox, Wärmepumpe, Küche, Rest).
* **Stacked-Bar-Chart**: Tägliche/Wöchentliche/Monatliche Balken mit Aufteilung nach PV-Direkt, Batterie und Netz.

---

## 4. UI/UX Layout für `EnergyDashboard.jsx`

```
+-----------------------------------------------------------------------------------+
| ⚡ Energiebilanz & Verbrauchs-Analyse                                            |
| [ Heute ] [ Letzte 7 Tage ] [ Dieser Monat ] [ Dieses Jahr ] [ 📅 Benutzerdefiniert ] |
+-----------------------------------------------------------------------------------+
|  [ ☀️ Erzeugung ]   [ 🏠 Verbrauch ]   [ 🛡️ Autarkie ]   [ 🔄 Eigenverbrauch ]   [ 💶 Ersparnis ] |
|     450 kWh            380 kWh             84 %                 73 %              +92,80 €        |
+-----------------------------------------------------------------------------------+
|  VIRTUELLE VERBRAUCHSZÄHLER (SUB-METERING)                                        |
|  +-------------------+  +-------------------+  +-------------------+  +---------+ |
|  | 🚗 Wallbox        |  | ♨️ Wärmepumpe     |  | 🍳 Küche & Geräte |  | 💡 Rest | |
|  | 142 kWh (37 %)    |  | 98 kWh (26 %)     |  | 45 kWh (12 %)     |  | 95 kWh  | |
|  | [██████░░] 68% PV  |  | [████░░░░] 42% PV |  | [█████░░░] 55% PV |  | (25 %)  | |
|  +-------------------+  +-------------------+  +-------------------+  +---------+ |
+-----------------------------------------------------------------------------------+
|  [ 📊 Verbrauchs-Aufteilung (Donut) ]  |  [ 📈 Erzeugung vs. Verbrauch (Balken) ]  |
+-----------------------------------------------------------------------------------+
```

