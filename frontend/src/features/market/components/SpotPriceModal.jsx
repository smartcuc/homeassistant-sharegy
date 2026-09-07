/*
# src/features/market/components/SpotPriceModal.jsx
*/
import { useState, useEffect, useMemo, useRef, useCallback, memo } from "react";
import { createPortal } from "react-dom";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import ReactECharts from "echarts-for-react";
import { apiFetch } from "../../../api/client";
import { useTheme } from "../../../theme/ThemeContext";

function SpotPriceModal({
    open,
    onClose,
}) {
    const { t } = useTranslation();
    const { isDark } = useTheme();
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

        const axisColor = isDark ? "#64748b" : "#94a3b8";
        const splitLineColor = isDark ? "#1e293b" : "#f1f5f9";
        const textColor = isDark ? "#94a3b8" : "#64748b";
        const tooltipBg = isDark ? "#0f172a" : "#ffffff";
        const tooltipBorder = isDark ? "#334155" : "#e2e8f0";

        return {
            tooltip: {
                trigger: "axis",
                backgroundColor: tooltipBg,
                borderColor: tooltipBorder,
                textStyle: {
                    color: isDark ? "#f1f5f9" : "#1e293b",
                },
                formatter: (params) => {
                    const endpreis = params[0];
                    const spotpreis = params[1];

                    if (!endpreis) return "";

                    return `
                        <div>
                            <div style="font-size:12px;color:${textColor};margin-bottom:6px;">
                                ${endpreis.name}
                            </div>
                            <div style="color:#ef4444;font-weight:600;">
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
                        color: axisColor,
                    },
                },
                axisLabel: {
                    color: textColor,
                    interval: (index, value) => {
                        if (range === "week" || range === "7d" || range === "5d") {
                            const [, time] = (value || "").split(" ");
                            return time === "00:00" || time === "00:00:00";
                        }
                        return index % 16 === 0;
                    },
                    formatter: (value) => {
                        const [date, time] = (value || "").split(" ");
                        if (range === "week" || range === "7d" || range === "5d") {
                            return date || value;
                        }
                        return time || value;
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
                        color: splitLineColor,
                    },
                },
                axisLabel: {
                    color: textColor,
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
                        color: "#ef4444",
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
                                    color: "rgba(239,68,68,0.22)",
                                },
                                {
                                    offset: 1,
                                    color: "rgba(239,68,68,0.00)",
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
                                    color: "#ef4444",
                                },
                                lineStyle: {
                                    color: "#ef4444",
                                    width: 2,
                                    type: "dashed",
                                },
                            }] : []),
                            ...(data?.tomorrow_label ? [{
                                xAxis: data.tomorrow_label,
                                label: {
                                    formatter: "Morgen",
                                    position: "end",
                                    color: textColor,
                                },
                                lineStyle: {
                                    color: axisColor,
                                    width: 2,
                                },
                            }] : []),
                            {
                                yAxis: liveStats.min,
                                label: {
                                    formatter: `Min ${liveStats.min.toFixed(2)} ct`,
                                    color: "#10b981",
                                },
                                lineStyle: {
                                    color: "#10b981",
                                    width: 1,
                                },
                            },
                            {
                                yAxis: liveStats.max,
                                label: {
                                    formatter: `Max ${liveStats.max.toFixed(2)} ct`,
                                    color: "#ef4444",
                                },
                                lineStyle: {
                                    color: "#ef4444",
                                    width: 1,
                                },
                            },
                            {
                                yAxis: liveStats.avg,
                                label: {
                                    formatter: `Ø ${liveStats.avg.toFixed(2)} ct`,
                                    color: textColor,
                                },
                                lineStyle: {
                                    color: axisColor,
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
                    borderColor: isDark ? "#334155" : "#e2e8f0",
                    textStyle: {
                        color: textColor,
                    },
                },
            ],
        };
    }, [data, chartData, range, liveStats, zoomRange, isDark]);

    /* ✅ SMARTE LADETIPPS & PREISSPITZEN */
    const smartRecommendations = useMemo(() => {
        const timestamps = chartData.xAxisData;
        const values = chartData.seriesData;
        if (!values || values.length < 3) return null;

        let bestAvg = Infinity;
        let bestIdx = 0;
        let peakVal = -Infinity;
        let peakIdx = 0;

        for (let i = 0; i <= values.length - 3; i++) {
            const avg3 = (values[i] + values[i + 1] + values[i + 2]) / 3;
            if (avg3 < bestAvg) {
                bestAvg = avg3;
                bestIdx = i;
            }
        }

        for (let i = 0; i < values.length; i++) {
            if (values[i] > peakVal) {
                peakVal = values[i];
                peakIdx = i;
            }
        }

        const formatTime = (ts) => {
            if (!ts) return "--:--";
            const str = String(ts);
            if (str.includes(" ") && str.includes(":")) {
                const parts = str.split(" ");
                if (range === "week" || range === "7d" || range === "5d") {
                    return `${parts[0]} ${parts[parts.length - 1].slice(0, 5)}`;
                }
                return parts[parts.length - 1].slice(0, 5);
            }
            const d = new Date(ts);
            return isNaN(d.getTime()) ? str : d.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" });
        };

        const bestStart = formatTime(timestamps[bestIdx]);
        const bestEnd = formatTime(timestamps[Math.min(timestamps.length - 1, bestIdx + 3)]);
        const peakTime = formatTime(timestamps[peakIdx]);

        return {
            bestStart,
            bestEnd,
            bestAvg: bestAvg.toFixed(1),
            peakTime,
            peakVal: peakVal.toFixed(1),
        };
    }, [chartData, range]);

    if (!open) {
        return null;
    }

    return createPortal(
        <div
            className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-950/70 backdrop-blur-xs animate-in fade-in duration-200"
            onClick={onClose}
        >
            <div
                className="bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 w-full max-w-5xl h-[88vh] max-h-[880px] flex flex-col overflow-hidden animate-in zoom-in-95 duration-200"
                onClick={(e) => e.stopPropagation()}
            >
                {/* HEADER */}
                <div
                    className="p-4 sm:p-5 border-b border-slate-200 dark:border-slate-800 shrink-0 bg-gradient-to-r from-amber-500/15 via-amber-500/5 to-transparent dark:from-amber-500/20 dark:via-amber-500/5 dark:to-transparent"
                >
                    <div className="flex flex-wrap gap-2 justify-between items-center">
                        <div>
                            <div className="text-xs font-semibold uppercase tracking-wider text-amber-600 dark:text-amber-400">
                                {t("spot_price.analyze_title", "Spotmarkt analysieren")}
                            </div>
                            <h3 className="font-bold text-lg sm:text-xl text-slate-900 dark:text-white flex items-center gap-2">
                                <span>💰</span> {t("spot_price.epex_title", "EPEX Spotpreise DE-LU")}
                            </h3>
                            <div className="text-xs text-slate-500 dark:text-slate-400">
                                {t("spot_price.data_source", "Datenquelle: Energy Charts")}
                            </div>
                        </div>

                        <div className="flex flex-wrap items-center gap-2">
                            {/* ZEITRAUM AUSWAHL */}
                            <div className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-xs border border-slate-200/80 dark:border-slate-700/80 rounded-2xl p-1 flex gap-1 shadow-2xs">
                                {[
                                    { key: "today", label: t("common.today", "Heute") },
                                    { key: "tomorrow", label: t("common.tomorrow", "Morgen") },
                                    { key: "2d", label: t("common.2d", "2 Tage") },
                                    { key: "week", label: t("common.week", "Woche") },
                                ].map(({ key, label }) => (
                                    <button
                                        key={key}
                                        type="button"
                                        onClick={() => {
                                            setRange(key);
                                            setZoomRange({ start: 0, end: 100 });
                                            setIsZoomed(false);
                                        }}
                                        className={`px-2.5 sm:px-3 py-1 text-xs rounded-xl font-bold transition cursor-pointer ${
                                            range === key
                                                ? "bg-amber-500 text-white shadow-xs"
                                                : "text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-700"
                                        }`}
                                    >
                                        {label}
                                    </button>
                                ))}
                            </div>

                            {isZoomed && (
                                <button
                                    type="button"
                                    onClick={handleResetZoom}
                                    className="px-3 py-1 text-xs bg-amber-50 dark:bg-amber-950/60 hover:bg-amber-100 dark:hover:bg-amber-900/60 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800 rounded-xl font-bold transition cursor-pointer"
                                >
                                    {t("common.reset", "Reset")}
                                </button>
                            )}

                            <button
                                type="button"
                                onClick={onClose}
                                className="w-8 h-8 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 flex items-center justify-center text-sm font-bold transition cursor-pointer shadow-2xs ml-1"
                                title="Schließen"
                            >
                                ✕
                            </button>
                        </div>
                    </div>

                    {/* STATISTIK-KACHELN */}
                    {data && (
                        <div className="mt-3.5 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2 sm:gap-3">
                            <div className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-xs border border-slate-200/80 dark:border-slate-700/80 rounded-xl p-2.5 flex flex-col justify-center shadow-2xs">
                                <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                                    {t("spot_price.spot_price", "Spotpreis")}
                                </div>
                                <div className="text-base sm:text-lg font-bold font-mono text-amber-600 dark:text-amber-400">
                                    {(data.current_spot ?? 0).toFixed(2)} ct
                                </div>
                            </div>

                            <div className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-xs border border-slate-200/80 dark:border-slate-700/80 rounded-xl p-2.5 flex flex-col justify-center shadow-2xs">
                                <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                                    {t("spot_price.effective_price", "Endpreis")}
                                </div>
                                <div className="text-base sm:text-lg font-bold font-mono text-rose-600 dark:text-rose-400">
                                    {(data.current_effective ?? 0).toFixed(2)} ct
                                </div>
                            </div>

                            <div className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-xs border border-slate-200/80 dark:border-slate-700/80 rounded-xl p-2.5 flex flex-col justify-center shadow-2xs">
                                <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                                    {t("spot_price.minimum", "Minimum")}
                                </div>
                                <div className="text-base sm:text-lg font-bold font-mono text-emerald-600 dark:text-emerald-400">
                                    {liveStats.min.toFixed(2)} ct
                                </div>
                            </div>

                            <div className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-xs border border-slate-200/80 dark:border-slate-700/80 rounded-xl p-2.5 flex flex-col justify-center shadow-2xs">
                                <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                                    {t("spot_price.maximum", "Maximum")}
                                </div>
                                <div className="text-base sm:text-lg font-bold font-mono text-rose-600 dark:text-rose-400">
                                    {liveStats.max.toFixed(2)} ct
                                </div>
                            </div>

                            <div className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-xs border border-slate-200/80 dark:border-slate-700/80 rounded-xl p-2.5 flex flex-col justify-center shadow-2xs col-span-2 sm:col-span-1">
                                <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                                    {t("spot_price.average", "Durchschnitt")}
                                </div>
                                <div className="text-base sm:text-lg font-bold font-mono text-slate-700 dark:text-slate-300">
                                    {liveStats.avg.toFixed(2)} ct
                                </div>
                            </div>
                        </div>
                    )}

                    {/* 💡 SMARTE LADEFENSTER & PREISSPITZEN EMPFEHLUNG */}
                    {smartRecommendations && (
                        <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                            <div className="bg-emerald-50/90 dark:bg-emerald-950/40 border border-emerald-200/80 dark:border-emerald-800/60 rounded-xl p-2.5 flex items-center gap-2.5">
                                <span className="text-lg shrink-0">🟢</span>
                                <div>
                                    <span className="font-bold text-emerald-800 dark:text-emerald-300">
                                        Bestes Ladefenster: {smartRecommendations.bestStart} – {smartRecommendations.bestEnd} Uhr
                                    </span>
                                    <div className="text-[11px] text-emerald-700/80 dark:text-emerald-400">
                                        Ø {smartRecommendations.bestAvg} ct/kWh · Ideal für Wallbox, Wärmepumpe & Akku
                                    </div>
                                </div>
                            </div>

                            <div className="bg-rose-50/90 dark:bg-rose-950/40 border border-rose-200/80 dark:border-rose-800/60 rounded-xl p-2.5 flex items-center gap-2.5">
                                <span className="text-lg shrink-0">🔴</span>
                                <div>
                                    <span className="font-bold text-rose-800 dark:text-rose-300">
                                        Teuerste Spitze: {smartRecommendations.peakTime} Uhr ({smartRecommendations.peakVal} ct/kWh)
                                    </span>
                                    <div className="text-[11px] text-rose-700/80 dark:text-rose-400">
                                        Netzbezug vermeiden · Speicherentladung priorisieren
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* CHART CONTAINER */}
                <div className="flex-1 p-3 sm:p-4 relative min-h-0 bg-slate-50/50 dark:bg-slate-900/50">
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
        </div>,
        document.body
    );
}

export default memo(SpotPriceModal);