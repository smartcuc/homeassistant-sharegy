/*
# src/features/billing/components/InvoicesListCard.jsx
*/

import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import Card from "../../../components/ui/Card";
import { apiFetch } from "../../../api/client";

export default function InvoicesListCard({ invoices, onRefresh }) {
    const { t } = useTranslation();
    const [seeding, setSeeding] = useState(false);

    const handleSeedDemo = async () => {
        setSeeding(true);
        try {
            await apiFetch("/api/billing/subscription/seed-demo/", { method: "POST" });
            if (onRefresh) onRefresh();
        } catch (err) {
            alert(t("billing.seed_error", "Fehler beim Erzeugen von Demo-Rechnungen."));
        } finally {
            setSeeding(false);
        }
    };

    return (
        <Card>
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-gray-100 dark:border-slate-800 pb-4 mb-4">
                <div>
                    <h3 className="font-bold text-gray-900 dark:text-white text-base flex items-center gap-2">
                        <span>📄</span> {t("billing.invoices_title", "Rechnungsverlauf & Belege")}
                    </h3>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                        {t("billing.invoices_desc", "Hier findest du alle ausgestellten Rechnungen mit ausgewiesener MwSt. zum Download.")}
                    </p>
                </div>

                {(!invoices || invoices.length === 0) && (
                    <button
                        type="button"
                        onClick={handleSeedDemo}
                        disabled={seeding}
                        className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 rounded-xl text-xs font-bold flex items-center gap-1.5 transition border border-slate-300 dark:border-slate-700 cursor-pointer shadow-2xs"
                    >
                        <span>✨</span>
                        <span>{seeding ? t("common.loading", "Lade...") : t("billing.seed_demo", "Demo-Rechnungen laden")}</span>
                    </button>
                )}
            </div>

            {invoices && invoices.length > 0 ? (
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                        <thead>
                            <tr className="border-b border-gray-200 dark:border-slate-700 text-gray-400 dark:text-gray-500 font-bold uppercase text-[10px] tracking-wider">
                                <th className="pb-3">{t("billing.th_invoice_nr", "Rechnungs-Nr.")}</th>
                                <th className="pb-3">{t("billing.th_date", "Datum")}</th>
                                <th className="pb-3">{t("billing.th_tariff_period", "Tarif / Zeitraum")}</th>
                                <th className="pb-3">{t("billing.th_amount", "Betrag")}</th>
                                <th className="pb-3">{t("billing.th_status", "Status")}</th>
                                <th className="pb-3 text-right">{t("billing.th_action", "Aktion")}</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100 dark:divide-slate-800">
                            {invoices.map((inv) => (
                                <tr key={inv.id} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/50 transition">
                                    <td className="py-3 font-bold text-gray-900 dark:text-white font-mono">
                                        {inv.invoice_number}
                                    </td>
                                    <td className="py-3 text-gray-600 dark:text-gray-300">
                                        {new Date(inv.created_at).toLocaleDateString("de-DE")}
                                    </td>
                                    <td className="py-3 text-gray-700 dark:text-gray-200 font-medium">
                                        {inv.plan_name}
                                        <span className="block text-[11px] text-gray-400 dark:text-gray-500">
                                            {new Date(inv.period_start).toLocaleDateString("de-DE")} – {new Date(inv.period_end).toLocaleDateString("de-DE")}
                                        </span>
                                    </td>
                                    <td className="py-3 font-extrabold text-gray-900 dark:text-white">
                                        {parseFloat(inv.amount_gross_eur).toFixed(2)} €
                                    </td>
                                    <td className="py-3">
                                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                                            <span>✓</span> {t("billing.paid", "Bezahlt")}
                                        </span>
                                    </td>
                                    <td className="py-3 text-right">
                                        <a
                                            href={`/api/billing/subscription/invoices/${inv.id}/pdf/`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="inline-flex items-center gap-1 px-3 py-1.5 bg-white dark:bg-slate-800 border border-gray-300 dark:border-slate-700 hover:border-gray-400 dark:hover:border-slate-600 text-gray-800 dark:text-gray-200 hover:text-indigo-600 dark:hover:text-indigo-400 rounded-xl font-bold shadow-2xs transition text-xs"
                                        >
                                            <span>📥</span> PDF
                                        </a>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            ) : (
                <div className="py-12 text-center space-y-3">
                    <div className="text-3xl">🧾</div>
                    <div className="text-xs font-medium text-gray-500 dark:text-gray-400 max-w-md mx-auto leading-relaxed">
                        {t("billing.no_invoices", "Noch keine Rechnungen vorhanden. Nach dem ersten Abrechnungszyklus werden deine Belege hier automatisch archiviert.")}
                    </div>
                </div>
            )}
        </Card>
    );
}
