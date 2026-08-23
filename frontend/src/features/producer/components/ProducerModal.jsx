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
            className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
            onClick={onClose}
        >
            <div
                className="bg-white rounded-2xl shadow-xl max-w-4xl w-full h-[80vh] flex flex-col overflow-hidden p-6"
                onClick={(e) => e.stopPropagation()}
            >
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                        <span>☀️</span> {t("producers.title", "Erzeuger")}
                    </h2>

                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600 text-lg"
                    >
                        ✕
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto space-y-4">
                    {data.length === 0 && (
                        <div className="text-center py-12 text-gray-400 text-sm">
                            {t("producers.empty", "Noch keine Erzeugersysteme vorhanden.")}
                        </div>
                    )}

                    {data.map((system) => (
                        <div
                            key={system.id}
                            className="border border-gray-200 rounded-xl p-4 bg-white shadow-xs"
                        >
                            <div className="font-semibold text-gray-900 text-base">
                                {system.name}
                            </div>

                            <div className="text-sm text-gray-500 capitalize">
                                {system.type}
                            </div>

                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-3">
                                <div className="bg-slate-50 p-2.5 rounded-lg">
                                    <div className="text-[10px] uppercase font-bold text-gray-400">
                                        {t("producers.power", "Leistung")}
                                    </div>
                                    <div className="font-semibold text-gray-900 text-sm">
                                        {system.peak_power_kw} kWp
                                    </div>
                                </div>

                                <div className="bg-slate-50 p-2.5 rounded-lg">
                                    <div className="text-[10px] uppercase font-bold text-gray-400">
                                        {t("producers.strings", "Strings")}
                                    </div>
                                    <div className="font-semibold text-gray-900 text-sm">
                                        {system.string_count}
                                    </div>
                                </div>

                                <div className="bg-slate-50 p-2.5 rounded-lg">
                                    <div className="text-[10px] uppercase font-bold text-gray-400">
                                        {t("producers.inverter", "WR")}
                                    </div>
                                    <div className="font-semibold text-gray-900 text-sm">
                                        {system.inverter_power_kw ?? "-"} kW
                                    </div>
                                </div>

                                <div className="bg-slate-50 p-2.5 rounded-lg">
                                    <div className="text-[10px] uppercase font-bold text-gray-400">
                                        {t("producers.battery", "Speicher")}
                                    </div>
                                    <div className="font-semibold text-gray-900 text-sm">
                                        {system.battery_capacity_kwh ?? "-"} kWh
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
