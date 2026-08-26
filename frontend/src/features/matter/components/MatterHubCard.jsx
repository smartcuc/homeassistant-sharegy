import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";
import MatterPairingModal from "./MatterPairingModal";

export default function MatterHubCard() {
    const { t } = useTranslation();
    const [statusData, setStatusData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isPairingOpen, setIsPairingOpen] = useState(false);
    const [actionLoading, setActionLoading] = useState(null);
    const [feedbackMsg, setFeedbackMsg] = useState(null);

    const loadStatus = async () => {
        try {
            const res = await apiFetch("/api/matter/status/");
            if (res && !res.error) {
                setStatusData(res);
            }
        } catch (err) {
            console.error("Error loading Matter status:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        let isMounted = true;
        const fetchStatus = async () => {
            try {
                const res = await apiFetch("/api/matter/status/");
                if (isMounted && res && !res.error) {
                    setStatusData(res);
                }
            } catch (err) {
                console.error("Error loading Matter status:", err);
            } finally {
                if (isMounted) {
                    setLoading(false);
                }
            }
        };

        fetchStatus();
        const interval = setInterval(fetchStatus, 8000);
        return () => {
            isMounted = false;
            clearInterval(interval);
        };
    }, []);

    const handleToggleNode = async (nodeId) => {
        setActionLoading(`toggle_${nodeId}`);
        try {
            await apiFetch(`/api/matter/nodes/${nodeId}/command/`, {
                method: "POST",
                body: JSON.stringify({ command: "toggle" }),
            });
            await loadStatus();
        } catch (err) {
            console.error("Command error:", err);
        } finally {
            setActionLoading(null);
        }
    };

    const handleDeleteNode = async (nodeId, nodeName) => {
        if (!window.confirm(t("matter.confirm_unpair", { name: nodeName, defaultValue: `Möchtest du das Matter-Gerät "${nodeName}" wirklich entkoppeln?` }))) {
            return;
        }
        setActionLoading(`del_${nodeId}`);
        try {
            await apiFetch(`/api/matter/nodes/${nodeId}/`, {
                method: "DELETE",
            });
            await loadStatus();
            setFeedbackMsg(t("matter.unpair_success", { name: nodeName, defaultValue: `Gerät "${nodeName}" erfolgreich entkoppelt.` }));
            setTimeout(() => setFeedbackMsg(null), 4000);
        } catch (err) {
            console.error("Delete error:", err);
        } finally {
            setActionLoading(null);
        }
    };

    const handleSimulate = async () => {
        setActionLoading("simulate");
        try {
            const res = await apiFetch("/api/matter/simulate/", { method: "POST" });
            if (res) {
                setFeedbackMsg(t("matter.simulate_success", { count: res.updated_nodes || 0, defaultValue: `Telemetrie für ${res.updated_nodes || 0} Matter-Geräte aktualisiert!` }));
                setTimeout(() => setFeedbackMsg(null), 3000);
                await loadStatus();
            }
        } catch (err) {
            console.error("Simulate error:", err);
        } finally {
            setActionLoading(null);
        }
    };

    const getDeviceIcon = (deviceType) => {
        switch (deviceType) {
            case "evse": return "🚗";
            case "solar_inverter": return "☀️";
            case "battery": return "🔋";
            case "heatpump": return "♨️";
            case "meter": return "⚡";
            default: return "🔌";
        }
    };

    return (
        <div className="bg-white rounded-2xl border border-gray-200/80 shadow-sm overflow-hidden">
            {/* Header Banner */}
            <div className="p-6 bg-gradient-to-r from-emerald-500/10 via-teal-500/5 to-transparent border-b border-gray-100 flex flex-wrap items-center justify-between gap-4">
                <div className="flex items-center gap-3.5">
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-600 to-teal-700 text-white flex items-center justify-center text-2xl shadow-lg shadow-emerald-500/20">
                        ⚡
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h2 className="text-lg font-bold text-gray-900">Matter 1.3 Energy Hub</h2>
                            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-emerald-100 text-emerald-800 border border-emerald-200">
                                {t("matter.certified_badge", "CSA Matter 1.3 Certified")}
                            </span>
                        </div>
                        <p className="text-xs text-gray-500 mt-0.5">
                            {t("matter.hub_subtitle", "Direkte Anbindung von Smart Plugs, EVSE-Wallboxen und Wechselrichtern via Matter-over-Thread / Wi-Fi & Cluster 0x0090/0x0091.")}
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={handleSimulate}
                        disabled={actionLoading === "simulate" || !statusData?.nodes_count}
                        className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-semibold rounded-xl transition-all disabled:opacity-40 flex items-center gap-1.5"
                        title={t("matter.live_test_title", "Simuliert Live-Leistungsmessung für alle gekoppelten Geräte")}
                    >
                        {actionLoading === "simulate" ? t("common.updating", "Aktualisiere...") : t("matter.live_test", "🔄 Live-Test")}
                    </button>
                    <button
                        onClick={() => setIsPairingOpen(true)}
                        className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-md shadow-emerald-600/20 flex items-center gap-1.5 transition-all"
                    >
                        <span>+</span> {t("matter.pair_device", "Neues Matter-Gerät koppeln")}
                    </button>
                </div>
            </div>

            {/* Hub Info Bar */}
            <div className="px-6 py-3 bg-gray-50/70 border-b border-gray-100 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
                <div>
                    <span className="text-gray-400 block text-[10px] uppercase font-semibold">{t("matter.fabric_id", "Fabric-ID")}</span>
                    <span className="font-mono font-medium text-gray-800">{statusData?.fabric_id || "-"}</span>
                </div>
                <div>
                    <span className="text-gray-400 block text-[10px] uppercase font-semibold">{t("matter.controller_node", "Controller Node")}</span>
                    <span className="font-mono font-medium text-gray-800">Node #{statusData?.controller_node_id || 1}</span>
                </div>
                <div>
                    <span className="text-gray-400 block text-[10px] uppercase font-semibold">{t("matter.paired_devices", "Gekoppelte Geräte")}</span>
                    <span className="font-bold text-gray-800">{t("matter.devices_count", { count: statusData?.nodes_count || 0, defaultValue: `${statusData?.nodes_count || 0} Geräte` })}</span>
                </div>
                <div>
                    <span className="text-gray-400 block text-[10px] uppercase font-semibold">{t("matter.standard_clusters", "Standard-Cluster")}</span>
                    <span className="text-emerald-700 font-semibold">0x0090 (Power), 0x0091 (Energy)</span>
                </div>
            </div>

            {/* Feedback Message */}
            {feedbackMsg && (
                <div className="mx-6 mt-4 p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl flex items-center gap-2 animate-fade-in">
                    <span>✅</span> {feedbackMsg}
                </div>
            )}

            {/* Device List */}
            <div className="p-6">
                {loading ? (
                    <div className="py-8 text-center text-xs text-gray-400 flex items-center justify-center gap-2">
                        <span className="w-4 h-4 border-2 border-emerald-500/30 border-t-emerald-600 rounded-full animate-spin"></span>
                        {t("common.loading", "Lade Matter-Geräte...")}
                    </div>
                ) : !statusData?.nodes || statusData.nodes.length === 0 ? (
                    <div className="py-10 text-center border-2 border-dashed border-gray-200 rounded-2xl bg-gray-50/50">
                        <div className="text-3xl mb-2">⚡</div>
                        <h3 className="text-sm font-bold text-gray-700 mb-1">{t("matter.no_devices_title", "Noch keine Matter-Geräte gekoppelt")}</h3>
                        <p className="text-xs text-gray-400 max-w-sm mx-auto mb-4">
                            {t("matter.no_devices_desc", "Kopple moderne Matter 1.3 Smart Plugs (z. B. Eve Energy, Shelly Matter) oder Wallboxen per QR-Code oder 11-stelligem Pairing-Code.")}
                        </p>
                        <button
                            onClick={() => setIsPairingOpen(true)}
                            className="px-4 py-2 bg-emerald-600 text-white text-xs font-semibold rounded-xl hover:bg-emerald-700 transition-all"
                        >
                            {t("matter.pair_first_device", "Jetzt erstes Gerät koppeln")}
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {statusData.nodes.map((node) => {
                            const isOn = node.attributes?.on_off !== false;
                            const powerW = node.attributes?.active_power_w ?? 0;
                            const energyKwh = node.attributes?.energy_kwh ?? 0;

                            return (
                                <div
                                    key={node.id}
                                    className="p-4 rounded-2xl border border-gray-200 hover:border-emerald-300 bg-white hover:shadow-md transition-all flex flex-col justify-between"
                                >
                                    <div>
                                        <div className="flex items-start justify-between gap-3 mb-2.5">
                                            <div className="flex items-center gap-3">
                                                <div className="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center text-xl">
                                                    {getDeviceIcon(node.device_type)}
                                                </div>
                                                <div>
                                                    <h4 className="text-sm font-bold text-gray-900 flex items-center gap-2">
                                                        {node.name}
                                                        <span className="w-2 h-2 rounded-full bg-emerald-500" title="Online (Matter-over-IP)"></span>
                                                    </h4>
                                                    <p className="text-[11px] text-gray-400 font-mono">
                                                        Node #{node.node_id} • IP: {node.ip_address || "Auto"}
                                                    </p>
                                                </div>
                                            </div>

                                            {/* On/Off Switch Button */}
                                            <button
                                                onClick={() => handleToggleNode(node.node_id)}
                                                disabled={actionLoading === `toggle_${node.node_id}`}
                                                className={`px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all shadow-sm ${isOn
                                                    ? "bg-emerald-600 text-white hover:bg-emerald-700 shadow-emerald-600/20"
                                                    : "bg-gray-100 text-gray-400 hover:bg-gray-200"
                                                    }`}
                                            >
                                                {actionLoading === `toggle_${node.node_id}` ? (
                                                    <span className="w-3 h-3 border border-current border-t-transparent rounded-full animate-spin"></span>
                                                ) : isOn ? (
                                                    <>{t("matter.status_on", "🟢 EIN")}</>
                                                ) : (
                                                    <>{t("matter.status_off", "⚪ AUS")}</>
                                                )}
                                            </button>
                                        </div>

                                        {/* Live Metrics Grid */}
                                        <div className="grid grid-cols-2 gap-2 my-3 p-2.5 bg-gray-50 rounded-xl border border-gray-100 text-xs">
                                            <div>
                                                <span className="text-gray-400 block text-[10px]">{t("matter.live_power", "Live-Leistung (0x0090)")}</span>
                                                <span className="font-bold text-gray-800 text-sm">
                                                    {powerW.toLocaleString(undefined, { maximumFractionDigits: 1 })} W
                                                </span>
                                            </div>
                                            <div>
                                                <span className="text-gray-400 block text-[10px]">{t("matter.meter_reading", "Zählerstand (0x0091)")}</span>
                                                <span className="font-semibold text-gray-700 text-sm">
                                                    {energyKwh.toLocaleString(undefined, { maximumFractionDigits: 2 })} kWh
                                                </span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Footer Actions */}
                                    <div className="pt-2.5 border-t border-gray-100 flex items-center justify-between text-[11px] text-gray-400">
                                        <span className="truncate">
                                            {t("matter.clusters_active", { count: node.clusters?.length || 0, defaultValue: `Clusters: ${node.clusters?.length || 0} aktiv` })}
                                        </span>
                                        <button
                                            onClick={() => handleDeleteNode(node.node_id, node.name)}
                                            disabled={actionLoading === `del_${node.node_id}`}
                                            className="text-red-500 hover:text-red-700 font-semibold hover:underline"
                                        >
                                            {t("matter.unpair", "Entkoppeln")}
                                        </button>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Pairing Modal */}
            <MatterPairingModal
                open={isPairingOpen}
                onClose={() => setIsPairingOpen(false)}
                onCommissioned={(newNode) => {
                    setFeedbackMsg(t("matter.pair_success", { name: newNode.name, defaultValue: `Matter-Gerät "${newNode.name}" erfolgreich gekoppelt!` }));
                    setTimeout(() => setFeedbackMsg(null), 5000);
                    loadStatus();
                }}
            />
        </div>
    );
}

