import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import { useLocation, useNavigate } from "react-router-dom";
import { apiFetch } from "../../../api/client";
import SubscriptionPlanCard from "../components/SubscriptionPlanCard";
import BillingAddressCard from "../components/BillingAddressCard";
import InvoicesListCard from "../components/InvoicesListCard";

export default function BillingPage() {
    const { t } = useTranslation();
    const location = useLocation();
    const navigate = useNavigate();

    const [statusBanner, setStatusBanner] = useState(null);

    const { data: billingData, isLoading, refetch } = useQuery({
        queryKey: ["billingOverview"],
        queryFn: () => apiFetch("/api/billing/subscription/me/"),
    });

    const { data: stripeConfig } = useQuery({
        queryKey: ["stripeConfig"],
        queryFn: () => apiFetch("/api/billing/stripe/config/").catch(() => null),
    });

    // Handle return from Stripe Checkout (?success=true or ?canceled=true)
    useEffect(() => {
        const params = new URLSearchParams(location.search);
        if (params.get("success") === "true") {
            const plan = params.get("plan") || "Pro";
            setStatusBanner({
                type: "success",
                title: t("billing.checkout_success_title", "🎉 Abonnement erfolgreich aktiviert!"),
                message: t(
                    "billing.checkout_success_desc",
                    "Vielen Dank! Dein Sharegy EMS-Abonnement wurde über Stripe freigeschaltet. Alle Pro-Funktionen stehen dir ab sofort zur Verfügung."
                ),
            });
            refetch();
            // Clean up URL query parameters without reloading
            navigate(location.pathname, { replace: true });
        } else if (params.get("canceled") === "true") {
            setStatusBanner({
                type: "info",
                title: t("billing.checkout_canceled_title", "Vorgang abgebrochen"),
                message: t("billing.checkout_canceled_desc", "Der Checkout-Vorgang wurde abgebrochen. Es wurden keine Beträge abgebucht."),
            });
            navigate(location.pathname, { replace: true });
        }
    }, [location.search]);

    if (isLoading) {
        return (
            <div className="max-w-7xl mx-auto p-6 text-gray-400 text-center py-20">
                {t("billing.loading", "Lade Abrechnungs- & Abonnement-Informationen...")}
            </div>
        );
    }

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            {/* Success / Cancel Banner */}
            {statusBanner && (
                <div
                    className={`p-4 rounded-2xl border flex items-start justify-between gap-3 animate-in fade-in ${
                        statusBanner.type === "success"
                            ? "bg-emerald-50 border-emerald-300 text-emerald-900"
                            : "bg-slate-50 border-slate-300 text-slate-800"
                    }`}
                >
                    <div>
                        <div className="font-bold text-sm">{statusBanner.title}</div>
                        <div className="text-xs mt-0.5 opacity-90">{statusBanner.message}</div>
                    </div>
                    <button
                        onClick={() => setStatusBanner(null)}
                        className="text-xs font-bold opacity-60 hover:opacity-100 cursor-pointer"
                    >
                        ✕
                    </button>
                </div>
            )}

            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
                        <span>💳</span>
                        {t("billing.title", "Abonnement, Tarife & Abrechnung")}
                    </h1>
                    <p className="text-gray-500 mt-1 text-sm">
                        {t("billing.subtitle", "Verwalte deinen Sharegy EMS-Tarif, deine Rechnungsadresse und lade Rechnungen als PDF herunter.")}
                    </p>
                </div>

                {stripeConfig?.sandbox_mode && (
                    <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-50 border border-amber-300 text-amber-900 text-xs font-bold shadow-2xs shrink-0 self-start sm:self-auto">
                        <span className="animate-pulse">🧪</span>
                        <span>{t("billing.sandbox_badge", "Stripe Testmodus (Sandbox)")}</span>
                    </div>
                )}
            </div>

            {/* Plan Selector */}
            <SubscriptionPlanCard subscriptionData={billingData} onRefresh={refetch} />

            {/* Billing Address & Invoices */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <BillingAddressCard billingAddress={billingData?.billing_address} onSaveSuccess={refetch} />
                <InvoicesListCard invoices={billingData?.invoices} onRefresh={refetch} />
            </div>
        </div>
    );
}
