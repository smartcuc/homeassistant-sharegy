################################################
# helpcenter/management/commands/seed_helpcenter.py
################################################

from django.core.management.base import BaseCommand
from helpcenter.models import HelpCategory, HelpArticle


class Command(BaseCommand):
    help = "Befüllt das Hilfesystem und Wissensportal mit initialen Kategorien und Handbuch-Artikeln."

    def handle(self, *args, **options):
        self.stdout.write("Befülle Hilfesystem & Wissensportal...")

        # 1. KATEGORIEN ANLEGEN
        categories_data = [
            {
                "key": "getting-started",
                "icon": "🚀",
                "title_de": "Erste Schritte & Grundlagen",
                "title_en": "Getting Started & Basics",
                "description_de": "Schnelleinstieg, Onboarding und grundlegende Funktionen der Plattform.",
                "description_en": "Quickstart guides, onboarding, and platform fundamentals.",
                "sort_order": 1,
            },
            {
                "key": "inverters-meters",
                "icon": "☀️",
                "title_de": "Wechselrichter & Zähler",
                "title_en": "Inverters & Smart Meters",
                "description_de": "Anleitungen zur Anbindung von SMA, Sungrow, Fronius, Deye, Huawei & MQTT.",
                "description_en": "Guides for connecting SMA, Sungrow, Fronius, Deye, Huawei & MQTT devices.",
                "sort_order": 2,
            },
            {
                "key": "forecast",
                "icon": "📈",
                "title_de": "Solar- & Lastprognose",
                "title_en": "Solar & Load Forecast",
                "description_de": "Hybrid-Prognosen, Güteberechnung (%-Trefferquote) und Ist-vs-Soll-Vergleich.",
                "description_en": "Hybrid forecasting, accuracy metrics, and actual-vs-forecast comparisons.",
                "sort_order": 3,
            },
            {
                "key": "optimizer",
                "icon": "🤖",
                "title_de": "Smart Energy Optimizer",
                "title_en": "Smart Energy Optimizer",
                "description_de": "Automatisierte Fahrpläne für E-Auto (Wallbox), Hausspeicher & Wärmepumpen.",
                "description_en": "Automated schedules for EV charging, battery storage & heat pumps.",
                "sort_order": 4,
            },
            {
                "key": "tariffs",
                "icon": "⚡",
                "title_de": "Strompreise & Börsenstrom",
                "title_en": "Electricity Tariffs & Dynamic Pricing",
                "description_de": "Dynamische Tarife, Tibber API, Formeln und stichtagsgenaue Tarifhistorie.",
                "description_en": "Dynamic tariffs, Tibber API, pricing formulas, and tariff history.",
                "sort_order": 5,
            },
            {
                "key": "alerts",
                "icon": "🚨",
                "title_de": "Alarm- & Notifikationszentrale",
                "title_en": "Alert & Notification Center",
                "description_de": "Ertragsausfall-Erkennung, Tiefentladeschutz, Schwellwerte und Push-Alarme.",
                "description_en": "Yield loss detection, battery protection, alert thresholds, and push alerts.",
                "sort_order": 6,
            },
            {
                "key": "billing",
                "icon": "🧾",
                "title_de": "Abrechnung & Mieterstrom",
                "title_en": "Billing & Sub-Metering",
                "description_de": "Sub-Metering, automatische Kostenaufteilung für WEGs und PDF-Reports.",
                "description_en": "Sub-metering, automated cost allocation for multi-tenant homes and PDF reports.",
                "sort_order": 7,
            },
        ]

        cats = {}
        for cdata in categories_data:
            cat, _ = HelpCategory.objects.update_or_create(
                key=cdata["key"],
                defaults=cdata,
            )
            cats[cat.key] = cat

        # 2. ARTIKEL ANLEGEN
        articles_data = [
            # --- FORECAST ---
            {
                "category": cats["forecast"],
                "slug": "solar-prognose-und-genauigkeit",
                "context_key": "forecast",
                "title_de": "Solar-Prognose & Ist-vs-Soll-Vergleich verstehen",
                "title_en": "Understanding Solar Forecast & Actual vs. Expected Comparison",
                "summary_de": "Wie die Hybrid-Prognose aus Wetterdaten und ML berechnet wird und was der Genauigkeits-Score bedeutet.",
                "summary_en": "How the hybrid weather & ML forecast is calculated and what the accuracy score means.",
                "content_de": """# Solar-Prognose & Genauigkeitsabgleich

Die Solar-Prognose berechnet auf Basis hochauflösender Wetterdaten (Globalstrahlung, Bewölkung, Temperatur) und deiner Anlagenausrichtung die erwartete stündliche PV-Erzeugung für die nächsten 24 bis 48 Stunden.

## Wie wird die Prognosegüte (%-Score) berechnet?

Der Genauigkeitsabgleich vergleicht stündlich die tatsächliche Erzeugung ($P_{\\text{Real}}$ in kWh) mit dem vorhergesagten Wert ($P_{\\text{Forecast}}$):

$$\\text{Prognosegüte} = \\max\\left(0, 1 - \\frac{\\sum |P_{\\text{Real}} - P_{\\text{Forecast}}|}{\\max(\\sum P_{\\text{Real}}, \\sum P_{\\text{Forecast}}, 0.1)}\\right) \\times 100$$

* 🟢 **Hervorragend ($\ge 90\\,\\%$)**: Exzellente Übereinstimmung mit realen Messwerten.
* 🟡 **Gut ($75 - 89\\,\\%$)**: Normale wetterbedingte Schwankungen (z. B. vereinzelte Wolkenfelder).
* 🔵 **In Kalibrierung ($< 75\\,\\%$)**: Das System lernt standortspezifische Eigenheiten ein.

## Adaptive Selbstkalibrierung

Erkennt das System an mehreren Tagen systematische Abweichungen (z. B. Schattenwurf durch Nachbargebäude am späten Nachmittag), passt ein selbstlernender Korrekturfaktor die zukünftigen Prognosen automatisch an.
""",
                "content_en": """# Understanding Solar Forecast & Accuracy

The solar forecast computes hourly PV production estimates for the next 24 to 48 hours based on high-resolution weather models, orientation, and machine learning.

## How Accuracy is Calculated

We compare actual inverter telemetry ($P_{\\text{Real}}$) against model forecasts ($P_{\\text{Forecast}}$):

$$\\text{Accuracy} = \\max\\left(0, 1 - \\frac{\\sum |P_{\\text{Real}} - P_{\\text{Forecast}}|}{\\max(\\sum P_{\\text{Real}}, \\sum P_{\\text{Forecast}}, 0.1)}\\right) \\times 100$$

* 🟢 **Excellent ($\ge 90\\,\\%$)**: Near-perfect model alignment.
* 🟡 **Good ($75 - 89\\,\\%$)**: Minor weather drift.
* 🔵 **Calibrating ($< 75\\,\\%$)**: Active local parameter tuning.
""",
                "tags": ["forecast", "solar", "genauigkeit", "wetter", "ml"],
                "is_featured": True,
                "sort_order": 1,
            },

            # --- OPTIMIZER ---
            {
                "category": cats["optimizer"],
                "slug": "smart-energy-optimizer-funktionsweise",
                "context_key": "optimizer",
                "title_de": "Smart Energy Optimizer: Zeitfenster & Fahrplan optimal nutzen",
                "title_en": "Smart Energy Optimizer: Best Time Windows & Scheduling",
                "summary_de": "So ermittelt der Optimizer die günstigsten Zeitfenster für Wallbox, Wärmepumpe und Speicherladung.",
                "summary_en": "How the optimizer identifies the most cost-effective windows for EV charging and appliances.",
                "content_de": """# Smart Energy Optimizer

Der Smart Energy Optimizer kombiniert **Solar-Prognose**, **dynamische Strompreise** und deinen **Haushaltsgrundverbrauch**, um automatisiert die besten Zeitfenster des Tages zu ermitteln.

## Zeitfenster-Modi

1. **1-Stunden-Fenster (1h)**: Ideal für Waschmaschine, Trockner oder Geschirrspüler.
2. **2-Stunden-Fenster (2h)**: Optimale Ladedauer für Wärmepumpen-Warmwasser-Überhöhung.
3. **4-Stunden-Fenster (4h)**: Ausgelegt für das Laden von Elektrofahrzeugen (Wallbox mit 11 kW / 22 kW).

## Sparpotenzial maximieren

* **Priorität 1**: 100 % kostenloser PV-Eigenverbrauch bei prognostiziertem Überschuss.
* **Priorität 2**: Netzbezug in Tiefpreis- oder Negativpreisphasen an der Strombörse.
* **Priorität 3**: Schutz des Batteriespeichers vor unnötigem Netzbezug bei anstehendem Sonnenschein.
""",
                "content_en": """# Smart Energy Optimizer

The Smart Energy Optimizer merges solar generation forecasts with dynamic spot market electricity prices to compute optimal schedules.
""",
                "tags": ["optimizer", "fahrplan", "wallbox", "wärmepumpe", "börsenstrom"],
                "is_featured": True,
                "sort_order": 2,
            },

            # --- ALARMS ---
            {
                "category": cats["alerts"],
                "slug": "alarmzentrale-und-anomalieerkennung",
                "context_key": "alerts",
                "title_de": "Alarmzentrale & Automatische Anomalieerkennung",
                "title_en": "Alert Center & Automated Anomaly Detection",
                "summary_de": "Übersicht der 8 Überwachungsregeln für Ertragsausfälle, Tiefentladeschutz und Dauerlasten.",
                "summary_en": "Overview of the 8 automated health checks for solar yield drop, battery SoC, and base load.",
                "content_de": """# Alarmzentrale & Echtzeit-Überwachung

Die Alarmzentrale überwacht kontinuierlich den Zustand deiner Energieflüsse und schlägt bei Unregelmäßigkeiten sofort Alarm.

## Die wichtigsten Überwachungsregeln

1. **Ertragsausfall (Keine PV-Erzeugung)**:
   * Wenn die Wetterdaten Sonnenschein ($> 400\\,\\text{W/m}^2$) melden, der Wechselrichter aber $0\\,\\text{W}$ liefert (z. B. Sicherung ausgelöst oder DC-Schalter aus).
2. **Batterie-Tiefentladeschutz**:
   * Warnung bei Absinken des Batteriestands unter $10\\,\\%$ zur Schonung der Zellchemie.
3. **Unerwarteter Nachtverbrauch (Dauerlast-Alarm)**:
   * Benachrichtigung bei konstantem Verbrauch $> 1.500\\,\\text{W}$ zwischen 01:00 und 05:00 Uhr (z. B. vergessene Heizlüfter oder defekte Pumpen).
4. **Börsenstrom-Preischance**:
   * Automatischer Spar-Tipp bei bevorstehenden Negativpreisen oder Tiefsttarifen.
""",
                "content_en": """# Alert Center & Live Monitoring

The Alert Center provides proactive protection against hardware faults, unexpected consumption, and low battery levels.
""",
                "tags": ["alerts", "alarmzentrale", "überwachung", "batterie", "wechselrichter"],
                "is_featured": True,
                "sort_order": 3,
            },

            # --- INVERTERS / WECHSELRICHTER ---
            {
                "category": cats["inverters-meters"],
                "slug": "sma-sungrow-modbus-tcp-einrichten",
                "context_key": "devices",
                "title_de": "Modbus TCP für SMA, Sungrow & Fronius freischalten",
                "title_en": "Enabling Modbus TCP for SMA, Sungrow & Fronius Inverters",
                "summary_de": "Schritt-für-Schritt-Anleitung zur Aktivierung der lokalen Modbus-TCP-Schnittstelle im Wechselrichter-Webinterface.",
                "summary_en": "Step-by-step instructions to enable local Modbus TCP in your inverter's web portal.",
                "content_de": """# Modbus TCP für Wechselrichter aktivieren

Um Echtzeit-Leistungsdaten (PV, Batterie, Netz) ohne Cloud-Verzögerung abzufragen, aktivieren Sie Modbus TCP im lokalen Webinterface Ihres Wechselrichters:

## SMA Sunny Tripower / Hybrid
1. Im Browser die IP-Adresse des SMA-Wechselrichters aufrufen.
2. Als **Installateur** einloggen.
3. Unter **Gerätekonfiguration** $\\rightarrow$ **Externe Kommunikation** $\\rightarrow$ **Modbus** navigieren.
4. **TCP-Server aktivieren** (Standard-Port: `502`, Unit-ID: `126` oder `3`).
5. Speichern.

## Sungrow SH5.0 / SH10RT
1. In die **iSolarCloud**-App oder das lokale Webportal einloggen.
2. In den **Erweiterten Einstellungen** $\\rightarrow$ **Modbus TCP** auf **Aktiviert** setzen.
3. Port: `502`.

> [!TIP]
> Die IP-Adresse des Wechselrichters im WLAN-Router (z. B. FRITZ!Box) als *„Diesem Netzwerkgerät immer die gleiche IPv4-Adresse zuweisen“* festlegen.
""",
                "content_en": """# Enabling Modbus TCP on Inverters

Follow these steps to unlock local low-latency telemetry from your SMA, Sungrow, or Fronius inverter.
""",
                "tags": ["inverter", "modbus", "sma", "sungrow", "fronius", "lan"],
                "is_featured": True,
                "sort_order": 4,
            },

            # --- TARIFFS ---
            {
                "category": cats["tariffs"],
                "slug": "stromtarife-und-stichtagsberechnung",
                "context_key": "tariffs",
                "title_de": "Strompreise, Stichtage & Tarifhistorie verwalten",
                "title_en": "Managing Electricity Tariffs, Dates & History",
                "summary_de": "Wie Tarifänderungen mit Stichtag (valid_from) erfasst werden, damit historische Energiebilanzen stimmig bleiben.",
                "summary_en": "How to record tariff changes with a valid-from date to preserve accurate historical billing.",
                "content_de": """# Strompreise & Tarifhistorie

Damit deine monatlichen und jährlichen Energiekosten mathematisch exakt bleiben, unterstützt Sharegy **stichtagsgenaue Tarifhistorien**.

## Tarifwechsel erfassen (z. B. zum 01.09.)

1. Öffne die Seite **Strompreise & Tarife**.
2. Wähle das Datum **Gültig ab** (z. B. `01.09.2026`).
3. Gib den neuen Arbeitspreis (ct/kWh), Grundpreis (€/Monat) oder Einspeisesatz ein.
4. Klicke auf **Speichern**.

### Automatische historische Verrechnung
* Alle Tage und Monate **vor dem 01.09.** werden weiterhin mit dem vorherigen Tarif berechnet.
* Alle Verbräuche **ab dem 01.09.** fließen mit dem neuen Satz in die Energiebilanz und Abrechnung ein.
""",
                "content_en": """# Tariffs & Historical Precision

Sharegy uses date-effective tariffs (`valid_from`) to guarantee exact retroactive energy accounting.
""",
                "tags": ["tariffs", "strompreis", "stichtag", "einspeisevergütung", "tibber"],
                "is_featured": False,
                "sort_order": 5,
            },

            # --- ENERGY DASHBOARD ---
            {
                "category": cats["getting-started"],
                "slug": "energiebilanz-und-autarkiegrad",
                "context_key": "energy_dashboard",
                "title_de": "Energiebilanz, Autarkiegrad & Eigenverbrauchsquote",
                "title_en": "Energy Balance, Self-Sufficiency & Autarky Rate",
                "summary_de": "Die wichtigsten Kennzahlen im Energie-Dashboard einfach erklärt.",
                "summary_en": "Key performance indicators of the energy balance dashboard explained.",
                "content_de": """# Energiebilanz & Autarkiegrad

Das Energie-Dashboard liefert eine ganzheitliche Übersicht über Erzeugung, Speicher, Verbrauch und Netzinteraktion.

## Kennzahlen im Überblick

* **Autarkiegrad (%)**: Anteil des gesamten Stromverbrauchs, der durch die eigene PV-Anlage und den Speicher gedeckt wurde (Ziel: $\ge 70\\,\\%$).
  $$\\text{Autarkie} = \\left(1 - \\frac{\\text{Netzbezug}}{\\text{Gesamtverbrauch}}\\right) \\times 100$$

* **Eigenverbrauchsquote (%)**: Anteil des erzeugten Solarstroms, der direkt im Haus verbraucht oder im Akku gespeichert wurde (anstatt eingespeist zu werden).
  $$\\text{Eigenverbrauch} = \\frac{\\text{Direktverbrauch} + \\text{Batterieladung}}{\\text{Gesamterzeugung}} \\times 100$$
""",
                "content_en": """# Energy Balance & Self-Sufficiency

An overview of autarky rates, self-consumption ratios, and solar flows.
""",
                "tags": ["energy", "autarkie", "eigenverbrauch", "bilanz"],
                "is_featured": True,
                "sort_order": 6,
            },
        ]

        for adata in articles_data:
            HelpArticle.objects.update_or_create(
                slug=adata["slug"],
                defaults=adata,
            )

        self.stdout.write(self.style.SUCCESS(f"Erfolgreich {len(categories_data)} Kategorien und {len(articles_data)} Handbuch-Artikel initialisiert!"))

