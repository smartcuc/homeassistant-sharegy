# 🗄️ Vollständige Datenmodell-Referenz

Sharegy ist in fachlich abgegrenzte Django-Apps unterteilt:

---

## 1. `devices` App (Smart Home & EMS Geräte)

### `Home`
Repräsentiert ein Kunden-Zuhause / Gebäude.
- `id` (AutoField): Primärschlüssel.
- `user` (ForeignKey -> `accounts.User`): Eigentümer.
- `name` (CharField): Name (z. B. „Musterstraße 12“).
- `timezone` (CharField): Zeitzone (z. B. `Europe/Berlin`).
- `postal_code`, `city`, `latitude`, `longitude`: Standortkoordinaten für Wetter- & PV-Prognosen.

### `Floor` & `Room`
Räumliche Hierarchie innerhalb eines Zuhauses für das Dashboard und Sankey-Diagramm.
- `Floor`: Stockwerk (z. B. Erdgeschoss, Obergeschoss, Keller).
- `Room`: Raum (z. B. Küche, Wohnzimmer, Technikraum, Garage).

### `Device`
Physisches oder virtuelles Smart-Home-Gerät (z. B. Shelly Plug, Wechselrichter, Wallbox, Wärmepumpe).
- `home`, `room`: Zuordnung.
- `name`, `device_type`, `manufacturer`, `model`, `serial_number`.
- `is_online`, `is_active`, `is_trash`: Status-Flags.

### `DeviceConfig`
Steuerungskonfiguration und Signaltyp für das EMS.
- `device` (OneToOneField -> `Device`).
- `energy_signal_type`: `"pv"` | `"battery"` | `"grid"` | `"load"`.
- `metric_key`: Schlüssel der Haupt-Leistungsmetrik (z. B. `power`, `power_w`, `active_power`).
- `deadband_w`: Schwellenwert in Watt für die Datenbank-Deduplizierung (Standard: `1.0 W`).

### `DeviceMetric` (TimescaleDB Hypertable)
Historische Zeitreihendaten der Gerätemessungen.
- `device` (ForeignKey -> `Device`).
- `timestamp` (DateTimeField): Messzeitpunkt (UTC).
- `metric_key` (CharField): Metrik-Identifikator (z. B. `power`, `voltage`, `current`, `energy_total`).
- `value` (FloatField): Numerischer Messwert.
- **Indizes**: `["timestamp", "device", "metric_key"]` (Primary Time-Series Scan) & `["device", "-timestamp"]`.

### `MetricDefinition`
Katalog aller standardisierten physikalischen Messgrößen und SI-Einheiten.
- `key` (CharField, unique): Technischer Schlüssel (z. B. `power`, `temperature`, `pressure`, `soc`, `voltage`, `current`, `co2`, `humidity`, `flow_rate`).
- `name` (CharField): Benutzerfreundliche Bezeichnung (z. B. „Wirkleistung“, „Luftdruck“, „Batterieladestand (SoC)“).
- `unit` (CharField): Physikalische SI-Einheit (z. B. `W`, `°C`, `hPa`, `%`, `V`, `A`, `kWh`, `ppm`, `lx`).

### `DeviceLatestMetric` (Snapshot-Tabelle)
Garantierte $O(1)$ Schnappschuss-Tabelle für den aktuellen Gerätezustand (1 Zeile pro Gerät/Metrik).
- `device`, `metric_key`, `timestamp`, `value`, `unit`, `updated_at`.

---

## 2. `energy` App (Flusslogik & Sankey)

### `EMSSignalSource`
Virtuelle Aggregationsquelle für den Haushalt.
- `home` (ForeignKey -> `Home`).
- `device` (ForeignKey -> `Device`).
- `energy_signal_type`: `"pv"`, `"battery"`, `"grid"`, `"load"`.

---

## 3. `market` App (Strompreise & Tarife)

### `SpotPrice` (TimescaleDB Hypertable)
Stündliche und 15-minütige EPEX Spot Day-Ahead Börsenstrompreise.
- `timestamp` (DateTimeField): Gültigkeitszeitpunkt (UTC).
- `price_eur_per_kwh` (DecimalField): Börsenpreis in €/kWh (bzw. Cent/kWh / 100).
- `source`: `"energy-charts"`, `"smard"`, `"epex"`.

### `HomeTariff`
Vom Nutzer gewählter Stromtarif pro Haushalt.
- `home` (ForeignKey -> `Home`).
- `valid_from` (DateField): Gültigkeitsbeginn.
- `tariff_type`: `"dynamic"` (Börsenstrom) | `"static"` (Festpreis).
- `static_price_eur_per_kwh`: Fester Arbeitspreis (nur bei `static`).
- **Constraint**: `UniqueConstraint(fields=["home", "valid_from"])`.

### `ElectricityPriceConfig`
Gesetzliche feste Preisbestandteile in Deutschland für dynamische Tarife.
- `valid_from` (DateField).
- `grid_fee_ct`: Netzentgelte (ct/kWh).
- `electricity_tax_ct`: Stromsteuer (2,05 ct/kWh).
- `concession_fee_ct`: Konzessionsabgabe (1,66 ct/kWh).
- `kwk_levy_ct`, `special_grid_levy_ct`, `offshore_levy_ct`: Gesetzliche Umlagen.
- `vat_percent`: Mehrwertsteuersatz (19,00 %).

---

## 4. `producer` & `forecast` Apps (PV-Anlagen & Prognose)

### `GeneratorSystem` & `GeneratorString`
Struktur der PV-Erzeugungsanlagen.
- `GeneratorSystem`: Gesamtanlage (z. B. 10 kWp Dachanlage).
- `GeneratorString`: Einzelner Modulstrang mit Ausrichtung (`azimuth`, 0°=Nord, 180°=Süd), Neigung (`tilt`, z. B. 35°), Modulanzahl und Spitzenleistung (`kwp`).

### `SolarForecast`
96-Stunden PV-Erzeugungsprognose in 15-Minuten-Schritten.
- `home`, `timestamp`, `expected_power_w`, `confidence_interval_low`, `confidence_interval_high`.

---

## 5. `core` & `accounts` Apps (Multi-Tenancy, B2B Whitelabel & Partner-Flotte)

### `Tenant`
Repräsentiert eine Liegenschaft, WEG oder ein B2B-Stadtwerk/EVU.
- `name`, `slug`, `created_at`.
- **Whitelabel-Branding**: `primary_color`, `secondary_color`, `accent_color`, `button_color`, `logo_url`, `favicon_url`, `company_legal_name`, `support_email`, `custom_domain`, `is_whitelabel_active`.

### `TenantMembership`
Verknüpfung von Benutzern mit Liegenschaften.
- `user`, `tenant`, `role` (`admin`, `member`, `installer`, `auditor`, `helpdesk`).

### `PartnerCompany`
Installateursbetrieb / Fachpartner für Flottenmanagement.
- `name`, `slug`, `partner_tier` (`standard`, `pro`, `premium`, `enterprise`), `contact_email`, `phone`, `city`, `postal_code`.

### `PartnerMembership`
Mitarbeiter des Installateursbetriebs.
- `user`, `partner_company`, `role` (`admin`, `technician`, `support`).

### `MaintenanceConsent`
DSGVO- und § 14a-konforme Kundenfreigabe für Fernwartung & Ferndiagnose.
- `home`, `partner_company`, `status` (`active`, `revoked`, `pending`), `allow_remote_control`, `valid_until`, `notes`.

### `Meter` & `BalanceSlot`
Eichrechtskonforme Zählpunkte und 15-Minuten-Lastgangsaldierung nach § 42b EnWG (Gemeinschaftliche Gebäudeversorgung).

- `generator_string` (ForeignKey $ightarrow$ `GeneratorString`).
- `timestamp` (DateTimeField): Prognosezeitpunkt.
- `power_w` (FloatField): Physikalisch/ML-berechnete prognostizierte Leistung.
- `method`: `"physics"` \| `"ml"` \| `"hybrid"`.
