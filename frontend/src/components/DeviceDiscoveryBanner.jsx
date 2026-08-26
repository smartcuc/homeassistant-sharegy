/*
# src/components/DeviceDiscoveryBanner.jsx
*/

import { useTranslation } from "react-i18next";

export default function DeviceDiscoveryBanner({ devices, onOpen }) {
    const { t } = useTranslation();
    if (!devices || !devices.unconfigured?.length) return null;

    return (
        <div className="bg-yellow-100 border border-yellow-300 p-4 rounded-xl mb-4">
            <div className="flex justify-between items-center">
                <div>
                    <strong>{t("banners.new_devices_detected", "Neue Geräte erkannt")}</strong> ({devices.unconfigured.length})
                </div>

                <button
                    onClick={onOpen}
                    className="bg-black text-white px-4 py-2 rounded-lg cursor-pointer"
                >
                    {t("banners.configure_now", "Jetzt konfigurieren")}
                </button>
            </div>
        </div>
    );
}
