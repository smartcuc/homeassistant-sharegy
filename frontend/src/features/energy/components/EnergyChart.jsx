/*
# src/features/energy/components/EnergyChart.jsx
*/

import { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import { useEnergy } from "../context/EnergyContext";

export default function EnergyChart() {
    const energy = useEnergy();
    const history = energy?.history;

    const chartOption = useMemo(() => {
        if (!history || !Array.isArray(history) || history.length === 0) return null;

        const timestamps = history.map((h, i) => h?.time || `${i}`);
        const values = history.map((h) => Number(h?.value ?? 0));

        return {
            tooltip: {
                trigger: "axis",
                formatter: (params) => {
                    const p = params[0];
                    return `${p.name}<br/><b>${Number(p.value).toFixed(1)} W</b>`;
                },
                backgroundColor: "rgba(255, 255, 255, 0.95)",
                borderColor: "#e2e8f0",
                textStyle: { color: "#1e293b", fontSize: 12 },
                extraCssText: "box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border-radius: 0.75rem;",
            },
            grid: {
                left: "3%",
                right: "3%",
                bottom: "5%",
                top: "10%",
                containLabel: true,
            },
            xAxis: {
                type: "category",
                data: timestamps,
                show: false,
                boundaryGap: false,
            },
            yAxis: {
                type: "value",
                axisLabel: {
                    formatter: "{value} W",
                    color: "#94a3b8",
                    fontSize: 11,
                },
                splitLine: {
                    lineStyle: {
                        color: "#f1f5f9",
                        type: "dashed",
                    },
                },
            },
            series: [
                {
                    name: "Leistung",
                    type: "line",
                    smooth: true,
                    showSymbol: false,
                    data: values,
                    itemStyle: {
                        color: "#3b82f6",
                    },
                    lineStyle: {
                        width: 2.5,
                        color: "#3b82f6",
                    },
                    areaStyle: {
                        color: {
                            type: "linear",
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [
                                { offset: 0, color: "rgba(59, 130, 246, 0.35)" },
                                { offset: 1, color: "rgba(59, 130, 246, 0.0)" },
                            ],
                        },
                    },
                },
            ],
        };
    }, [history]);

    if (!history || !Array.isArray(history)) {
        return <div>Loading chart…</div>;
    }

    if (history.length === 0) {
        return <div>No data yet</div>;
    }

    if (!chartOption) {
        return <div className="text-gray-400">Warte auf Live-Daten…</div>;
    }

    return (
        <div style={{ height: 300 }}>
            <h3 style={{ marginBottom: 10 }} className="font-bold text-gray-800">
                📈 Live Leistungs‑Verlauf
            </h3>
            <ReactECharts
                option={chartOption}
                style={{ height: "260px", width: "100%" }}
                notMerge={true}
                lazyUpdate={true}
            />
        </div>
    );
}

