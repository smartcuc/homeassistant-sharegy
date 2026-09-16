/*
# src/features/energy/components/LiveEnergySankeyECharts.jsx
*/

import ReactECharts from "echarts-for-react";
import { useMemo } from "react";
import { useTheme } from "../../../theme/ThemeContext";

function getNodeColor(node) {
    switch (node.id) {
        case "pv":
            return "#f59e0b"; // Solar: Amber
        case "battery":
            return "#10b981"; // Batterie Entladung: Emerald
        case "battery_charge":
            return "#059669"; // Batterieladung: Deep Emerald
        case "grid":
            return "#3b82f6"; // Netz Bezug: Blue
        case "grid_export":
            return "#6366f1"; // Netzeinspeisung: Indigo
        case "sum":
        case "house":
            return "#8b5cf6"; // Hauszentrale: Purple
        case "untracked":
            return "#94a3b8"; // Nicht erfasst: Slate
        default:
            switch (node.type) {
                case "floor":
                    return "#a855f7";
                case "room":
                    return "#c084fc";
                case "consumer":
                    return "#f43f5e"; // Verbraucher: Rose
                case "untracked":
                    return "#94a3b8";
                default:
                    return "#64748b";
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

        // Links filtern (Verhindert Geister-Linien mit Wert 0 und ungültige Referenzen)
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
                    borderRadius: 3,
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
                backgroundColor: isDark ? "rgba(15, 23, 42, 0.95)" : "rgba(255, 255, 255, 0.98)",
                borderColor: isDark ? "#334155" : "#e2e8f0",
                borderWidth: 1,
                padding: [8, 12],
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
                        return `<div style="font-weight:600;margin-bottom:2px;">Energiefluss</div><div>${srcLabel} ➔ ${tgtLabel}: <b style="color:${isDark ? '#38bdf8' : '#0284c7'}">${valStr}</b></div>`;
                    }
                    const node = validNodeMap.get(String(params.name));
                    const label = node ? node.label : params.name;
                    const val = Number(params.value) || 0;
                    const valStr = val >= 1000
                        ? `${(val / 1000).toFixed(2)} kW`
                        : `${val.toFixed(0)} W`;
                    return `<div><b>${label}</b>: <span style="color:${isDark ? '#38bdf8' : '#0284c7'}">${valStr}</span></div>`;
                },
            },
            series: [
                {
                    type: "sankey",
                    orient: "horizontal",
                    nodeAlign: "justify",
                    left: 30,
                    right: 110,
                    top: 20,
                    bottom: 20,
                    data: nodes,
                    links,
                    nodeWidth: 18,
                    nodeGap: 16,
                    draggable: false,
                    layoutIterations: 32,
                    emphasis: {
                        focus: "adjacency",
                        lineStyle: {
                            opacity: isDark ? 0.75 : 0.65,
                        },
                    },
                    lineStyle: {
                        color: "gradient",
                        opacity: isDark ? 0.45 : 0.35,
                        curveness: 0.5,
                    },
                    label: {
                        position: "right",
                        color: isDark ? "#f8fafc" : "#1e293b",
                        fontSize: 11,
                        lineHeight: 14,
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
        return <div className="text-slate-500 dark:text-slate-400 text-sm p-4 text-center">Keine Energiedaten vorhanden</div>;
    }

    if (data.nodes.length === 0 || data.links.length === 0) {
        return <div className="text-slate-500 dark:text-slate-400 text-sm p-4 text-center">Warten auf Live-Daten…</div>;
    }

    if (!option) {
        return <div className="text-slate-500 dark:text-slate-400 p-8 text-center text-sm">Keine aktiven Energieflüsse im Moment</div>;
    }

    return (
        <div className="w-full">
            <div className="w-full h-[340px] sm:h-[400px] lg:h-[450px]">
                <ReactECharts
                    option={option}
                    style={{ height: "100%", width: "100%" }}
                    notMerge={true}
                    lazyUpdate={false}
                />
            </div>
        </div>
    );
}

