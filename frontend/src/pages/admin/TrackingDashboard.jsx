/*
#
*/

import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import { apiFetch } from "../../api/client";

function formatStats(stats) {
    const map = {};
    stats.forEach((s) => {
        map[s.event] = s.count;
    });
    return map;
}

export default function TrackingDashboard() {
    const { data, isLoading } = useQuery({
        queryKey: ["tracking"],
        queryFn: () => apiFetch("/api/tracking/stats/"),
    });

    const stats = data?.stats || [];

    const map = formatStats(stats);

    const funnel = [
        "landing_view",
        "signup_click",
        "magic_link_requested",
        "email_open",
        "magic_link_click",
        "magic_login_success",
        "dashboard_open",
    ];

    const chartOption = useMemo(() => {
        const dailyList = data?.daily || [];
        if (!dailyList || dailyList.length === 0) return null;
        return {
            tooltip: {
                trigger: "axis",
                backgroundColor: "rgba(255, 255, 255, 0.95)",
                borderColor: "#e2e8f0",
                textStyle: { color: "#1e293b", fontSize: 12 },
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
                data: dailyList.map((d) => d.date),
                axisLabel: { color: "#94a3b8", fontSize: 11 },
                axisLine: { lineStyle: { color: "#cbd5e1" } },
            },
            yAxis: {
                type: "value",
                axisLabel: { color: "#94a3b8", fontSize: 11 },
                splitLine: { lineStyle: { color: "#f1f5f9", type: "dashed" } },
            },
            series: [
                {
                    name: "Events",
                    type: "line",
                    smooth: true,
                    showSymbol: true,
                    symbolSize: 6,
                    itemStyle: { color: "#6366f1" },
                    lineStyle: { width: 2.5, color: "#6366f1" },
                    areaStyle: {
                        color: {
                            type: "linear",
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [
                                { offset: 0, color: "rgba(99, 102, 241, 0.35)" },
                                { offset: 1, color: "rgba(99, 102, 241, 0.0)" },
                            ],
                        },
                    },
                    data: dailyList.map((d) => d.count),
                },
            ],
        };
    }, [data]);

    if (isLoading) {
        return <div className="p-6">Loading…</div>;
    }

    return (
        <div className="p-6 space-y-8">

            {/* ✅ HEADER */}
            <h1 className="text-2xl font-semibold">Analytics</h1>

            {/* ✅ FUNNEL */}
            <div className="bg-white p-6 rounded-2xl shadow">
                <h2 className="text-lg font-medium mb-4">Conversion Funnel</h2>

                {funnel.map((step, i) => {
                    const value = map[step] || 0;
                    const prev = i === 0 ? value : (map[funnel[i - 1]] || 1);
                    const percent = i === 0 ? 100 : Math.round((value / prev) * 100);

                    return (
                        <div key={step} className="mb-4">
                            <div className="flex justify-between text-sm mb-1">
                                <span>{step}</span>
                                <span>{value} ({percent}%)</span>
                            </div>

                            <div className="h-3 bg-gray-100 rounded">
                                <div
                                    className="h-3 bg-indigo-500 rounded"
                                    style={{ width: `${percent}%` }}
                                />
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* ✅ CHART */}
            <div className="bg-white p-6 rounded-2xl shadow">
                <h2 className="text-lg font-medium mb-4">Events (Last 7 Days)</h2>

                <div style={{ width: "100%", height: 300 }}>
                    {chartOption ? (
                        <ReactECharts
                            option={chartOption}
                            style={{ height: "100%", width: "100%" }}
                            notMerge={true}
                            lazyUpdate={true}
                        />
                    ) : (
                        <div className="h-full flex items-center justify-center text-gray-400 text-xs">
                            Keine Daten für die letzten 7 Tage
                        </div>
                    )}
                </div>
            </div>

            {/* ✅ TOP EVENTS */}
            <div className="bg-white p-6 rounded-2xl shadow">
                <h2 className="text-lg font-medium mb-4">Top Events</h2>

                {stats
                    .sort((a, b) => b.count - a.count)
                    .slice(0, 10)
                    .map((item) => (
                        <div
                            key={item.event}
                            className="flex justify-between py-1 text-sm"
                        >
                            <span>{item.event}</span>
                            <span>{item.count}</span>
                        </div>
                    ))}
            </div>

        </div>
    );
}
