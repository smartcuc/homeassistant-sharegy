import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";
import { useSubscription } from "../../../hooks/useSubscription";
import ProBadge from "../../../components/common/ProBadge";
import ProUpgradeModal from "../../../components/common/ProUpgradeModal";

import LivePowerBudgetHeader from "../components/LivePowerBudgetHeader";
import PriorityCascadeBar from "../components/PriorityCascadeBar";
import DispatchTimelineCard from "../components/DispatchTimelineCard";
import BWWPLoadManagementCard from "../../energy/components/BWWPLoadManagementCard";
import BatteryStorageControlCard from "../components/BatteryStorageControlCard";
import WallboxCard from "../../energy/components/WallboxCard";
import PoolPumpCard from "../components/PoolPumpCard";
import AirConditioningCard from "../components/AirConditioningCard";
import SmartApplianceCard from "../components/SmartApplianceCard";
import HeatingRodCard from "../components/HeatingRodCard";
import AddWallboxModal from "../../devices/components/AddWallboxModal";

export default function ControlPage() {
    const { t } = useTranslation();
    const { isPro } = useSubscription();
    const queryClient = useQueryClient();

    const [activeTab, setActiveTab] = useState("all");
    const [proModalOpen, setProModalOpen] = useState(false);
    const [addWallboxOpen, setAddWallboxOpen] = useState(false);
    const [actionFeedback, setActionFeedback] = useState(null);

    // 1. Hub Live-Daten laden (Budget, Verbraucher, Fahrplan, Prioritäten)
    const hubQuery = useQuery({
        queryKey: ["load-management-hub"],
        queryFn: () => apiFetch("/api/energy/load-management/hub/"),
        refetchInterval: 10000,
    });

    // 2. Prioritäten Mutation
    const priorityMutation = useMutation({
        mutationFn: (payload) =>
            apiFetch("/api/energy/load-management/hub/priorities/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["load-management-hub"] });
            showFeedback("Prioritäten-Kaskade erfolgreich aktualisiert.");
        },
    });

    // 3. Quick-Action Mutation
    const actionMutation = useMutation({
        mutationFn: (payload) =>
            apiFetch("/api/energy/load-management/hub/action/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            }),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ["load-management-hub"] });
            queryClient.invalidateQueries({ queryKey: ["bwwp-load-mgmt"] });
            queryClient.invalidateQueries({ queryKey: ["storages"] });
            queryClient.invalidateQueries({ queryKey: ["wallboxes"] });
            showFeedback(data.message || "Aktion erfolgreich ausgeführt.");
        },
    });

    const showFeedback = (msg) => {
        setActionFeedback(msg);
        setTimeout(() => setActionFeedback(null), 4000);
    };

    const hubData = hubQuery.data || {};
    const liveBudget = hubData.live_budget || {};
    const consumers = hubData.consumers || [];
    const dispatchSchedule = hubData.dispatch_schedule || [];
    const priorityOrder = hubData.priority_order || ["battery", "bwwp", "wallbox", "heatpump", "pool", "ac", "appliances", "heating_rod"];
    const masterMode = hubData.master_mode || "autopilot";

    const handlePriorityOrderChange = (newOrder) => {
        priorityMutation.mutate({
            priority_order: newOrder,
            master_mode: masterMode,
        });
    };

    const handleMasterModeChange = (newMode) => {
        priorityMutation.mutate({
            priority_order: priorityOrder,
            master_mode: newMode,
        });
    };

    const handleQuickAction = (category, action, deviceId = null, params = {}) => {
        actionMutation.mutate({
            category,
            action,
            device_id: deviceId,
            params,
        });
    };

    // Filter consumers by category tab
    const filteredConsumers = consumers.filter((c) => {
        if (activeTab === "all") return true;
        if (activeTab === "heat") return ["bwwp", "heatpump", "heating_rod"].includes(c.category);
        if (activeTab === "mobility") return c.category === "wallbox";
        if (activeTab === "storage") return c.category === "battery";
        if (activeTab === "pool") return c.category === "pool";
        if (activeTab === "ac") return c.category === "ac";
        if (activeTab === "appliances") return c.category === "appliances";
        return true;
    });

    const poolConsumers = consumers.filter((c) => c.category === "pool");
    const acConsumers = consumers.filter((c) => c.category === "ac");
    const applianceConsumers = consumers.filter((c) => c.category === "appliances");
    const heatingRodConsumers = consumers.filter((c) => c.category === "heating_rod");

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            {/* Action Feedback Banner */}
            {actionFeedback && (
                <div className="fixed bottom-6 right-6 z-50 px-4 py-3 bg-slate-900 text-white text-xs font-bold rounded-2xl shadow-2xl border border-emerald-500/40 flex items-center gap-2.5 animate-bounce">
                    <span className="text-emerald-400 text-base">✓</span>
                    <span>{actionFeedback}</span>
                </div>
            )}

            {/* PAGE HEADER */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                    <span>🎛️</span> {t("control.title", "Energiesteuerung & Lastmanagement")}
                </h1>
                <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
                    {t("control.subtitle", "Intelligente PV-Überschusssteuerung, Prioritäten-Kaskade und automatisierte Verbraucher-Fahrpläne.")}
                </p>
            </div>

            {/* 1. Live Power Budget & Master Autopilot Header */}
            <LivePowerBudgetHeader
                budget={liveBudget}
                masterMode={masterMode}
                onMasterModeChange={handleMasterModeChange}
                isSaving={priorityMutation.isPending}
            />

            {/* 2. Priority Cascade Bar (Merit-Order) */}
            <PriorityCascadeBar
                priorityOrder={priorityOrder}
                onOrderChange={handlePriorityOrderChange}
                isSaving={priorityMutation.isPending}
            />

            {/* 3. 24h Dispatch Timeline & Schedule */}
            <DispatchTimelineCard schedule={dispatchSchedule} />

            {/* 4. SECTION: STEUERBARE GROSSVERBRAUCHER & AKTOREN */}
            <div className="space-y-4 pt-2">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 dark:border-slate-800 pb-3">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-xl shadow-2xs">
                            ⚡
                        </div>
                        <div>
                            <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                <span>Steuerbare Großverbraucher & Aktoren</span>
                                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-950/50 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                                    {consumers.length} Verbraucher
                                </span>
                            </h2>
                            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                                Direktsteuerung, Betriebsmodi und Sollwerte für alle angebundenen Relais, Wallboxen und Wärmepumpen.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Filter Tabs matching Merit-Order names */}
                <div className="flex items-center gap-2 overflow-x-auto pb-1">
                    {[
                        { key: "all", label: "Alle Verbraucher", icon: "🎛️" },
                        { key: "battery", label: "Heimspeicher", icon: "🔋" },
                        { key: "bwwp", label: "BWWP (Warmwasser)", icon: "♨️" },
                        { key: "wallbox", label: "Wallbox (E-Auto)", icon: "🚗" },
                        { key: "heatpump", label: "Wärmepumpe", icon: "🔥" },
                        { key: "pool", label: "Pool & Filter", icon: "🏊" },
                        { key: "ac", label: "Klimaanlage (Pre-Cool)", icon: "❄️" },
                        { key: "appliances", label: "Haushaltsgeräte", icon: "🧺" },
                        { key: "heating_rod", label: "Heizstab (Puffer)", icon: "⚡" },
                    ].map((tab) => (
                        <button
                            key={tab.key}
                            type="button"
                            onClick={() => setActiveTab(tab.key)}
                            className={`px-3.5 py-2 rounded-2xl text-xs font-bold transition flex items-center gap-2 shrink-0 cursor-pointer ${
                                activeTab === tab.key
                                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                                    : "bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800"
                            }`}
                        >
                            <span>{tab.icon}</span>
                            <span>{tab.label}</span>
                        </button>
                    ))}
                </div>

                {/* Consumer Cards Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* ♨️ BWWP & Wärmepumpen SG-Ready Lastmanagement */}
                    {(activeTab === "all" || activeTab === "bwwp" || activeTab === "heatpump") && (
                        <BWWPLoadManagementCard />
                    )}

                    {/* 🚗 Wallbox / OCPP E-Auto Ladekarte */}
                    {(activeTab === "all" || activeTab === "wallbox") && (
                        <WallboxCard onOpenAddModal={() => setAddWallboxOpen(true)} />
                    )}

                    {/* 🔋 Heimspeicher / Battery Storage Control */}
                    {(activeTab === "all" || activeTab === "battery") && (
                        <BatteryStorageControlCard />
                    )}

                    {/* 🏊 Poolpumpen & Filteranlagen */}
                    {(activeTab === "all" || activeTab === "pool") &&
                        poolConsumers.map((c) => (
                            <PoolPumpCard
                                key={c.id}
                                consumer={c}
                                onAction={handleQuickAction}
                                isPending={actionMutation.isPending}
                            />
                        ))}

                    {/* ❄️ Klimaanlagen (Pre-Cooling) */}
                    {(activeTab === "all" || activeTab === "ac") &&
                        acConsumers.map((c) => (
                            <AirConditioningCard
                                key={c.id}
                                consumer={c}
                                onAction={handleQuickAction}
                                isPending={actionMutation.isPending}
                            />
                        ))}

                    {/* 🧺 Haushaltsgeräte / Ready-to-Start Smart Plugs */}
                    {(activeTab === "all" || activeTab === "appliances") &&
                        applianceConsumers.map((c) => (
                            <SmartApplianceCard
                                key={c.id}
                                consumer={c}
                                onAction={handleQuickAction}
                                isPending={actionMutation.isPending}
                            />
                        ))}

                    {/* ⚡ Heizstab / Power-to-Heat Puffer */}
                    {(activeTab === "all" || activeTab === "heating_rod") &&
                        heatingRodConsumers.map((c) => (
                            <HeatingRodCard
                                key={c.id}
                                consumer={c}
                                onAction={handleQuickAction}
                                isPending={actionMutation.isPending}
                            />
                        ))}
                </div>
            </div>

            {/* Add Wallbox Modal */}
            <AddWallboxModal
                open={addWallboxOpen}
                onClose={() => setAddWallboxOpen(false)}
            />

            {/* Pro Upgrade Modal */}
            <ProUpgradeModal
                open={proModalOpen}
                onClose={() => setProModalOpen(false)}
                featureName="Smart Load Management & Autopilot Hub"
                featureDesc="Automatisiere die Verteilung von Solarüberschuss und Börsenstrompreisen auf all deine flexiblen Großverbraucher."
            />
        </div>
    );
}
