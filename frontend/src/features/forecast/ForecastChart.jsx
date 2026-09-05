/*
# src/features/forecast/ForecastChart.jsx
*/

import { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import { formatHour, formatNumber, formatDateTime } from "../../utils/format";
import { useTimezone } from "../../hooks/useTimezone";

export default function ForecastChart({ points = [] }) {
    const FORECAST_COLOR = "#f59e0b";
    const timezone = useTimezone();

    const validPoints = Array.isArray(points) ? points : [];

    const option = useMemo(() => {
        if (validPoints.length === 0) return null;

        const xAxisData = validPoints.map((p) =>
            formatHour(p.t * 1000, timezone)
        );

        const seriesData = validPoints.map((p) => Number(p.v));

        return {
            tooltip: {
                trigger: "axis",
                backgroundColor: "rgba(15, 23, 42, 0.95)",
                borderColor: "#334155",
                borderRadius: 12,
                padding: [10, 14],
                textStyle: { color: "#fff", fontSize: 12 },
                axisPointer: {
                    type: "line",
                    lineStyle: {
                        color: "#f59e0b",
                        width: 1.5,
                        type: "dashed",
                    },
                },
                formatter: function (params) {
                    const p = params?.[0];
                    if (!p) return "";

                    const point = validPoints[p.dataIndex];
                    if (!point) return "";

                    return `
                        <div style="font-weight: bold; margin-bottom: 6px; font-size: 12px; color: #cbd5e1;">
                            ⏰ ${formatDateTime(point.t * 1000, timezone)}
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between; gap: 16px;">
                            <span style="color: #fbbf24; font-size: 12px; font-weight: 600;">☀️ Solar Forecast:</span>
                            <b style="font-family: monospace; font-size: 13px; color: #ffffff;">${formatNumber(p.value, 3)} kWh</b>
                        </div>
                    `;
                },
            },
            grid: {
                top: 25,
                left: 55,
                right: 20,
                bottom: 35,
                containLabel: true,
            },
            xAxis: {
                type: "category",
                data: xAxisData,
                boundaryGap: false,
                axisLine: { lineStyle: { color: "#e2e8f0" } },
                axisLabel: { color: "#64748b", fontSize: 11, fontWeight: 500 },
                axisTick: { show: false },
            },
            yAxis: {
                type: "value",
                axisLine: { show: false },
                axisTick: { show: false },
                splitLine: {
                    lineStyle: {
                        color: "#f1f5f9",
                        type: "dashed",
                    },
                },
                axisLabel: {
                    color: "#64748b",
                    fontSize: 11,
                    formatter: (value) => `${formatNumber(value, 1)} kWh`,
                },
            },
            series: [
                {
                    name: "Solar Forecast",
                    type: "line",
                    smooth: 0.35,
                    showSymbol: false,
                    data: seriesData,
                    lineStyle: {
                        width: 3,
                        color: FORECAST_COLOR,
                    },
                    areaStyle: {
                        color: {
                            type: "linear",
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [
                                { offset: 0, color: "rgba(245, 158, 11, 0.42)" },
                                { offset: 0.8, color: "rgba(245, 158, 11, 0.06)" },
                                { offset: 1, color: "rgba(245, 158, 11, 0.00)" },
                            ],
                        },
                    },
                },
            ],
        };
    }, [validPoints, timezone]);

    if (validPoints.length === 0 || !option) {
        return (
            <div className="h-96 w-full flex items-center justify-center text-gray-400 text-xs bg-slate-50/50 rounded-2xl border border-slate-100">
                Keine Prognosedaten verfügbar
            </div>
        );
    }

    return (
        <ReactECharts
            option={option}
            style={{
                height: "380px",
                width: "100%",
            }}
            notMerge={true}
            lazyUpdate={true}
        />
    );
}