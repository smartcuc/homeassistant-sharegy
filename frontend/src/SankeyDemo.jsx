/*
# SankeyDemo.jsx
*/

import { useMemo } from "react";
import ReactECharts from "echarts-for-react";

export default function SankeyDemo({ theme }) {
    const chartOption = useMemo(() => {
        return {
            tooltip: {
                trigger: "item",
                triggerOn: "mousemove",
                formatter: "{b}: {c} kW",
            },
            series: [
                {
                    type: "sankey",
                    layout: "none",
                    emphasis: {
                        focus: "adjacency",
                    },
                    nodeAlign: "justify",
                    nodeGap: 24,
                    nodeWidth: 20,
                    data: [
                        { name: "Solar", itemStyle: { color: "#fbbf24" } },
                        { name: "Netz", itemStyle: { color: "#60a5fa" } },
                        { name: "Haushalt", itemStyle: { color: theme?.primary || "#6366f1" } },
                        { name: "Batterie", itemStyle: { color: "#34d399" } },
                    ],
                    links: [
                        { source: "Solar", target: "Haushalt", value: 7 },
                        { source: "Solar", target: "Batterie", value: 3 },
                        { source: "Netz", target: "Haushalt", value: 4 },
                    ],
                    lineStyle: {
                        color: "gradient",
                        curveness: 0.5,
                        opacity: 0.4,
                    },
                    label: {
                        color: "#1e293b",
                        fontSize: 12,
                        fontWeight: "bold",
                    },
                },
            ],
        };
    }, [theme]);

    return (
        <div className="max-w-5xl mx-auto bg-white p-8 rounded-2xl shadow-xs border border-gray-100">
            <h3 className="text-xl font-bold mb-6 text-center text-gray-900">
                Energiefluss (Demo)
            </h3>
            <div style={{ width: "100%", height: 320 }}>
                <ReactECharts
                    option={chartOption}
                    style={{ height: "100%", width: "100%" }}
                    notMerge={true}
                    lazyUpdate={true}
                />
            </div>
        </div>
    );
}
