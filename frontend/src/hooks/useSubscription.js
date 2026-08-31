/*
# src/hooks/useSubscription.js
*/

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../api/client";

export function useSubscription() {
    const query = useQuery({
        queryKey: ["billingOverview"],
        queryFn: () => apiFetch("/api/billing/subscription/me/"),
        staleTime: 1000 * 60 * 5, // 5 Minuten Cache
    });

    const sub = query.data?.subscription;
    const isPro = Boolean(sub?.is_pro);
    const isLandlord = Boolean(sub?.is_landlord);
    const plan = sub?.plan || "free";
    const entitlements = sub?.entitlements || {
        unlimited_history: isPro,
        forecast_trio: isPro,
        spot_optimizer: isPro,
        battery_arbitrage: isPro,
        live_co2_signal: isPro,
        proactive_alerts: isPro,
        multi_format_exports: isPro,
        multi_home_landlord: isLandlord,
        tenant_sub_billing: isLandlord,
    };

    return {
        isPro,
        isLandlord,
        plan,
        planName: sub?.plan_name || "Sharegy Free",
        status: sub?.status || "active",
        subscription: sub,
        entitlements,
        availablePlans: query.data?.available_plans || {},
        invoices: query.data?.invoices || [],
        isLoading: query.isLoading,
        isError: query.isError,
        refetch: query.refetch,
    };
}
