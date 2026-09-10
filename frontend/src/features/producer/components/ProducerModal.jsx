/*
# src/features/producer/components/ProducerModal.jsx
*/

import { useQuery } from "@tanstack/react-query";
import { getGenerators } from "../api";
import { useTranslation } from "react-i18next";

export default function ProducerModal({
    open,
    onClose,
}) {
    const { t } = useTranslation();

    const { data = [] } = useQuery({
        queryKey: ["generators"],
        queryFn: getGenerators,
        enabled: open,
    });

    if (!open) {
        return null;
    }

    return (
        <div
            className="fixed inset-0 bg-slate-950/75 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-in fade-in duration-200"
            onClick={onClose}
        >
            <div
                className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl shadow-2xl max-w-4xl w-full max-h-[85vh] flex flex-col overflow-hidden p-5 sm:p-6 animate-in zoom-in-95 duration-200"
                onClick={(e) => e.stopPropagation()}
            >
                <div className="flex justify-between items-center pb-4 mb-4 border-b border-slate-100 dark:border-slate-800 shrink-0">
                    <h2 className="text-lg sm:text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <span>☀️</span> {t("producers.title", "Erzeuger")}
                    </h2>

                    <button
                        type="button"
                        onClick={onClose}
                        className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 flex items-center justify-center text-sm font-bold transition cursor-pointer"
                    >
                        ✕
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto space-y-3.5 pr-1">
                    {data.length === 0 && (
                        <div className="text-center py-12 text-slate-400 text-xs sm:text-sm">
                            {t("producers.empty", "Noch keine Erzeugersysteme vorhanden.")}
                        </div>
                    )}

                    {data.map((system) => (
                        <div
                            key={system.id}
                            className="border border-slate-200 dark:border-slate-800 rounded-2xl p-4 bg-slate-50/70 dark:bg-slate-800/60 shadow-2xs space-y-2"
                        >
                            <div className="font-bold text-slate-900 dark:text-white text-sm sm:text-base flex items-center justify-between">
                                <span>{system.name}</span>
                                {system.peak_power_kw && (
                                    <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded-lg bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300">
                                        {system.peak_power_kw} kWp
                                    </span>
                                )}
                            </div>

                            {system.generator_type && (
                                <div className="text-xs text-slate-500 dark:text-slate-400">
                                    {t(`generator_types.${system.generator_type.key}`, system.generator_type.name)}
                                </div>
                            )}

                            {system.strings?.length > 0 && (
                                <div className="pt-2 border-t border-slate-200/60 dark:border-slate-700/60 space-y-1.5">
                                    <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                                        Strings ({system.strings.length}):
                                    </div>
                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                        {system.strings.map((str) => (
                                            <div
                                                key={str.id}
                                                className="p-2.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs"
                                            >
                                                <div className="font-semibold text-slate-900 dark:text-white">{str.name}</div>
                                                <div className="text-[11px] text-slate-500 dark:text-slate-400 font-mono mt-0.5">
                                                    {str.module_count} Module · {str.peak_power_kwp} kWp {str.tilt_deg ? `· ${str.tilt_deg}°` : ""}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>

                <div className="pt-4 mt-2 border-t border-slate-100 dark:border-slate-800 flex justify-end shrink-0">
                    <button
                        type="button"
                        onClick={onClose}
                        className="px-4 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-xl transition cursor-pointer"
                    >
                        {t("common.close", "Schließen")}
                    </button>
                </div>
            </div>
        </div>
    );
}
