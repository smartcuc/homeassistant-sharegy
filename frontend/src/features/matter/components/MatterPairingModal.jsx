import { useState } from "react";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function MatterPairingModal({ open, onClose, onCommissioned }) {
    const { t } = useTranslation();
    const [name, setName] = useState("");
    const [pairingMode, setPairingMode] = useState("qr"); // qr, manual, pin
    const [pairingCode, setPairingCode] = useState("");
    const [deviceType, setDeviceType] = useState("smart_plug");
    const [role, setRole] = useState("consumer");
    const [ipAddress, setIpAddress] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    if (!open) return null;

    const deviceTypes = [
        { id: "smart_plug", label: t("matter.type_smart_plug", "Smart Plug / Zwischenstecker"), icon: "🔌", defaultRole: "consumer" },
        { id: "evse", label: t("matter.type_evse", "Matter EVSE (Wallbox)"), icon: "🚗", defaultRole: "consumer" },
        { id: "heatpump", label: t("matter.type_heatpump", "Wärmepumpe / Heizstab"), icon: "♨️", defaultRole: "consumer" },
        { id: "solar_inverter", label: t("matter.type_inverter", "Solar-Wechselrichter / BKW"), icon: "☀️", defaultRole: "producer" },
        { id: "battery", label: t("matter.type_battery", "Batteriespeicher"), icon: "🔋", defaultRole: "battery" },
        { id: "meter", label: t("matter.type_meter", "Matter Smart Meter"), icon: "⚡", defaultRole: "grid" },
    ];

    const handleDeviceTypeChange = (typeId) => {
        setDeviceType(typeId);
        const dt = deviceTypes.find(d => d.id === typeId);
        if (dt) setRole(dt.defaultRole);
    };

    const handlePair = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        let codeToSend = pairingCode.trim();
        if (pairingMode === "qr" && !codeToSend.toUpperCase().startsWith("MT:")) {
            codeToSend = `MT:${codeToSend}`;
        }

        try {
            const res = await apiFetch("/api/matter/commission/", {
                method: "POST",
                body: JSON.stringify({
                    name: name.trim() || t("matter.default_device_name", "Neues Matter-Gerät"),
                    pairing_code: codeToSend,
                    device_type: deviceType,
                    role: role,
                    ip_address: ipAddress.trim() || undefined,
                }),
            });

            if (res && res.status === "commissioned") {
                onCommissioned?.(res);
                onClose();
            } else if (res && res.error) {
                setError(res.error);
            }
        } catch (err) {
            setError(err.message || t("matter.pairing_failed", "Kopplung mit Matter-Gerät fehlgeschlagen."));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-fade-in">
            <div className="bg-white rounded-2xl shadow-2xl border border-gray-100 max-w-lg w-full overflow-hidden flex flex-col max-h-[90vh]">

                {/* Header */}
                <div className="px-6 py-4 bg-gradient-to-r from-emerald-600 to-teal-700 text-white flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center text-xl shadow-inner">
                            ⚡
                        </div>
                        <div>
                            <h2 className="text-lg font-bold">{t("matter.modal_title", "Matter 1.3 Gerät koppeln")}</h2>
                            <p className="text-xs text-emerald-100">{t("matter.modal_subtitle", "Commissioning via Matter Fabric (Thread / Wi-Fi / IP)")}</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-white/80 hover:text-white text-2xl font-semibold leading-none"
                    >
                        &times;
                    </button>
                </div>

                {/* Body Form */}
                <form onSubmit={handlePair} className="p-6 space-y-4 overflow-y-auto">
                    {error && (
                        <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center gap-2">
                            <span>⚠️</span> {error}
                        </div>
                    )}

                    {/* Geräte-Name */}
                    <div>
                        <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
                            {t("matter.device_name_label", "Gerätename")}
                        </label>
                        <input
                            type="text"
                            required
                            placeholder={t("matter.device_name_placeholder", "z. B. Eve Energy Küche oder Easee Wallbox")}
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 focus:bg-white outline-none transition-all"
                        />
                    </div>

                    {/* Gerätetyp */}
                    <div>
                        <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
                            {t("matter.device_type_label", "Matter 1.3 Gerätetyp")}
                        </label>
                        <div className="grid grid-cols-2 gap-2">
                            {deviceTypes.map((dt) => (
                                <button
                                    key={dt.id}
                                    type="button"
                                    onClick={() => handleDeviceTypeChange(dt.id)}
                                    className={`flex items-center gap-2.5 p-2.5 rounded-xl border text-left text-xs transition-all ${deviceType === dt.id
                                        ? "border-emerald-600 bg-emerald-50 text-emerald-900 font-semibold shadow-sm"
                                        : "border-gray-200 bg-white text-gray-700 hover:bg-gray-50"
                                        }`}
                                >
                                    <span className="text-base">{dt.icon}</span>
                                    <span className="truncate">{dt.label}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Pairing Modus Tabs */}
                    <div>
                        <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
                            {t("matter.pairing_method", "Pairing-Methode")}
                        </label>
                        <div className="flex bg-gray-100 p-1 rounded-xl gap-1 text-xs">
                            <button
                                type="button"
                                onClick={() => setPairingMode("qr")}
                                className={`flex-1 py-1.5 rounded-lg font-medium transition-all ${pairingMode === "qr" ? "bg-white text-gray-900 shadow-sm" : "text-gray-500 hover:text-gray-900"
                                    }`}
                            >
                                📷 QR-Payload (MT:...)
                            </button>
                            <button
                                type="button"
                                onClick={() => setPairingMode("manual")}
                                className={`flex-1 py-1.5 rounded-lg font-medium transition-all ${pairingMode === "manual" ? "bg-white text-gray-900 shadow-sm" : "text-gray-500 hover:text-gray-900"
                                    }`}
                            >
                                🔢 11/21-stellig
                            </button>
                            <button
                                type="button"
                                onClick={() => setPairingMode("pin")}
                                className={`flex-1 py-1.5 rounded-lg font-medium transition-all ${pairingMode === "pin" ? "bg-white text-gray-900 shadow-sm" : "text-gray-500 hover:text-gray-900"
                                    }`}
                            >
                                🔑 Setup-PIN
                            </button>
                        </div>
                    </div>

                    {/* Code Eingabe */}
                    <div>
                        <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
                            {pairingMode === "qr" && t("matter.qr_payload_label", "Matter QR-Code Payload (MT:...)")}
                            {pairingMode === "manual" && t("matter.manual_code_label", "Manueller Pairing-Code (11 oder 21 Ziffern)")}
                            {pairingMode === "pin" && t("matter.setup_pin_label", "Matter Setup-PIN (8 Ziffern)")}
                        </label>
                        <input
                            type="text"
                            required
                            placeholder={
                                pairingMode === "qr"
                                    ? "MT:Y.K9042C00KA0648G00"
                                    : pairingMode === "manual"
                                        ? "34970112332"
                                        : "20202021"
                            }
                            value={pairingCode}
                            onChange={(e) => setPairingCode(e.target.value)}
                            className="w-full px-3.5 py-2.5 font-mono text-sm bg-gray-50 border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:bg-white outline-none transition-all"
                        />
                        <p className="text-[11px] text-gray-400 mt-1">
                            {pairingMode === "qr" && t("matter.qr_hint", "Steht auf dem Typenschild des Matter-Geräts oder im Beipackzettel.")}
                            {pairingMode === "manual" && t("matter.manual_hint", "Zifferncode ohne Bindestriche eingeben.")}
                            {pairingMode === "pin" && t("matter.pin_hint", "Standard Setup-Code zur Direkt-Kopplung im lokalen Netzwerk.")}
                        </p>
                    </div>

                    {/* Optional IP */}
                    <div>
                        <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
                            {t("matter.ip_label", "IP-Adresse (Optional / LAN)")}
                        </label>
                        <input
                            type="text"
                            placeholder={t("matter.ip_placeholder", "z. B. 192.168.1.145 (leer lassen für Auto-Discovery)")}
                            value={ipAddress}
                            onChange={(e) => setIpAddress(e.target.value)}
                            className="w-full px-3.5 py-2 bg-gray-50 border border-gray-300 rounded-xl text-xs focus:ring-2 focus:ring-emerald-500 focus:bg-white outline-none transition-all"
                        />
                    </div>

                    {/* Footer Buttons */}
                    <div className="pt-3 flex items-center justify-end gap-3 border-t border-gray-100">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-xs font-semibold text-gray-600 hover:text-gray-900 transition-colors"
                        >
                            {t("common.cancel", "Abbrechen")}
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-lg shadow-emerald-600/20 disabled:opacity-50 flex items-center gap-2 transition-all"
                        >
                            {loading ? (
                                <>
                                    <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                                    {t("matter.pairing_in_progress", "Kopple Gerät...")}
                                </>
                            ) : (
                                <>⚡ {t("matter.connect_device", "Gerät verbinden")}</>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

