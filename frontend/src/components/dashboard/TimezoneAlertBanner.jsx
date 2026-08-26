/*
# src/components/dashboard/TimezoneAlertBanner.jsx
*/

import { useMemo } from "react";
import { useTranslation } from "react-i18next";

export default function TimezoneAlertBanner({
    timezone,
    onAccept,
    onSettings,
}) {
    const { t } = useTranslation();

    const detectedTimezone = useMemo(
        () =>
            Intl.DateTimeFormat()
                .resolvedOptions()
                .timeZone,
        []
    );

    if (timezone) {
        return null;
    }

    return (
        <div
            className="
                mb-4
                p-4
                rounded-lg
                border
                border-amber-300
                bg-amber-50
                flex
                items-center
                justify-between
            "
        >
            <div>
                <div className="text-amber-900 font-medium">
                    {t("banners.timezone_warning", "⚠️ Zeitzone nicht konfiguriert")}
                </div>

                <div className="text-sm text-amber-800 mt-1">
                    {t("banners.timezone_desc", "Für korrekte Zeitreihen, Berichte und Benachrichtigungen sollte eine Zeitzone ausgewählt werden.")}
                </div>

                <div className="text-xs text-amber-700 mt-2">
                    {t("banners.detected_timezone", "Erkannte Zeitzone:")}
                    <span className="font-semibold ml-1">
                        {detectedTimezone}
                    </span>
                </div>
            </div>

            <div className="flex gap-2">

                <button
                    onClick={() => onAccept(detectedTimezone)}
                    className="
                        px-3
                        py-1
                        rounded
                        bg-amber-500
                        text-white
                        text-sm
                        hover:bg-amber-600
                    "
                >
                    {t("banners.accept_timezone", { tz: detectedTimezone, defaultValue: `${detectedTimezone} übernehmen` })}
                </button>

                <button
                    onClick={onSettings}
                    className="
                        px-3
                        py-1
                        rounded
                        border
                        border-amber-300
                        bg-white
                        text-amber-900
                        text-sm
                        hover:bg-amber-100
                    "
                >
                    {t("banners.open_settings", "Einstellungen öffnen")}
                </button>

            </div>
        </div>
    );
}

