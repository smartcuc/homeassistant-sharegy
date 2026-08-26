/*
# src/features/energy/components/SubmeterStackedTrendChart.jsx
*/

import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import ReactECharts from "echarts-for-react";
import { apiFetch } from "../../../api/client";

export default function SubmeterStackedTrendChart({ period = "30d", onSelectMeter }) {
    const { t } = useTranslation();
    const [hiddenMeters, setHiddenMeters] = useState(new Set());

    const trendQuery = useQuery({
        queryKey: ["submeter-stacked-trends", period],
        queryFn: () => apiFetch(`/api/energy/submeters/trends/?period=${period}`),
    });

    const data = trendQuery.data;
    const meters = data?.meters || [];
    const rawTimeseries = data?.timeseries || [];

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

    const chartOption = useMemo(() => {
        if (!data || !data.meters || !data.timeseries || data.meters.length === 0 || data.timeseries.length === 0) return null;

        const currentMeters = data.meters;
        const currentTimeseries = data.timeseries;
        const dates = currentTimeseries.map((pt) => pt.date);
        const visibleMeters = currentMeters.filter((m) => !hiddenMeters.has(m.id));

        const series = visibleMeters.map((m) => ({
            name: `${m.icon || ""} ${m.name}`.trim(),
            meterId: m.id,
            type: "bar",
            stack: "submeters",
            emphasis: {
                focus: "series",
            },
            itemStyle: {
                color: m.color || "#6366f1",
            },
            data: currentTimeseries.map((pt) => Number(pt.meters[m.id]?.kwh || 0)),
        }));

        return {
            tooltip: {
                trigger: "axis",
                axisPointer: {
                    type: "shadow",
                },
                backgroundColor: "rgba(255, 255, 255, 0.95)",
                borderColor: "#e2e8f0",
                textStyle: { color: "#1e293b", fontSize: 12 },
                extraCssText: "box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border-radius: 0.75rem;",
                formatter: (params) => {
                    if (!params || !params.length) return "";
                    let total = 0;
                    let html = `<div style="font-weight:bold;margin-bottom:4px;">${params[0].name}</div>`;
                    params.forEach((item) => {
                        const val = Number(item.value || 0);
                        total += val;
                        html += `<div style="display:flex;justify-content:space-between;gap:12px;font-size:11px;">
                            <span>${item.marker} ${item.seriesName}:</span>
                            <span style="font-weight:bold;font-family:monospace;">${val.toFixed(2)} kWh</span>
                        </div>`;
                    });
                    html += `<div style="border-top:1px solid #e2e8f0;margin-top:4px;padding-top:4px;display:flex;justify-content:space-between;gap:12px;font-size:11px;font-weight:bold;">
                        <span>Gesamt:</span>
                        <span style="font-family:monospace;color:#4f46e5;">${total.toFixed(2)} kWh</span>
                    </div>`;
                    return html;
                },
            },
            grid: {
                left: "2%",
                right: "2%",
                bottom: "3%",
                top: "10%",
                containLabel: true,
            },
            xAxis: {
                type: "category",
                data: dates,
                axisLabel: {
                    fontSize: 11,
                    color: "#94a3b8",
                },
                axisLine: {
                    lineStyle: { color: "#cbd5e1" },
                },
            },
            yAxis: {
                type: "value",
                axisLabel: {
                    formatter: "{value} kWh",
                    fontSize: 11,
                    color: "#94a3b8",
                },
                splitLine: {
                    lineStyle: { color: "#f1f5f9", type: "dashed" },
                },
            },
            series,
        };
    }, [data, hiddenMeters]);

    const onChartClick = (params) => {
        if (onSelectMeter && params.seriesName) {
            const found = meters.find((m) => `${m.icon || ""} ${m.name}`.trim() === params.seriesName);
            if (found) onSelectMeter(found);
        }
    };

    if (trendQuery.isLoading) {
        return (
            <div className="bg-white border border-gray-200 rounded-3xl p-6 shadow-xs animate-pulse text-center text-xs text-gray-400">
                Lade historische Zählertrends...
            </div>
        );
    }

    if (meters.length === 0 || rawTimeseries.length === 0 || !chartOption) {
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
                <ReactECharts
                    option={chartOption}
                    style={{ height: "100%", width: "100%" }}
                    notMerge={true}
                    lazyUpdate={true}
                    onEvents={{ click: onChartClick }}
                />
            </div>
        </div>
    );
}

