/*
# src/components/device/DeviceSetupFlow.jsx
*/

import { useState } from "react";
import { useTranslation } from "react-i18next";

export default function DeviceSetupFlow({ device, onDone }) {
    const { t } = useTranslation();
    const [type, setType] = useState(null);
    const [metrics, setMetrics] = useState([]);
    const [loading, setLoading] = useState(false);

    const typeOptions = [
        ["heatpump", t("device_setup.type_heatpump", "Wärmepumpe")],
        ["pv", t("device_setup.type_pv", "PV Anlage")],
        ["battery", t("device_setup.type_battery", "Batterie")],
        ["meter", t("device_setup.type_meter", "Zähler")],
        ["other", t("device_setup.type_other", "Sonstiges")]
    ];

    const metricOptions = [
        ["power", t("device_setup.metric_power", "Strom")],
        ["temperature", t("device_setup.metric_temperature", "Temperatur")],
        ["status", t("device_setup.metric_status", "Status")],
        ["energy", t("device_setup.metric_energy", "Energie")]
    ];

    function toggleMetric(m) {
        setMetrics((prev) =>
            prev.includes(m)
                ? prev.filter(x => x !== m)
                : [...prev, m]
        );
    }

    async function save() {
        try {
            setLoading(true);

            await fetch(`/api/devices/by-id/${device.id}/configure/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem("token")}`
                },
                body: JSON.stringify({
                    type,
                    metrics
                })
            });

            onDone();

        } catch (e) {
            alert(t("common.error_saving", "Fehler beim Speichern"));
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="p-6 max-w-md mx-auto">

            <h2 className="text-lg font-semibold mb-4">
                {t("device_setup.title", "Gerät einrichten")}
            </h2>

            {/* TYPE */}
            <div className="mb-6">
                <h3 className="text-sm text-gray-500 mb-2">
                    {t("device_setup.type_question", "Was ist das für ein Gerät?")}
                </h3>

                <div className="space-y-2">
                    {typeOptions.map(([key, label]) => (
                        <button
                            key={key}
                            onClick={() => setType(key)}
                            className={`w-full p-3 rounded border ${type === key
                                ? "bg-indigo-100 border-indigo-500"
                                : "bg-white"
                                }`}
                        >
                            {label}
                        </button>
                    ))}
                </div>
            </div>

            {/* METRICS */}
            <div className="mb-6">
                <h3 className="text-sm text-gray-500 mb-2">
                    {t("device_setup.metric_question", "Was misst das Gerät?")}
                </h3>

                <div className="space-y-2">
                    {metricOptions.map(([key, label]) => (
                        <label key={key} className="flex items-center gap-2">
                            <input
                                type="checkbox"
                                checked={metrics.includes(key)}
                                onChange={() => toggleMetric(key)}
                            />
                            {label}
                        </label>
                    ))}
                </div>
            </div>

            {/* ACTION */}
            <button
                onClick={save}
                disabled={!type || loading}
                className="w-full bg-indigo-600 text-white px-4 py-2 rounded disabled:opacity-50"
            >
                {loading ? t("common.saving", "Speichere...") : t("device_setup.submit_btn", "Gerät fertig einrichten")}
            </button>

        </div>
    );
}
