import os
import re
import json

src_dir = r"c:\Users\Public\Dev\eswes\frontend\src"
de_path = r"c:\Users\Public\Dev\eswes\frontend\src\i18n\locales\de.json"
en_path = r"c:\Users\Public\Dev\eswes\frontend\src\i18n\locales\en.json"
pl_path = r"c:\Users\Public\Dev\eswes\frontend\src\i18n\locales\pl.json"

with open(de_path, "r", encoding="utf-8") as f:
    de_data = json.load(f)
with open(en_path, "r", encoding="utf-8") as f:
    en_data = json.load(f)
with open(pl_path, "r", encoding="utf-8") as f:
    pl_data = json.load(f)

def get_flat(d, prefix=""):
    res = {}
    for k, v in d.items():
        full = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            res.update(get_flat(v, full))
        else:
            res[full] = v
    return res

def set_nested(d, path, val):
    parts = path.split(".")
    curr = d
    for p in parts[:-1]:
        if p not in curr or not isinstance(curr[p], dict):
            curr[p] = {}
        curr = curr[p]
    curr[parts[-1]] = val

de_flat = get_flat(de_data)
en_flat = get_flat(en_data)
pl_flat = get_flat(pl_data)

# Regex to find t("...", "...")
t_regex = re.compile(r't\(\s*["\']([a-zA-Z0-9_\.\-]+)["\'](?:\s*,\s*["\']((?:[^"\\]|\\.)*)["\'])?')

extracted = {}
for root, dirs, files in os.walk(src_dir):
    for f in files:
        if f.endswith(".jsx") or f.endswith(".js"):
            full_path = os.path.join(root, f)
            with open(full_path, "r", encoding="utf-8") as file:
                content = file.read()
            for m in t_regex.finditer(content):
                key = m.group(1)
                fallback = m.group(2)
                if key.startswith(".") or "/" in key:
                    continue
                extracted[key] = fallback or key

print(f"Total extracted keys: {len(extracted)}")

# Dictionary of high-quality English and Polish translations for newly extracted/missing keys
# Common translation rules / mappings for German terms:
common_en_dict = {
    # General / Navigation / Banners
    "banners.new_devices_detected": "New devices detected",
    "banners.configure_now": "Configure now",
    "banners.timezone_warning": "⚠️ Timezone not configured",
    "banners.timezone_desc": "For accurate time series, reports, and alerts, a timezone should be selected.",
    "banners.detected_timezone": "Detected timezone:",
    "banners.accept_timezone": "Accept timezone",
    "banners.open_settings": "Open settings",
    "banners.devices_need_config": "Devices require configuration",
    "banners.set_device_types_desc": "Set device roles and types to calculate energy flow accurately.",
    "banners.open_devices": "Open devices →",
    "common.back_to_top": "Back to top",
    "common.my_home": "My Home",
    "common.realtime": "Realtime",
    "common.sending": "Sending...",
    "common.offline": "Offline",
    "common.active": "Active",
    "common.idle": "Idle",
    "common.standby": "Standby",
    "common.copied": "Copied to clipboard!",
    "common.copy": "Copy",
    "common.error_saving": "Error while saving",
    "auth.login": "Sign In",
    "nav.energy_control": "Energy Control",
    "nav.agent_support_hub": "Support Hub (Triage)",
    "nav.logout": "Sign Out",
    "settings.appearance": "Appearance & Theme",
    "help.title": "Help & Handbook",
    "theme.light_mode": "Switch to light mode",
    "theme.dark_mode": "Switch to dark mode",
    "homes.switcher_title": "Switch property",
    "homes.select_property": "Select property",
    "homes.manage_structures": "Manage properties",
    "homes.single_badge_title": "Manage building & room structure",
    "dashboard.live_energy_ticker_title": "Open live energy flow & dashboard",

    # Waterfall
    "waterfall.title": "Live Power Dispatcher (Surplus Waterfall)",
    "waterfall.subtitle": "Dynamic merit-order allocation of solar power across all consumer stages.",
    "waterfall.pv_gen": "1. Total Solar Generation",
    "waterfall.pv_desc": "Available gross power from solar array",
    "waterfall.load_title": "2. House Baseload (Priority 0)",
    "waterfall.load_desc": "Direct power supply for household consumers",
    "waterfall.storage_title": "3. Home Battery (Priority 1)",
    "waterfall.storage_desc": "Battery charging for night coverage",
    "waterfall.bwwp_title": "4. Heat Pump / Hot Water (Priority 2)",
    "waterfall.bwwp_desc": "SG-Ready thermal solar boost up to 60°C",
    "waterfall.wallbox_title": "5. Wallbox / EV (Priority 3)",
    "waterfall.wallbox_desc": "OCPP 1.6-J dynamic PV surplus charging",
    "waterfall.remaining": "Remaining",
    "waterfall.grid_export": "Grid Export",
    "waterfall.ready_0w": "Ready (0 W)",

    # Recap
    "recap.title": "Savings & ROI Recap",
    "recap.subtitle": "Real grid cost savings compared to standard basic grid tariff.",
    "recap.share_btn": "Share Achievements",
    "recap.cost_savings": "Cost Savings",
    "recap.vs_grid": "✓ Compared to {{price}} ct/kWh grid",
    "recap.own_power": "Self-generated power from PV & storage",
    "recap.trees_equiv": "🌳 Equivalent to ~{{trees}} trees",
    "recap.grid_fee_bonus": "§ 14a Grid Fee Discount",
    "recap.modul1_badge": "🛡️ Module 1 flat discount active",

    # Wallbox
    "wallbox.mode_pv_surplus": "☀️ Solar Surplus Only",
    "wallbox.mode_min_pv": "⛅ Min + Solar Surplus",
    "wallbox.mode_spot_price": "💶 Spot Price Guided",
    "wallbox.mode_instant": "⚡ Fast Charge (Max Power)",
    "wallbox.mode_off": "🛑 Locked / Paused",
    "wallbox.status_charging": "Actively Charging",
    "wallbox.status_preparing": "Vehicle Connected",
    "wallbox.waiting_for_solar": "Waiting for Solar Power",
    "wallbox.status_ready": "Ready",
    "wallbox.loading_data": "Loading Wallbox & Smart Charging data...",
    "wallbox.empty_title": "EV & Wallbox Smart Charging",
    "wallbox.empty_subtitle": "Hardware-free solar surplus and spot price charging for any modern wallbox.",
    "wallbox.empty_no_wallbox": "No wallbox connected",
    "wallbox.empty_connect_desc": "Connect your Easee, go-eCharger, Keba, Alfen, Mennekes, Zaptec, or OpenWB in under 60 seconds via Cloud WebSocket.",
    "wallbox.connect_btn": "Connect Wallbox Now",
    "wallbox.charging_power": "Charging Power",
    "wallbox.charged_session": "Charged (Session)",
    "wallbox.km_range": "km range added",
    "wallbox.km_total": "km total",
    "wallbox.ev_battery": "EV Battery",
    "wallbox.departure_title": "Departure Ready & Target Charging",
    "wallbox.departure_subtitle": "Charges primarily with PV surplus & cheapest overnight spot prices",
    "wallbox.departure_time": "Departure:",
    "wallbox.target_soc": "Target:",
    "wallbox.smart_charging_mode": "Smart Charging Mode",
    "wallbox.mode_desc_pv": "True solar surplus only",
    "wallbox.mode_desc_min_pv": "Min. baseload + solar boost",
    "wallbox.mode_desc_spot": "Cheapest spot market hours",
    "wallbox.mode_desc_instant": "Maximum charging power",
    "wallbox.mode_desc_paused": "Charging paused",
    "wallbox.opt_pv_surplus": "☀️ Solar Only",
    "wallbox.opt_min_pv": "⛅ Min + PV",
    "wallbox.opt_spot_price": "💶 Spot Price",
    "wallbox.opt_instant": "⚡ Fast Charge",
    "wallbox.opt_off": "🛑 Locked",
    "wallbox.enwg_badge": "§ 14a EnWG controllable (4.2 kW grid protection active)",
    "wallbox.enwg_bonus": "+160 € / yr discount",
    "wallbox.cable": "Cable:",
    "wallbox.connected": "Plugged in",
    "wallbox.start_btn": "▶️ Start",
    "wallbox.stop_btn": "⏹️ Stop",
    "wallbox.unlock_cable_title": "Unlock charging cable",
    "wallbox.pro_modal_title": "Smart Wallbox Charging",
    "wallbox.pro_modal_desc": "Automatic solar surplus control and dynamic spot price charging for your electric vehicle.",

    # Simple Dashboard
    "simple_dashboard.badge_solar": "🟢 100% Solar Powered",
    "simple_dashboard.headline_solar": "Your household is currently running self-sufficiently on solar energy.",
    "simple_dashboard.subline_solar_surplus": "PV produces {{pv}}. Surplus of {{surplus}} flows into grid or battery storage.",
    "simple_dashboard.subline_solar_covered": "Solar system covers your current household consumption of {{load}}.",
    "simple_dashboard.badge_battery": "🔋 Battery Powered",
    "simple_dashboard.headline_battery": "Your household is powered by the battery storage system.",
    "simple_dashboard.subline_battery_soc": "Battery level is at {{soc}}%. Discharge power: {{power}}.",
    "simple_dashboard.subline_battery_power": "Current discharge power: {{power}}.",
    "simple_dashboard.badge_grid_import": "⚡ Grid Import Active",
    "simple_dashboard.headline_grid_import": "Currently drawing electricity from the public grid.",
    "simple_dashboard.subline_grid_import": "Grid import: {{power}} · Optimized load management active.",
    "simple_dashboard.badge_grid_export": "📤 Grid Feed-in",
    "simple_dashboard.headline_grid_export": "Solar surplus is being fed into the electricity grid.",
    "simple_dashboard.subline_grid_export": "Feed-in: {{power}} at your guaranteed tariff rate.",
    "simple_dashboard.badge_balanced": "✨ Balanced Operation",
    "simple_dashboard.headline_balanced": "Energy management is running in optimal equilibrium.",
    "simple_dashboard.subline_balanced": "Generation, storage utilization, and consumption are balanced.",
    "simple_dashboard.live_flow_title": "Live Energy Flow",
    "simple_dashboard.live_flow_desc": "Real-time measurements of all primary components right now.",
    "simple_dashboard.open_expert_view": "Open Expert View",
    "simple_dashboard.total_energy_period": "Total Energy for Period ({{period}})",
    "simple_dashboard.top_consumers": "Top Energy Consumers",
    "simple_dashboard.manage_devices": "Manage devices →",

    # Energy terms
    "energy.period_today": "Today",
    "energy.period_7d": "Last 7 Days",
    "energy.period_30d": "Last 30 Days",
    "energy.period_year": "This Year",
    "energy.custom_period_tooltip": "Set custom date range",
    "energy.custom_period": "Custom Range...",
    "energy.generation": "Generation",
    "energy.household": "Household",
    "energy.demand": "Demand",
    "energy.battery_storage": "Storage",
    "energy.battery_charging": "⚡ Charging",
    "energy.battery_discharging": "🏠 Discharging",
    "energy.feedin": "Feed-in",
    "energy.grid_import": "Grid Import",
    "energy.export_action": "📤 Feed-in",
    "energy.import_action": "📥 Import",
    "energy.kwh_balance": "kWh Balance",
    "energy.solar_generation_total": "Total Solar Generation",
    "energy.house_consumption_total": "Total House Consumption",
    "energy.grid_import_total": "Grid Electricity Imported",
    "energy.solar_export_total": "Solar Electricity Exported",
    "energy.demand_coverage": "Demand Coverage:",
    "energy.solar_battery": "Solar & Battery",
    "energy.grid": "Grid",
    "energy.autarky_rate": "Autarky Rate",
    "energy.co2_saved": "CO₂ Avoided",
    "energy.total_with_kwh": "Total: {{val}} kWh",
    "energy.charge_with_kwh": "Charged: {{val}} kWh",

    # Alerts
    "alerts.severity_critical": "Critical",
    "alerts.severity_warning": "Warnings",
    "alerts.severity_info": "Savings Tips",
    "alerts.modal_title": "Alert & Notification Center",
    "alerts.modal_subtitle": "Real-time monitoring of yield losses, battery state, baseloads, and spot market opportunities.",
    "alerts.summary_total": "Active Total",
    "alerts.tab_all": "All Active",
    "alerts.tab_history": "History",
    "alerts.empty_history": "No resolved alerts",
    "alerts.empty_active": "No active alerts",
    "alerts.empty_history_desc": "Acknowledged or automatically resolved alerts are archived in history.",
    "alerts.empty_active_desc": "All monitored systems, batteries, and generation assets are operating optimally.",
    "alerts.action_resolve": "✓ Resolve",
    "alerts.action_seen": "Acknowledge",
    "alerts.monitoring_active": "Live rule monitoring active",
    "alerts.critical_badge": "Critical System Alert",
    "alerts.warning_badge": "System Notice",
    "alerts.info_badge": "Savings Opportunity",
    "alerts.more": "more",
    "alerts.open_center": "Open Alert Center →",
    "alerts.open_notifications_title": "Open Alert & Notification Center",
    "alerts.page_title": "Alert & Notification Center",
    "alerts.page_subtitle": "Real-time monitoring of yield losses, battery health, baseloads, and spot market savings.",
    "alerts.active_total": "Active Alerts",
    "alerts.resolved_history": "History",
    "alerts.live_monitoring": "Live Monitoring Active",
    "alerts.all_optimal_title": "Everything Optimal – No Active Alerts",
    "alerts.all_optimal": "All monitored PV arrays, battery storage units, inverters, and household loads are operating smoothly in the optimal range.",
    "alerts.mark_resolved": "Resolved",
    "alerts.mark_seen": "Acknowledge",

    # Billing
    "billing.nav_title": "Tariffs & Subscription",
    "billing.pro_highlights": "Sharegy Pro Benefits",
    "billing.seed_error": "Error generating demo invoices.",
    "billing.invoices_title": "Invoices",
    "billing.invoices_desc": "Download all issued invoices with itemized VAT here.",
    "billing.seed_demo": "Load Demo Invoices",
    "billing.th_invoice_nr": "Invoice No.",
    "billing.th_date": "Date",
    "billing.th_tariff_period": "Tariff / Period",
    "billing.th_amount": "Amount",
    "billing.th_status": "Status",
    "billing.th_action": "Action",
    "billing.paid": "Paid",
    "billing.no_invoices": "No invoices yet. After the first billing cycle, your documents will appear here automatically.",
    "billing.terms_required": "Please accept the Terms of Service and Privacy Policy to proceed.",
    "billing.plan_change_error": "Error initiating plan checkout.",
    "billing.network_error": "Network error during plan change.",
    "billing.cancel_confirm": "Are you sure you want to cancel your subscription at the end of the billing period?",
    "billing.cancel_error": "Error cancelling subscription.",
    "billing.reactivate_error": "Error reactivating subscription.",
    "billing.plan_free_name": "Sharegy Free",
    "billing.plan_free_badge": "Basic",
    "billing.plan_pro_name": "Sharegy Pro",
    "billing.plan_pro_badge": "Pro",

    # Devices & Interfaces
    "device_chart.channel_label": "Measurement Channel:",
    "device_chart.no_data": "No metrics available for this period",
    "device_remove.online_warning": "⚠ At least one selected device is currently online.\\n\\nIf MQTT, Home Assistant, or ioBroker continue sending data, the device may be re-discovered automatically.\\n\\nMove to trash anyway?",
    "device_remove.error": "Error removing device.",
    "interfaces.copy_not_supported": "Clipboard copy not supported",
    "interfaces.regenerate_confirm": "Are you sure you want to regenerate the MQTT password? Existing devices must be updated with the new credentials.",
    "interfaces.regenerate_success": "New MQTT password generated successfully!",
    "interfaces.regenerate_error": "Error generating new password.",
    "interfaces.title": "Interfaces & Integrations",
    "interfaces.subtitle": "Connect your devices and central hubs via Outbound WebSocket (Shelly), Sungrow direct pairing, Cloud inverters, Home Assistant plugin, or MQTT.",
    "interfaces.qr_code": "QR Code",
    "interfaces.copy_all": "Copy All Credentials",
    "interfaces.loading": "Loading interface credentials...",
    "interfaces.broker_host": "Broker Host",
    "interfaces.port": "Port (TCP)",
    "interfaces.username": "Username",
    "interfaces.password": "Password",
    "interfaces.base_topic": "Your personal base topic:",
    "interfaces.regenerate_btn": "Regenerate Password",

    # Market
    "market.spot_price_title": "Current Spot Market Electricity Price (EPEX Spot)",
    "tariffs.invalid_price": "Please enter a valid energy price in ct/kWh.",
    "tariffs.invalid_feedin_price": "Please enter a valid feed-in tariff in ct/kWh.",
    "tariffs.save_success": "Electricity & feed-in tariff saved successfully.",

    # Community
    "community.invite_link": "Invite Link",
    "notifications.hide_settings": "Close Push Settings",
    "notifications.configure_push": "Configure Push Alerts",
    "notifications.device_removed": "Device successfully unregistered.",
    "notifications.unsubscribed": "Push notifications successfully deactivated on this device.",
}

# Polish translations dictionary for high coverage
common_pl_dict = {
    "banners.new_devices_detected": "Wykryto nowe urządzenia",
    "banners.configure_now": "Skonfiguruj teraz",
    "banners.timezone_warning": "⚠️ Strefa czasowa nie jest skonfigurowana",
    "banners.timezone_desc": "Wybierz strefę czasową, aby zapewnić prawidłowe wykresy i powiadomienia.",
    "banners.detected_timezone": "Wykryta strefa czasowa:",
    "banners.accept_timezone": "Zaakceptuj strefę czasową",
    "banners.open_settings": "Otwórz ustawienia",
    "banners.devices_need_config": "Urządzenia wymagają konfiguracji",
    "banners.set_device_types_desc": "Ustaw typy urządzeń, aby prawidłowo obliczać przepływ energii.",
    "banners.open_devices": "Otwórz urządzenia →",
    "common.back_to_top": "Przewiń do góry",
    "common.my_home": "Mój dom",
    "common.realtime": "Czas rzeczywisty",
    "common.sending": "Wysyłanie...",
    "common.offline": "Offline",
    "common.active": "Aktywny",
    "common.idle": "Bezczynny",
    "common.standby": "Czuwanie",
    "common.copied": "Skopiowano do schowka!",
    "common.copy": "Kopiuj",
    "common.error_saving": "Błąd podczas zapisywania",
    "auth.login": "Zaloguj się",
    "nav.energy_control": "Sterowanie energią",
    "nav.agent_support_hub": "Centrum wsparcia",
    "nav.logout": "Wyloguj się",
    "settings.appearance": "Wygląd i motyw",
    "help.title": "Pomoc i podręcznik",
    "theme.light_mode": "Przełącz na jasny motyw",
    "theme.dark_mode": "Przełącz na ciemny motyw",
    "homes.switcher_title": "Zmień nieruchomość",
    "homes.select_property": "Wybierz nieruchomość",
    "homes.manage_structures": "Zarządzaj nieruchomościami",
    "homes.single_badge_title": "Zarządzaj strukturą budynku",
    "dashboard.live_energy_ticker_title": "Otwórz przepływ energii na żywo",
    "waterfall.title": "Rozdział mocy na żywo (Kaskada nadwyżki)",
    "waterfall.subtitle": "Dynamiczny podział energii słonecznej na poszczególne poziomy zużycia.",
    "waterfall.pv_gen": "1. Całkowita generacja PV",
    "waterfall.pv_desc": "Dostępna moc brutto z dachu",
    "waterfall.load_title": "2. Zużycie domowe (Priorytet 0)",
    "waterfall.load_desc": "Bezpośrednie zasilanie odbiorników domowych",
    "waterfall.storage_title": "3. Magazyn energii (Priorytet 1)",
    "waterfall.storage_desc": "Ładowanie baterii na potrzeby nocne",
    "waterfall.bwwp_title": "4. Pompa ciepła CWU (Priorytet 2)",
    "waterfall.bwwp_desc": "SG-Ready termiczne doładowanie słoneczne do 60°C",
    "waterfall.wallbox_title": "5. Wallbox / Samochód EV (Priorytet 3)",
    "waterfall.wallbox_desc": "OCPP 1.6-J dynamiczne ładowanie z nadwyżki PV",
    "waterfall.remaining": "Pozostało",
    "waterfall.grid_export": "Eksport do sieci",
    "waterfall.ready_0w": "Gotowy (0 W)",
    "recap.title": "Podsumowanie oszczędności i ROI",
    "recap.subtitle": "Rzeczywiste oszczędności kosztów sieciowych w porównaniu ze standardową taryfą.",
    "recap.share_btn": "Podziel się sukcesem",
    "recap.cost_savings": "Oszczędności kosztów",
    "recap.vs_grid": "✓ W porównaniu do {{price}} gr/kWh z sieci",
    "recap.own_power": "Energia własna z PV i magazynu",
    "recap.trees_equiv": "🌳 Odpowiednik ~{{trees}} drzew",
    "recap.grid_fee_bonus": "§ 14a Ulga w opłacie sieciowej",
    "recap.modul1_badge": "🛡️ Ryczałt modułu 1 aktywny",
    "wallbox.mode_pv_surplus": "☀️ Tylko nadwyżka PV",
    "wallbox.mode_min_pv": "⛅ Min + Nadwyżka PV",
    "wallbox.mode_spot_price": "💶 Według ceny giełdowej",
    "wallbox.mode_instant": "⚡ Szybkie ładowanie (Maks. moc)",
    "wallbox.mode_off": "🛑 Zablokowane / Wstrzymane",
    "wallbox.status_charging": "Ładuje aktywnie",
    "wallbox.status_preparing": "Pojazd podłączony",
    "wallbox.waiting_for_solar": "Oczekiwanie na energię słoneczną",
    "wallbox.status_ready": "Gotowy",
    "wallbox.loading_data": "Ładowanie danych stacji ładowania...",
    "wallbox.empty_title": "Inteligentne ładowanie pojazdów elektrycznych",
    "wallbox.empty_subtitle": "Ładowanie z nadwyżki fotowoltaiki i dynamicznych cen bez dodatkowego sprzętu.",
    "wallbox.empty_no_wallbox": "Brak podłączonej stacji Wallbox",
    "wallbox.empty_connect_desc": "Połącz swoją stację w mniej niż 60 sekund przez Cloud WebSocket.",
    "wallbox.connect_btn": "Połącz stację ładowania",
    "wallbox.charging_power": "Moc ładowania",
    "wallbox.charged_session": "Naładowano (Sesja)",
    "wallbox.km_range": "km dodanego zasięgu",
    "wallbox.km_total": "km łącznie",
    "wallbox.ev_battery": "Bateria pojazdu",
    "wallbox.departure_title": "Planer gotowości do odjazdu",
    "wallbox.departure_subtitle": "Ładuje głównie z nadwyżki PV i najtańszych godzin nocnych",
    "wallbox.departure_time": "Odjazd:",
    "wallbox.target_soc": "Cel:",
    "wallbox.smart_charging_mode": "Tryb inteligentnego ładowania",
    "wallbox.mode_desc_pv": "Tylko rzeczywista nadwyżka słoneczna",
    "wallbox.mode_desc_min_pv": "Moc podstawowa + doładowanie solarne",
    "wallbox.mode_desc_spot": "Najtańsze godziny giełdowe",
    "wallbox.mode_desc_instant": "Maksymalna moc ładowania",
    "wallbox.mode_desc_paused": "Ładowanie wstrzymane",
    "wallbox.opt_pv_surplus": "☀️ Tylko PV",
    "wallbox.opt_min_pv": "⛅ Min + PV",
    "wallbox.opt_spot_price": "💶 Cena giełdowa",
    "wallbox.opt_instant": "⚡ Szybkie",
    "wallbox.opt_off": "🛑 Zablokowane",
    "wallbox.enwg_badge": "§ 14a Sterowalny punkt poboru aktywny",
    "wallbox.enwg_bonus": "+160 € / rok korzyści",
    "wallbox.cable": "Kabel:",
    "wallbox.connected": "Podłączony",
    "wallbox.start_btn": "▶️ Start",
    "wallbox.stop_btn": "⏹️ Stop",
    "wallbox.unlock_cable_title": "Odblokuj kabel ładowania",
    "wallbox.pro_modal_title": "Inteligentne ładowanie Wallbox",
    "wallbox.pro_modal_desc": "Automatyczne sterowanie nadwyżką PV i dynamiczne ceny giełdowe dla Twojego samochodu.",
    "simple_dashboard.badge_solar": "🟢 100% Energia słoneczna",
    "simple_dashboard.headline_solar": "Twoje gospodarstwo działa obecnie w pełni samowystarczalnie dzięki fotowoltaice.",
    "simple_dashboard.subline_solar_surplus": "PV produkuje {{pv}}. Nadwyżka {{surplus}} płynie do sieci lub magazynu.",
    "simple_dashboard.subline_solar_covered": "Instalacja PV pokrywa aktualne zużycie domowe na poziomie {{load}}.",
    "simple_dashboard.badge_battery": "🔋 Zasilanie z magazynu",
    "simple_dashboard.headline_battery": "Twój dom jest zasilany z magazynu energii.",
    "simple_dashboard.subline_battery_soc": "Poziom baterii: {{soc}}%. Moc rozładowania: {{power}}.",
    "simple_dashboard.subline_battery_power": "Aktualna moc rozładowania: {{power}}.",
    "simple_dashboard.badge_grid_import": "⚡ Pobór z sieci aktywny",
    "simple_dashboard.headline_grid_import": "Obecnie prąd jest pobierany z sieci publicznej.",
    "simple_dashboard.subline_grid_import": "Pobór z sieci: {{power}} · Aktywne zoptymalizowane zarządzanie.",
    "simple_dashboard.badge_grid_export": "📤 Oddawanie do sieci",
    "simple_dashboard.headline_grid_export": "Nadwyżka słoneczna jest oddawana do sieci elektroenergetycznej.",
    "simple_dashboard.subline_grid_export": "Oddawanie: {{power}} po gwarantowanej stawce.",
    "simple_dashboard.badge_balanced": "✨ Zrównoważona praca",
    "simple_dashboard.headline_balanced": "Zarządzanie energią działa w optymalnej równowadze.",
    "simple_dashboard.subline_balanced": "Produkcja, magazynowanie i zużycie są optymalnie zbilansowane.",
    "simple_dashboard.live_flow_title": "Przepływ energii na żywo",
    "simple_dashboard.live_flow_desc": "Pomiary w czasie rzeczywistym wszystkich głównych komponentów.",
    "simple_dashboard.open_expert_view": "Otwórz widok eksperta",
    "simple_dashboard.total_energy_period": "Całkowita energia w okresie ({{period}})",
    "simple_dashboard.top_consumers": "Najwięksi odbiorcy energii",
    "simple_dashboard.manage_devices": "Zarządzaj urządzeniami →",
    "energy.period_today": "Dzisiaj",
    "energy.period_7d": "Ostatnie 7 dni",
    "energy.period_30d": "Ostatnie 30 dni",
    "energy.period_year": "Bieżący rok",
    "energy.custom_period_tooltip": "Ustaw własny zakres dat",
    "energy.custom_period": "Zakres...",
    "energy.generation": "Generacja",
    "energy.household": "Gospodarstwo",
    "energy.demand": "Zapotrzebowanie",
    "energy.battery_storage": "Magazyn",
    "energy.battery_charging": "⚡ Ładowanie",
    "energy.battery_discharging": "🏠 Rozładowanie",
    "energy.feedin": "Oddawanie",
    "energy.grid_import": "Pobór z sieci",
    "energy.export_action": "📤 Oddawanie",
    "energy.import_action": "📥 Pobór",
    "energy.kwh_balance": "Bilans kWh",
    "energy.solar_generation_total": "Całkowita produkcja PV",
    "energy.house_consumption_total": "Całkowite zużycie domowe",
    "energy.grid_import_total": "Prąd pobrany z sieci",
    "energy.solar_export_total": "Prąd słoneczny oddany do sieci",
    "energy.demand_coverage": "Pokrycie zużycia:",
    "energy.solar_battery": "PV i bateria",
    "energy.grid": "Sieć",
    "energy.autarky_rate": "Stopień autarkii",
    "energy.co2_saved": "Zaoszczędzone CO₂",
    "energy.total_with_kwh": "Razem: {{val}} kWh",
    "energy.charge_with_kwh": "Naładowano: {{val}} kWh",
}

# Now populate de, en, pl with extracted keys
added_count = 0
for k, default_de in extracted.items():
    # If not in de, add it
    if k not in de_flat:
        set_nested(de_data, k, default_de)
        de_flat[k] = default_de
        added_count += 1
    
    # Check en
    if k not in en_flat:
        en_val = common_en_dict.get(k)
        if not en_val:
            # Check if default_de is already in common_en_dict values or translates simply
            en_val = common_en_dict.get(k, default_de)
        set_nested(en_data, k, en_val)
        en_flat[k] = en_val
        
    # Check pl
    if k not in pl_flat:
        pl_val = common_pl_dict.get(k, en_flat.get(k, default_de))
        set_nested(pl_data, k, pl_val)
        pl_flat[k] = pl_val

print(f"Added {added_count} new keys to de_data!")

# Check parity across all 3
all_keys = set(de_flat.keys()) | set(en_flat.keys()) | set(pl_flat.keys())
print(f"Total unified keys across all locales: {len(all_keys)}")

for k in all_keys:
    if k not in de_flat:
        set_nested(de_data, k, en_flat.get(k, k))
    if k not in en_flat:
        set_nested(en_data, k, common_en_dict.get(k, de_flat.get(k, k)))
    if k not in pl_flat:
        set_nested(pl_data, k, common_pl_dict.get(k, en_flat.get(k, k)))

# Save all 3 locale JSON files
with open(de_path, "w", encoding="utf-8") as f:
    json.dump(de_data, f, indent=2, ensure_ascii=False)

with open(en_path, "w", encoding="utf-8") as f:
    json.dump(en_data, f, indent=2, ensure_ascii=False)

with open(pl_path, "w", encoding="utf-8") as f:
    json.dump(pl_data, f, indent=2, ensure_ascii=False)

print("Successfully synced de.json, en.json, and pl.json!")
