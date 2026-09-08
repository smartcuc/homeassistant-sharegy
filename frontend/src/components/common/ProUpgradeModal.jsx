/*
# src/components/common/ProUpgradeModal.jsx
*/

import React from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useSubscription } from "../../hooks/useSubscription";
import ProBadge from "./ProBadge";

export default function ProUpgradeModal({
    open,
    onClose,
    featureName,
    featureDesc,
}) {
    const navigate = useNavigate();
    const { t } = useTranslation();
    const { proYearlyMonthlyEquiv } = useSubscription();

    const resolvedFeatureName = featureName || t("billing.pro_modal.default_feature", "Dieses Feature");
    const resolvedFeatureDesc = featureDesc || t("billing.pro_modal.default_desc", "Erweitere dein Energiemanagement mit Sharegy Pro für maximale Transparenz und Einsparungen.");

    if (!open) return null;

    const handleUpgradeClick = () => {
        onClose();
        navigate("/app/billing");
    };

    return (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-fade-in">
            <div className="bg-white rounded-3xl shadow-2xl border border-indigo-100 w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
                {/* Header Banner */}
                <div className="p-6 bg-gradient-to-br from-indigo-900 via-indigo-800 to-slate-900 text-white relative overflow-hidden">
                    <div className="absolute top-0 right-0 -mr-8 -mt-8 w-40 h-40 bg-indigo-500/20 rounded-full blur-2xl"></div>
                    <div className="flex items-center justify-between relative z-10">
                        <ProBadge size="lg" />
                        <button
                            onClick={onClose}
                            className="text-white/70 hover:text-white p-1.5 rounded-xl hover:bg-white/10 transition cursor-pointer text-sm"
                        >
                            ✕
                        </button>
                    </div>

                    <div className="mt-4 relative z-10 space-y-1">
                        <h3 className="text-xl font-extrabold text-white">
                            {t("billing.pro_modal.unlock", "{{feature}} freischalten", { feature: resolvedFeatureName })}
                        </h3>
                        <p className="text-xs text-indigo-200 leading-relaxed">
                            {resolvedFeatureDesc}
                        </p>
                    </div>
                </div>

                {/* Benefits List */}
                <div className="p-6 space-y-4 overflow-y-auto">
                    <div className="text-xs font-bold uppercase tracking-wider text-gray-400">
                        {t("billing.pro_highlights", "Sharegy Pro Vorteile")}
                    </div>

                    <div className="space-y-2.5">
                        {[
                            {
                                icon: "☀️",
                                title: t("billing.pro_modal.benefit1_title", "48h-Prognose-Trio"),
                                desc: t("billing.pro_modal.benefit1_desc", "Doppelter Planungshorizont für Solar, Haushaltslast & Batteriespeicher"),
                            },
                            {
                                icon: "📊",
                                title: t("billing.pro_modal.benefit2_title", "Multi-Format Exporte"),
                                desc: t("billing.pro_modal.benefit2_desc", "Druckfähige PDF-Berichte, Excel-Arbeitsmappen & unbegrenzte Historie"),
                            },
                            {
                                icon: "🚨",
                                title: t("billing.pro_modal.benefit3_title", "Proaktive AI-Alarmzentrale"),
                                desc: t("billing.pro_modal.benefit3_desc", "8 intelligente Regeln für Frost, Leckagen, Negativpreise & Signalverlust"),
                            },
                            {
                                icon: "⚡",
                                title: t("billing.pro_modal.benefit4_title", "Börsenstrom & Arbitrage-Simulation"),
                                desc: t("billing.pro_modal.benefit4_desc", "Multi-Dauer Ladestrategien & dynamischer Strompreis-Optimierer"),
                            },
                        ].map((item, idx) => (
                            <div key={idx} className="flex items-start gap-3 p-3 rounded-2xl bg-slate-50 border border-slate-100">
                                <span className="text-xl shrink-0 p-1.5 bg-white rounded-xl shadow-2xs">{item.icon}</span>
                                <div>
                                    <h4 className="font-bold text-xs text-gray-900">{item.title}</h4>
                                    <p className="text-[11px] text-gray-500 mt-0.5">{item.desc}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Footer Action */}
                <div className="p-5 bg-slate-50 border-t border-gray-100 flex flex-col sm:flex-row items-center justify-between gap-3">
                    <div className="text-center sm:text-left">
                        <div className="text-xs font-extrabold text-gray-900">
                            {t("billing.pro_modal.from_price", "ab {{price}} € / Monat", { price: proYearlyMonthlyEquiv })}
                        </div>
                        <div className="text-[10px] text-gray-400">
                            {t("billing.pro_modal.cancel_anytime", "Monatlich kündbar · Sofortige Freischaltung")}
                        </div>
                    </div>

                    <div className="flex items-center gap-2 w-full sm:w-auto">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 sm:flex-none px-3.5 py-2.5 rounded-xl border border-gray-200 text-xs font-semibold text-gray-600 hover:bg-gray-100 transition cursor-pointer"
                        >
                            {t("billing.pro_modal.later", "Später")}
                        </button>
                        <button
                            type="button"
                            onClick={handleUpgradeClick}
                            className="flex-1 sm:flex-none px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 text-white font-bold text-xs shadow-md shadow-indigo-200 transition cursor-pointer flex items-center justify-center gap-1.5"
                        >
                            <span>⭐</span>
                            <span>{t("billing.pro_modal.upgrade_now", "Jetzt Pro upgraden")}</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
