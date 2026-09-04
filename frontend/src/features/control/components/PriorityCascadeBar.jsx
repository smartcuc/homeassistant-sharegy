import { useTranslation } from "react-i18next";

const CATEGORY_META = {
    battery: { name: "Heimspeicher", icon: "🔋", color: "bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800" },
    bwwp: { name: "BWWP (Warmwasser)", icon: "♨️", color: "bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800" },
    wallbox: { name: "Wallbox (E-Auto)", icon: "🚗", color: "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800" },
    heatpump: { name: "Wärmepumpe", icon: "🔥", color: "bg-orange-50 dark:bg-orange-950/40 text-orange-700 dark:text-orange-300 border-orange-200 dark:border-orange-800" },
    pool: { name: "Pool & Filter", icon: "🏊", color: "bg-cyan-50 dark:bg-cyan-950/40 text-cyan-700 dark:text-cyan-300 border-cyan-200 dark:border-cyan-800" },
    ac: { name: "Klimaanlage (Pre-Cool)", icon: "❄️", color: "bg-sky-50 dark:bg-sky-950/40 text-sky-700 dark:text-sky-300 border-sky-200 dark:border-sky-800" },
    appliances: { name: "Haushaltsgeräte", icon: "🧺", color: "bg-purple-50 dark:bg-purple-950/40 text-purple-700 dark:text-purple-300 border-purple-200 dark:border-purple-800" },
    heating_rod: { name: "Heizstab (Puffer)", icon: "⚡", color: "bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800" },
    other: { name: "Sonstiger Verbraucher", icon: "🔌", color: "bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700" },
};

export default function PriorityCascadeBar({ priorityOrder = [], onOrderChange, isSaving }) {
    const { t } = useTranslation();

    const moveItem = (index, direction) => {
        const newOrder = [...priorityOrder];
        const targetIndex = index + direction;
        if (targetIndex < 0 || targetIndex >= newOrder.length) return;

        const temp = newOrder[index];
        newOrder[index] = newOrder[targetIndex];
        newOrder[targetIndex] = temp;

        onOrderChange(newOrder);
    };

    return (
        <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 border border-slate-200/90 dark:border-slate-800 shadow-xs space-y-4">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-600 dark:text-amber-400 flex items-center justify-center text-xl shadow-2xs">
                        🥇
                    </div>
                    <div>
                        <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                            <span>Prioritäten-Kaskade (Merit-Order)</span>
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                                {priorityOrder.length} Stufen
                            </span>
                        </h3>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                            Reihenfolge der Lastzuteilung bei Solarüberschuss. Nutze die Pfeiltasten zum Verschieben der Ränge.
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-2 self-start sm:self-auto">
                    <span className="text-xs font-semibold text-slate-400">
                        {isSaving ? "⏳ Speichern..." : "✓ Automatisch aktiv"}
                    </span>
                </div>
            </div>

            {/* Responsive Flex-Wrap Flow (No horizontal scrollbar!) */}
            <div className="flex flex-wrap items-center gap-2.5 pt-1">
                {priorityOrder.map((catKey, idx) => {
                    const meta = CATEGORY_META[catKey] || { name: catKey, icon: "🔌", color: "bg-slate-50 text-slate-700 border-slate-200" };
                    const isFirst = idx === 0;
                    const isLast = idx === priorityOrder.length - 1;

                    return (
                        <div
                            key={catKey}
                            className={`flex items-center gap-2 px-3 py-2 rounded-2xl border ${meta.color} shadow-2xs transition-all duration-150 hover:shadow-xs group`}
                        >
                            {/* Rank Badge */}
                            <div className={`w-6 h-6 rounded-full text-xs font-black flex items-center justify-center shrink-0 shadow-2xs ${
                                isFirst
                                    ? "bg-amber-500 text-white ring-2 ring-amber-300 dark:ring-amber-600"
                                    : "bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-black/5 dark:border-white/10"
                            }`}>
                                {idx + 1}
                            </div>

                            {/* Icon & Label */}
                            <span className="text-base shrink-0">{meta.icon}</span>
                            <span className="text-xs font-bold whitespace-nowrap">{meta.name}</span>

                            {/* Reorder Controls */}
                            <div className="flex items-center gap-0.5 ml-1 pl-1 border-l border-black/10 dark:border-white/10 opacity-70 group-hover:opacity-100">
                                <button
                                    type="button"
                                    onClick={() => moveItem(idx, -1)}
                                    disabled={isFirst || isSaving}
                                    className={`w-5 h-5 rounded-md flex items-center justify-center text-[10px] font-bold transition ${
                                        isFirst
                                            ? "text-black/20 dark:text-white/20 cursor-not-allowed"
                                            : "hover:bg-black/10 dark:hover:bg-white/10 text-slate-700 dark:text-slate-200 cursor-pointer"
                                    }`}
                                    title={isFirst ? "Bereits höchste Priorität" : "Höhere Priorität (nach links)"}
                                >
                                    ◀
                                </button>
                                <button
                                    type="button"
                                    onClick={() => moveItem(idx, 1)}
                                    disabled={isLast || isSaving}
                                    className={`w-5 h-5 rounded-md flex items-center justify-center text-[10px] font-bold transition ${
                                        isLast
                                            ? "text-black/20 dark:text-white/20 cursor-not-allowed"
                                            : "hover:bg-black/10 dark:hover:bg-white/10 text-slate-700 dark:text-slate-200 cursor-pointer"
                                    }`}
                                    title={isLast ? "Bereits niedrigste Priorität" : "Niedrigere Priorität (nach rechts)"}
                                >
                                    ▶
                                </button>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Smart Merit-Order Guidance Note */}
            <div className="text-[11px] text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-800/50 p-3 rounded-2xl border border-slate-100 dark:border-slate-800 flex items-start gap-2">
                <span className="text-amber-500 text-sm">💡</span>
                <span>
                    <strong>Merit-Order Prinzip:</strong> Rang 1 (z. B. Heimspeicher) erhält erzeugten Solarüberschuss vorrangig. Sobald die Leistung ausreicht oder der Speicher voll ist, wird der Überschuss kaskadierend an die nachfolgenden Ränge weitergereicht.
                </span>
            </div>
        </div>
    );
}
