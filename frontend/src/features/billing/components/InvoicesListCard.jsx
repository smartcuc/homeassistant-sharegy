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
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h3 className="font-bold text-gray-900 text-base flex items-center gap-2">
                        <span>📄</span> {t("billing.invoices_title", "Rechnungsverlauf & Belege")}
                    </h3>
                    <p className="text-xs text-gray-500 mt-0.5">
                        {t("billing.invoices_desc", "Hier findest du alle ausgestellten Rechnungen mit ausgewiesener MwSt. zum Download.")}
                    </p>
                </div>

                {(!invoices || invoices.length === 0) && (
                    <button
                        type="button"
                        onClick={handleSeedDemo}
                        disabled={seeding}
                        className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-xl text-xs font-bold flex items-center gap-1.5 transition border border-gray-300"
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
                            <tr className="border-b border-gray-200 text-gray-400 font-bold uppercase">
                                <th className="pb-3">{t("billing.th_invoice_nr", "Rechnungs-Nr.")}</th>
                                <th className="pb-3">{t("billing.th_date", "Datum")}</th>
                                <th className="pb-3">{t("billing.th_tariff_period", "Tarif / Zeitraum")}</th>
                                <th className="pb-3">{t("billing.th_amount", "Betrag")}</th>
                                <th className="pb-3">{t("billing.th_status", "Status")}</th>
                                <th className="pb-3 text-right">{t("billing.th_action", "Aktion")}</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {invoices.map((inv) => (
                                <tr key={inv.id} className="hover:bg-gray-50/80 transition">
                                    <td className="py-3 font-bold text-gray-900 font-mono">
                                        {inv.invoice_number}
                                    </td>
                                    <td className="py-3 text-gray-600">
                                        {new Date(inv.created_at).toLocaleDateString()}
                                    </td>
                                    <td className="py-3 text-gray-700 font-medium">
                                        {inv.plan_name}
                                        <span className="block text-[11px] text-gray-400">
                                            {new Date(inv.period_start).toLocaleDateString()} – {new Date(inv.period_end).toLocaleDateString()}
                                        </span>
                                    </td>
                                    <td className="py-3 font-extrabold text-gray-900">
                                        {parseFloat(inv.amount_gross_eur).toFixed(2)} €
                                    </td>
                                    <td className="py-3">
                                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
                                            <span>✓</span> {t("billing.paid", "Bezahlt")}
                                        </span>
                                    </td>
                                    <td className="py-3 text-right">
                                        <a
                                            href={`/api/billing/subscription/invoices/${inv.id}/pdf/`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white border border-gray-300 hover:border-gray-400 text-gray-700 hover:text-gray-900 rounded-xl font-bold shadow-xs transition"
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
                <div className="py-10 text-center text-gray-400 text-xs">
                    {t("billing.no_invoices", "Noch keine Rechnungen vorhanden. Nach dem ersten Abrechnungszyklus werden deine Belege hier automatisch archiviert.")}
                </div>
            )}
        </Card>
    );
}
