/*
# src/components/device/DeviceChartModal.jsx
*/

import { useState, useEffect, useMemo, useRef, useCallback, memo } from "react";
import { useQuery } from "@tanstack/react-query";

import ReactECharts from "echarts-for-react";
import { apiFetch } from "../../api/client";
import { useTranslation } from "react-i18next";
import ExportDropdown from "../../features/energy/components/ExportDropdown";
import DateRangePickerModal from "../../features/energy/components/DateRangePickerModal";
import { useSubscription } from "../../hooks/useSubscription";
import ProBadge from "../common/ProBadge";
import ProUpgradeModal from "../common/ProUpgradeModal";

/* =========================================
   HELPERS
========================================= */

function formatTime(ts, isMultiDay = false) {
    const d = new Date(ts * 1000);
    if (isMultiDay) {
        return `${d.getDate().toString().padStart(2, '0')}.${(d.getMonth() + 1).toString().padStart(2, '0')} ${d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
    }
    return d.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });
}

function getDeviceStyle(device) {

    const config = device.config || {};

    if (config.is_grid_source) {
        return {
            color: "#10b981",
            icon: "🔌",
        };
    }

    switch (config.role?.key) {

        case "producer":
            return {
                color: "#f59e0b",
                icon: "☀️",
            };

        case "consumer":
            return {
                color: "#2563eb",
                icon: "⚡",
            };

        case "battery":
            return {
                color: "#8b5cf6",
                icon: "🔋",
            };

        default:
            return {
                color: "#64748b",
                icon: "🔧",
            };
    }
}


/* =========================================
   COMPONENT
========================================= */

function DeviceChartModal({ device, onClose }) {
    const { t } = useTranslation();
    const { isPro } = useSubscription();
    const [range, setRange] = useState("24h");
    const [customDates, setCustomDates] = useState({ startDate: null, endDate: null, label: null });
    const [isDatePickerOpen, setIsDatePickerOpen] = useState(false);
    const [proModalOpen, setProModalOpen] = useState(false);
    const [live, setLive] = useState(false);
    const [isZoomed, setIsZoomed] = useState(false);
    const [selectedMetric, setSelectedMetric] = useState(null);
    const chartRef = useRef(null);
    const deviceStyle = getDeviceStyle(device);
    const mainColor = deviceStyle.color;

    const handleRangeClick = (period) => {
        if (period === "30d" && !isPro) {
            setProModalOpen(true);
            return;
        }
        setRange(period);
        if (period !== "1h") {
            setLive(false);
        }
    };

    const handleCustomDateClick = () => {
        if (!isPro) {
            setProModalOpen(true);
            return;
        }
        setIsDatePickerOpen(true);
    };

    /* ✅ ESC schließen */
    useEffect(() => {
        function handleKey(e) {
            if (e.key === "Escape") onClose();
        }
        window.addEventListener("keydown", handleKey);
        return () => window.removeEventListener("keydown", handleKey);
    }, [onClose]);

    /* ✅ STATE FÜR ZOOM-BEREICH */
    const [zoomRange, setZoomRange] = useState({ start: 0, end: 100 });

    /* ✅ MULTI-METRIC CHANNELS ABFRAGEN */
    const metricsQuery = useQuery({
        queryKey: ["device-metrics", device.id],
        queryFn: () => apiFetch(`/api/devices/${device.id}/metrics/`),
        staleTime: 1000 * 60 * 30, // 30 Minuten
        refetchOnWindowFocus: false,
    });

    const allMetrics = metricsQuery.data?.metrics || [];
    const availableMetrics = allMetrics.filter(m => !m.key.toLowerCase().startsWith("daily_"));
    const primaryMetricKey = metricsQuery.data?.primary_metric || "power";
    const activeMetricKey = selectedMetric || primaryMetricKey;
    const activeMetricObj = availableMetrics.find(m => m.key === activeMetricKey) || availableMetrics[0];

    /* ✅ DATA FETCHING (Ruhiggestellt für Stunden/Tage; nur bei Live alle 10s) */
    const query = useQuery({
        queryKey: ["timeseries", device.id, range, activeMetricKey, customDates.startDate, customDates.endDate],
        queryFn: () => {
            let url = `/api/devices/${device.id}/timeseries/?range=${range}&metric=${encodeURIComponent(activeMetricKey)}`;
            if (range === "custom" && customDates.startDate && customDates.endDate) {
                url += `&start_date=${customDates.startDate}&end_date=${customDates.endDate}`;
            }
            return apiFetch(url);
        },
        staleTime: live ? 0 : 1000 * 60 * 15, // 15 Minuten Cache für historische Stunden/Tageswerte
        refetchInterval: live ? 10000 : false, // Nur bei aktivem Live-Modus alle 10 Sekunden
        refetchIntervalInBackground: false,
        refetchOnWindowFocus: false,
        refetchOnMount: false,
    });


    const data = query.data;
    const unit = data?.unit || activeMetricObj?.unit || device.unit || "";
    const isMultiDay = range === "5d" || range === "7d" || range === "30d" || range === "custom";

    /* ✅ DATA FORMATTING FOR ECHARTS */
    const chartData = useMemo(() => {
        let points = data?.points || [];

        // Single-point Duplizierung für glatte Linie auch bei nur 1 Messwert
        if (points.length === 1) {
            const single = points[0];
            points = [
                { t: single.t - 300, v: single.v },
                single,
            ];
        }

        const xAxisData = [];
        const seriesData = [];

        points.forEach(p => {
            xAxisData.push(formatTime(p.t, isMultiDay));
            seriesData.push(Number(p.v ?? 0));
        });

        return { xAxisData, seriesData };
    }, [data, isMultiDay]);

    /* ✅ REAKTIVE STATS (Präzise Berechnung der sichtbaren Punkte) */
    const liveStats = useMemo(() => {
        const values = chartData.seriesData;
        if (!values || values.length === 0) {
            return { min: 0, max: 0, avg: 0 };
        }

        // Berechne die echten Array-Grenzen anhand der Zoom-Prozentwerte
        const startIndex = Math.max(0, Math.floor((zoomRange.start / 100) * values.length));
        const endIndex = Math.min(values.length, Math.ceil((zoomRange.end / 100) * values.length));

        // Hole exakt den sichtbaren Ausschnitt
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


    /* ✅ ABSOLUT SICHERES ECHARTS ZOOM-EVENT */
    const handleDataZoom = useCallback(() => {
        if (!chartRef.current) return;

        // Hole die echten, aktuellen Zoom-Prozentwerte direkt aus der Chart-Instanz
        const chartInstance = chartRef.current.getEchartsInstance();
        const option = chartInstance.getOption();
        const dataZoom = option.dataZoom?.[0];

        if (dataZoom) {
            const start = dataZoom.start ?? 0;
            const end = dataZoom.end ?? 100;

            setZoomRange({ start, end });
            setIsZoomed(start > 0 || end < 100);
        }
    }, []);

    // onEvents greift sauber auf das weiter oben deklarierte handleDataZoom zu
    const onEvents = useMemo(() => ({
        datazoom: handleDataZoom,
    }), [handleDataZoom]);

    /* ✅ NATIVES RESET (Wenn der Nutzer den Zoom zurücksetzt) */
    const handleResetZoom = () => {
        if (chartRef.current) {
            const chartInstance = chartRef.current.getEchartsInstance();
            chartInstance.dispatchAction({
                type: 'dataZoom',
                start: 0,
                end: 100
            });
            setZoomRange({ start: 0, end: 100 }); // Stats zurücksetzen
            setIsZoomed(false);
        }
    };

    /* ✅ ERMITTLE DEN AKTUELLSTEN WERT AUS DER LIVE-KURVE */
    const trueLiveValue = chartData.seriesData.length > 0
        ? chartData.seriesData[chartData.seriesData.length - 1]
        : (device?.value ?? 0.0);


    /* ✅ ECHARTS OPTIONS CONFIGURATION */
    const option = useMemo(() => {
        return {
            // Schickes, reaktionsschnelles Tooltip
            tooltip: {
                trigger: 'axis',
                formatter: function (params) {
                    const p = params[0];

                    return `
                        ${p.name}<br/>
                        <span style="color:${mainColor};font-weight:bold;">
                            ${Number(p.value).toFixed(2)} ${unit}
                        </span>
                    `;
                },
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                borderColor: '#e2e8f0',
                borderWidth: 1,
                textStyle: { color: '#1e293b' }
            },
            grid: {
                top: '4%',
                left: '3%',
                right: '4%',
                bottom: '15%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                data: chartData.xAxisData,
                boundaryGap: false,
                axisLine: { lineStyle: { color: '#cbd5e1' } },
                axisLabel: { color: '#64748b' }
            },
            yAxis: {
                type: 'value',
                axisLine: { show: false },
                axisLabel: {
                    color: '#64748b',
                    // 💡 Rundet die Achsenbeschriftung auf 2 Nachkommastellen
                    formatter: (value) => `${Number(value).toFixed(2)} ${unit}`
                },
                splitLine: { lineStyle: { color: '#f1f5f9' } }
            },

            // 💡 NATIVE ZOOM ENGINE (Ersetzt die Recharts Maus-Events komplett!)
            dataZoom: [
                {
                    type: 'inside', // Erlaubt Scrollen/Pinchen direkt im Chart
                    start: 0,
                    end: 100
                },
                {
                    type: 'slider', // Der sichtbare Schieberegler unten
                    start: 0,
                    end: 100,
                    foregroundColor: '#6366f1',
                    textStyle: { color: '#64748b' },
                    borderColor: '#f1f5f9'
                }
            ],
            series: [
                {
                    name: device.display_name,
                    type: 'line',
                    data: chartData.seriesData,
                    showSymbol: false,
                    smooth: true, // Macht die Kurve elegant weich
                    lineStyle: {
                        // color: '#6366f1',
                        color: mainColor,
                        width: 2.5
                    },
                    // Hübscher Farbverlauf unter der Linie
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
                                    color: `${mainColor}33`,
                                },
                                {
                                    offset: 1,
                                    color: `${mainColor}00`,
                                },
                            ],
                        },
                    },
                    // 📈 Automatische Min/Max Punkte im Chart markieren
                    markPoint: null,

                    // 💡 2. Neues `markLine` für gepunktete Linien zur Y-Achse
                    markLine: {
                        symbol: ['none', 'none'], // Entfernt Pfeile an den Linienenden
                        silent: true,            // Maus-Events für Linien deaktivieren
                        data: [
                            {
                                type: 'max',
                                name: 'Max',
                                lineStyle: { color: '#f97316', type: 'dashed', width: 1 },
                                label: {
                                    position: 'start', // Platziert den Text direkt an der Y-Achse
                                    formatter: (params) => `Max: ${Number(params.value).toFixed(2)} ${unit}`,
                                    backgroundColor: '#fff7ed',
                                    borderColor: '#ffedd5',
                                    borderWidth: 1,
                                    // padding:,
                                    borderRadius: 4,
                                    //color: '#991b1b',
                                    color: '#c2410c',
                                    fontSize: 10
                                }
                            },
                            {
                                type: 'min',
                                name: 'Min',
                                lineStyle: { color: '#64748b', type: 'dashed', width: 1 },
                                label: {
                                    position: 'start',
                                    formatter: (params) => `Min: ${Number(params.value).toFixed(2)} ${unit}`,
                                    backgroundColor: '#f8fafc',
                                    borderColor: '#e2e8f0',
                                    borderWidth: 1,
                                    // padding:,
                                    borderRadius: 4,
                                    //color: '#155e75',
                                    color: '#334155',
                                    fontSize: 10
                                }
                            },
                            {
                                type: 'average',
                                name: 'Schnitt',
                                lineStyle: { color: '#cbd5e1', type: 'dotted', width: 1 },
                                label: {
                                    position: 'end', // Am rechten Rand des Charts platzieren
                                    formatter: (params) => `Ø: ${Number(params.value).toFixed(2)} ${unit}`,
                                    backgroundColor: '#f8fafc',
                                    borderColor: '#e2e8f0',
                                    borderWidth: 1,
                                    padding: 4,
                                    borderRadius: 4,
                                    //color: '#475569',
                                    color: '#94a3b8',
                                    fontSize: 10
                                }
                            }
                        ]

                    },
                }
            ]
        };
    }, [chartData, unit, device.display_name, mainColor]);

    return (
        <div
            className="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
            onClick={onClose}
        >
            <div
                className="bg-white rounded-2xl shadow-xl w-full max-w-5xl h-[80vh] flex flex-col overflow-hidden"
                onClick={(e) => e.stopPropagation()}
            >

                {/* HEADER */}
                <div
                    className="p-4 border-b"
                    style={{
                        background: `linear-gradient(
                            135deg,
                            ${mainColor}30,
                            ${mainColor}08
                        )`
                    }}
                >
                    <div className="flex justify-between items-center">
                        <div>
                            <div className="text-xs text-gray-500">Zeitreihe analysieren</div>
                            <h3 className="font-semibold text-lg text-gray-900">{deviceStyle.icon} {device.display_name}</h3>
                            <div className="text-xs text-gray-500">{device.identifier}</div>
                        </div>

                        <div className="flex items-center gap-2">

                            {range === "1h" && (
                                <button
                                    onClick={() => setLive(v => !v)}
                                    className={`
                                        px-3 py-1
                                        text-sm
                                        rounded-lg
                                        font-medium
                                        transition-colors
                                        flex items-center gap-2
                                        ${live
                                            ? "bg-green-500 text-white"
                                            : "bg-gray-100 text-gray-700"
                                        }
                                    `}
                                >
                                    <span
                                        className={`
                                            inline-block
                                            w-2
                                            h-2
                                            rounded-full
                                            ${live
                                                ? "bg-white animate-pulse"
                                                : "bg-gray-400"
                                            }
                `}
                                    />

                                    Live
                                </button>
                            )}

                            <div className="flex rounded-lg overflow-hidden border shadow-sm bg-white">
                                {["1h", "6h", "24h", "5d", "30d"].map(period => (
                                    <button
                                        key={period}
                                        onClick={() => handleRangeClick(period)}
                                        className={`
                                            px-3 py-1
                                            text-sm
                                            font-medium
                                            transition-colors
                                            flex items-center gap-1
                                            ${range === period
                                                ? "text-white"
                                                : "text-gray-500 hover:bg-gray-50"
                                            }
                                      `}
                                        style={
                                            range === period
                                                ? { backgroundColor: mainColor }
                                                : undefined
                                        }
                                    >
                                        <span>{period}</span>
                                        {period === "30d" && !isPro && <ProBadge size="xs" />}
                                    </button>
                                ))}

                                <button
                                    onClick={handleCustomDateClick}
                                    className={`
                                        px-3 py-1
                                        text-sm
                                        font-medium
                                        transition-colors
                                        flex items-center gap-1
                                        ${range === "custom"
                                            ? "text-white"
                                            : "text-gray-500 hover:bg-gray-50"
                                        }
                                    `}
                                    style={
                                        range === "custom"
                                            ? { backgroundColor: mainColor }
                                            : undefined
                                    }
                                    title={t("energy.custom_period_tooltip", "Frei wählbaren Zeitraum einstellen")}
                                >
                                    <span>📅</span>
                                    <span className="hidden sm:inline">
                                        {range === "custom" && customDates.label ? customDates.label : t("energy.custom_period", "Zeitraum...")}
                                    </span>
                                    {!isPro && <ProBadge size="xs" />}
                                </button>
                            </div>

                            {/* Multi-Format Export Dropdown (Task 2.11) */}
                            <ExportDropdown
                                deviceId={device.id}
                                metric={activeMetricKey}
                                period={range}
                                startDate={customDates.startDate}
                                endDate={customDates.endDate}
                            />

                            {isZoomed && (
                                <button
                                    onClick={handleResetZoom}
                                    className="
                                        px-3
                                        py-1
                                        text-sm
                                        bg-gray-100
                                        hover:bg-gray-200
                                        rounded-lg
                                        text-gray-600
                                        font-medium
                                        transition-colors
                                    "
                                >
                                    Reset
                                </button>
                            )}

                            <button
                                onClick={onClose}
                                className="
                                    text-gray-400
                                    hover:text-gray-600
                                    text-lg
                                    p-1
                                    transition-colors
                                "
                            >
                                ✕
                            </button>

                        </div>
                    </div>

                    {liveStats && (
                        <div className="mt-4 flex justify-center">
                            <div className={`grid gap-3 w-1/2 min-w-[500px] ${live ? "grid-cols-4" : "grid-cols-3"}`}>
                                {live && (
                                    <div className="bg-white/70 rounded-lg p-2">
                                        <div className="text-xs text-gray-500">
                                            {t("device_chart.stat_current", "Aktuell")}
                                        </div>
                                        <div
                                            className="font-semibold"
                                            style={{ color: mainColor }}
                                        >
                                            {Number(trueLiveValue).toFixed(2)} {unit}
                                        </div>
                                    </div>
                                )}

                                {/* MINIMUM */}
                                <div className="bg-white/70 rounded-lg p-2">
                                    <div className="text-xs text-gray-500">
                                        {t("device_chart.stat_min", "Minimum")}
                                    </div>
                                    <div className="font-semibold text-slate-600">
                                        {liveStats.min.toFixed(2)} {unit}
                                    </div>
                                </div>

                                {/* MAXIMUM */}
                                <div className="bg-white/70 rounded-lg p-2">
                                    <div className="text-xs text-gray-500">
                                        {t("device_chart.stat_max", "Maximum")}
                                    </div>
                                    <div className="font-semibold text-orange-600">
                                        {liveStats.max.toFixed(2)} {unit}
                                    </div>
                                </div>

                                {/* DURCHSCHNITT */}
                                <div className="bg-white/70 rounded-lg p-2">
                                    <div className="text-xs text-gray-500">
                                        {t("device_chart.stat_avg", "Durchschnitt")}
                                    </div>
                                    <div className="font-semibold text-gray-700">
                                        {liveStats.avg.toFixed(2)} {unit}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                </div>

                {/* MULTI-METRIC CHANNELS TAB BAR */}
                {availableMetrics.length > 1 && (
                    <div className="flex items-center gap-2 px-6 py-2.5 bg-slate-50 border-b border-slate-200 overflow-x-auto shrink-0">
                        <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mr-1 flex items-center gap-1">
                            <span>📊</span> {t("device_chart.channel_label", "Messkanal:")}
                        </span>
                        {availableMetrics.map((m) => {
                            const isActive = (m.key === activeMetricKey);
                            return (
                                <button
                                    key={m.key}
                                    onClick={() => setSelectedMetric(m.key)}
                                    className={`
                                        px-3 py-1 text-xs rounded-lg transition-all flex items-center gap-1.5 font-medium
                                        ${isActive
                                            ? "bg-white text-slate-800 border border-slate-300 shadow-sm font-semibold ring-1 ring-slate-300"
                                            : "bg-slate-100/80 text-slate-600 hover:bg-slate-200/80 border border-transparent"
                                        }
                                    `}
                                >
                                    <span>{m.icon || "📈"}</span>
                                    <span>{m.name}</span>
                                    {m.latest_value !== null && m.latest_value !== undefined && (
                                        <span className={`text-[10px] ml-0.5 font-mono ${isActive ? "text-indigo-600 font-bold" : "text-slate-400"}`}>
                                            ({Number(m.latest_value).toFixed(1)} {m.unit})
                                        </span>
                                    )}
                                </button>
                            );
                        })}
                    </div>
                )}

                {/* CHART CONTAINER */}
                <div className="flex-1 p-4 relative min-h-0 flex flex-col justify-center">
                    {query.isLoading ? (
                        <div className="flex flex-col items-center justify-center py-24 text-slate-400 gap-2">
                            <span className="text-xl animate-pulse">⏳</span>
                            <span className="text-sm">{t("common.loading", "Lade Zeitreihe...")}</span>
                        </div>
                    ) : chartData.seriesData.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-24 text-slate-400 gap-2">
                            <span className="text-2xl">📉</span>
                            <span className="text-sm font-medium">{t("device_chart.no_data", "Keine Messwerte für diesen Zeitraum vorhanden")}</span>
                        </div>
                    ) : (
                        <ReactECharts
                            ref={chartRef}
                            option={option}
                            onEvents={onEvents}
                            notMerge={true}
                            style={{ height: "400px", width: "100%" }}
                        />
                    )}
                </div>
            </div>

            {/* Date-Range-Picker Modal (Task 2.11) */}
            <DateRangePickerModal
                isOpen={isDatePickerOpen}
                onClose={() => setIsDatePickerOpen(false)}
                initialStart={customDates.startDate}
                initialEnd={customDates.endDate}
                onApply={(applied) => {
                    setRange(applied.period);
                    setCustomDates({
                        startDate: applied.startDate,
                        endDate: applied.endDate,
                        label: applied.label,
                    });
                    setLive(false);
                }}
            />

            {/* Pro Upgrade Modal */}
            <ProUpgradeModal
                open={proModalOpen}
                onClose={() => setProModalOpen(false)}
                featureName="Langzeit-Messwertanalyse (30 Tage & Custom)"
                featureDesc="Greife auf unbegrenzte historische Sensordaten, 30-Tage-Verläufe und benutzerdefinierte Auswertungszeiträume zu mit Sharegy Pro."
            />
        </div>
    );
}

export default memo(DeviceChartModal);
