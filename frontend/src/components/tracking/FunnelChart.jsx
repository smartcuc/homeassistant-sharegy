/*
# src/components/tracking/FunnelChart.jsx
*/

import { useMemo } from "react";
import ReactECharts from "echarts-for-react";

export default function TrackingFunnel({ data }) {
    const steps = Array.isArray(data?.steps) ? data.steps : [];

    const formatted = useMemo(() => {
        return steps
            .filter((s) => s && s.label)
            .map((s) => ({
                name: s.label,
                value: Number(s.count) || 0,
            }));
    }, [steps]);

    const option = useMemo(() => {
        if (formatted.length === 0) return null;

        return {
            tooltip: {
                trigger: "item",
                formatter: "{b}: {c}",
            },

            series: [
                {
                    type: "funnel",

                    left: "10%",
                    top: 10,
                    bottom: 10,
                    width: "80%",

                    sort: "descending",

                    label: {
                        show: true,
                        position: "right",
                        color: "#000",
                        formatter: "{b}: {c}",
                    },

                    itemStyle: {
                        borderColor: "#fff",
                        borderWidth: 2,
                    },

                    data: formatted,
                },
            ],
        };
    }, [formatted]);

    if (formatted.length === 0 || !option) {
        return (
            <div className="bg-white p-4 rounded-xl shadow text-xs text-gray-400">
                Keine Funnel-Schritte vorhanden
            </div>
        );
    }

    return (
        <div className="bg-white p-4 rounded-xl shadow">
            <h3 className="mb-4 font-semibold">
                Funnel
            </h3>

            <ReactECharts
                option={option}
                style={{
                    width: "400px",
                    height: "250px",
                }}
                notMerge={true}
                lazyUpdate={true}
            />
        </div>
    );
}