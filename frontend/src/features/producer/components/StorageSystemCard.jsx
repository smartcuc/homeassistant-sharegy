/*
# src/features/producer/components/StorageSystemCard.jsx
*/

import { useTranslation } from "react-i18next";

export default function StorageSystemCard({ storage, onEdit, onDelete }) {
    const { t } = useTranslation();

    const soc = storage.live_soc_pct;
    const power = storage.live_power_w;
    const capacity = storage.capacity_kwh || 10.0;
    const storedKwh = storage.current_stored_kwh ?? (soc !== null ? ((soc / 100) * capacity).toFixed(1) : "-");

    // Status Styling
    const status = storage.status || "idle";
    const statusConfig = {
        charging: {
            label: t("storage.status_charging", "Lädt"),
            badge: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
            powerText: `+${((power || 0) / 1000).toFixed(2)} kW`,
            powerColor: "text-emerald-400",
            icon: "⚡",
        },
        discharging: {
            label: t("storage.status_discharging", "Entlädt"),
            badge: "bg-amber-500/20 text-amber-300 border-amber-500/30",
            powerText: `${((power || 0) / 1000).toFixed(2)} kW`,
            powerColor: "text-amber-400",
            icon: "🔋",
        },
        full: {
            label: t("storage.status_full", "Voll"),
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
        label: "Bereit",
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
                            {capacity} kWh Nennkapazität · max. {storage.max_charge_power_kw} kW
                        </p>
                    </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-1.5">
                    <button
                        onClick={() => onEdit(storage)}
                        className="px-2.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition cursor-pointer border border-slate-700"
                        title="Speicher & Messpunkte bearbeiten"
                    >
                        ✏️ Bearbeiten
                    </button>
                    <button
                        onClick={() => onDelete(storage.id, storage.name)}
                        className="p-1.5 rounded-xl bg-rose-950/40 hover:bg-rose-900/60 text-rose-400 text-xs transition cursor-pointer border border-rose-900/50"
                        title="Löschen"
                    >
                        🗑️
                    </button>
                </div>
            </div>

            {/* KPI Highlights: Live SoC & Live Power */}
            <div className="grid grid-cols-2 gap-4">
                {/* 1. Ladestand SoC */}
                <div className="p-4 rounded-2xl bg-slate-800/60 border border-slate-700/60 space-y-2">
                    <div className="flex items-center justify-between text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                        <span>⚡ Live-Ladestand</span>
                        <span className="font-mono text-emerald-400">{storedKwh} / {capacity} kWh</span>
                    </div>

                    <div className="flex items-baseline gap-2">
                        <span className="text-3xl font-black text-white font-mono">
                            {soc !== null ? soc : "-"}
                        </span>
                        <span className="text-sm font-semibold text-slate-400">%</span>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full h-2.5 bg-slate-700/60 rounded-full overflow-hidden p-0.5 border border-slate-600/40">
                        <div
                            className={`h-full rounded-full transition-all duration-500 ${socColor}`}
                            style={{ width: `${Math.min(100, Math.max(soc || 0, 3))}%` }}
                        />
                    </div>
                </div>

                {/* 2. Aktuelle Leistung */}
                <div className="p-4 rounded-2xl bg-slate-800/60 border border-slate-700/60 space-y-2">
                    <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                        ⚡ Lade- / Entladefluss
                    </div>

                    <div className="flex items-baseline gap-2">
                        <span className={`text-3xl font-black font-mono ${statusConfig.powerColor}`}>
                            {statusConfig.powerText}
                        </span>
                    </div>

                    <div className="text-[10px] text-slate-400 truncate">
                        Effizienz: {storage.charge_efficiency_pct}% · Reserve: {storage.min_soc_reserve_pct}%
                    </div>
                </div>
            </div>

            {/* Mapped Signal Sources (Bündelung von Messpunkten) */}
            <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-2.5">
                <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center justify-between">
                    <span>📡 Verknüpfte Messpunkte & Sensoren</span>
                    {storage.primary_device && (
                        <span className="text-[10px] text-indigo-300 bg-indigo-950/80 px-2 py-0.5 rounded-md border border-indigo-800/60">
                            Zentrales Gerät
                        </span>
                    )}
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                    {/* SoC Source */}
                    <div className="flex items-center gap-2 p-2 rounded-xl bg-slate-900/90 border border-slate-800">
                        <span className="text-emerald-400">🔋</span>
                        <div className="truncate">
                            <div className="text-[10px] text-slate-400">SoC-Sensor (%)</div>
                            <div className="font-semibold text-slate-200 truncate">
                                {storage.soc_device?.name || storage.primary_device?.name || "Nicht zugeordnet"}
                            </div>
                        </div>
                    </div>

                    {/* Power Source */}
                    <div className="flex items-center gap-2 p-2 rounded-xl bg-slate-900/90 border border-slate-800">
                        <span className="text-amber-400">⚡</span>
                        <div className="truncate">
                            <div className="text-[10px] text-slate-400">Leistungsmesser (W)</div>
                            <div className="font-semibold text-slate-200 truncate">
                                {storage.power_device?.name || storage.primary_device?.name || "Nicht zugeordnet"}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

