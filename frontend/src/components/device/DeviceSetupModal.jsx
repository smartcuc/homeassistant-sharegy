import useModalDismiss from "../../hooks/useModalDismiss";
import { useState, useEffect, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useUnconfiguredDevices } from "../../hooks/useUnconfiguredDevices";
import { useSettings } from "../../hooks/useSettings";
import { useStructure } from "../../hooks/useStructure";
import { apiFetch } from "../../api/client";
import { useTranslation } from "react-i18next";

export default function DeviceSetupModal({
    open,
    onClose,
    onDeviceUpdated,
    mode = "bulk",
    singleDevice = null
}) {
    const { t } = useTranslation();
    useModalDismiss(open, onClose);
    const queryClient = useQueryClient();
    const isBulk = mode === "bulk";

    const query = useUnconfiguredDevices();
    const bulkDevices = query?.data?.devices || [];

    const devices = (isBulk
        ? bulkDevices
        : singleDevice ? [singleDevice] : []
    ).slice().sort((a, b) =>
        (a.display_name || "").localeCompare(b.display_name || "")
    );

    const [index, setIndex] = useState(0);

    const device = isBulk
        ? devices[index]
        : singleDevice;

    const { settings } = useSettings();
    const homes = settings?.homes || [];
    const hasMultipleHomes = homes.length > 1;

    const { data: structure } = useStructure();
    const roles = structure?.roles || [];
    const generatorTypes = structure?.generator_types || [];
    const energySignalTypes = structure?.energy_signal_types || [];

    const floors = structure?.floors || [];
    const rooms = structure?.rooms || [];

    const sortedRoles = [...roles].sort((a, b) =>
        a.label.localeCompare(b.label, "de")
    );

    const metricDefinitions =
        structure?.metric_definitions || [];

    const sortedMetricDefinitions =
        [...metricDefinitions].sort((a, b) =>
            (a.name || "").localeCompare(
                b.name || "",
                "de"
            )
        );

    const sortedGeneratorTypes =
        [...generatorTypes].sort((a, b) =>
            (a.name || "").localeCompare(
                b.name || "",
                "de"
            )
        );

    const sortedRooms = [...rooms].sort((a, b) =>
        a.name.localeCompare(b.name, "de")
    );

    const sortedFloors = [...floors].sort((a, b) =>
        a.name.localeCompare(b.name, "de")
    );

    const [localValues, setLocalValues] = useState({});
    const [saving, setSaving] = useState({});
    const [saved, setSaved] = useState({});
    const [error, setError] = useState({});
    const [serverDevices, setServerDevices] = useState({});

    const debounceTimers = useRef({});

    /* RESET */
    useEffect(() => {
        if (open) {
            setIndex(0);
            setLocalValues({});
            setSaving({});
            setSaved({});
            setError({});
            setServerDevices({});
        }
    }, [open]);

    if (!open || !device) {
        return null;
    }

    const currentValues = localValues[device.id] || {};
    const serverDevice = serverDevices[device.id] || device;

    const displayName =
        currentValues.display_name !== undefined
            ? currentValues.display_name
            : serverDevice.display_name || "";

    const roleId =
        currentValues.role_id !== undefined
            ? currentValues.role_id
            : serverDevice.config?.role?.id || "";

    const metricDefinitionId =
        currentValues.metric_definition_id !== undefined
            ? currentValues.metric_definition_id
            : serverDevice.config?.metric_definition?.id || "";

    const generatorTypeId =
        currentValues.generator_type_id !== undefined
            ? currentValues.generator_type_id
            : serverDevice.config?.generator_type?.id || "";

    const energySignalTypeId =
        currentValues.energy_signal_type_id !== undefined
            ? currentValues.energy_signal_type_id
            : serverDevice.config?.energy_signal_type?.id || "";

    const floorId =
        currentValues.floor_id !== undefined
            ? currentValues.floor_id
            : serverDevice.config?.floor?.id || "";

    const roomId =
        currentValues.room_id !== undefined
            ? currentValues.room_id
            : serverDevice.config?.room?.id || "";

    const homeId =
        currentValues.home_id !== undefined
            ? currentValues.home_id
            : serverDevice.config?.home?.id || "";

    const selectedRole = roles.find(r => Number(r.id) === Number(roleId));

    const selectedMetric = metricDefinitions.find(
        m => Number(m.id) === Number(metricDefinitionId)
    );

    const showEnergySignal =
        selectedMetric &&
        (
            selectedMetric.unit === "W" ||
            selectedMetric.unit === "kWh"
        );

    const progress = devices.length > 0 ? ((index + 1) / devices.length) * 100 : 100;
    const key = device.id;

    function handleChange(deviceId, field, value) {
        const nextDeviceValues = {
            ...(localValues[deviceId] || {}),
            [field]: value,
        };

        setLocalValues(prev => ({
            ...prev,
            [deviceId]: nextDeviceValues,
        }));

        setSaved(prev => ({
            ...prev,
            [deviceId]: false,
        }));

        if (debounceTimers.current[deviceId]) {
            clearTimeout(debounceTimers.current[deviceId]);
        }

        debounceTimers.current[deviceId] = setTimeout(() => {
            saveToServer(deviceId, nextDeviceValues);
        }, 300);
    }

    async function saveToServer(deviceId, explicitValues) {
        const values = explicitValues || localValues[deviceId];
        if (!values || Object.keys(values).length === 0) return;

        setSaving(prev => ({
            ...prev,
            [deviceId]: true,
        }));

        setError(prev => ({
            ...prev,
            [deviceId]: null,
        }));

        try {
            const res = await apiFetch(
                `/api/devices/${deviceId}/config/`,
                {
                    method: "PATCH",
                    body: JSON.stringify(values),
                }
            );

            // ✅ Entpacke response: backend liefert { status: "ok", device: { ... } }
            const updatedDevice = res?.device || res;

            setServerDevices(prev => ({
                ...prev,
                [deviceId]: updatedDevice,
            }));

            setSaved(prev => ({
                ...prev,
                [deviceId]: true,
            }));

            if (onDeviceUpdated) {
                onDeviceUpdated(updatedDevice);
            }

            queryClient.invalidateQueries({ queryKey: ["devices"] });
            queryClient.invalidateQueries({ queryKey: ["devices-status"] });
            queryClient.invalidateQueries({ queryKey: ["unconfigured-devices"] });
            queryClient.invalidateQueries({ queryKey: ["dashboard-devices"] });
            queryClient.invalidateQueries({ queryKey: ["device-metrics"] });
            queryClient.invalidateQueries({ queryKey: ["timeseries"] });
            queryClient.invalidateQueries({ queryKey: ["producers"] });
            queryClient.invalidateQueries({ queryKey: ["storages"] });
            queryClient.invalidateQueries({ queryKey: ["battery-soc-forecast"] });

            if (query?.refetch) query.refetch();
        } catch (err) {
            setError(prev => ({
                ...prev,
                [deviceId]: err.message,
            }));
        } finally {
            setSaving(prev => ({
                ...prev,
                [deviceId]: false,
            }));
        }
    }

    return (
        <div
            className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
            onClick={onClose}
        >
            <div
                className="bg-white rounded-2xl shadow-xl max-w-2xl w-full h-[80vh] flex flex-col overflow-hidden"
                onClick={(e) => e.stopPropagation()}
            >
                {/* HEADER */}
                <div className="p-4 border-b bg-gradient-to-r from-indigo-50 to-blue-50">
                    <div className="flex justify-between items-start">
                        <div>
                            <div className="text-xs text-gray-500">
                                {isBulk
                                    ? t("common.page_of", { current: index + 1, total: devices.length, defaultValue: `Gerät ${index + 1} von ${devices.length}` })
                                    : t("device_setup.title_single", "Gerät konfigurieren")}
                            </div>

                            <h2 className="text-lg font-semibold text-gray-900">
                                ⚙️ {isBulk ? t("device_setup.title_single", "Gerät einrichten") : (device.display_name || device.identifier)}
                            </h2>

                            <div className="text-sm text-gray-500">
                                {t("device_setup.signal_prompt", "Funktion, Messdaten und Position festlegen")}
                            </div>
                        </div>

                        <button
                            onClick={onClose}
                            className="text-gray-400 hover:text-gray-600 text-lg"
                        >
                            ✕
                        </button>
                    </div>

                    <div className="w-full bg-gray-200 h-2 rounded mt-4">
                        <div
                            className="bg-indigo-600 h-2 rounded transition-all"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                </div>

                {/* CONTENT */}
                <div className="flex-1 overflow-y-auto">
                    <div className="max-w-xl mx-auto p-6 space-y-4">
                        {/* NAME */}
                        <div>
                            <label className="text-xs text-gray-500 font-semibold block mb-1">
                                {t("device_add.device_name", "Name")}
                            </label>

                            <input
                                value={displayName}
                                onChange={(e) =>
                                    handleChange(
                                        device.id,
                                        "display_name",
                                        e.target.value
                                    )
                                }
                                className="border px-3 py-2 w-full rounded-xl text-sm"
                            />

                            <p className="text-xs text-gray-400 mt-1">
                                {t("common.value", "Anzeige im Dashboard")}
                            </p>
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                            {/* ROLE */}
                            <div>
                                <label className="text-xs text-gray-500 font-semibold block mb-1">
                                    {t("device_setup.role_label", "Funktion des Geräts")} *
                                </label>

                                <select
                                    value={roleId}
                                    onChange={(e) =>
                                        handleChange(
                                            device.id,
                                            "role_id",
                                            e.target.value
                                                ? Number(e.target.value)
                                                : null
                                        )
                                    }
                                    className={`border px-3 py-2 w-full rounded-xl text-sm bg-white ${!roleId ? "border-red-300 bg-red-50" : ""}`}
                                >
                                    <option value="">
                                        {t("device_setup.role_prompt", "⚡ Funktion")}
                                    </option>

                                    {sortedRoles.map(r => (
                                        <option key={r.id} value={r.id}>
                                            {t(`roles.${r.key}`, r.label)}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {/* METRIC */}
                            <div>
                                <label className="text-xs text-gray-500 font-semibold block mb-1">
                                    {t("device_setup.metric_label", "Messgröße")} *
                                </label>

                                <select
                                    value={metricDefinitionId}
                                    onChange={(e) =>
                                        handleChange(
                                            device.id,
                                            "metric_definition_id",
                                            e.target.value
                                                ? Number(e.target.value)
                                                : null
                                        )
                                    }
                                    className={`border px-3 py-2 w-full rounded-xl text-sm bg-white ${!metricDefinitionId ? "border-red-300 bg-red-50" : ""}`}
                                >
                                    <option value="">
                                        {t("device_setup.metric_prompt", "📊 Messgröße")}
                                    </option>

                                    {sortedMetricDefinitions.map(m => (
                                        <option key={m.id} value={m.id}>
                                            {t(`metric_definitions.${m.key}`, m.name)} ({m.unit})
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        {selectedRole?.key === "producer" && (
                            <div>
                                <label className="text-xs text-gray-500 font-semibold block mb-1">
                                    {t("device_setup.generator_label", "Erzeugertyp")}
                                </label>

                                <select
                                    value={generatorTypeId}
                                    onChange={(e) =>
                                        handleChange(
                                            device.id,
                                            "generator_type_id",
                                            e.target.value
                                                ? Number(e.target.value)
                                                : null
                                        )
                                    }
                                    className="border px-3 py-2 w-full rounded-xl text-sm bg-white"
                                >
                                    <option value="">
                                        {t("device_setup.generator_prompt", "☀️ Erzeugertyp")}
                                    </option>

                                    {sortedGeneratorTypes.map(type => (
                                        <option key={type.id} value={type.id}>
                                            {type.icon} {t(`generator_types.${type.key}`, type.name)}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        )}

                        {showEnergySignal && (
                            <div>
                                <label className="text-xs text-gray-500 font-semibold block mb-1">
                                    {t("device_setup.signal_label", "Energiesignal")}
                                </label>

                                <select
                                    value={energySignalTypeId}
                                    onChange={(e) =>
                                        handleChange(
                                            device.id,
                                            "energy_signal_type_id",
                                            Number(e.target.value)
                                        )
                                    }
                                    className="border px-3 py-2 w-full rounded-xl text-sm bg-white"
                                >
                                    <option value="">
                                        {t("device_setup.signal_prompt", "⚡ Energiesignal")}
                                    </option>

                                    {energySignalTypes.map(type => (
                                        <option key={type.id} value={type.id}>
                                            {t(`energy_signals.${type.key}`, type.name)}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        )}

                        {/* LOCATION */}
                        <div>
                            <label className="text-xs text-gray-500 font-semibold block mb-1">
                                {t("structure.title", "Position")}
                            </label>

                            <div className="grid grid-cols-2 gap-3 mt-2">
                                {hasMultipleHomes && (
                                    <select
                                        value={homeId}
                                        onChange={(e) =>
                                            handleChange(
                                                device.id,
                                                "home_id",
                                                e.target.value
                                                    ? Number(e.target.value)
                                                    : null
                                            )
                                        }
                                        className="border px-3 py-2 rounded-xl text-sm bg-white"
                                    >
                                        <option value="">🏠 {t("profile.home_single", "Zuhause")}</option>
                                        {homes.map(h => (
                                            <option key={h.id} value={h.id}>{h.name}</option>
                                        ))}
                                    </select>
                                )}

                                <select
                                    value={floorId}
                                    onChange={(e) =>
                                        handleChange(
                                            device.id,
                                            "floor_id",
                                            e.target.value
                                                ? Number(e.target.value)
                                                : null
                                        )
                                    }
                                    className="border px-3 py-2 rounded-xl text-sm bg-white"
                                >
                                    <option value="">🏢 {t("device_setup.floor_prompt", "Etage")}</option>
                                    {sortedFloors.map(f => (
                                        <option key={f.id} value={f.id}>{f.name}</option>
                                    ))}
                                </select>

                                <select
                                    value={roomId}
                                    onChange={(e) =>
                                        handleChange(
                                            device.id,
                                            "room_id",
                                            e.target.value
                                                ? Number(e.target.value)
                                                : null
                                        )
                                    }
                                    className="border px-3 py-2 rounded-xl text-sm bg-white"
                                >
                                    <option value="">🚪 {t("device_setup.room_prompt", "Raum")}</option>
                                    {sortedRooms.map(r => (
                                        <option key={r.id} value={r.id}>{r.name}</option>
                                    ))}
                                </select>
                            </div>
                        </div>
                    </div>
                </div>

                {/* FOOTER */}
                <div className="border-t p-4 flex justify-between items-center bg-gray-50">
                    <div className="text-xs">
                        {saving[key] && <span>⏳ {t("common.saving", "Speichern...")}</span>}
                        {saved[key] && <span className="text-green-600 font-semibold">✅ {t("device_setup.auto_saved", "Gespeichert")}</span>}
                        {error[key] && <span className="text-red-600 font-semibold">❌ {t("common.error", "Fehler")}</span>}
                    </div>

                    <div className="flex gap-2">
                        {devices.length > 1 && (
                            <button
                                onClick={() => setIndex(i => Math.max(0, i - 1))}
                                disabled={index === 0}
                                className="px-4 py-2 border rounded-xl text-sm font-medium disabled:opacity-30 hover:bg-gray-100 transition"
                            >
                                ← {t("common.back", "Zurück")}
                            </button>
                        )}

                        <button
                            onClick={() => {
                                if (devices.length <= 1 || index === devices.length - 1) {
                                    onClose();
                                } else {
                                    setIndex(i => i + 1);
                                }
                            }}
                            className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold shadow-xs transition"
                        >
                            {devices.length <= 1 || index === devices.length - 1
                                ? t("common.finish", "Fertig")
                                : `${t("common.next", "Weiter")} →`}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}