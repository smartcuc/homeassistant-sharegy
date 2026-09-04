import { useTranslation } from "react-i18next";

export default function DispatchTimelineCard({ schedule = [] }) {
    const { t } = useTranslation();

    if (!schedule || schedule.length === 0) {
        return null;
    }

    return (
        <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 border border-slate-200/90 dark:border-slate-800 shadow-xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-2xl bg-indigo-500/10 dark:bg-indigo-400/15 border border-indigo-500/20 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-xl">
                        📅
                    </div>
                    <div>
                        <h3 className="text-base font-bold text-slate-900 dark:text-white">
                            24h-Fahrplan & Dispatch-Timeline
                        </h3>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                            Geplante Einschaltfenster basierend auf Solarprognose, dynamischen Spotpreisen & Prioritäten.
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-2 self-start sm:self-auto text-xs font-semibold text-slate-500">
                    <span className="flex items-center gap-1">
                        <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> ☀️ PV-Überschuss
                    </span>
                    <span className="flex items-center gap-1 ml-2">
                        <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> ⚡ Tiefstpreis
                    </span>
                </div>
            </div>

            {/* Scrollable Timeline Horizontal Grid */}
            <div className="overflow-x-auto pb-3 pt-1">
                <div className="flex gap-2.5 min-w-[900px]">
                    {schedule.map((slot, i) => {
                        const hasDevices = slot.scheduled_devices && slot.scheduled_devices.length > 0;
                        const isDay = slot.hour >= 6 && slot.hour <= 20;

                        return (
                            <div
                                key={slot.timestamp || i}
                                className={`flex-1 min-w-[85px] rounded-2xl border p-2.5 flex flex-col justify-between transition ${
                                    hasDevices
                                        ? "bg-indigo-50/50 dark:bg-indigo-950/20 border-indigo-200 dark:border-indigo-800/80 shadow-2xs"
                                        : "bg-slate-50/50 dark:bg-slate-800/30 border-slate-200/60 dark:border-slate-800"
                                }`}
                            >
                                {/* Slot Time & Metrics */}
                                <div className="space-y-1 text-center border-b border-slate-200/50 dark:border-slate-800 pb-1.5">
                                    <div className="text-xs font-bold font-mono text-slate-800 dark:text-slate-200">
                                        {slot.time_label}
                                    </div>
                                    <div className="text-[10px] text-slate-400">
                                        {isDay ? "☀️" : "🌙"} {slot.pv_kw > 0 ? `${slot.pv_kw} kW` : "0 kW"}
                                    </div>
                                    <div className={`text-[10px] font-mono font-semibold ${
                                        slot.price_ct <= 20 ? "text-emerald-600 dark:text-emerald-400" : "text-slate-600 dark:text-slate-300"
                                    }`}>
                                        {slot.price_ct.toFixed(1)} ct
                                    </div>
                                </div>

                                {/* Scheduled Device Badges */}
                                <div className="mt-2 space-y-1 min-h-[44px] flex flex-col justify-start">
                                    {hasDevices ? (
                                        slot.scheduled_devices.map((dev, devIdx) => (
                                            <div
                                                key={devIdx}
                                                className="px-1.5 py-1 rounded-lg bg-white dark:bg-slate-800 border border-indigo-100 dark:border-indigo-800/60 text-[10px] font-bold text-slate-800 dark:text-slate-200 flex items-center justify-between shadow-2xs"
                                                title={`${dev.name} (${dev.power_kw} kW) - ${dev.reason}`}
                                            >
                                                <span className="truncate flex items-center gap-1">
                                                    <span>{dev.icon}</span>
                                                    <span className="truncate max-w-[45px]">{dev.name.split(" ")[0]}</span>
                                                </span>
                                                <span className="text-indigo-600 dark:text-indigo-400 font-mono text-[9px] shrink-0">
                                                    {dev.power_kw}k
                                                </span>
                                            </div>
                                        ))
                                    ) : (
                                        <div className="text-[10px] text-slate-300 dark:text-slate-600 text-center my-auto">
                                            –
                                        </div>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
