import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { apiFetch } from "../../api/client";
import { useUser } from "../../hooks/useUser";
import { useHomes } from "../../hooks/useHomes";
import { useDeviceStatus } from "../../hooks/useDevices";
import UserMenu from "../UserMenu";
import SpotPriceModal from "../../features/market/components/SpotPriceModal";
import SupportDrawer from "../../features/support/components/SupportDrawer";
import AlertCenterModal from "../../features/alerts/components/AlertCenterModal";
import { LifeBuoy, Bell, Zap } from "lucide-react";

export default function AppTopbar() {
    const { t } = useTranslation();
    const { user } = useUser();
    const navigate = useNavigate();
    const { homes = [], primaryHome } = useHomes();

    const [spotModalOpen, setSpotModalOpen] = useState(false);
    const [supportOpen, setSupportOpen] = useState(false);
    const [alertsModalOpen, setAlertsModalOpen] = useState(false);

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
            ? "text-emerald-600 bg-emerald-50 border-emerald-200"
            : spotPrice?.status === "warning"
                ? "text-amber-600 bg-amber-50 border-amber-200"
                : "text-rose-600 bg-rose-50 border-rose-200";

    // ⚡ Live Energy Pulse (Echtzeit-Ticker für Netz & Autarkie)
    const energyQuery = useQuery({
        queryKey: ["energy-dashboard"],
        queryFn: () => apiFetch("/api/energy/dashboard/me/"),
        refetchInterval: 3000,
        refetchIntervalInBackground: true,
    });
    const kpis = energyQuery.data?.kpis || {};
    const gridPower = kpis.grid?.power !== undefined ? Number(kpis.grid.power) : null;
    const pvPower = kpis.solar?.power !== undefined ? Number(kpis.solar.power) : null;
    const autarky = kpis.autarky?.value !== undefined ? Math.round(Number(kpis.autarky.value)) : null;

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

    // Status-Punkt Farbe für Geräte
    const statusDotClass = isDeviceLoading
        ? "bg-slate-400 animate-pulse"
        : total === 0
            ? "bg-slate-300"
            : online === total
                ? "bg-emerald-500 shadow-xs shadow-emerald-500/50"
                : online > 0
                    ? "bg-amber-500 shadow-xs shadow-amber-500/50"
                    : "bg-rose-500 shadow-xs shadow-rose-500/50";

    const formatPower = (val) => {
        if (val === null || val === undefined) return "--";
        const absVal = Math.abs(val);
        if (absVal >= 1000) {
            return `${(val / 1000).toFixed(1)} kW`;
        }
        return `${Math.round(val)} W`;
    };

    return (
        <header className="h-14 bg-white/90 backdrop-blur-md border-b border-slate-200/80 sticky top-0 z-30 flex items-center justify-between px-3 sm:px-4 transition-all">
            {/* LEFT: 🏡 Gebäude- / Liegenschafts-Kontext */}
            <div className="flex items-center gap-2 sm:gap-3 min-w-0 shrink-0">
                {homes.length > 1 ? (
                    <div className="flex items-center gap-1.5">
                        <span className="text-sm shrink-0">🏡</span>
                        <select
                            className="
                                border border-slate-200
                                rounded-xl
                                px-2 sm:px-2.5
                                py-1
                                text-xs
                                font-semibold
                                text-slate-700
                                bg-slate-50
                                hover:border-indigo-400
                                focus:outline-none focus:ring-2 focus:ring-indigo-500/20
                                transition
                                cursor-pointer
                                max-w-[120px] sm:max-w-[180px] truncate
                            "
                            defaultValue={primaryHome?.id}
                        >
                            {homes.map((h) => (
                                <option key={h.id} value={h.id}>
                                    {h.name || "Mein Zuhause"}
                                </option>
                            ))}
                        </select>
                    </div>
                ) : (
                    <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 bg-slate-100/80 border border-slate-200/90 px-2.5 sm:px-3 py-1 rounded-xl shadow-2xs truncate max-w-[130px] sm:max-w-[200px]">
                        <span className="text-sm shrink-0">🏡</span>
                        <span className="truncate">{primaryHome?.name || t("common.my_home", "Mein Zuhause")}</span>
                    </div>
                )}
            </div>

            {/* CENTER: ⚡ Live Energy-Pulse / Kompakt-Ticker (Desktop & Tablet) */}
            <div className="hidden md:flex items-center gap-2">
                <Link
                    to="/app/energy"
                    title={t("dashboard.live_energy_ticker_title", "Live-Energiefluss & Autarkie öffnen")}
                    className="flex items-center gap-2.5 px-3 py-1 bg-slate-50 hover:bg-indigo-50/60 border border-slate-200/90 hover:border-indigo-200 rounded-xl transition cursor-pointer shadow-2xs group"
                >
                    {/* Pulsierender LIVE Dot */}
                    <div className="flex items-center gap-1.5">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                        </span>
                        <span className="text-[10px] font-black uppercase tracking-wider text-slate-500 group-hover:text-indigo-600">
                            LIVE
                        </span>
                    </div>

                    <div className="h-3 w-px bg-slate-200" />

                    {/* Netzzustand */}
                    <div className="flex items-center gap-1 text-xs font-mono font-bold">
                        <span className="text-slate-400 text-[11px]">Netz:</span>
                        <span className={gridPower !== null ? (gridPower < -5 ? "text-emerald-600" : gridPower > 5 ? "text-amber-600" : "text-slate-700") : "text-slate-500"}>
                            {gridPower !== null ? (gridPower < -5 ? `+${formatPower(Math.abs(gridPower))} 📤` : gridPower > 5 ? `${formatPower(gridPower)} 📥` : "0 W") : "--"}
                        </span>
                    </div>

                    {/* PV Ertrag falls vorhanden */}
                    {pvPower !== null && pvPower > 10 && (
                        <>
                            <div className="h-3 w-px bg-slate-200" />
                            <div className="flex items-center gap-1 text-xs font-mono font-bold text-amber-600">
                                <span>☀️</span>
                                <span>{formatPower(pvPower)}</span>
                            </div>
                        </>
                    )}

                    {/* Autarkiegrad */}
                    {autarky !== null && (
                        <>
                            <div className="h-3 w-px bg-slate-200" />
                            <div className="flex items-center gap-1 text-xs font-semibold text-indigo-700 bg-indigo-50/80 px-1.5 py-0.5 rounded-md">
                                <span>🛡️</span>
                                <span>{autarky}%</span>
                            </div>
                        </>
                    )}
                </Link>
            </div>

            {/* RIGHT: Actions & User Menu */}
            <div className="flex items-center gap-1.5 sm:gap-3">
                {/* 📶 Live Geräte Status */}
                <Link
                    to="/app/devices"
                    title={t("devices.title", "Geräteübersicht öffnen")}
                    className="
                        flex
                        items-center
                        gap-1.5
                        text-xs sm:text-sm
                        text-gray-600
                        hover:text-indigo-600
                        px-2 sm:px-2.5
                        py-1
                        rounded-xl
                        hover:bg-slate-50
                        border border-transparent hover:border-slate-200
                        transition
                    "
                >
                    <span className={`w-2 h-2 rounded-full shrink-0 ${statusDotClass}`}></span>
                    <span className="font-medium text-xs hidden lg:inline">
                        {isDeviceLoading
                            ? t("common.loading", "Lädt...")
                            : total === 0
                                ? t("devices.no_devices", "Keine Geräte")
                                : t("devices.online_summary", {
                                    online,
                                    total,
                                    defaultValue: `${online}/${total} Geräte online`,
                                })}
                    </span>
                    <span className="font-semibold text-xs inline lg:hidden font-mono">
                        {online}/{total}
                    </span>
                </Link>

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
                    className="relative p-2 text-slate-600 hover:text-indigo-600 hover:bg-slate-100 rounded-xl transition cursor-pointer border border-transparent hover:border-slate-200"
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

                {/* 🛟 Hilfe & Support Trigger */}
                <button
                    type="button"
                    onClick={() => setSupportOpen(true)}
                    title={t("support.open_drawer_title", "Hilfe, Wissensportal & Support-Tickets")}
                    className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-200 rounded-xl transition cursor-pointer shadow-2xs"
                >
                    <LifeBuoy className="w-3.5 h-3.5 text-indigo-600 shrink-0" />
                    <span className="hidden lg:inline">{t("support.btn_unified_label", "Hilfe & Support")}</span>
                </button>

                <UserMenu user={user} />

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
            </div>
        </header>
    );
}