/*
# src/features/energy/components/EnergySankey.jsx
*/

import { useMemo, useState } from "react";
import LiveEnergySankeyECharts from "./LiveEnergySankeyECharts";
import useEnergySocket from "../hooks/useEnergySocket";
import { useEnergy } from "../context/EnergyContext";

export default function EnergySankey() {
    const energy = useEnergy();
    const devices = energy?.devices;
    const updateMetric = energy?.updateMetric;

    const [grouped, setGrouped] = useState(true);

    // ✅ WebSocket immer oben (kein conditional hook!)
    useEnergySocket(updateMetric);

    // ✅ Daten vorbereiten (immer safe ausführen)
    const data = useMemo(() => {
        if (!devices || Object.keys(devices).length === 0) {
            return { nodes: [], links: [] };
        }

        const nodes = [];
        const links = [];

        const HOUSE = "house";

        if (grouped) {
            // =========================
            // ✅ GROUPED MODE
            // =========================

            let pv = 0;
            let battery = 0;
            let consumption = 0;

            Object.values(devices).forEach((d) => {
                if (!d?.power) return;

                if (d.type === "pv") pv += d.power;
                else if (d.type === "battery") battery += d.power;
                else consumption += Math.abs(d.power);
            });

            nodes.push(
                { id: "pv", label: "PV" },
                { id: "battery", label: "Batterie" },
                { id: HOUSE, label: "Haus" },
                { id: "consumer", label: "Verbraucher" }
            );

            if (pv > 0) {
                links.push({ source: "pv", target: HOUSE, value: pv });
            }

            if (battery > 0) {
                links.push({ source: "battery", target: HOUSE, value: battery });
            }

            if (consumption > 0) {
                links.push({
                    source: HOUSE,
                    target: "consumer",
                    value: consumption,
                });
            }
        } else {
            // =========================
            // ✅ DEVICE MODE
            // =========================

            nodes.push({ id: HOUSE, label: "Haus" });

            Object.entries(devices).forEach(([id, d]) => {
                if (!d?.power) return;

                const nodeId = `device_${id}`;

                nodes.push({
                    id: nodeId,
                    label: d.type || `Device ${id}`,
                });

                if (d.type === "pv") {
                    links.push({
                        source: nodeId,
                        target: HOUSE,
                        value: d.power,
                    });
                } else if (d.type === "battery" && d.power > 0) {
                    links.push({
                        source: nodeId,
                        target: HOUSE,
                        value: d.power,
                    });
                } else {
                    links.push({
                        source: HOUSE,
                        target: nodeId,
                        value: Math.abs(d.power),
                    });
                }
            });
        }

        return { nodes, links };
    }, [devices, grouped]);

    // ✅ FINAL SAFETY
    if (
        !data ||
        !Array.isArray(data.nodes) ||
        !Array.isArray(data.links) ||
        data.nodes.length === 0 ||
        data.links.length === 0
    ) {
        return <div className="text-gray-400">Warte auf Live-Daten…</div>;
    }

    return (
        <div className="space-y-4">
            {/* ✅ TOGGLE */}
            <div className="inline-flex bg-slate-100 p-1 rounded-xl border border-slate-200">
                <button
                    onClick={() => setGrouped(true)}
                    className={`px-3 py-1 rounded-lg text-xs font-semibold cursor-pointer ${grouped ? "bg-white text-indigo-700 shadow-xs font-bold" : "text-gray-600"}`}
                >
                    Gruppiert
                </button>
                <button
                    onClick={() => setGrouped(false)}
                    className={`px-3 py-1 rounded-lg text-xs font-semibold cursor-pointer ${!grouped ? "bg-white text-indigo-700 shadow-xs font-bold" : "text-gray-600"}`}
                >
                    Einzelgeräte
                </button>
            </div>

            <div style={{ height: 500 }}>
                <LiveEnergySankeyECharts data={data} />
            </div>
        </div>
    );
}
