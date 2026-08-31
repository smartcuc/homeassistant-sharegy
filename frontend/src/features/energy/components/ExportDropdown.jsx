/*
# src/features/energy/components/ExportDropdown.jsx
*/

import { useState, useRef, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useSubscription } from "../../../hooks/useSubscription";
import ProBadge from "../../../components/common/ProBadge";
import ProUpgradeModal from "../../../components/common/ProUpgradeModal";

export default function ExportDropdown({
    period,
    startDate,
    endDate,
    deviceId,
    metric,
    endpoint,
    className = "",
    buttonStyle,
}) {
    const { t } = useTranslation();
    const { isPro } = useSubscription();
    const [isOpen, setIsOpen] = useState(false);
    const [downloading, setDownloading] = useState(false);
    const [proModalOpen, setProModalOpen] = useState(false);
    const menuRef = useRef(null);

    useEffect(() => {
        const handleClickOutside = (e) => {
            if (menuRef.current && !menuRef.current.contains(e.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const triggerDownload = (format) => {
        // PDF und Excel sind Pro-exklusive Features
        if (!isPro && (format === "xlsx" || format === "pdf")) {
            setIsOpen(false);
            setProModalOpen(true);
            return;
        }

        setDownloading(true);
        setIsOpen(false);

        let url;
        if (endpoint) {
            url = `${endpoint}${endpoint.includes("?") ? "&" : "?"}export_format=${format}&period=${period || "24h"}&range=${period || "24h"}`;
        } else if (deviceId) {
            url = `/api/devices/${deviceId}/export/?export_format=${format}&period=${period || "24h"}&range=${period || "24h"}`;
            if (metric) url += `&metric=${encodeURIComponent(metric)}`;
        } else {
            url = `/api/energy/export/balance/?export_format=${format}&period=${period || "today"}`;
        }

        if (startDate) url += `&start_date=${startDate}`;
        if (endDate) url += `&end_date=${endDate}`;

        window.open(url, "_blank");
        setTimeout(() => setDownloading(false), 1500);
    };

    return (
        <>
            <div className={`relative inline-block text-left ${className}`} ref={menuRef}>
                <button
                    type="button"
                    onClick={() => setIsOpen(!isOpen)}
                    disabled={downloading}
                    style={buttonStyle}
                    className="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 shadow-2xs flex items-center gap-2 transition cursor-pointer disabled:opacity-50"
                >
                    <span>📥</span>
                    <span>{downloading ? t("common.downloading", "Lade...") : t("energy.export", "Exportieren")}</span>
                    <span className="text-[10px] text-slate-400">▼</span>
                </button>

                {isOpen && (
                    <div className="absolute right-0 mt-2 w-64 bg-white rounded-2xl shadow-xl border border-slate-100 py-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
                        <div className="px-3.5 py-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-400">
                            {t("energy.export_format", "Format wählen")}
                        </div>

                        <button
                            onClick={() => triggerDownload("xlsx")}
                            className="w-full text-left px-3.5 py-2 text-xs font-medium text-slate-700 hover:bg-indigo-50 hover:text-indigo-600 flex items-center justify-between gap-2.5 transition cursor-pointer"
                        >
                            <div className="flex items-center gap-2.5">
                                <span className="text-base">📊</span>
                                <div>
                                    <div className="font-semibold">{t("energy.export_excel", "Excel Arbeitsmappe (.xlsx)")}</div>
                                    <div className="text-[10px] text-slate-400">{t("energy.export_excel_desc", "KPIs, Submetering & Stunden")}</div>
                                </div>
                            </div>
                            {!isPro && <ProBadge size="xs" />}
                        </button>

                        <button
                            onClick={() => triggerDownload("pdf")}
                            className="w-full text-left px-3.5 py-2 text-xs font-medium text-slate-700 hover:bg-indigo-50 hover:text-indigo-600 flex items-center justify-between gap-2.5 transition cursor-pointer"
                        >
                            <div className="flex items-center gap-2.5">
                                <span className="text-base">📄</span>
                                <div>
                                    <div className="font-semibold">{t("energy.export_pdf", "Druckfähiger PDF-Bericht")}</div>
                                    <div className="text-[10px] text-slate-400">{t("energy.export_pdf_desc", "Für Abrechnung & Vorsteuer")}</div>
                                </div>
                            </div>
                            {!isPro && <ProBadge size="xs" />}
                        </button>

                        <button
                            onClick={() => triggerDownload("csv")}
                            className="w-full text-left px-3.5 py-2 text-xs font-medium text-slate-700 hover:bg-indigo-50 hover:text-indigo-600 flex items-center gap-2.5 transition cursor-pointer"
                        >
                            <span className="text-base">📝</span>
                            <div>
                                <div className="font-semibold">{t("energy.export_csv", "CSV-Datei (Semikolon)")}</div>
                                <div className="text-[10px] text-slate-400">{t("energy.export_csv_desc", "Für Buchhaltung & Tabellen")}</div>
                            </div>
                        </button>

                        <button
                            onClick={() => triggerDownload("json")}
                            className="w-full text-left px-3.5 py-2 text-xs font-medium text-slate-700 hover:bg-indigo-50 hover:text-indigo-600 flex items-center gap-2.5 transition cursor-pointer"
                        >
                            <span className="text-base">💾</span>
                            <div>
                                <div className="font-semibold">{t("energy.export_json", "JSON-Rohdaten")}</div>
                                <div className="text-[10px] text-slate-400">{t("energy.export_json_desc", "Für Smart-Home & Backups")}</div>
                            </div>
                        </button>
                    </div>
                )}
            </div>

            {/* Pro Upgrade Dialog */}
            <ProUpgradeModal
                open={proModalOpen}
                onClose={() => setProModalOpen(false)}
                featureName="Multi-Format Exporte (Excel & PDF)"
                featureDesc="Druckfertige Monats- und Jahresberichte im PDF-Format sowie detailreiche Excel-Arbeitsmappen mit Submetering-Messreihen sind exklusiv in Sharegy Pro enthalten."
            />
        </>
    );
}
