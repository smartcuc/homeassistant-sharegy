/*
# src/features/energy/components/SubmeterStackedTrendChart.jsx
*/

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid,
    Legend,
} from "recharts";
import { apiFetch } from "../../../api/client";

export default function SubmeterStackedTrendChart({ period = "30d", onSelectMeter }) {
    const { t } = useTranslation();
    const [hiddenMeters, setHiddenMeters] = useState(new Set());

    const trendQuery = useQuery({
        queryKey: ["submeter-stacked-trends", period],
        queryFn: () => apiFetch(`/api/energy/submeters/trends/?period=${period}`),
    });

    const data = trendQuery.data || {};
    const meters = data.meters || [];
    const rawTimeseries = data.timeseries || [];

    // Flatten data for Recharts: { date: "...", meter_id1: 4.2, meter_id2: 2.1, ... }
    const chartData = rawTimeseries.map((pt) => {
        const row = { date: pt.date };
        meters.forEach((m) => {
            row[m.id] = pt.meters[m.id]?.kwh || 0;
        });
        return row;
    });

    const toggleMeter = (mId) => {
        setHiddenMeters((prev) => {
            const next = new Set(prev);
            if (next.has(mId)) {
                next.delete(mId);
            } else {
                next.add(mId);
            }
            return next;
        });
    };

    if (trendQuery.isLoading) {
        return (
            <div className="bg-white border border-gray-200 rounded-3xl p-6 shadow-xs animate-pulse text-center text-xs text-gray-400">
                Lade historische Zählertrends...
            </div>
        );
    }

    if (meters.length === 0 || rawTimeseries.length === 0) {
        return null;
    }

    return (
        <div className="bg-white border border-gray-200 rounded-3xl p-6 shadow-xs space-y-4">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                    <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
                        <span>📊</span> {t("energy.submeter_trends_title", "Historische Trendanalyse aller Verbraucher")}
                    </h3>
                    <p className="text-xs text-gray-500 mt-0.5">
                        {t("energy.submeter_trends_subtitle", "Gestapelter Zeitverlauf der Lasten im gewählten Zeitraum. Klicke auf einen Zähler für Detailanalysen.")}
                    </p>
                </div>

                <span className="text-xs font-semibold px-2.5 py-1 bg-indigo-50 text-indigo-700 rounded-xl self-start sm:self-auto">
                    {data.period_label || period}
                </span>
            </div>

            {/* Interactive Legend / Filter Badges */}
            <div className="flex flex-wrap gap-2 pt-1">
                {meters.map((m) => {
                    const isHidden = hiddenMeters.has(m.id);
                    return (
                        <button
                            key={m.id}
                            onClick={() => toggleMeter(m.id)}
                            onDoubleClick={() => onSelectMeter && onSelectMeter(m)}
                            className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-2 border transition cursor-pointer ${isHidden
                                ? "bg-gray-100 border-gray-200 text-gray-400 opacity-60 line-through"
                                : "bg-white border-gray-200 text-gray-800 hover:border-indigo-300 shadow-2xs"
                                }`}
                            title="Klick: Ein-/Ausblenden · Doppelklick: Detailanalyse"
                        >
                            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: m.color }} />
                            <span>{m.icon}</span>
                            <span>{m.name}</span>
                            <span className="text-[10px] text-gray-400 font-mono">
                                ({Number(m.total_kwh).toFixed(1)} kWh)
                            </span>
                        </button>
                    );
                })}
            </div>

            {/* Chart Area */}
            <div className="h-72 w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                        <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="#94a3b8" />
                        <YAxis tick={{ fontSize: 11 }} stroke="#94a3b8" unit=" kWh" />
                        <Tooltip
                            formatter={(value, name) => {
                                const m = meters.find((item) => item.id === name);
                                const label = m ? `${m.icon} ${m.name}` : name;
                                return [`${Number(value).toFixed(2)} kWh`, label];
                            }}
                            contentStyle={{
                                borderRadius: "1rem",
                                border: "1px solid #e2e8f0",
                                boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                                fontSize: "12px",
                            }}
                        />
                        <Legend
                            formatter={(val) => {
                                const m = meters.find((item) => item.id === val);
                                return m ? `${m.icon} ${m.name}` : val;
                            }}
                            wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }}
                        />
                        {meters.map((m, idx) => {
                            if (hiddenMeters.has(m.id)) return null;
                            const isTop = idx === meters.length - 1;
                            return (
                                <Bar
                                    key={m.id}
                                    dataKey={m.id}
                                    stackId="submeters"
                                    fill={m.color}
                                    radius={isTop ? [4, 4, 0, 0] : [0, 0, 0, 0]}
                                    onClick={() => onSelectMeter && onSelectMeter(m)}
                                    className="cursor-pointer hover:opacity-85 transition"
                                />
                            );
                        })}
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}

