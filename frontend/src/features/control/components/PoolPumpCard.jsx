import { useTranslation } from "react-i18next";

export default function PoolPumpCard({ consumer, onAction, isPending }) {
    const { t } = useTranslation();
    if (!consumer) return null;

    const details = consumer.details || {};
    const minRuntime = details.min_daily_runtime_min || 300; // 5 hours
    const completedRuntime = details.runtime_completed_min || 180; // 3 hours
    const runtimePct = Math.min(100, Math.round((completedRuntime / minRuntime) * 100));
    const isRunning = consumer.status_state === "on" || consumer.power_w > 20;

    return (
        <div className="bg-gradient-to-br from-white via-slate-50/70 to-cyan-50/30 dark:from-slate-900 dark:via-slate-900/90 dark:to-cyan-950/20 rounded-3xl p-6 border border-slate-200/90 dark:border-slate-800 shadow-sm relative overflow-hidden flex flex-col justify-between">
            {/* Ambient Glow */}
            <div className="absolute top-0 right-0 w-48 h-48 bg-cyan-500/10 rounded-full blur-2xl pointer-events-none" />

            <div className="space-y-4 relative z-10">
                {/* Header */}
                <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-2xl shadow-xs">
                            🏊
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h3 className="font-bold text-base text-slate-900 dark:text-white">
                                    {consumer.name}
                                </h3>
                                <span className={`px-2 py-0.5 text-[11px] font-bold rounded-full border ${
                                    isRunning
                                        ? "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 animate-pulse"
                                        : "bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400 border-slate-200"
                                }`}>
                                    {isRunning ? "● Läuft" : "⚪ Standby"}
                                </span>
                            </div>
                            <p className="text-xs text-slate-400 mt-0.5">
                                Sommer-Peak Shaving & Solar-Filterung
                            </p>
                        </div>
                    </div>
                </div>

                {/* Metrics */}
                <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/60">
                        <div className="text-[11px] text-slate-500">Leistung (Live)</div>
                        <div className="text-lg font-bold font-mono text-slate-900 dark:text-white mt-0.5">
                            {isRunning ? `${consumer.power_w.toFixed(0)} W` : "0 W"}
                        </div>
                    </div>

                    <div className="p-3 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/60">
                        <div className="text-[11px] text-slate-500">Tages-Laufzeit</div>
                        <div className="text-lg font-bold font-mono text-cyan-600 dark:text-cyan-400 mt-0.5">
                            {(completedRuntime / 60).toFixed(1)} / {(minRuntime / 60).toFixed(0)} h
                        </div>
                    </div>
                </div>

                {/* Daily Runtime Progress Bar */}
                <div className="space-y-1.5">
                    <div className="flex justify-between text-xs text-slate-500">
                        <span>Filterhygiene ({runtimePct}%)</span>
                        <span className="font-mono">Ziel: {(minRuntime / 60).toFixed(0)}h / Tag</span>
                    </div>
                    <div className="h-2.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full transition-all duration-500"
                            style={{ width: `${runtimePct}%` }}
                        />
                    </div>
                </div>
            </div>

            {/* Actions */}
            <div className="pt-4 mt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between gap-3 relative z-10">
                <span className="text-xs text-slate-400">
                    Modus: <strong className="text-slate-700 dark:text-slate-200">Solar-Automatik</strong>
                </span>
                <button
                    type="button"
                    onClick={() => onAction("pool", isRunning ? "off" : "start", consumer.id)}
                    disabled={isPending}
                    className={`px-4 py-2 rounded-xl text-xs font-bold transition shadow-xs cursor-pointer ${
                        isRunning
                            ? "bg-slate-200 hover:bg-slate-300 text-slate-800 dark:bg-slate-800 dark:text-slate-200"
                            : "bg-cyan-600 hover:bg-cyan-700 text-white shadow-cyan-600/20"
                    }`}
                >
                    {isRunning ? "⏹️ Filterung stoppen" : "▶️ Jetzt 2h filtern"}
                </button>
            </div>
        </div>
    );
}
