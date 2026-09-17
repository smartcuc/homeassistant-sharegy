import useModalDismiss from "../../hooks/useModalDismiss";
/*
# src/components/device/HomeSetupStatusModal.jsx
*/

import React from "react";
import { useTranslation } from "react-i18next";
import SystemReadinessCard from "../../features/energy/components/SystemReadinessCard";

export default function HomeSetupStatusModal({ open, onClose, onOpenAddDevice }) {
    const { t } = useTranslation();
    useModalDismiss(open, onClose);
    if (!open) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-fade-in" onClick={onClose}>
            <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden" onClick={(e) => e.stopPropagation()}>
                {/* Header mit Omi-Check im Text */}
                <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/70">
                    <div className="flex items-center gap-3">
                        <span className="text-3xl p-2.5 bg-white rounded-2xl shadow-xs border border-slate-200">🩺</span>
                        <div>
                            <h2 className="text-xl font-black text-gray-900 tracking-tight">
                                {t("system_health.modal_title", "System-Check & Einrichtungsgrad (Omi-Check)")}
                            </h2>
                            <p className="text-xs text-gray-500 mt-0.5">
                                {t("system_health.modal_desc", "Automatische Prüfung der 4 Kernsäulen (PV, Netz, Speicher, Last) für ein fehlerfreies Energiemanagement.")}
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="w-9 h-9 rounded-full bg-white border border-slate-200 text-gray-400 hover:text-gray-700 hover:bg-gray-100 flex items-center justify-center text-lg font-bold transition cursor-pointer"
                        title={t("common.close", "Schließen")}
                    >
                        ✕
                    </button>
                </div>

                {/* Body */}
                <div className="flex-1 overflow-y-auto p-6">
                    <SystemReadinessCard
                        inModal={true}
                        onOpenAddDevice={() => {
                            if (onClose) onClose();
                            if (onOpenAddDevice) onOpenAddDevice();
                        }}
                    />
                </div>
            </div>
        </div>
    );
}
