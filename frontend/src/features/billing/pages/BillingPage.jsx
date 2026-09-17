/*
# src/features/billing/pages/BillingPage.jsx
*/

import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import { useLocation, useNavigate, Link } from "react-router-dom";
import { apiFetch } from "../../../api/client";
import SubscriptionPlanCard from "../components/SubscriptionPlanCard";
import { useUserNavigation } from "../../../hooks/useUserNavigation";
import { NAV_MODES } from "../../../config/navigationConfig";

export default function BillingPage() {
    const { t } = useTranslation();
    const location = useLocation();
    const navigate = useNavigate();
    const { activeMode } = useUserNavigation();

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
            setStatusBanner({
                type: "success",
                title: t("billing.checkout_success_title", "🎉 Abonnement erfolgreich aktiviert!"),
                message: t(
                    "billing.checkout_success_desc",
                    "Vielen Dank! Dein Sharegy EMS-Abonnement wurde über Stripe freigeschaltet. Alle Funktionen stehen dir ab sofort zur Verfügung."
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
        <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-6">
            {/* Success / Cancel Banner */}
            {statusBanner && (
                <div
                    className={`p-4 rounded-2xl border flex items-start justify-between gap-3 animate-in fade-in ${
                        statusBanner.type === "success"
                            ? "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-300 dark:border-emerald-800 text-emerald-900 dark:text-emerald-200"
                            : "bg-slate-50 dark:bg-slate-800 border-slate-300 dark:border-slate-700 text-slate-800 dark:text-slate-200"
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
                    <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-2.5">
                        <span>💳</span>
                        <span>{t("billing.title", "Abonnement & Tarife")}</span>
                    </h1>
                    <p className="text-gray-500 dark:text-gray-400 mt-1 text-xs sm:text-sm">
                        {t("billing.subtitle", "Verwalte deinen Sharegy EMS-Tarif, wechsle zwischen Monats- und Jahresintervall oder erweitere deine Funktionen.")}
                    </p>
                </div>

                {stripeConfig?.sandbox_mode && (
                    <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-50 dark:bg-amber-950/60 border border-amber-300 dark:border-amber-700 text-amber-900 dark:text-amber-200 text-xs font-bold shadow-2xs shrink-0 self-start sm:self-auto">
                        <span className="animate-pulse">🧪</span>
                        <span>{t("billing.sandbox_badge", "Stripe Testmodus (Sandbox)")}</span>
                    </div>
                )}
            </div>

            {/* 🏢 Community Member Notice Banner */}
            {activeMode === NAV_MODES.SHARING_ONLY && (
                <div className="p-4 rounded-2xl bg-indigo-50/80 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-indigo-900 dark:text-indigo-200 shadow-xs">
                    <div className="flex items-center gap-2.5">
                        <span className="text-xl shrink-0">🏢</span>
                        <div>
                            <span className="font-bold block text-sm text-indigo-950 dark:text-indigo-100">
                                {t("billing.community_notice_title", "Suchst du deine Strom-Abrechnungsnachweise der Gemeinschaft?")}
                            </span>
                            <span className="text-indigo-700/80 dark:text-indigo-300/80">
                                {t("billing.community_notice_desc", "Deine monatlichen Abrechnungsnachweise nach § 42b EnWG (kWh Solar vs. Netz) und der aktive Sharing-Tarif werden im Community Cockpit verwaltet.")}
                            </span>
                        </div>
                    </div>
                    <Link
                        to="/app/tenant?tab=settlement"
                        className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-xs transition flex items-center gap-1.5 shrink-0 self-start sm:self-auto cursor-pointer"
                    >
                        <span>{t("billing.to_community_statements", "Zu den Community-Abrechnungen")}</span>
                        <span>➔</span>
                    </Link>
                </div>
            )}

            {/* Plan Selector & Checkout */}
            <SubscriptionPlanCard subscriptionData={billingData} onRefresh={refetch} />

            {/* Footnote / Link to Profile Invoices & Address */}
            <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-700/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                <div className="flex items-center gap-2 text-gray-600 dark:text-gray-300">
                    <span className="text-lg">📄</span>
                    <span>Rechnungsbelege mit MwSt. oder Rechnungsanschrift gesucht?</span>
                </div>
                <Link
                    to="/app/profile?tab=invoices"
                    className="px-4 py-2 bg-white dark:bg-slate-700 hover:bg-gray-100 dark:hover:bg-slate-600 border border-gray-200 dark:border-slate-600 text-gray-800 dark:text-gray-200 font-bold rounded-xl shadow-2xs transition flex items-center gap-1.5 self-start sm:self-auto"
                >
                    <span>Zu meinen Rechnungen im Profil</span>
                    <span>➔</span>
                </Link>
            </div>
        </div>
    );
}
