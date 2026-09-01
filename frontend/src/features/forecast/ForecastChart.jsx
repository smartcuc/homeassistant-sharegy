/*
# src/features/forecast/ForecastChart.jsx
*/

import { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import { formatHour, formatNumber, formatDateTime, } from "../../utils/format";
import { useTimezone } from "../../hooks/useTimezone";

export default function ForecastChart({ points = [] }) {
    const FORECAST_COLOR = "#f59e0b";
    const timezone = useTimezone();

    const validPoints = Array.isArray(points) ? points : [];

    const option = useMemo(() => {
        if (validPoints.length === 0) return null;

        const xAxisData = validPoints.map(
            p => formatHour(
                p.t * 1000,
                timezone
            )
        );

        const seriesData = validPoints.map(
            p => Number(p.v)
        );

        return {
            tooltip: {
                trigger: "axis",

                formatter: function (params) {
                    const p = params?.[0];
                    if (!p) return "";

                    const point =
                        validPoints[p.dataIndex];

                    if (!point) {
                        return "";
                    }

                    return `
                        <b>
                            ${formatDateTime(
                        point.t * 1000,
                        timezone
                    )}
                        </b>
                        <br/>
                        ☀️ Forecast:
                        <b>
                            ${formatNumber(
                        p.value,
                        3
                    )} kWh
                        </b>
                    `;
                },
            },
            grid: {
                top: 20,
                left: 80,
                right: 20,
                bottom: 50,
            },

            xAxis: {
                type: "category",
                data: xAxisData,
                boundaryGap: false,
            },

            yAxis: {
                type: "value",

                axisLabel: {
                    formatter: value =>
                        `${formatNumber(value, 1)} kWh`,
                },
            },

            series: [
                {
                    name: "Solar Forecast",
                    type: "line",
                    smooth: true,
                    showSymbol: false,
                    data: seriesData,

                    lineStyle: {
                        width: 3,
                        color: FORECAST_COLOR,
                    },

                    areaStyle: {
                        opacity: 0.5,
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
                height: "400px",
                width: "100%",
            }}
            notMerge={true}
            lazyUpdate={true}
        />
    );
}