/*
# src/components/dashboard/UnconfiguredDevicesBanner.jsx
*/

import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useUnconfiguredDevices } from "../../hooks/useUnconfiguredDevices";

const STORAGE_KEY = "banner_unconfigured_devices_dismissed";

export default function UnconfiguredDevicesBanner({ onOpen }) {
    const { t } = useTranslation();
    const query = useUnconfiguredDevices();
    const count = query?.data?.count || 0;

    // ✅ Lazy state initialization from sessionStorage
    const [dismissed, setDismissed] = useState(() => {
        try {
            return sessionStorage.getItem(STORAGE_KEY) === "true";
        } catch {
            return false;
        }
    });

    // ✅ schließen
    function handleDismiss() {
        sessionStorage.setItem(STORAGE_KEY, "true");
        setDismissed(true);
    }

    if (!count || dismissed) return null;

    return (
        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg mb-6 relative">

            {/* ❌ Close */}
            <button
                onClick={handleDismiss}
                className="absolute top-2 right-2 text-yellow-600 hover:text-yellow-800 text-sm"
            >
                ✕
            </button>

            <div className="flex items-center justify-between pr-6">

                <div>
                    <div className="font-medium text-yellow-800">
                        {t("banners.devices_need_config", { count, defaultValue: `⚠️ ${count} Gerät${count > 1 ? "e" : ""} benötigen Konfiguration` })}
                    </div>

                    <div className="text-sm text-yellow-700 mt-1">
                        {t("banners.set_device_types_desc", "Setze Gerätetypen, damit Energy Flow korrekt berechnet werden kann.")}
                    </div>
                </div>

                <button
                    onClick={onOpen}
                    className="text-sm text-yellow-800 underline hover:text-yellow-900 whitespace-nowrap"
                >
                    {t("banners.open_devices", "Geräte öffnen →")}
                </button>

            </div>

        </div>
    );
}
