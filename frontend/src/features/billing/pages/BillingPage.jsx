import React from "react";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../../../api/client";
import SubscriptionPlanCard from "../components/SubscriptionPlanCard";
import BillingAddressCard from "../components/BillingAddressCard";
import InvoicesListCard from "../components/InvoicesListCard";

export default function BillingPage() {
    const { data: billingData, isLoading, refetch } = useQuery({
        queryKey: ["billingOverview"],
        queryFn: () => apiFetch("/api/billing/subscription/me/"),
    });

    if (isLoading) {
        return (
            <div className="max-w-5xl mx-auto p-6 text-gray-400 text-center py-20">
                Lade Abrechnungs- & Abonnement-Informationen...
            </div>
        );
    }

    return (
        <div className="max-w-5xl mx-auto p-6 space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
                    <span>💳</span>
                    Abonnement, Tarife & Abrechnung
                </h1>
                <p className="text-gray-500 mt-1 text-sm">
                    Verwalte deinen Sharegy EMS-Tarif, deine Rechnungsadresse und lade Rechnungen als PDF herunter.
                </p>
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
