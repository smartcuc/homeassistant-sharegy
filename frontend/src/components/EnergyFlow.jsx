/*
# src/components/EnergyFlow.jsx
*/

import { useEffect, useState } from "react";
import LiveEnergyFlowSimulator from "./landing/LiveEnergyFlowSimulator";

export default function EnergyFlow({ mode = "demo", endpoint = null, data = null }) {
    const [flowData, setFlowData] = useState(null);
    const [hoverText, setHoverText] = useState(null);

    // If demo mode or no custom live endpoint is supplied, use the high-end interactive simulator
    if (mode === "demo" || (!endpoint && !data?.endpoint)) {
        return <LiveEnergyFlowSimulator />;
    }

    const activeEndpoint = endpoint || data?.endpoint;

    useEffect(() => {
        if (activeEndpoint) {
            fetch(activeEndpoint)
                .then(res => res.json())
                .then(setFlowData)
                .catch(() => setFlowData(getDemoFlow()));
        }
    }, [activeEndpoint]);

    if (!flowData) {
        return <div className="text-gray-400 text-center py-10">Lade Energiefluss...</div>;
    }

    const { nodes, flows } = flowData;

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-3xl shadow-xl p-8 max-w-3xl mx-auto text-white">
            <h2 className="text-xl font-bold text-center mb-6 flex items-center justify-center gap-2">
                <span>⚡</span>
                <span>Energie fließt live</span>
            </h2>

            <svg viewBox="0 0 500 300" className="w-full">
                {/* FLOWS */}
                {flows.map(f => (
                    <g key={f.id}>
                        {/* Hover area */}
                        <path
                            d={f.path}
                            stroke="transparent"
                            strokeWidth="20"
                            fill="none"
                            onMouseEnter={() => setHoverText(f.label)}
                            onMouseLeave={() => setHoverText(null)}
                        />

                        {/* visible line */}
                        <path
                            d={f.path}
                            stroke={f.color}
                            strokeWidth="3"
                            fill="none"
                            strokeOpacity="0.6"
                        />

                        {/* moving dots */}
                        {[0, 0.8].map((delay, i) => (
                            <circle key={i} r="5" fill={f.color}>
                                <animateMotion
                                    dur={`${f.speed}s`}
                                    begin={`${delay}s`}
                                    repeatCount="indefinite"
                                    path={f.path}
                                />
                            </circle>
                        ))}
                    </g>
                ))}

                {/* NODES */}
                {nodes.map(n => (
                    <g key={n.id} transform={`translate(${n.x}, ${n.y})`}>
                        <circle
                            r="28"
                            fill={n.type === "solar" ? "#fb923c30" : "#6366f130"}
                        />

                        <rect
                            x="-20"
                            y="-20"
                            width="40"
                            height="40"
                            rx="10"
                            fill={n.type === "solar" ? "#f97316" : "#6366f1"}
                        />

                        <text
                            textAnchor="middle"
                            y="6"
                            fontSize="18"
                            fill="white"
                        >
                            {n.icon}
                        </text>

                        <text
                            textAnchor="middle"
                            y="40"
                            fontSize="12"
                            fill="#cbd5e1"
                            fontWeight="bold"
                        >
                            {n.name}
                        </text>
                    </g>
                ))}
            </svg>

            {/* TOOLTIP */}
            {hoverText && (
                <div className="mt-4 text-center text-sm font-semibold text-emerald-400 bg-slate-950/80 border border-slate-800 py-2 px-4 rounded-xl">
                    {hoverText}
                </div>
            )}
        </div>
    );
}

/* ✅ DEMO DATA */
function getDemoFlow() {
    return {
        nodes: [
            { id: 1, name: "Solar", x: 100, y: 220, type: "solar", icon: "☀️" },
            { id: 2, name: "Haus A", x: 400, y: 200, type: "home", icon: "🏠" },
            { id: 3, name: "Haus B", x: 250, y: 80, type: "home", icon: "🏠" },
        ],
        flows: [
            {
                id: 1,
                label: "Solar → Haus A (5 kWh)",
                color: "#f97316",
                path: "M100,220 Q250,140 400,200",
                speed: 2
            },
            {
                id: 2,
                label: "Solar → Haus B (3 kWh)",
                color: "#10b981",
                path: "M100,220 Q180,150 250,80",
                speed: 3
            },
            {
                id: 3,
                label: "Haus B → Haus A (2 kWh)",
                color: "#6366f1",
                path: "M250,80 Q340,140 400,200",
                speed: 2.5
            }
        ]
    };
}