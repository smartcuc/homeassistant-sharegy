import { useQuery } from "@tanstack/react-query";
import { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { apiFetch } from "../../api/client";
import { useUser } from "../../hooks/useUser";
import { useHomes } from "../../hooks/useHomes";
import { useDeviceStatus } from "../../hooks/useDevices";
import { useTheme } from "../../theme/ThemeContext";
import UserMenu from "../UserMenu";
import SpotPriceModal from "../../features/market/components/SpotPriceModal";
import SupportDrawer from "../../features/support/components/SupportDrawer";
import AlertCenterModal from "../../features/alerts/components/AlertCenterModal";
import { LifeBuoy, Bell, Sun, Moon, Check, ChevronDown, Building2, Home, Menu } from "lucide-react";

export default function AppTopbar({ onOpenMobileMenu }) {
    const { t, i18n } = useTranslation();
    const { user } = useUser();
    const navigate = useNavigate();
    const { homes = [], primaryHome } = useHomes();
    const { isDark, toggleTheme } = useTheme();

    const [spotModalOpen, setSpotModalOpen] = useState(false);
    const [supportOpen, setSupportOpen] = useState(false);
    const [alertsModalOpen, setAlertsModalOpen] = useState(false);
    const [homeDropdownOpen, setHomeDropdownOpen] = useState(false);
    const homeDropdownRef = useRef(null);

    // Sprach-Dropdown State (DE, EN, PL, TR, RU, RO)
    const [langDropdownOpen, setLangDropdownOpen] = useState(false);
    const langDropdownRef = useRef(null);

    const languages = [
        { code: "de", label: "Deutsch", flag: "🇩🇪" },
        { code: "en", label: "English", flag: "🇬🇧" },
        { code: "pl", label: "Polski", flag: "🇵🇱" },
        { code: "tr", label: "Türkçe", flag: "🇹🇷" },
        { code: "ru", label: "Русский", flag: "🇷🇺" },
        { code: "ro", label: "Română", flag: "🇷🇴" },
    ];

    const currentLang = (i18n.resolvedLanguage || i18n.language || "de").substring(0, 2);
    const currentLangObj = languages.find((l) => l.code === currentLang) || languages[0];

    const handleLanguageChange = async (langCode) => {
        setLangDropdownOpen(false);
        await i18n.changeLanguage(langCode);
        localStorage.setItem("i18nextLng", langCode);
        try {
            await apiFetch("/api/language/", {
                method: "POST",
                body: JSON.stringify({ language: langCode }),
            });
        } catch {
            // Ignore API fallback
        }
    };

    // Aktive Liegenschaft (Default ist primaryHome)
    const [selectedHomeId, setSelectedHomeId] = useState(() => {
        return localStorage.getItem("sharegy_active_home_id") || primaryHome?.id;
    });

    const activeHome = homes.find((h) => String(h.id) === String(selectedHomeId)) || primaryHome || homes[0];

    // Outside-Click Listener für Dropdowns
    useEffect(() => {
        function handleClickOutside(e) {
            if (homeDropdownRef.current && !homeDropdownRef.current.contains(e.target)) {
                setHomeDropdownOpen(false);
            }
            if (langDropdownRef.current && !langDropdownRef.current.contains(e.target)) {
                setLangDropdownOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const handleSelectHome = (homeId) => {
        setSelectedHomeId(homeId);
        localStorage.setItem("sharegy_active_home_id", String(homeId));
        setHomeDropdownOpen(false);
    };

    // 📶 Live Geräte-Status aus dem Backend
    const { data: devices = [], isLoading: isDeviceLoading } = useDeviceStatus();
    const total = Array.isArray(devices) ? devices.length : 0;
    const online = Array.isArray(devices)
        ? devices.filter((d) => d.status === "online" || d.status === "stale").length
        : 0;

    // 💰 Live Spotpreis
    const spotPriceQuery = useQuery({
        queryKey: ["spot-price"],
        queryFn: () => apiFetch("/api/market/current/"),
        refetchInterval: 60000,
    });
    const spotPrice = spotPriceQuery.data;
    const spotColor =
        spotPrice?.status === "good"
            ? "text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800/60"
            : spotPrice?.status === "warning"
                ? "text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800/60"
                : "text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800/60";

    // ⚡ Live Energy Pulse (Echtzeit-Ticker für Solar, Haus, Netz & Speicher)
    const energyQuery = useQuery({
        queryKey: ["energy-dashboard"],
        queryFn: () => apiFetch("/api/energy/dashboard/me/"),
        refetchInterval: 3000,
        refetchIntervalInBackground: true,
    });
    const liveData = energyQuery.data || {};
    const kpis = liveData.kpis || {};
    const gridPower = liveData.grid_power_w !== undefined ? Number(liveData.grid_power_w) : (kpis.grid_power_w !== undefined ? Number(kpis.grid_power_w) : null);
    const pvPower = liveData.pv_power_w !== undefined ? Number(liveData.pv_power_w) : (kpis.pv_power_w !== undefined ? Number(kpis.pv_power_w) : null);
    const loadPower = liveData.load_power_w !== undefined ? Number(liveData.load_power_w) : (kpis.load_power_w !== undefined ? Number(kpis.load_power_w) : null);
    const batteryPower = liveData.battery_power_w !== undefined ? Number(liveData.battery_power_w) : (kpis.battery_power_w !== undefined ? Number(kpis.battery_power_w) : null);
    const batterySoc = liveData.battery_soc_pct !== undefined && liveData.battery_soc_pct !== null
        ? Math.round(Number(liveData.battery_soc_pct))
        : (kpis.battery_soc_pct !== undefined ? Math.round(Number(kpis.battery_soc_pct)) : null);

    // 🔔 Live Alerts & Benachrichtigungen
    const alertsQuery = useQuery({
        queryKey: ["alerts-list"],
        queryFn: () => apiFetch("/api/alerts/"),
        refetchInterval: 15000,
        refetchIntervalInBackground: true,
    });
    const alertsData = alertsQuery.data || {};
    const activeAlertsCount = alertsData.summary?.active_total ?? (Array.isArray(alertsData.alerts) ? alertsData.alerts.length : 0);
    const hasCriticalAlert = (alertsData.summary?.critical || 0) > 0;

    const formatPower = (val) => {
        if (val === null || val === undefined) return "--";
        const absVal = Math.abs(val);
        if (absVal >= 1000) {
            return `${(val / 1000).toFixed(1)} kW`;
        }
        return `${Math.round(val)} W`;
    };

    const hasAnyLiveMetric = gridPower !== null || pvPower !== null || loadPower !== null || batterySoc !== null;

    return (
        <>
            <header className="h-14 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b border-slate-200/80 dark:border-slate-800 sticky top-0 z-30 flex items-center justify-between px-3 sm:px-4 transition-colors">
                {/* LEFT: 🏡 Gebäude- / Liegenschafts-Kontext & Mobile Drawer Button */}
                <div className="flex items-center gap-1.5 sm:gap-3 min-w-0 shrink-0">
                    {onOpenMobileMenu && (
                        <button
                            type="button"
                            onClick={onOpenMobileMenu}
                            aria-label="Menü öffnen"
                            className="md:hidden p-1.5 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition shrink-0 cursor-pointer"
                        >
                            <Menu className="w-5 h-5" />
                        </button>
                    )}
                    {homes.length > 1 ? (
                        /* 🏢 Mehrere Liegenschaften -> Moderner Switcher */
                        <div className="relative" ref={homeDropdownRef}>
                            <button
                                type="button"
                                onClick={() => setHomeDropdownOpen(!homeDropdownOpen)}
                                className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 dark:text-slate-200 bg-slate-100/90 dark:bg-slate-800/90 hover:bg-slate-200/80 dark:hover:bg-slate-700/80 border border-slate-200/90 dark:border-slate-700 px-2.5 sm:px-3 py-1 rounded-xl shadow-2xs transition cursor-pointer group max-w-[140px] sm:max-w-[200px]"
                                title={t("homes.switcher_title", "Liegenschaft wechseln")}
                            >
                                <span className="text-sm shrink-0">🏡</span>
                                <span className="truncate">{activeHome?.name || t("common.my_home", "Mein Zuhause")}</span>
                                <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform duration-200 shrink-0 ${homeDropdownOpen ? "rotate-180" : ""}`} />
                            </button>

                            {homeDropdownOpen && (
                                <div className="absolute left-0 mt-2 w-64 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-xl py-2 z-50 animate-in fade-in zoom-in-95 duration-150">
                                    <div className="px-3.5 py-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 border-b border-slate-100 dark:border-slate-800 mb-1 flex items-center justify-between">
                                        <span>{t("homes.select_property", "Liegenschaft wählen")}</span>
                                        <span className="font-mono text-slate-500 dark:text-slate-400">({homes.length})</span>
                                    </div>
                                    <div className="max-h-60 overflow-y-auto space-y-0.5 px-1.5">
                                        {homes.map((h) => {
                                            const isSelected = String(h.id) === String(activeHome?.id);
                                            return (
                                                <button
                                                    key={h.id}
                                                    type="button"
                                                    onClick={() => handleSelectHome(h.id)}
                                                    className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs text-left transition cursor-pointer ${
                                                        isSelected
                                                            ? "bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 font-bold border border-indigo-100 dark:border-indigo-900/50"
                                                            : "text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                                                    }`}
                                                >
                                                    <div className="flex items-center gap-2 min-w-0 flex-1">
                                                        <span className="text-base shrink-0">🏡</span>
                                                        <div className="truncate">
                                                            <div className="truncate">{h.name || "Mein Zuhause"}</div>
                                                            {h.city && <div className="text-[10px] text-slate-400 font-normal truncate">{h.city}</div>}
                                                        </div>
                                                    </div>
                                                    {isSelected && <Check className="w-4 h-4 text-indigo-600 dark:text-indigo-400 shrink-0 ml-1.5" />}
                                                </button>
                                            );
                                        })}
                                    </div>
                                    <div className="pt-1 mt-1 border-t border-slate-100 dark:border-slate-800 px-2">
                                        <Link
                                            to="/app/structure"
                                            onClick={() => setHomeDropdownOpen(false)}
                                            className="flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] font-semibold text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 rounded-lg transition"
                                        >
                                            <span>⚙️</span>
                                            <span>{t("homes.manage_structures", "Liegenschaften verwalten")}</span>
                                        </Link>
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        /* 🏡 Nur 1 Liegenschaft -> Schickes Kontext-Badge mit Link zur Struktur */
                        <Link
                            to="/app/structure"
                            title={t("homes.single_badge_title", "Gebäude- & Raumstruktur verwalten")}
                            className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 dark:text-slate-200 bg-slate-100/90 dark:bg-slate-800/90 hover:bg-slate-200/80 dark:hover:bg-slate-700/80 border border-slate-200/90 dark:border-slate-700 px-2.5 sm:px-3 py-1 rounded-xl shadow-2xs truncate max-w-[140px] sm:max-w-[200px] transition group cursor-pointer"
                        >
                            <span className="text-sm shrink-0">🏡</span>
                            <span className="truncate group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                                {primaryHome?.name || t("common.my_home", "Mein Zuhause")}
                            </span>
                        </Link>
                    )}
                </div>

                {/* CENTER: ⚡ Live Energy-Pulse / Kompakt-Ticker (Echte Echtzeit-Leistung aller Komponenten) */}
                {hasAnyLiveMetric && (
                    <div className="flex items-center gap-1.5 sm:gap-2 min-w-0">
                        <Link
                            to="/app/energy"
                            title={t("dashboard.live_energy_ticker_title", "Live-Energiefluss & Dashboard öffnen")}
                            className="flex items-center gap-1.5 sm:gap-2.5 px-2 sm:px-3 py-1 bg-slate-50 dark:bg-slate-800/80 hover:bg-indigo-50/60 dark:hover:bg-slate-700/80 border border-slate-200/90 dark:border-slate-700 hover:border-indigo-200 dark:hover:border-indigo-500 rounded-xl transition cursor-pointer shadow-2xs group shrink-0"
                        >
                            {/* Pulsierender LIVE Dot */}
                            <div className="flex items-center gap-1">
                                <span className="relative flex h-2 w-2 shrink-0">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                                </span>
                                <span className="text-[10px] font-black uppercase tracking-wider text-slate-500 dark:text-slate-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 hidden xs:inline">
                                    LIVE
                                </span>
                            </div>

                            {/* ☀️ Solar Erzeugung */}
                            {pvPower !== null && pvPower > 10 && (
                                <>
                                    <div className="h-3 w-px bg-slate-200 dark:bg-slate-700" />
                                    <div className="flex items-center gap-1 text-xs font-mono font-bold text-amber-600 dark:text-amber-400">
                                        <span>☀️</span>
                                        <span>{formatPower(pvPower)}</span>
                                    </div>
                                </>
                            )}

                            {/* 🏠 Hausverbrauch */}
                            {loadPower !== null && loadPower > 10 && (
                                <>
                                    <div className="h-3 w-px bg-slate-200 dark:bg-slate-700 hidden sm:block" />
                                    <div className="hidden sm:flex items-center gap-1 text-xs font-mono font-bold text-rose-600 dark:text-rose-400">
                                        <span>🏠</span>
                                        <span>{formatPower(loadPower)}</span>
                                    </div>
                                </>
                            )}

                            {/* ⚡ Netz Einspeisung / Bezug */}
                            {gridPower !== null && (
                                <>
                                    <div className="h-3 w-px bg-slate-200 dark:bg-slate-700" />
                                    <div className="flex items-center gap-1 text-xs font-mono font-bold">
                                        {gridPower < -20 ? (
                                            <span className="text-emerald-600 dark:text-emerald-400 flex items-center gap-0.5">
                                                <span>⚡</span>
                                                <span>+{formatPower(Math.abs(gridPower))} 📤</span>
                                            </span>
                                        ) : gridPower > 20 ? (
                                            <span className="text-amber-600 dark:text-amber-400 flex items-center gap-0.5">
                                                <span>⚡</span>
                                                <span>{formatPower(gridPower)} 📥</span>
                                            </span>
                                        ) : (
                                            <span className="text-slate-600 dark:text-slate-400">⚡ 0 W</span>
                                        )}
                                    </div>
                                </>
                            )}

                            {/* 🔋 Batteriespeicher SoC */}
                            {batterySoc !== null && (
                                <>
                                    <div className="h-3 w-px bg-slate-200 dark:bg-slate-700 hidden md:block" />
                                    <div className="hidden md:flex items-center gap-1 text-xs font-semibold text-emerald-700 dark:text-emerald-300 bg-emerald-50/80 dark:bg-emerald-950/60 px-1.5 py-0.5 rounded-md border border-emerald-100 dark:border-emerald-900/50">
                                        <span>🔋</span>
                                        <span>{batterySoc}%</span>
                                    </div>
                                </>
                            )}
                        </Link>
                    </div>
                )}

                {/* RIGHT: Actions & User Menu */}
                <div className="flex items-center gap-1.5 sm:gap-2.5">

                {/* 💰 Börsenstrompreis Spot-Preis */}
                {spotPrice && (
                    <button
                        type="button"
                        onClick={() => setSpotModalOpen(true)}
                        title="Aktueller Börsenstrompreis (EPEX Spot)"
                        className={`
                            flex
                            items-center
                            gap-1
                            text-xs
                            font-bold
                            font-mono
                            px-2 sm:px-2.5
                            py-1
                            rounded-xl
                            border
                            ${spotColor}
                            hover:opacity-85
                            transition-all
                            cursor-pointer
                            shadow-2xs
                        `}
                    >
                        <span>💰</span>
                        <span className="hidden sm:inline">
                            {spotPrice.price_ct.toFixed(1)} ct/kWh
                        </span>
                        <span className="inline sm:hidden">
                            {spotPrice.price_ct.toFixed(1)}ct
                        </span>
                    </button>
                )}

                {/* 🔔 Benachrichtigungs-Zentrale (Notification Bell) */}
                <button
                    type="button"
                    onClick={() => setAlertsModalOpen(true)}
                    title={t("alerts.open_notifications_title", "Alarm- & Notifikationszentrale öffnen")}
                    className="relative p-2 text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition cursor-pointer border border-transparent hover:border-slate-200 dark:hover:border-slate-700"
                >
                    <Bell className="w-4 h-4" />
                    {activeAlertsCount > 0 && (
                        <span className={`absolute -top-0.5 -right-0.5 flex h-4 min-w-4 px-1 items-center justify-center rounded-full text-[9px] font-black text-white shadow-xs ${
                            hasCriticalAlert ? "bg-rose-500 animate-bounce" : "bg-amber-500"
                        }`}>
                            {activeAlertsCount > 9 ? "9+" : activeAlertsCount}
                        </span>
                    )}
                </button>

                {/* 🌙 / ☀️ Dark/Light-Mode Toggle */}
                <button
                    type="button"
                    onClick={toggleTheme}
                    title={isDark ? t("theme.light_mode", "Zu hellem Design wechseln") : t("theme.dark_mode", "Zu dunklem Design wechseln")}
                    className="p-2 text-slate-600 dark:text-slate-300 hover:text-amber-500 dark:hover:text-amber-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition cursor-pointer border border-transparent hover:border-slate-200 dark:hover:border-slate-700"
                >
                    {isDark ? (
                        <Sun className="w-4 h-4 text-amber-400 hover:rotate-45 transition-transform" />
                    ) : (
                        <Moon className="w-4 h-4 text-slate-600 dark:text-slate-300 hover:-rotate-12 transition-transform" />
                    )}
                </button>

                {/* 🌐 Sprach-Wähler (DE, EN, PL, TR, RU, RO) */}
                <div className="relative" ref={langDropdownRef}>
                    <button
                        type="button"
                        onClick={() => setLangDropdownOpen(!langDropdownOpen)}
                        title={t("settings.language", "Sprache wählen")}
                        className="flex items-center gap-1 px-2 py-1.5 text-xs font-bold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition cursor-pointer border border-transparent hover:border-slate-200 dark:hover:border-slate-700"
                        aria-expanded={langDropdownOpen}
                    >
                        <span className="text-base leading-none">{currentLangObj.flag}</span>
                        <span className="hidden sm:inline font-mono uppercase text-[11px]">{currentLangObj.code}</span>
                        <ChevronDown className={`w-3 h-3 text-slate-400 transition-transform duration-200 ${langDropdownOpen ? "rotate-180" : ""}`} />
                    </button>

                    {langDropdownOpen && (
                        <div className="absolute right-0 mt-2 w-44 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-2xl shadow-xl py-1.5 z-50 animate-in fade-in zoom-in-95 duration-150">
                            <div className="px-3 py-1.5 text-[10px] uppercase font-bold text-gray-400 tracking-wider border-b border-gray-100 dark:border-slate-800">
                                {t("settings.language", "Sprache wählen")}
                            </div>
                            <div className="py-1">
                                {languages.map((lang) => {
                                    const isActive = currentLang === lang.code;
                                    return (
                                        <button
                                            key={lang.code}
                                            type="button"
                                            onClick={() => handleLanguageChange(lang.code)}
                                            className={`w-full px-3 py-1.5 text-xs text-left flex items-center justify-between transition cursor-pointer ${
                                                isActive
                                                    ? "bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 font-bold"
                                                    : "text-gray-700 dark:text-gray-300 hover:bg-slate-50 dark:hover:bg-slate-800/60"
                                            }`}
                                        >
                                            <span className="flex items-center gap-2">
                                                <span className="text-base">{lang.flag}</span>
                                                <span>{lang.label}</span>
                                            </span>
                                            {isActive && <Check className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />}
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    )}
                </div>

                {/* 🛟 Hilfe & Support Trigger */}
                <button
                    type="button"
                    onClick={() => setSupportOpen(true)}
                    title={t("support.open_drawer_title", "Hilfe, Wissensportal & Support-Tickets")}
                    className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-semibold text-slate-700 dark:text-slate-200 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 rounded-xl transition cursor-pointer shadow-2xs"
                >
                    <LifeBuoy className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400 shrink-0" />
                    <span className="hidden lg:inline">{t("support.btn_unified_label", "Hilfe & Support")}</span>
                </button>

                <UserMenu user={user} />
            </div>
        </header>

        {/* MODALS */}
        {spotModalOpen && (
            <SpotPriceModal
                open={spotModalOpen}
                onClose={() => setSpotModalOpen(false)}
            />
        )}
        {supportOpen && (
            <SupportDrawer
                isOpen={supportOpen}
                onClose={() => setSupportOpen(false)}
            />
        )}
        {alertsModalOpen && (
            <AlertCenterModal
                isOpen={alertsModalOpen}
                onClose={() => setAlertsModalOpen(false)}
            />
        )}
    </>
    );
}