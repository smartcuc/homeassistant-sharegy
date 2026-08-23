/*
# src/components/layout/Topbar.jsx
*/

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { apiFetch } from "../../api/client";
import { useUser } from "../../hooks/useUser";
import { useDeviceStatus } from "../../hooks/useDevices";
import UserMenu from "../UserMenu";
import SpotPriceModal from "../../features/market/components/SpotPriceModal";

export default function AppTopbar() {
    const { t } = useTranslation();
    const { user } = useUser();

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
            {/* LEFT */}
            <div className="flex items-center gap-4">
                {/* 🏠 Home Switcher */}
                {user?.homes?.length > 1 && (
                    <select
                        className="
                            border
                            rounded-lg
                            px-3
                            py-1
                            text-sm
                            bg-white
                            hover:border-indigo-400
                        "
                    >
                        {user.homes.map((h) => (
                            <option key={h.id} value={h.id}>
                                {h.name}
                            </option>
                        ))}
                    </select>
                )}

                {/* 📍 Kontext */}
                <div className="text-sm text-gray-400">
                    Dashboard
                </div>
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

                <UserMenu user={user} />
                <SpotPriceModal
                    open={spotModalOpen}
                    onClose={() => setSpotModalOpen(false)}
                />
            </div>
        </div>
    );
}