import { useTranslation } from "react-i18next";

export default function HeatingRodCard({ consumer, onAction, isPending }) {
    const { t } = useTranslation();
    if (!consumer) return null;

    const isRunning = consumer.status_state === "on" || consumer.power_w > 20;

    return (
        <div className="bg-gradient-to-br from-white via-slate-50/70 to-amber-50/30 dark:from-slate-900 dark:via-slate-900/90 dark:to-amber-950/20 rounded-3xl p-6 border border-slate-200/90 dark:border-slate-800 shadow-sm relative overflow-hidden flex flex-col justify-between">
            {/* Ambient Glow */}
            <div className="absolute top-0 right-0 w-48 h-48 bg-amber-500/10 rounded-full blur-2xl pointer-events-none" />

            <div className="space-y-4 relative z-10">
                {/* Header */}
                <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-2xl shadow-xs">
                            ⚡
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h3 className="font-bold text-base text-slate-900 dark:text-white">
                                    {consumer.name}
                                </h3>
                                <span className={`px-2 py-0.5 text-[11px] font-bold rounded-full border ${
                                    isRunning
                                        ? "bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/30 animate-pulse"
                                        : "bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400 border-slate-200"
                                }`}>
                                    {isRunning ? t("control.heating_rod_running", "⚡ Heizen aktiv") : t("control.ac_standby", "⚪ Standby")}
                                </span>
                            </div>
                            <p className="text-xs text-slate-400 mt-0.5">
                                {t("control.heating_rod_subtitle", "Power-to-Heat · Pufferspeicher Überschussverwertung")}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Metrics */}
                <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/60">
                        <div className="text-[11px] text-slate-500">{t("control.heating_power", "Heizleistung (Live)")}</div>
                        <div className="text-lg font-bold font-mono text-slate-900 dark:text-white mt-0.5">
                            {isRunning ? `${consumer.power_w.toFixed(0)} W` : "0 W"}
                        </div>
                    </div>

                    <div className="p-3 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200/80 dark:border-slate-700/60">
                        <div className="text-[11px] text-slate-500">{t("control.activation_threshold", "Aktivierungsschwelle")}</div>
                        <div className="text-lg font-bold font-mono text-amber-600 dark:text-amber-400 mt-0.5">
                            {t("control.threshold_from", "ab {{power}} W PV", { power: "1.500" })}
                        </div>
                    </div>
                </div>

                {/* Mode / Strategy Strip */}
                <div className="p-3 bg-white/70 dark:bg-slate-800/50 rounded-2xl border border-slate-200/60 dark:border-slate-700/50 flex items-center justify-between gap-3 text-xs">
                    <div className="min-w-0">
                        <div className="font-bold text-slate-800 dark:text-slate-200 truncate">{t("control.surplus_utilization", "⚡ Überschuss-Verwertung")}</div>
                        <div className="text-[11px] text-slate-400 truncate">{t("control.surplus_utilization_desc", "Heizt Puffer bei vollem Speicher vor Netzeinspeisung")}</div>
                    </div>
                    <span className="font-mono text-xs font-bold text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/60 px-2.5 py-1 rounded-xl border border-amber-200 dark:border-amber-800 shrink-0">
                        {t("control.threshold_from", "ab {{power}} W PV", { power: "1.500" })}
                    </span>
                </div>
            </div>

            {/* Actions */}
            <div className="pt-4 mt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between gap-3 relative z-10">
                <span className="text-xs text-slate-400">
                    {t("control.mode_label", "Modus:")} <strong className="text-amber-600">{t("control.surplus_utilization", "Überschuss-Verwertung")}</strong>
                </span>
                <button
                    type="button"
                    onClick={() => onAction("heating_rod", isRunning ? "off" : "start", consumer.id)}
                    disabled={isPending}
                    className={`px-4 py-2 rounded-xl text-xs font-bold transition shadow-xs cursor-pointer ${
                        isRunning
                            ? "bg-slate-200 hover:bg-slate-300 text-slate-800 dark:bg-slate-800 dark:text-slate-200"
                            : "bg-amber-600 hover:bg-amber-700 text-white shadow-amber-600/20"
                    }`}
                >
                    {isRunning ? t("control.heating_rod_off", "⏹️ Heizstab Aus") : t("control.heating_rod_boost", "🔥 Sofort-Pufferladung")}
                </button>
            </div>
        </div>
    );
}
