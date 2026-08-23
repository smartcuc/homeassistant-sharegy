/*
# src/features/energy/components/LiveEnergySankeyECharts.jsx
*/

import ReactECharts from "echarts-for-react";
import { useEffect, useRef, useMemo } from "react";

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
    const chartRef = useRef(null);

    useEffect(() => {
        return () => {
            if (currentRef) {
                const echartsInstance = currentRef.getEchartsInstance();
            }
        }
    };
}, []);

const option = useMemo(() => {
    if (!data || !Array.isArray(data.nodes) || !Array.isArray(data.links)) {
        return null;
    }

    // Links filtern (Verhindert Geister-Linien mit dem Wert 0)
    const links = data.links
        .filter((link) => (link.value || 0) > 0)
        .map((link) => ({
            source: link.source,
            target: link.target,
            value: link.value,
        }));

    if (links.length === 0) {
        return null;
    }

    const connectedNodeIds = new Set();
    links.forEach((l) => {
        connectedNodeIds.add(l.source);
        connectedNodeIds.add(l.target);
    });

    // Nur Knoten übergeben, die an einem aktiven Fluss teilnehmen
    const nodes = data.nodes
        .filter((node) => connectedNodeIds.has(node.id))
        .map((node) => ({
            name: node.id,
            itemStyle: {
                color: getNodeColor(node),
            },
            rawLabel: node.label,
            nodeType: node.type,
        }));

    return {
        animation: false,
        tooltip: {
            trigger: "item",
            formatter: (params) => {
                if (params.dataType === "edge") {
                    const srcNode = data.nodes.find((n) => n.id === params.data.source);
                    const tgtNode = data.nodes.find((n) => n.id === params.data.target);
                    const srcLabel = srcNode ? srcNode.label : params.data.source;
                    const tgtLabel = tgtNode ? tgtNode.label : params.data.target;
                    const valStr = params.data.value >= 1000
                        ? `${(params.data.value / 1000).toFixed(2)} kW`
                        : `${params.data.value.toFixed(0)} W`;
                    return `${srcLabel} → ${tgtLabel}: <b>${valStr}</b>`;
                }
                const node = data.nodes.find((n) => n.id === params.name);
                const label = node ? node.label : params.name;
                const valStr = params.value >= 1000
                    ? `${(params.value / 1000).toFixed(2)} kW`
                    : `${params.value.toFixed(0)} W`;
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
                        const node = data.nodes.find((n) => n.id === params.name);
                        const label = node ? node.label : params.name;
                        const value = params.value || 0;

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
            ref={chartRef}
            option={option}
            style={{ height: "100%", width: "100%" }}
            notMerge={true}
            lazyUpdate={true}
        />
    </div>
);
}
