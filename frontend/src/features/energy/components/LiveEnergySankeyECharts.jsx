/*
# src/features/energy/components/LiveEnergySankeyECharts.jsx
*/

import ReactECharts from "echarts-for-react";
import { useMemo } from "react";
import { useTheme } from "../../../theme/ThemeContext";

function getNodeColor(node) {
    switch (node.id) {
        case "pv":
            return "#fbbf24";
        case "battery":
        case "battery_charge":
            return "#34d399";
        case "grid":
        case "grid_export":
            return "#60a5fa";
        case "sum":
            return "#8b5cf6";
        default:
            switch (node.type) {
                case "floor":
                    return "#a855f7";
                case "room":
                    return "#c084fc";
                case "consumer":
                    return "#f472b6";
                case "untracked":
                    return "#d1d5db";
                default:
                    return "#cbd5e1";
            }
    }
}

export default function LiveEnergySankeyECharts({ data }) {
    const { isDark } = useTheme();

    const option = useMemo(() => {
        if (!data || !Array.isArray(data.nodes) || !Array.isArray(data.links)) {
            return null;
        }

        // Map aller deklarierten Knoten
        const validNodeMap = new Map();
        data.nodes.forEach((n) => {
            if (n && n.id != null) {
                validNodeMap.set(String(n.id), n);
            }
        });

        // Links filtern (Verhindert Geister-Linien mit dem Wert 0 und ungültige Referenzen)
        const links = data.links
            .filter((link) => {
                const val = Number(link?.value) || 0;
                return (
                    val > 0 &&
                    link?.source != null &&
                    link?.target != null &&
                    String(link.source) !== String(link.target)
                );
            })
            .map((link) => ({
                source: String(link.source),
                target: String(link.target),
                value: Number(link.value),
            }));

        if (links.length === 0) {
            return null;
        }

        const connectedNodeIds = new Set();
        links.forEach((l) => {
            connectedNodeIds.add(l.source);
            connectedNodeIds.add(l.target);
        });

        // Garantieren, dass für JEDEN in links vorhandenen Endpunkt auch ein Node existiert
        const nodes = Array.from(connectedNodeIds).map((nodeId) => {
            const originalNode = validNodeMap.get(nodeId) || { id: nodeId, label: nodeId };
            return {
                name: nodeId,
                itemStyle: {
                    color: getNodeColor(originalNode),
                },
                rawLabel: originalNode.label || nodeId,
                nodeType: originalNode.type,
            };
        });

        if (nodes.length === 0) {
            return null;
        }

        return {
            animation: false,
            tooltip: {
                trigger: "item",
                backgroundColor: isDark ? "rgba(15, 23, 42, 0.92)" : "rgba(255, 255, 255, 0.95)",
                borderColor: isDark ? "#334155" : "#e2e8f0",
                textStyle: {
                    color: isDark ? "#f8fafc" : "#0f172a",
                    fontSize: 12,
                },
                formatter: (params) => {
                    if (!params || !params.data) return "";
                    if (params.dataType === "edge") {
                        const srcNode = validNodeMap.get(String(params.data.source));
                        const tgtNode = validNodeMap.get(String(params.data.target));
                        const srcLabel = srcNode ? srcNode.label : params.data.source;
                        const tgtLabel = tgtNode ? tgtNode.label : params.data.target;
                        const val = Number(params.data.value) || 0;
                        const valStr = val >= 1000
                            ? `${(val / 1000).toFixed(2)} kW`
                            : `${val.toFixed(0)} W`;
                        return `${srcLabel} → ${tgtLabel}: <b>${valStr}</b>`;
                    }
                    const node = validNodeMap.get(String(params.name));
                    const label = node ? node.label : params.name;
                    const val = Number(params.value) || 0;
                    const valStr = val >= 1000
                        ? `${(val / 1000).toFixed(2)} kW`
                        : `${val.toFixed(0)} W`;
                    return `${label}: <b>${valStr}</b>`;
                },
            },
            series: [
                {
                    type: "sankey",
                    left: 20,
                    right: 20,
                    top: 20,
                    bottom: 20,
                    data: nodes,
                    links,
                    nodeWidth: 16,
                    nodeGap: 14,
                    draggable: false,
                    layoutIterations: 32,
                    emphasis: {
                        focus: "adjacency",
                    },
                    lineStyle: {
                        color: "gradient",
                        opacity: isDark ? 0.45 : 0.35,
                        curveness: 0.5,
                    },
                    label: {
                        color: isDark ? "#f8fafc" : "#1e293b",
                        fontSize: 11,
                        lineHeight: 15,
                        fontWeight: "600",
                        formatter: (params) => {
                            if (!params) return "";
                            const node = validNodeMap.get(String(params.name));
                            const label = node ? node.label : params.name;
                            const value = Number(params.value) || 0;

                            return value >= 1000
                                ? `${label}\n${(value / 1000).toFixed(1)} kW`
                                : `${label}\n${value.toFixed(0)} W`;
                        },
                    },
                },
            ],
        };
    }, [data, isDark]);

    if (!data || !Array.isArray(data.nodes) || !Array.isArray(data.links)) {
        return <div className="text-slate-600 dark:text-slate-300 text-sm p-4 text-center">Keine Energiedaten</div>;
    }

    if (data.nodes.length === 0 || data.links.length === 0) {
        return <div className="text-slate-600 dark:text-slate-300 text-sm p-4 text-center">Warten auf Live-Daten…</div>;
    }

    if (!option) {
        return <div className="text-slate-600 dark:text-slate-300 p-8 text-center text-sm">Keine aktiven Energieflüsse im Moment</div>;
    }

    return (
        <div className="w-full space-y-1">
            {/* Mobile / Tablet Scroll Hint (< md screens) */}
            <div className="md:hidden flex items-center justify-end gap-1.5 text-[11px] text-slate-500 dark:text-slate-400 font-medium pr-2">
                <span className="animate-pulse">↔️</span> Wischen für Vollansicht
            </div>

            <div className="w-full overflow-x-auto pb-2 -mx-2 px-2 touch-pan-x scrollbar-thin">
                <div className="min-w-[620px] md:min-w-0 h-[340px] sm:h-[400px] md:h-[460px] lg:h-[480px]">
                    <ReactECharts
                        option={option}
                        style={{ height: "100%", width: "100%" }}
                        notMerge={true}
                        lazyUpdate={false}
                    />
                </div>
            </div>
        </div>
    );
}
