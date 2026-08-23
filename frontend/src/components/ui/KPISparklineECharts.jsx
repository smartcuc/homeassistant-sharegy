/* Test mit 0-line
# src/components/ui/KPISparklineECharts.jsx
*/

import ReactECharts from "echarts-for-react";

export default function KPISparklineECharts({
    values = [],
    color = "#2563eb",
    chartType = "line",
    unit = "N/A",
}) {
    const chartValues =
        Array.isArray(values) && values.length === 1
            ? [values[0], values[0]]
            : Array.isArray(values)
                ? values
                : [];

    const option = {
        animation: false,

        grid: {
            top: 2,
            bottom: 2,
            left: 2,
            right: 2,
        },

        xAxis: {
            type: "category",
            show: false,
            data: chartValues.map((_, i) => i),
        },

        yAxis: {
            type: "value",
            show: false,
            scale: true,
        },

        series: [
            {
                data: chartValues,
                type: chartType,

                smooth: chartType === "line",

                showSymbol: false,

                lineStyle: {
                    width: 2.5,
                    color,
                },

                areaStyle:
                    chartType === "line"
                        ? {
                            opacity: 0.15,
                            color,
                        }
                        : undefined,

                itemStyle: {
                    color,
                    borderRadius: [2, 2, 0, 0],
                },

                markLine:
                    chartType === "line"
                        ? {
                            silent: true,
                            symbol: "none",

                            lineStyle: {
                                color: "#e5e7eb",
                                width: 1,
                                type: "dashed",
                            },

                            data: [
                                {
                                    yAxis: 0,
                                },
                            ],
                        }
                        : undefined,
            },
        ],

        tooltip: {
            trigger: "axis",
            backgroundColor: "rgba(255,255,255,0.96)",
            borderColor: "#e5e7eb",
            borderWidth: 1,

            textStyle: {
                color: color,
            },

            formatter: (params) => {
                const p = params?.[0];

                if (!p || p.value == null) {
                    return "Keine Daten";
                }

                return `
                    <div style="font-weight:600">
                        ${Number(p.value).toFixed(2)} ${unit}
                    </div>
                `;
            },
        },

    };

    return (
        <div className="h-14 mt-1">
            <ReactECharts
                option={option}
                style={{
                    height: "100%",
                    width: "100%",
                }}
            />
        </div>
    );
}
