/*
# src/features/market/components/SpotPriceModal.jsx
*/
import { useState, useEffect, useMemo, useRef, useCallback, memo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import ReactECharts from "echarts-for-react";
import { apiFetch } from "../../../api/client";

function SpotPriceModal({
    open,
    onClose,
}) {
    const { t } = useTranslation();
    const [range, setRange] = useState("2d");
    const [zoomRange, setZoomRange] = useState({ start: 0, end: 100 });
    const [isZoomed, setIsZoomed] = useState(false);
    const chartRef = useRef(null);

    /* ✅ ESC schließen */
    useEffect(() => {
        if (!open) return;
        function handleKey(e) {
            if (e.key === "Escape") onClose();
        }
        window.addEventListener("keydown", handleKey);
        return () => window.removeEventListener("keydown", handleKey);
    }, [open, onClose]);

    /* ✅ DATA FETCHING: Ruhigstellen (Kein automatischer Refresh alle X Sekunden) */
    const { data } = useQuery({
        queryKey: ["spot-price-chart", range],
        queryFn: () => apiFetch(`/api/market/chart/?range=${range}`),
        enabled: open,
        staleTime: 1000 * 60 * 30, // 30 Minuten Cache – Spotpreise ändern sich nur stündlich/täglich
        refetchInterval: false,     // Keinen periodischen Poller ausführen
        refetchOnWindowFocus: false,
        refetchOnMount: false,
    });

    /* ✅ Daten-Mapping für ECharts */
    const chartData = useMemo(() => {
        return {
            xAxisData: data?.timestamps || [],
            seriesData: data?.effective_values || [],
        };
    }, [data]);

    /* ✅ REAKTIVE STATS (Präzise Berechnung der sichtbaren Punkte) */
    const liveStats = useMemo(() => {
        const values = chartData.seriesData;
        if (!values || values.length === 0) {
            return { min: 0, max: 0, avg: 0 };
        }

        const startIndex = Math.max(0, Math.floor((zoomRange.start / 100) * values.length));
        const endIndex = Math.min(values.length, Math.ceil((zoomRange.end / 100) * values.length));

        const visibleValues = values.slice(startIndex, endIndex);

        if (visibleValues.length === 0) {
            const fallback = values[values.length - 1] || 0;
            return { min: fallback, max: fallback, avg: fallback };
        }

        const min = Math.min(...visibleValues);
        const max = Math.max(...visibleValues);
        const avg = visibleValues.reduce((a, b) => a + b, 0) / visibleValues.length;

        return { min, max, avg };
    }, [chartData, zoomRange]);

    /* ✅ ECHARTS ZOOM-EVENT */
    const handleDataZoom = useCallback((event) => {
        if (!chartRef.current) return;

        const chartInstance = chartRef.current.getEchartsInstance();
        const optionObj = chartInstance.getOption();
        const dataZoom = optionObj.dataZoom?.find(
            z => z.start !== undefined
        );

        if (dataZoom) {
            const start = dataZoom.start ?? 0;
            const end = dataZoom.end ?? 100;

            setZoomRange({ start, end });
            setIsZoomed(start > 0 || end < 100);
        }
    }, []);

    const onEvents = useMemo(() => ({
        datazoom: handleDataZoom,
    }), [handleDataZoom]);

    /* ✅ NATIVES RESET */
    const handleResetZoom = () => {
        if (chartRef.current) {
            const chartInstance = chartRef.current.getEchartsInstance();
            chartInstance.dispatchAction({
                type: 'dataZoom',
                start: 0,
                end: 100
            });
            setZoomRange({ start: 0, end: 100 });
            setIsZoomed(false);
        }
    };

    /* ✅ ECHARTS OPTION (Vollständig mit useMemo stabilisiert gegen flackernde Re-Renders) */
    const echartsOption = useMemo(() => {
        if (!data) return null;

        return {
            tooltip: {
                trigger: "axis",
                formatter: (params) => {
                    const endpreis = params[0];
                    const spotpreis = params[1];

                    if (!endpreis) return "";

                    return `
                        <div>
                            <div style="font-size:12px;color:#64748b;margin-bottom:6px;">
                                ${endpreis.name}
                            </div>
                            <div style="color:#dc2626;font-weight:600;">
                                Endpreis: ${Number(endpreis.value).toLocaleString("de-DE", {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2,
                                })} ct/kWh
                            </div>
                            ${spotpreis ? `
                                <div style="color:#f59e0b;font-weight:600;">
                                    Spotpreis: ${Number(spotpreis.value).toLocaleString("de-DE", {
                                        minimumFractionDigits: 2,
                                        maximumFractionDigits: 2,
                                    })} ct/kWh
                                </div>
                            ` : ""}
                        </div>
                    `;
                },
            },
            grid: {
                top: "8%",
                left: "4%",
                right: "10%",
                bottom: "15%",
                containLabel: true,
            },
            xAxis: {
                type: "category",
                data: chartData.xAxisData,
                boundaryGap: false,
                axisLine: {
                    lineStyle: {
                        color: "#cbd5e1",
                    },
                },
                axisLabel: {
                    color: "#64748b",
                    interval: range === "5d" ? 95 : 15,
                    formatter: (value) => {
                        const [date, time] = value.split(" ");
                        if (range === "5d") {
                            if (time === "00:00") return date;
                            return "";
                        }
                        return time;
                    },
                },
            },
            yAxis: {
                type: "value",
                axisLine: {
                    show: false,
                },
                splitLine: {
                    lineStyle: {
                        color: "#f1f5f9",
                    },
                },
                axisLabel: {
                    color: "#64748b",
                    formatter: "{value} ct",
                },
            },
            series: [
                {
                    name: "Endpreis",
                    type: "line",
                    smooth: true,
                    showSymbol: false,
                    data: data.effective_values,
                    lineStyle: {
                        color: "#dc2626",
                        width: 3,
                    },
                    areaStyle: {
                        color: {
                            type: "linear",
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [
                                {
                                    offset: 0,
                                    color: "rgba(220,38,38,0.18)",
                                },
                                {
                                    offset: 1,
                                    color: "rgba(220,38,38,0.00)",
                                },
                            ],
                        },
                    },
                    markLine: {
                        symbol: ["none", "none"],
                        silent: true,
                        data: [
                            ...(data?.now_label ? [{
                                xAxis: data.now_label,
                                label: {
                                    formatter: "Jetzt",
                                    position: "end",
                                },
                                lineStyle: {
                                    color: "#dc2626",
                                    width: 2,
                                    type: "dashed",
                                },
                            }] : []),
                            ...(data?.tomorrow_label ? [{
                                xAxis: data.tomorrow_label,
                                label: {
                                    formatter: "Morgen",
                                    position: "end",
                                },
                                lineStyle: {
                                    color: "#64748b",
                                    width: 2,
                                },
                            }] : []),
                            {
                                yAxis: liveStats.min,
                                label: {
                                    formatter: `Min ${liveStats.min.toFixed(2)} ct`,
                                },
                                lineStyle: {
                                    color: "#16a34a",
                                    width: 1,
                                },
                            },
                            {
                                yAxis: liveStats.max,
                                label: {
                                    formatter: `Max ${liveStats.max.toFixed(2)} ct`,
                                },
                                lineStyle: {
                                    color: "#dc2626",
                                    width: 1,
                                },
                            },
                            {
                                yAxis: liveStats.avg,
                                label: {
                                    formatter: `Ø ${liveStats.avg.toFixed(2)} ct`,
                                },
                                lineStyle: {
                                    color: "#64748b",
                                    width: 1,
                                    type: "dashed",
                                },
                            },
                        ],
                    },
                },
                {
                    name: "Spotpreis",
                    type: "line",
                    smooth: true,
                    showSymbol: false,
                    data: data.spot_values,
                    lineStyle: {
                        color: "#f59e0b",
                        width: 2,
                    },
                },
            ],
            dataZoom: [
                {
                    type: "inside",
                    start: zoomRange.start,
                    end: zoomRange.end,
                },
                {
                    type: "slider",
                    start: zoomRange.start,
                    end: zoomRange.end,
                    foregroundColor: "#f59e0b",
                    borderColor: "#f1f5f9",
                    textStyle: {
                        color: "#64748b",
                    },
                },
            ],
        };
    }, [data, chartData, range, liveStats, zoomRange]);

    if (!open) {
        return null;
    }

    return (
        <div
            className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 animate-in fade-in duration-200"
            onClick={onClose}
        >
            <div
                className="bg-white rounded-2xl shadow-xl w-full max-w-5xl h-[80vh] flex flex-col overflow-hidden animate-in zoom-in-95 duration-200"
                onClick={(e) => e.stopPropagation()}
            >
                {/* HEADER */}
                <div
                    className="p-4 border-b shrink-0"
                    style={{
                        background: `linear-gradient(135deg, rgba(245,158,11,.20), rgba(245,158,11,.05))`
                    }}
                >
                    <div className="flex justify-between items-center">
                        <div>
                            <div className="text-xs text-gray-500">
                                {t("spot_price.analyze_title", "Spotmarkt analysieren")}
                            </div>
                            <h3 className="font-semibold text-lg text-gray-900">
                                💰 {t("spot_price.epex_title", "EPEX Spotpreise DE-LU")}
                            </h3>
                            <div className="text-xs text-gray-500">
                                {t("spot_price.data_source", "Datenquelle: Energy Charts")}
                            </div>
                        </div>

                        <div className="flex items-center gap-2">
                            <div className="flex rounded-lg overflow-hidden border shadow-sm bg-white">
                                {[
                                    ["2d", t("spot_price.range_2d", "Heute + Morgen")],
                                    ["today", t("spot_price.range_today", "Heute")],
                                    ["tomorrow", t("spot_price.range_tomorrow", "Morgen")],
                                    ["5d", t("spot_price.range_5d", "5 Tage")],
                                ].map(([value, label]) => (
                                    <button
                                        key={value}
                                        onClick={() => setRange(value)}
                                        className={`px-3 py-1 text-xs font-semibold transition cursor-pointer ${
                                            range === value
                                                ? "bg-amber-500 text-white shadow-xs"
                                                : "text-slate-600 hover:bg-slate-50"
                                        }`}
                                    >
                                        {label}
                                    </button>
                                ))}
                            </div>

                            {isZoomed && (
                                <button
                                    onClick={handleResetZoom}
                                    className="px-3 py-1 text-sm bg-amber-50 hover:bg-amber-100 text-amber-700 border border-amber-200 rounded-lg font-medium transition-colors cursor-pointer"
                                >
                                    {t("common.reset", "Reset")}
                                </button>
                            )}

                            <button
                                onClick={onClose}
                                className="text-gray-400 hover:text-gray-600 text-lg p-1 transition-colors cursor-pointer"
                            >
                                ✕
                            </button>
                        </div>
                    </div>

                    {/* STATISTIK-KACHELN */}
                    {data && (
                        <div className="mt-4 flex justify-center">
                            <div className="grid grid-cols-5 gap-3 w-[70%] min-w-[700px]">
                                <div className="bg-white/70 rounded-lg p-3 min-h-[64px] flex flex-col justify-center shadow-sm">
                                    <div className="text-xs text-gray-500">
                                        {t("spot_price.spot_price", "Spotpreis")}
                                    </div>
                                    <div className="font-semibold text-amber-600">
                                        {(data.current_spot ?? 0).toFixed(2)} ct
                                    </div>
                                </div>

                                <div className="bg-white/70 rounded-lg p-3 min-h-[64px] flex flex-col justify-center shadow-sm">
                                    <div className="text-xs text-gray-500">
                                        {t("spot_price.effective_price", "Endpreis")}
                                    </div>
                                    <div className="font-semibold text-red-600">
                                        {(data.current_effective ?? 0).toFixed(2)} ct
                                    </div>
                                </div>

                                <div className="bg-white/70 rounded-lg p-3 min-h-[64px] flex flex-col justify-center shadow-sm">
                                    <div className="text-xs text-gray-500">{t("spot_price.minimum", "Minimum")}</div>
                                    <div className="font-semibold text-green-600">
                                        {liveStats.min.toFixed(2)} ct
                                    </div>
                                </div>

                                <div className="bg-white/70 rounded-lg p-3 min-h-[64px] flex flex-col justify-center shadow-sm">
                                    <div className="text-xs text-gray-500">{t("spot_price.maximum", "Maximum")}</div>
                                    <div className="font-semibold text-red-600">
                                        {liveStats.max.toFixed(2)} ct
                                    </div>
                                </div>

                                <div className="bg-white/70 rounded-lg p-3 min-h-[64px] flex flex-col justify-center shadow-sm">
                                    <div className="text-xs text-gray-500">{t("spot_price.average", "Durchschnitt")}</div>
                                    <div className="font-semibold text-gray-700">
                                        {liveStats.avg.toFixed(2)} ct
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* CHART CONTAINER */}
                <div className="flex-1 p-4 relative min-h-0">
                    {echartsOption && (
                        <ReactECharts
                            ref={chartRef}
                            onEvents={onEvents}
                            notMerge={true}
                            lazyUpdate={true}
                            style={{ width: "100%", height: "100%" }}
                            option={echartsOption}
                        />
                    )}
                </div>
            </div>
        </div>
    );
}

export default memo(SpotPriceModal);