/*
# src/features/energy/components/LiveEnergySankeyECharts.jsx
*/

import ReactECharts from "echarts-for-react";
import { useMemo } from "react";

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
                    left: 120,
                    right: 60,
                    top: 20,
                    bottom: 20,
                    data: nodes,
                    links,
                    nodeWidth: 18,
                    nodeGap: 24,
                    draggable: false,
                    layoutIterations: 0,
                    emphasis: {
                        focus: "adjacency",
                    },
                    lineStyle: {
                        color: "gradient",
                        opacity: 0.35,
                        curveness: 0.5,
                    },
                    label: {
                        color: "#374151",
                        fontSize: 12,
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
    }, [data]);

    if (!data || !Array.isArray(data.nodes) || !Array.isArray(data.links)) {
        return <div className="text-gray-400">Keine Energiedaten</div>;
    }

    if (data.nodes.length === 0 || data.links.length === 0) {
        return <div className="text-gray-400">Warten auf Live-Daten…</div>;
    }

    if (!option) {
        return <div className="text-gray-400 p-8 text-center">Keine aktiven Energieflüsse im Moment</div>;
    }

    return (
        <div style={{ height: 550 }}>
            <ReactECharts
                option={option}
                style={{ height: "100%", width: "100%" }}
                notMerge={true}
                lazyUpdate={false}
            />
        </div>
    );
}
