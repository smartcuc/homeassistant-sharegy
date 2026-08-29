import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { apiFetch } from "../../api/client";
import { useUser } from "../../hooks/useUser";
import { useHomes } from "../../hooks/useHomes";
import { useDeviceStatus } from "../../hooks/useDevices";
import UserMenu from "../UserMenu";
import SpotPriceModal from "../../features/market/components/SpotPriceModal";
import SupportDrawer from "../../features/support/components/SupportDrawer";
import { LifeBuoy } from "lucide-react";

export default function AppTopbar() {
    const { t } = useTranslation();
    const { user } = useUser();
    const { homes = [], primaryHome } = useHomes();


    // 📶 Live Geräte-Status aus dem Backend
    const { data: devices = [], isLoading: isDeviceLoading } = useDeviceStatus();
    const total = Array.isArray(devices) ? devices.length : 0;
    const online = Array.isArray(devices)
        ? devices.filter((d) => d.status === "online" || d.status === "stale").length
        : 0;

    const spotPriceQuery = useQuery({
        queryKey: ["spot-price"],
        queryFn: () => apiFetch("/api/market/current/"),
        refetchInterval: 60000,
    });

    const spotPrice = spotPriceQuery.data;

    const spotColor =
        spotPrice?.status === "good"
            ? "text-green-600"
            : spotPrice?.status === "warning"
                ? "text-amber-600"
                : "text-red-600";

    const [spotModalOpen, setSpotModalOpen] = useState(false);
    const [supportOpen, setSupportOpen] = useState(false);

    // Status-Punkt Farbe
    const statusDotClass = isDeviceLoading
        ? "bg-slate-400 animate-pulse"
        : total === 0
            ? "bg-slate-300"
            : online === total
                ? "bg-emerald-500 shadow-xs shadow-emerald-500/50"
                : online > 0
                    ? "bg-amber-500 shadow-xs shadow-amber-500/50"
                    : "bg-rose-500 shadow-xs shadow-rose-500/50";

    return (
        <div className="h-14 bg-white border-b flex items-center justify-between px-4">
            {/* LEFT: 🏡 Gebäude- / Liegenschafts-Kontext */}
            <div className="flex items-center gap-3">
                {homes.length > 1 ? (
                    <div className="flex items-center gap-1.5">
                        <span className="text-sm">🏡</span>
                        <select
                            className="
                                border border-slate-200
                                rounded-xl
                                px-2.5
                                py-1
                                text-xs
                                font-semibold
                                text-slate-700
                                bg-slate-50
                                hover:border-indigo-400
                                focus:outline-none focus:ring-2 focus:ring-indigo-500/20
                                transition
                                cursor-pointer
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
                    <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 bg-slate-100/80 border border-slate-200/90 px-3 py-1.5 rounded-xl shadow-2xs">
                        <span className="text-sm">🏡</span>
                        <span>{primaryHome?.name || t("common.my_home", "Mein Zuhause")}</span>
                    </div>
                )}
            </div>

            {/* RIGHT */}
            <div className="flex items-center gap-4">
                {/* 📶 Live Geräte Status */}
                <Link
                    to="/app/devices"
                    title={t("devices.title", "Geräteübersicht öffnen")}
                    className="
                        flex
                        items-center
                        gap-2
                        text-sm
                        text-gray-600
                        hover:text-indigo-600
                        px-2.5
                        py-1
                        rounded-lg
                        hover:bg-gray-50
                        transition
                    "
                >
                    <span className={`w-2 h-2 rounded-full ${statusDotClass}`}></span>

                    <span className="font-medium text-xs sm:text-sm">
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
                </Link>

                {/* 👤 Spot-Preis & User */}
                {spotPrice && (
                    <button
                        onClick={() => setSpotModalOpen(true)}
                        title="Aktueller Börsenstrompreis (EPEX Spot)"
                        className={`
                            flex
                            items-center
                            gap-1
                            text-sm
                            font-semibold
                            ${spotColor}
                            hover:opacity-80
                            transition-opacity
                            cursor-pointer
                        `}
                    >
                        <span>💰</span>
                        <span>
                            {spotPrice.price_ct.toFixed(2)} ct/kWh
                        </span>
                    </button>
                )}

                {/* 🛟 Einheitlicher Hilfe & Support Trigger */}
                <button
                    onClick={() => setSupportOpen(true)}
                    title={t("support.open_drawer_title", "Hilfe, Wissensportal & Support-Tickets")}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 dark:text-slate-200 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 rounded-lg transition cursor-pointer shadow-2xs"
                >
                    <LifeBuoy className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
                    <span className="hidden sm:inline">{t("support.btn_unified_label", "Hilfe & Support")}</span>
                </button>


                <UserMenu user={user} />
                {spotModalOpen && (
                    <SpotPriceModal
                        open={spotModalOpen}
                        onClose={() => setSpotModalOpen(false)}
                    />
                )}
                <SupportDrawer
                    isOpen={supportOpen}
                    onClose={() => setSupportOpen(false)}
                />
            </div>
        </div>
    );
}