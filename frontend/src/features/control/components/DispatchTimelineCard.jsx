import { useState } from "react";
import { useTranslation } from "react-i18next";

export default function DispatchTimelineCard({ schedule = [] }) {
    const { t } = useTranslation();

    // Helper to sanitize device names from legacy identifiers
    const getCleanDeviceName = (name, category) => {
        if (!name) return category === "bwwp" ? t("control.warmwasser", "Warmwasser") : "";
        const lower = name.toLowerCase();
        if (category === "bwwp" || lower.includes("bwwp") || lower.includes("brauchwasser")) {
            return t("control.warmwasser", "Warmwasser");
        }
        if (lower.includes("aircon_power") || lower === "aircon") {
            return category === "ac" ? t("control.aircon", "Klimaanlage") : t("control.warmwasser", "Warmwasser");
        }
        return name;
    };

    // Default selected slot: the current hour or first slot with scheduled devices
    const [selectedSlotIndex, setSelectedSlotIndex] = useState(() => {
        if (!schedule || schedule.length === 0) return 0;
        const withDevices = schedule.findIndex((s) => s.scheduled_devices && s.scheduled_devices.length > 0);
        return withDevices !== -1 ? withDevices : 12; // default to noon if none
    });

    if (!schedule || schedule.length === 0) {
        return null;
    }

    const maxPv = Math.max(...schedule.map((s) => s.pv_kw || 0), 4.0);
    const selectedSlot = schedule[selectedSlotIndex] || schedule[0];

    // Group scheduled devices into clear summary blocks (e.g. "Wallbox 11:00 - 15:00")
    const deviceRuns = {};
    schedule.forEach((slot) => {
        (slot.scheduled_devices || []).forEach((dev) => {
            const cleanName = getCleanDeviceName(dev.name, dev.category);
            if (!deviceRuns[cleanName]) {
                deviceRuns[cleanName] = {
                    name: cleanName,
                    icon: dev.icon,
                    category: dev.category,
                    power_kw: dev.power_kw,
                    reason: dev.reason,
                    hours: [],
                };
            }
            deviceRuns[cleanName].hours.push(slot.time_label);
        });
    });

    const activeScheduleSummaries = Object.values(deviceRuns).map((run) => {
        const start = run.hours[0];
        const endHourNum = parseInt(run.hours[run.hours.length - 1].split(":")[0], 10) + 1;
        const end = `${String(endHourNum).padStart(2, "0")}:00`;
        return {
            ...run,
            timeRange: `${start} – ${end}`,
            totalHours: run.hours.length,
        };
    });

    return (
        <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 border border-slate-200/90 dark:border-slate-800 shadow-xs space-y-5">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-3">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-xl shadow-2xs">
                        📅
                    </div>
                    <div>
                        <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                            <span>{t("control.timeline_title", "24h-Fahrplan & Dispatch-Timeline")}</span>
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-950/50 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                                {t("control.timeline_24h_view", "24 Stunden Übersicht")}
                            </span>
                        </h3>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                            {t("control.timeline_desc", "Automatische Schaltungen basierend auf Solarprognose, Spotmarktpreisen und Prioritäten. Klicke auf eine Stunde für Details.")}
                        </p>
                    </div>
                </div>

                <div className="flex flex-wrap items-center gap-3 text-xs font-semibold text-slate-500 dark:text-slate-400 self-start sm:self-auto">
                    <span className="flex items-center gap-1.5">
                        <span className="w-2.5 h-2.5 rounded-full bg-amber-500 shadow-2xs"></span> {t("control.legend_pv", "☀️ PV-Ertrag")}
                    </span>
                    <span className="flex items-center gap-1.5">
                        <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-2xs"></span> {t("control.legend_lowest_price", "⚡ Tiefstpreis")}
                    </span>
                    <span className="flex items-center gap-1.5">
                        <span className="w-2.5 h-2.5 rounded-full bg-indigo-600 shadow-2xs"></span> {t("control.legend_activity", "🎛️ Aktivität")}
                    </span>
                </div>
            </div>

            {/* 24-Hour Continuous Visual Strip (100% Container Width, Zero Horizontal Scroll!) */}
            <div className="space-y-1.5">
                <div className="grid grid-cols-24 gap-0.5 sm:gap-1 w-full bg-slate-50 dark:bg-slate-950/60 p-2 sm:p-3 rounded-2xl border border-slate-200/80 dark:border-slate-800/80">
                    {schedule.map((slot, idx) => {
                        const hasDevices = slot.scheduled_devices && slot.scheduled_devices.length > 0;
                        const isSelected = selectedSlotIndex === idx;
                        const pvHeightPct = Math.min(100, Math.round(((slot.pv_kw || 0) / maxPv) * 100));
                        const isCheap = (slot.price_ct || 25) <= 20.0;
                        const isHighPrice = (slot.price_ct || 25) >= 28.0;

                        return (
                            <button
                                key={slot.timestamp || idx}
                                type="button"
                                onClick={() => setSelectedSlotIndex(idx)}
                                className={`flex flex-col items-center justify-end rounded-xl p-1 transition-all cursor-pointer relative group h-24 ${
                                    isSelected
                                        ? "bg-indigo-600/15 dark:bg-indigo-500/25 ring-2 ring-indigo-600 shadow-sm"
                                        : "hover:bg-slate-200/60 dark:hover:bg-slate-800/60"
                                }`}
                                title={`${slot.time_label}: PV ${slot.pv_kw} kW, Preis ${slot.price_ct.toFixed(1)} ct/kWh`}
                            >
                                {/* Scheduled Device Indicator Indicator Dot / Icon */}
                                {hasDevices ? (
                                    <div className="w-4 h-4 sm:w-5 sm:h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center text-[9px] sm:text-[10px] shadow-sm mb-1 animate-pulse">
                                        {slot.scheduled_devices[0]?.icon || "⚡"}
                                    </div>
                                ) : (
                                    <div className="h-4 sm:h-5 mb-1 flex items-center justify-center">
                                        <div className={`w-1.5 h-1.5 rounded-full ${
                                            isCheap ? "bg-emerald-500" : isHighPrice ? "bg-rose-400" : "bg-slate-300 dark:bg-slate-700"
                                        }`} />
                                    </div>
                                )}

                                {/* PV Production Bar */}
                                <div className="w-full bg-slate-200 dark:bg-slate-800 rounded-md h-9 flex items-end overflow-hidden">
                                    <div
                                        style={{ height: `${pvHeightPct}%` }}
                                        className={`w-full rounded-sm transition-all duration-300 ${
                                            slot.pv_kw > 0
                                                ? "bg-gradient-to-t from-amber-500 to-amber-400 dark:from-amber-600 dark:to-amber-400"
                                                : "bg-transparent"
                                        }`}
                                    />
                                </div>

                                {/* Hour Label (Key hours highlighted) */}
                                <div className={`text-[9px] sm:text-[10px] font-mono mt-1 font-semibold ${
                                    isSelected
                                        ? "text-indigo-600 dark:text-indigo-400 font-bold"
                                        : "text-slate-500 dark:text-slate-400"
                                }`}>
                                    {slot.hour % 3 === 0 || slot.hour === 23 ? `${slot.hour}h` : "·"}
                                </div>
                            </button>
                        );
                    })}
                </div>

                {/* Legend Time Scale */}
                <div className="flex justify-between px-2 text-[10px] font-mono text-slate-400">
                    <span>00:00</span>
                    <span>06:00</span>
                    <span>12:00</span>
                    <span>18:00</span>
                    <span>23:00</span>
                </div>
            </div>

            {/* Selected Slot Inspector & Action Summary Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* 1. Detail-Inspektor für die gewählte Stunde */}
                <div className="bg-slate-50 dark:bg-slate-800/50 rounded-2xl p-4 border border-slate-200/80 dark:border-slate-800 space-y-3">
                    <div className="flex items-center justify-between border-b border-slate-200/60 dark:border-slate-700 pb-2">
                        <div className="flex items-center gap-2">
                            <span className="text-base">⏰</span>
                            <span className="text-sm font-bold text-slate-900 dark:text-white">
                                {selectedSlot.time_label} – {String((selectedSlot.hour + 1) % 24).padStart(2, "0")}:00
                            </span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-md bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300">
                                ☀️ {selectedSlot.pv_kw.toFixed(1)} kW
                            </span>
                            <span className={`text-xs font-mono font-bold px-2 py-0.5 rounded-md ${
                                selectedSlot.price_ct <= 20
                                    ? "bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300"
                                    : "bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200"
                            }`}>
                                ⚡ {selectedSlot.price_ct.toFixed(1)} ct
                            </span>
                        </div>
                    </div>

                    <div>
                        <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">
                            {t("control.scheduled_loads_hour", "Geplante Lasten in dieser Stunde:")}
                        </div>
                        {selectedSlot.scheduled_devices && selectedSlot.scheduled_devices.length > 0 ? (
                            <div className="space-y-1.5">
                                {selectedSlot.scheduled_devices.map((dev, devIdx) => {
                                    const cleanName = getCleanDeviceName(dev.name, dev.category);
                                    return (
                                        <div
                                            key={devIdx}
                                            className="flex items-center justify-between p-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs shadow-2xs"
                                        >
                                            <div className="flex items-center gap-2 font-bold text-slate-800 dark:text-slate-200">
                                                <span className="text-base">{dev.icon}</span>
                                                <span>{cleanName}</span>
                                                <span className="text-[10px] font-normal px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                                                    {dev.reason}
                                                </span>
                                            </div>
                                            <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400">
                                                {dev.power_kw} kW
                                            </span>
                                        </div>
                                    );
                                })}
                            </div>
                        ) : (
                            <div className="text-xs text-slate-400 dark:text-slate-500 py-1">
                                {t("control.no_special_dispatches", "Keine Sonderzuschaltungen geplant · Standard Grundlast-Betrieb (~0,35 kW).")}
                            </div>
                        )}
                    </div>
                </div>

                {/* 2. Zusammenfassung: Heute geplante Schaltungen */}
                <div className="bg-slate-50 dark:bg-slate-800/50 rounded-2xl p-4 border border-slate-200/80 dark:border-slate-800 space-y-3">
                    <div className="flex items-center justify-between border-b border-slate-200/60 dark:border-slate-700 pb-2">
                        <div className="flex items-center gap-2">
                            <span className="text-base">📋</span>
                            <span className="text-sm font-bold text-slate-900 dark:text-white">
                                {t("control.today_scheduled_actions", "Heute geplante Schaltungen")}
                            </span>
                        </div>
                        <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">
                            {t("control.actions_count", "{{count}} Aktionen", { count: activeScheduleSummaries.length })}
                        </span>
                    </div>

                    {activeScheduleSummaries.length > 0 ? (
                        <div className="space-y-1.5">
                            {activeScheduleSummaries.map((summary, idx) => (
                                <div
                                    key={idx}
                                    className="flex items-center justify-between p-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs shadow-2xs"
                                >
                                    <div className="flex items-center gap-2 font-bold text-slate-800 dark:text-slate-200">
                                        <span className="text-base">{summary.icon}</span>
                                        <div>
                                            <div>{summary.name}</div>
                                            <div className="text-[10px] font-normal text-slate-500 dark:text-slate-400">
                                                {summary.reason}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className="font-mono font-bold text-slate-900 dark:text-white">
                                            {summary.timeRange}
                                        </div>
                                        <div className="text-[10px] text-slate-400">
                                            {summary.totalHours}h ({summary.power_kw} kW)
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-xs text-slate-400 dark:text-slate-500 py-3 text-center">
                            {t("control.no_special_runs_needed", "Für heute sind keine Sonder-Laufzeiten erforderlich.")}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
