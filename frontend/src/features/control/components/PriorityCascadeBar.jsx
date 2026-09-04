import { useState } from "react";
import { useTranslation } from "react-i18next";

const CATEGORY_META = {
    battery: { name: "Heimspeicher", icon: "🔋", color: "bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 border-indigo-300" },
    bwwp: { name: "BWWP (Warmwasser)", icon: "♨️", color: "bg-blue-500/10 text-blue-700 dark:text-blue-300 border-blue-300" },
    wallbox: { name: "Wallbox (E-Auto)", icon: "🚗", color: "bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border-emerald-300" },
    heatpump: { name: "Wärmepumpe", icon: "🔥", color: "bg-orange-500/10 text-orange-700 dark:text-orange-300 border-orange-300" },
    pool: { name: "Pool & Filter", icon: "🏊", color: "bg-cyan-500/10 text-cyan-700 dark:text-cyan-300 border-cyan-300" },
    ac: { name: "Klimaanlage (Pre-Cool)", icon: "❄️", color: "bg-sky-500/10 text-sky-700 dark:text-sky-300 border-sky-300" },
    appliances: { name: "Haushaltsgeräte", icon: "🧺", color: "bg-purple-500/10 text-purple-700 dark:text-purple-300 border-purple-300" },
    heating_rod: { name: "Heizstab (Puffer)", icon: "⚡", color: "bg-amber-500/10 text-amber-700 dark:text-amber-300 border-amber-300" },
    other: { name: "Sonstiger Verbraucher", icon: "🔌", color: "bg-slate-500/10 text-slate-700 dark:text-slate-300 border-slate-300" },
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
        <div className="bg-white dark:bg-slate-900 rounded-3xl p-5 border border-slate-200/90 dark:border-slate-800 shadow-xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
                <div>
                    <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <span>🥇</span>
                        <span>Prioritäten-Kaskade (Merit-Order)</span>
                    </h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                        Reihenfolge der Lastzuteilung bei Solarüberschuss. Nutze die Pfeile zum Verschieben.
                    </p>
                </div>
                <span className="text-[11px] font-semibold text-slate-400 self-start sm:self-auto">
                    {isSaving ? "⏳ Speichern..." : "✓ Gespeichert"}
                </span>
            </div>

            {/* Horizontal Scrollable Cascade */}
            <div className="flex items-center gap-2 overflow-x-auto pb-2 pt-1 pr-2">
                {priorityOrder.map((catKey, idx) => {
                    const meta = CATEGORY_META[catKey] || { name: catKey, icon: "🔌", color: "bg-slate-100" };
                    const isFirst = idx === 0;
                    const isLast = idx === priorityOrder.length - 1;

                    return (
                        <div key={catKey} className="flex items-center gap-2 shrink-0">
                            {/* Card Item */}
                            <div className={`flex items-center gap-2.5 px-3 py-2 rounded-2xl border ${meta.color} shadow-2xs group transition hover:scale-105`}>
                                <div className="w-6 h-6 rounded-full bg-white dark:bg-slate-800 shadow-xs text-xs font-black flex items-center justify-center text-slate-700 dark:text-slate-200 shrink-0">
                                    {idx + 1}
                                </div>
                                <span className="text-lg shrink-0">{meta.icon}</span>
                                <span className="text-xs font-bold whitespace-nowrap">{meta.name}</span>

                                {/* Reorder Controls */}
                                <div className="flex items-center gap-0.5 ml-1.5 opacity-70 group-hover:opacity-100">
                                    {!isFirst && (
                                        <button
                                            type="button"
                                            onClick={() => moveItem(idx, -1)}
                                            disabled={isSaving}
                                            className="w-5 h-5 rounded-md hover:bg-black/10 dark:hover:bg-white/10 flex items-center justify-center text-xs cursor-pointer font-bold"
                                            title="Höhere Priorität"
                                        >
                                            ◀
                                        </button>
                                    )}
                                    {!isLast && (
                                        <button
                                            type="button"
                                            onClick={() => moveItem(idx, 1)}
                                            disabled={isSaving}
                                            className="w-5 h-5 rounded-md hover:bg-black/10 dark:hover:bg-white/10 flex items-center justify-center text-xs cursor-pointer font-bold"
                                            title="Niedrigere Priorität"
                                        >
                                            ▶
                                        </button>
                                    )}
                                </div>
                            </div>

                            {/* Arrow Separator */}
                            {!isLast && (
                                <span className="text-slate-300 dark:text-slate-600 font-bold text-xs">➔</span>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
