/*
# src/features/producer/components/StorageSystemCard.jsx
*/

import { useTranslation } from "react-i18next";

export default function StorageSystemCard({ storage, onEdit, onDelete, onControl }) {
    const { t } = useTranslation();

    const soc = storage.live_soc_pct;
    const power = storage.live_power_w;
    const capacity = storage.capacity_kwh || 10.0;
    const storedKwh = storage.current_stored_kwh ?? (soc !== null ? ((soc / 100) * capacity).toFixed(1) : "-");

    // Status Styling (Laden: negativ / Entladen: positiv)
    const status = storage.status || "idle";
    const statusConfig = {
        charging: {
            label: t("storage.status_charging", "Lädt"),
            badge: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
            powerText: `-${(Math.abs(power || 0) / 1000).toFixed(2)} kW`,
            powerColor: "text-emerald-400",
            icon: "⚡",
        },
        discharging: {
            label: t("storage.status_discharging", "Entlädt"),
            badge: "bg-amber-500/20 text-amber-300 border-amber-500/30",
            powerText: `+${(Math.abs(power || 0) / 1000).toFixed(2)} kW`,
            powerColor: "text-amber-400",
            icon: "🔋",
        },
        full: {
            label: t("storage.status_full", "Voll (Standby)"),
            badge: "bg-blue-500/20 text-blue-300 border-blue-500/30",
            powerText: "0.00 kW",
            powerColor: "text-slate-400",
            icon: "🏆",
        },
        empty_reserve: {
            label: t("storage.status_empty_reserve", "Notstromreserve"),
            badge: "bg-rose-500/20 text-rose-300 border-rose-500/30",
            powerText: "0.00 kW",
            powerColor: "text-rose-400",
            icon: "🛡️",
        },
        idle: {
            label: t("storage.status_idle", "Standby"),
            badge: "bg-slate-700/40 text-slate-300 border-slate-600/40",
            powerText: "0.00 kW",
            powerColor: "text-slate-400",
            icon: "💤",
        },
    }[status] || {
        label: t("common.ready", "Bereit"),
        badge: "bg-slate-700/40 text-slate-300 border-slate-600/40",
        powerText: "-",
        powerColor: "text-slate-400",
        icon: "🔋",
    };

    // SoC Bar Color
    const socColor = soc === null
        ? "bg-slate-600"
        : soc <= storage.min_soc_reserve_pct
            ? "bg-rose-500"
            : soc <= 40
                ? "bg-amber-400"
                : "bg-emerald-500";

    return (
        <div className="bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900 border border-slate-800 rounded-3xl p-6 text-white shadow-xl flex flex-col justify-between space-y-6">
            {/* Header */}
            <div className="flex items-start justify-between gap-4 border-b border-slate-800 pb-4">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-2xl shadow-inner">
                        🔋
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h3 className="text-base font-bold text-white tracking-tight">
                                {storage.name}
                            </h3>
                            <span className={`text-[10px] uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full border ${statusConfig.badge}`}>
                                {statusConfig.icon} {statusConfig.label}
                            </span>
                        </div>
                        <p className="text-xs text-slate-400 font-mono mt-0.5">
                            {t("storage_system.specs", { cap: capacity, power: storage.max_charge_power_kw, defaultValue: `${capacity} kWh Nennkapazität · max. ${storage.max_charge_power_kw} kW` })}
                        </p>
                    </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-1.5">
                    <button
                        onClick={() => onEdit(storage)}
                        className="px-2.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition cursor-pointer border border-slate-700"
                        title={t("storage_system.edit_title", "Speicher & Messpunkte bearbeiten")}
                    >
                        ✏️ {t("common.edit", "Bearbeiten")}
                    </button>
                    <button
                        onClick={() => onDelete(storage.id, storage.name)}
                        className="p-1.5 rounded-xl bg-rose-950/40 hover:bg-rose-900/60 text-rose-400 text-xs transition cursor-pointer border border-rose-900/50"
                        title={t("common.delete", "Löschen")}
                    >
                        🗑️
                    </button>
                </div>
            </div>

            {/* KPI Highlights: Live SoC & Live Power */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* 1. Ladestand SoC */}
                <div className="p-4 rounded-2xl bg-slate-800/60 border border-slate-700/60 space-y-2.5">
                    <div className="flex items-center justify-between text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                        <span className="flex items-center gap-1.5">
                            <span className="text-sm">🔋</span>
                            <span>{t("storage_system.live_soc", "Live-Ladestand")}</span>
                        </span>
                        <span className="font-mono text-emerald-400 font-bold">{storedKwh} / {capacity} kWh</span>
                    </div>

                    <div className="flex items-baseline gap-2">
                        <span className="text-3xl font-black text-white font-mono tracking-tight">
                            {soc !== null ? soc : "-"}
                        </span>
                        <span className="text-sm font-semibold text-slate-400">%</span>
                        {status === "charging" && (
                            <span className="text-[10px] font-bold text-emerald-400 bg-emerald-950/60 border border-emerald-800/60 px-2 py-0.5 rounded-full animate-pulse">
                                + Lädt
                            </span>
                        )}
                        {status === "discharging" && (
                            <span className="text-[10px] font-bold text-amber-400 bg-amber-950/60 border border-amber-800/60 px-2 py-0.5 rounded-full animate-pulse">
                                - Entlädt
                            </span>
                        )}
                    </div>

                    {/* Enhanced Progress Bar with Reserve Marker */}
                    <div className="space-y-1">
                        <div className="relative w-full h-3 bg-slate-950/80 rounded-full overflow-hidden p-0.5 border border-slate-700/80">
                            {/* Min Reserve Marker Line */}
                            {storage.min_soc_reserve_pct > 0 && (
                                <div 
                                    className="absolute top-0 bottom-0 w-0.5 bg-rose-500/80 z-10" 
                                    style={{ left: `${Math.min(98, Math.max(2, storage.min_soc_reserve_pct))}%` }}
                                    title={`Notstromreserve: ${storage.min_soc_reserve_pct}%`}
                                />
                            )}
                            <div
                                className={`h-full rounded-full transition-all duration-700 shadow-sm ${
                                    soc === null
                                        ? "bg-slate-600"
                                        : soc <= storage.min_soc_reserve_pct
                                            ? "bg-gradient-to-r from-rose-600 to-rose-500 shadow-rose-500/30"
                                            : soc <= 40
                                                ? "bg-gradient-to-r from-amber-500 to-amber-400 shadow-amber-400/30"
                                                : "bg-gradient-to-r from-emerald-600 to-emerald-400 shadow-emerald-400/30"
                                }`}
                                style={{ width: `${Math.min(100, Math.max(soc || 0, 3))}%` }}
                            />
                        </div>
                        <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono">
                            <span>0%</span>
                            {storage.min_soc_reserve_pct > 0 && (
                                <span className="text-rose-400/90 font-medium">{t("storage.reserve", "Reserve")}: {storage.min_soc_reserve_pct}%</span>
                            )}
                            <span>100%</span>
                        </div>
                    </div>
                </div>

                {/* 2. Aktuelle Leistung */}
                <div className="p-4 rounded-2xl bg-slate-800/60 border border-slate-700/60 space-y-2.5 flex flex-col justify-between">
                    <div>
                        <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                            <span className="text-sm">⚡</span>
                            <span>{t("storage_system.charge_flow", "Lade- / Entladefluss")}</span>
                        </div>

                        <div className="flex items-baseline gap-2 mt-2">
                            <span className={`text-3xl font-black font-mono tracking-tight ${statusConfig.powerColor}`}>
                                {statusConfig.powerText}
                            </span>
                        </div>
                    </div>

                    <div className="pt-2 border-t border-slate-700/50 flex items-center justify-between text-[11px] text-slate-400">
                        <span>{t("storage.efficiency", "Wirkungsgrad")}: <strong className="text-slate-200">{storage.charge_efficiency_pct}%</strong></span>
                        <span>Max: <strong className="text-slate-200">{storage.max_charge_power_kw} kW</strong></span>
                    </div>
                </div>
            </div>

            {/* ⚡ EMS Steuerung Status & Shortcut */}
            <div className="p-3.5 rounded-2xl bg-gradient-to-r from-blue-950/40 via-indigo-950/30 to-slate-900 border border-blue-800/40 flex flex-wrap items-center justify-between gap-2 text-xs">
                <div className="flex items-center gap-2">
                    <span className="text-sm">🎛️</span>
                    <span className="text-slate-300">
                        {t("storage.control_mode_label", "Steuerungsmodus")}: <strong className="text-white capitalize">{
                            storage.control_mode === "price_optimized" ? t("storage.mode_price_optimized", "💶 Preisgeführt (Börsenpreis)") :
                            storage.control_mode === "forced_charge" ? t("storage.mode_forced_charge", "⚡ Sofortladen") :
                            storage.control_mode === "forced_discharge" ? t("storage.mode_forced_discharge", "🔋 Zwangsentladung") :
                            storage.control_mode === "idle" ? t("storage.mode_idle", "💤 Standby") :
                            t("storage.mode_pv_autarky", "☀️ PV-Autarkie")
                        }</strong>
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                        storage.ems_control_enabled 
                            ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30" 
                            : "bg-slate-700/50 text-slate-400 border-slate-600/50"
                    }`}>
                        {storage.ems_control_enabled ? t("common.active", "Aktiv") : t("common.standby", "Standby")}
                    </span>
                </div>

                <a
                    href="/app/control"
                    className="px-2.5 py-1 rounded-lg bg-blue-600/30 hover:bg-blue-600/50 border border-blue-500/40 text-blue-200 text-[11px] font-semibold transition flex items-center gap-1 cursor-pointer"
                >
                    <span>⚡ {t("storage.open_control_btn", "Energiesteuerung öffnen")}</span>
                    <span>→</span>
                </a>
            </div>

            {/* Mapped Signal Sources (Bündelung von Messpunkten) */}
            <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-2.5">
                <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center justify-between">
                    <span>📡 {t("storage_system.linked_sensors", "Verknüpfte Messpunkte & Sensoren")}</span>
                    {storage.primary_device && (
                        <span className="text-[10px] text-indigo-300 bg-indigo-950/80 px-2 py-0.5 rounded-md border border-indigo-800/60">
                            {t("storage_system.central_device", "Zentrales Gerät")}
                        </span>
                    )}
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                    {/* SoC Source */}
                    <div className="flex items-center gap-2 p-2 rounded-xl bg-slate-900/90 border border-slate-800">
                        <span className="text-emerald-400">🔋</span>
                        <div className="truncate">
                            <div className="text-[10px] text-slate-400">{t("storage_system.soc_sensor", "Batterie - SoC")}</div>
                            <div className="font-semibold text-slate-200 truncate">
                                {storage.soc_device?.name || storage.primary_device?.name || t("common.unassigned", "Nicht zugeordnet")}
                            </div>
                        </div>
                    </div>

                    {/* Power Source */}
                    <div className="flex items-center gap-2 p-2 rounded-xl bg-slate-900/90 border border-slate-800">
                        <span className="text-amber-400">⚡</span>
                        <div className="truncate">
                            <div className="text-[10px] text-slate-400">{t("storage_system.power_meter", "Batterie - Leistung")}</div>
                            <div className="font-semibold text-slate-200 truncate">
                                {storage.power_device?.name || storage.primary_device?.name || t("common.unassigned", "Nicht zugeordnet")}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

