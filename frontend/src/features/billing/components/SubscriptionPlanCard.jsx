import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";
import { trackEvent } from "../../../tracking/ga";

export default function SubscriptionPlanCard({ subscriptionData, onRefresh }) {
    const { t } = useTranslation();
    const [interval, setInterval] = useState("month");
    const [loadingPlan, setLoadingPlan] = useState(null);
    const [actionMsg, setActionMsg] = useState(null);

    // AGB Zustimmung & E-Mail
    const [termsAccepted, setTermsAccepted] = useState(true);

    // Gutschein State
    const [showCouponInput, setShowCouponInput] = useState(false);
    const [couponCode, setCouponCode] = useState("");
    const [couponLoading, setCouponLoading] = useState(false);
    const [validatedCoupon, setValidatedCoupon] = useState(null);
    const [couponMsg, setCouponMsg] = useState(null);

    const currentPlan = subscriptionData?.subscription?.plan || "free";
    const isPro = subscriptionData?.subscription?.is_pro;
    const isLandlord = subscriptionData?.subscription?.is_landlord;
    const currentPeriodEnd = subscriptionData?.subscription?.current_period_end;
    const cancelAtEnd = subscriptionData?.subscription?.cancel_at_period_end;

    // Stripe Portal State
    const [portalLoading, setPortalLoading] = useState(false);

    // Plan-Wechsel (via Stripe Checkout für Bezahlpläne)
    const handlePlanChange = async (targetPlan) => {
        if (targetPlan !== "free" && !termsAccepted) {
            setActionMsg({
                type: "error",
                text: t("billing.terms_required", "Bitte bestätige die AGB und Datenschutzbestimmungen, um fortzufahren."),
            });
            return;
        }

        setLoadingPlan(targetPlan);
        setActionMsg(null);
        try {
            if (targetPlan === "free") {
                // Direktes Downgrade auf Free
                const res = await apiFetch("/api/billing/subscription/change-plan/", {
                    method: "POST",
                    body: JSON.stringify({
                        plan: "free",
                        terms_accepted: termsAccepted,
                    }),
                });
                if (res.status === "success") {
                    trackEvent("plan_downgrade", "billing", "free");
                    setActionMsg({ type: "success", text: res.message });
                    if (onRefresh) onRefresh();
                } else {
                    setActionMsg({ type: "error", text: res.message || "Fehler beim Wechseln auf Free." });
                }
            } else {
                // Stripe Checkout Session für Bezahlpläne initialisieren
                const res = await apiFetch("/api/billing/stripe/checkout/", {
                    method: "POST",
                    body: JSON.stringify({
                        plan: targetPlan,
                        terms_accepted: termsAccepted,
                    }),
                });

                if (res.status === "success" && res.checkout_url) {
                    trackEvent("stripe_checkout_initiated", "billing", targetPlan);
                    // Weiterleitung zur Stripe Checkout Session
                    window.location.href = res.checkout_url;
                } else {
                    setActionMsg({
                        type: "error",
                        text: res.message || t("billing.plan_change_error", "Fehler beim Starten des Checkouts."),
                    });
                }
            }
        } catch (err) {
            setActionMsg({
                type: "error",
                text: err.message || t("billing.network_error", "Netzwerkfehler beim Planwechsel."),
            });
        } finally {
            setLoadingPlan(null);
        }
    };

    // Stripe Customer Portal öffnen
    const handleOpenStripePortal = async () => {
        setPortalLoading(true);
        setActionMsg(null);
        try {
            const res = await apiFetch("/api/billing/stripe/portal/", {
                method: "POST",
                body: JSON.stringify({ return_url: window.location.href }),
            });
            if (res.status === "success" && res.portal_url) {
                window.location.href = res.portal_url;
            } else {
                setActionMsg({ type: "error", text: res.message || "Kundenportal konnte nicht geöffnet werden." });
            }
        } catch (err) {
            setActionMsg({ type: "error", text: err.message || "Fehler beim Verbinden mit dem Kundenportal." });
        } finally {
            setPortalLoading(false);
        }
    };

    // Gutschein validieren
    const handleValidateCoupon = async (e) => {
        if (e) e.preventDefault();
        const clean = couponCode.trim();
        if (!clean) return;

        setCouponLoading(true);
        setCouponMsg(null);
        setValidatedCoupon(null);

        try {
            const res = await apiFetch("/api/billing/subscription/coupons/validate/", {
                method: "POST",
                body: JSON.stringify({ code: clean }),
            });
            if (res.status === "success" && res.coupon) {
                setValidatedCoupon(res.coupon);
                setCouponMsg({
                    type: "success",
                    text: `✅ Code '${res.coupon.code}' gültig: ${res.coupon.description}`,
                });
            } else {
                setCouponMsg({
                    type: "error",
                    text: res.message || "Gutscheincode konnte nicht validiert werden.",
                });
            }
        } catch (err) {
            setCouponMsg({
                type: "error",
                text: err.message || "Ungültiger oder abgelaufener Gutscheincode.",
            });
        } finally {
            setCouponLoading(false);
        }
    };

    // Gutschein einlösen
    const handleRedeemCoupon = async () => {
        if (!validatedCoupon) return;
        if (!termsAccepted) {
            setCouponMsg({
                type: "error",
                text: t("billing.terms_required", "Bitte bestätige die AGB und Datenschutzbestimmungen, um den Gutschein einzulösen."),
            });
            return;
        }

        setCouponLoading(true);
        try {
            const res = await apiFetch("/api/billing/subscription/coupons/redeem/", {
                method: "POST",
                body: JSON.stringify({
                    code: validatedCoupon.code,
                    terms_accepted: termsAccepted,
                }),
            });
            if (res.status === "success") {
                trackEvent("coupon_redeemed", "billing", validatedCoupon.code);
                setCouponMsg({ type: "success", text: res.message });
                setValidatedCoupon(null);
                setCouponCode("");
                if (onRefresh) onRefresh();
            } else {
                setCouponMsg({ type: "error", text: res.message || "Fehler beim Einlösen des Gutscheins." });
            }
        } catch (err) {
            setCouponMsg({ type: "error", text: err.message || "Fehler beim Einlösen." });
        } finally {
            setCouponLoading(false);
        }
    };

    const handleCancel = async () => {
        if (!window.confirm(t("billing.cancel_confirm", "Möchtest du dein Abonnement wirklich zum Ende des Abrechnungszeitraums kündigen?"))) return;
        try {
            await apiFetch("/api/billing/subscription/cancel/", {
                method: "POST",
                body: JSON.stringify({ at_period_end: true }),
            });
            if (onRefresh) onRefresh();
        } catch (err) {
            alert(t("billing.cancel_error", "Fehler beim Kündigen."));
        }
    };

    const handleReactivate = async () => {
        try {
            await apiFetch("/api/billing/subscription/reactivate/", {
                method: "POST",
            });
            if (onRefresh) onRefresh();
        } catch (err) {
            alert(t("billing.reactivate_error", "Fehler beim Reaktivieren."));
        }
    };

    const availablePlans = subscriptionData?.available_plans;
    const formatPrice = (val, fallback) => {
        if (val == null || val === "") return fallback;
        const num = Number(val);
        return isNaN(num) ? fallback : `${num.toFixed(2).replace(".", ",")} €`;
    };

    const proMonthlyPrice = formatPrice(availablePlans?.pro_monthly?.price_gross_eur, "4,99 €");
    const proYearlyPrice = formatPrice(availablePlans?.pro_yearly?.price_gross_eur, "49,99 €");
    const proMonthlyEquiv = formatPrice(availablePlans?.pro_yearly?.price_monthly_equivalent, "4,17 €");

    const landlordMonthlyPrice = formatPrice(availablePlans?.landlord_monthly?.price_gross_eur, "14,99 €");
    const landlordYearlyPrice = formatPrice(availablePlans?.landlord_yearly?.price_gross_eur, "149,99 €");
    const landlordMonthlyEquiv = formatPrice(availablePlans?.landlord_yearly?.price_monthly_equivalent, "12,50 €");

    const plans = [
        {
            id: "free",
            name: t("billing.plan_free_name", "Sharegy Free"),
            badge: t("billing.plan_free_badge", "Basis"),
            iconEmoji: "🌱",
            priceMonthly: "0 €",
            priceYearly: "0 €",
            priceSub: t("billing.free_forever", "Dauerhaft kostenlos"),
            desc: t("billing.plan_free_desc", "Ideal für den Einstieg und die reine Live-Visualisierung deines Zuhauses."),
            features: [
                t("billing.f_sankey", "Live-Sankey Energiefluss & 24h-Historie"),
                t("billing.f_weather", "Basis-Wetter- & Solarprognose (24h)"),
                t("billing.f_shelly", "Shelly WSS & Live Relais-Aktorik"),
                t("billing.f_bridge", "Home Assistant & Grafana Bridge"),
                t("billing.f_residual", "Residual-Zähler & Grundlastmessung"),
            ],
            current: currentPlan === "free",
        },
        {
            id: interval === "month" ? "pro_monthly" : "pro_yearly",
            name: t("billing.plan_pro_name", "Sharegy Pro"),
            badge: t("billing.plan_pro_badge", "⭐ Beliebteste Wahl"),
            badgeColor: "bg-emerald-100 text-emerald-800 border-emerald-300",
            iconEmoji: "⚡",
            priceMonthly: proMonthlyPrice,
            priceYearly: proYearlyPrice,
            priceSub: interval === "year" 
                ? t("billing.year_equiv", { defaultValue: `entspricht ${proMonthlyEquiv} / Monat`, equiv: proMonthlyEquiv }) 
                : t("billing.monthly_cancelable", "monatlich kündbar"),
            desc: t("billing.plan_pro_desc", "Volle KI-Power, Speicher-Arbitrage und automatische Börsenpreis-Optimierung."),
            highlight: true,
            features: [
                t("billing.f_pro_forecast", "48h-Prognose-Trio (PV + Last + Speicher-SoC)"),
                t("billing.f_pro_optimizer", "Multi-Dauer Börsenstrom-Optimizer (1h, 2h, 4h)"),
                t("billing.f_pro_arbitrage", "Batterie-Arbitrage Simulator (Netzladen)"),
                t("billing.f_pro_co2", "Live CO₂-Grid-Signal & Grünstrom-Index (36h)"),
                t("billing.f_pro_alerts", "Proaktive AI-Alarmzentrale (8 Schutzregeln)"),
                t("billing.f_pro_trends", "Unbegrenzte Historie & Submeter-Trends"),
                t("billing.f_pro_exports", "Multi-Format Daten-Export (Excel, PDF, CSV)"),
            ],
            current: isPro && !isLandlord,
        },
        {
            id: interval === "month" ? "landlord_monthly" : "landlord_yearly",
            name: t("billing.plan_landlord_name", "Vermieter & Quartiere"),
            badge: t("billing.plan_landlord_badge", "Multi-Unit"),
            badgeColor: "bg-indigo-100 text-indigo-800 border-indigo-300",
            iconEmoji: "🏢",
            priceMonthly: landlordMonthlyPrice,
            priceYearly: landlordYearlyPrice,
            priceSub: interval === "year" 
                ? t("billing.year_equiv", { defaultValue: `entspricht ${landlordMonthlyEquiv} / Monat`, equiv: landlordMonthlyEquiv }) 
                : t("billing.monthly_cancelable", "monatlich kündbar"),
            desc: t("billing.plan_landlord_desc", "Für Mehrfamilienhäuser, Vermieter und Mieterstrom-Gemeinschaften."),
            features: [
                t("billing.f_landlord_pro", "Alle Pro-Funktionen inklusive"),
                t("billing.f_landlord_multi", "Multi-Home & Mehrparteien-Verwaltung"),
                t("billing.f_landlord_submeter", "Unterzähler-Abrechnungsberichte"),
                t("billing.f_landlord_tax", "Mieterstrom-Abrechnungs-PDFs für Steuer"),
                t("billing.f_landlord_p2p", "Quartiers-Clearing & P2P-Bilanzen"),
                t("billing.f_landlord_sla", "Prioritäts-Support mit SLA"),
            ],
            current: isLandlord,
        },
    ];

    return (
        <div className="space-y-6">
            {/* Status Banner */}
            {cancelAtEnd && (
                <div className="p-4 rounded-2xl border border-amber-300 bg-amber-50 text-amber-900 flex items-center justify-between">
                    <div>
                        <div className="font-bold text-sm">{t("billing.canceled_title", "Abonnement zum Periodenende gekündigt")}</div>
                        <div className="text-xs text-amber-700 mt-0.5">
                            {t("billing.canceled_desc", {
                                date: currentPeriodEnd ? new Date(currentPeriodEnd).toLocaleDateString() : t("billing.period_end", "Ende der Laufzeit"),
                                defaultValue: `Dein Zugang bleibt bis zum ${currentPeriodEnd ? new Date(currentPeriodEnd).toLocaleDateString() : "Ende der Laufzeit"} vollständig aktiv.`
                            })}
                        </div>
                    </div>
                    <button
                        onClick={handleReactivate}
                        className="px-3.5 py-1.5 bg-white border border-amber-300 text-amber-900 rounded-xl text-xs font-bold shadow-xs hover:bg-amber-100 transition cursor-pointer"
                    >
                        {t("billing.revoke_cancel", "Kündigung widerrufen")}
                    </button>
                </div>
            )}

            {actionMsg && (
                <div className={`p-4 rounded-2xl border text-sm font-semibold ${
                    actionMsg.type === "success" ? "border-emerald-300 bg-emerald-50 text-emerald-900" : "border-rose-300 bg-rose-50 text-rose-900"
                }`}>
                    {actionMsg.text}
                </div>
            )}



            {/* Billing Interval Toggle */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white dark:bg-slate-900 p-4 rounded-2xl border border-gray-200 dark:border-slate-800 shadow-xs">
                <div>
                    <h3 className="font-bold text-gray-900 dark:text-white text-base flex items-center gap-2">
                        <span>✨</span>
                        {t("billing.plans_title", "Verfügbare Tarife & Abonnement-Pläne")}
                    </h3>
                    <p className="text-xs text-gray-500 mt-0.5">
                        {t("billing.plans_subtitle", "Wähle das passende Leistungspaket für dein Smart Home oder Mehrparteienhaus.")}
                    </p>
                </div>

                <div className="flex items-center bg-gray-100 dark:bg-slate-800 p-1 rounded-xl self-start sm:self-auto border border-gray-200 dark:border-slate-700">
                    <button
                        type="button"
                        onClick={() => setInterval("month")}
                        className={`px-4 py-1.5 rounded-lg text-xs font-bold transition cursor-pointer ${
                            interval === "month" ? "bg-white dark:bg-slate-900 text-gray-900 dark:text-white shadow-xs" : "text-gray-500 hover:text-gray-900 dark:hover:text-white"
                        }`}
                    >
                        {t("billing.monthly", "Monatlich")}
                    </button>
                    <button
                        type="button"
                        onClick={() => setInterval("year")}
                        className={`px-4 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 cursor-pointer ${
                            interval === "year" ? "bg-white dark:bg-slate-900 text-emerald-800 dark:text-emerald-400 shadow-xs" : "text-gray-500 hover:text-gray-900 dark:hover:text-white"
                        }`}
                    >
                        <span>{t("billing.yearly", "Jährlich")}</span>
                        <span className="bg-emerald-600 text-white text-[10px] px-1.5 py-0.5 rounded-full font-extrabold uppercase">
                            {t("billing.discount_badge", "-17% Rabatt")}
                        </span>
                    </button>
                </div>
            </div>

            {/* Plan Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {plans.map((p) => {
                    const price = interval === "year" ? p.priceYearly : p.priceMonthly;
                    const isCurrent = p.current;

                    return (
                        <div
                            key={p.id}
                            className={`rounded-2xl p-6 transition flex flex-col justify-between relative border ${
                                p.highlight
                                    ? "bg-gradient-to-b from-emerald-50/50 to-white dark:from-emerald-950/20 dark:to-slate-900 border-emerald-400 ring-2 ring-emerald-500/20 shadow-md"
                                    : "bg-white dark:bg-slate-900 border-gray-200 dark:border-slate-800 hover:border-gray-300 shadow-xs"
                            }`}
                        >
                            {p.badge && (
                                <span className={`absolute -top-3 right-5 text-[11px] font-extrabold px-2.5 py-0.5 rounded-full border shadow-xs ${
                                    p.badgeColor || "bg-gray-100 text-gray-700 border-gray-300 dark:bg-slate-800 dark:text-gray-300 dark:border-slate-700"
                                }`}>
                                    {p.badge}
                                </span>
                            )}

                            <div>
                                <div className="flex items-center gap-3 mb-3">
                                    <div className="w-10 h-10 rounded-xl bg-gray-100 dark:bg-slate-800 flex items-center justify-center text-lg">
                                        {p.iconEmoji}
                                    </div>
                                    <div>
                                        <h4 className="font-bold text-gray-900 dark:text-white text-base">{p.name}</h4>
                                        <div className="text-[11px] text-gray-400 font-medium">SaaS Cloud</div>
                                    </div>
                                </div>

                                <div className="my-4">
                                    <div className="flex items-baseline gap-1">
                                        <span className="text-3xl font-extrabold text-gray-900 dark:text-white">{price}</span>
                                        <span className="text-xs text-gray-500 font-semibold">
                                            {interval === "year" ? t("billing.per_year", "/ Jahr") : t("billing.per_month", "/ Monat")}
                                        </span>
                                    </div>
                                    <div className="text-[11px] text-emerald-700 dark:text-emerald-400 font-semibold mt-0.5">{p.priceSub}</div>
                                    <p className="text-xs text-gray-500 mt-2">{p.desc}</p>
                                </div>

                                <hr className="my-4 border-gray-100 dark:border-slate-800" />

                                <div className="space-y-2.5 mb-6">
                                    <div className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">
                                        {t("billing.included_features", "Enthaltene Features")}
                                    </div>
                                    {p.features.map((feat, idx) => (
                                        <div key={idx} className="flex items-start gap-2 text-xs text-gray-700 dark:text-gray-300">
                                            <span className="text-emerald-600 font-bold">✓</span>
                                            <span>{feat}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div>
                                {isCurrent ? (
                                    <div className="space-y-2">
                                        <div className="w-full py-2.5 rounded-xl bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 text-xs font-bold text-center border border-emerald-200 dark:border-emerald-800">
                                            {t("billing.current_plan", "✅ Dein aktueller Plan")}
                                        </div>
                                        {p.id !== "free" && (
                                            <button
                                                type="button"
                                                disabled={portalLoading}
                                                onClick={handleOpenStripePortal}
                                                className="w-full py-1.5 px-3 rounded-lg bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 text-[11px] font-bold transition flex items-center justify-center gap-1.5 border border-indigo-200 dark:border-indigo-800/60 cursor-pointer"
                                            >
                                                <span>⚙️</span>
                                                <span>{portalLoading ? "Verbinde..." : t("billing.manage_stripe", "Zahlungsdaten im Stripe Portal verwalten")}</span>
                                            </button>
                                        )}
                                        {p.id !== "free" && !cancelAtEnd && (
                                            <button
                                                type="button"
                                                onClick={handleCancel}
                                                className="w-full text-center text-[11px] text-gray-400 hover:text-rose-600 transition pt-1 cursor-pointer"
                                            >
                                                {t("billing.cancel_sub", "Abonnement kündigen")}
                                            </button>
                                        )}
                                    </div>
                                ) : (
                                    <button
                                        type="button"
                                        disabled={loadingPlan !== null}
                                        onClick={() => handlePlanChange(p.id)}
                                        className={`w-full py-2.5 px-4 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition shadow-xs cursor-pointer ${
                                            p.highlight
                                                ? "bg-emerald-600 hover:bg-emerald-700 text-white"
                                                : "bg-gray-900 hover:bg-black dark:bg-indigo-600 dark:hover:bg-indigo-700 text-white"
                                        }`}
                                    >
                                        {loadingPlan === p.id ? (
                                            <span>{t("billing.switching", "Wird umgestellt...")}</span>
                                        ) : (
                                            <>
                                                <span>
                                                    {p.id === "free" ? t("billing.switch_to_free", "Auf Free wechseln") : t("billing.choose_plan", "Diesen Plan wählen")}
                                                </span>
                                                <span>→</span>
                                            </>
                                        )}
                                    </button>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* GUTSCHEINCODE (DEZENT & AUFKLAPPBAR) */}
            <div className="pt-1">
                {!showCouponInput ? (
                    <div className="flex justify-center">
                        <button
                            type="button"
                            onClick={() => setShowCouponInput(true)}
                            className="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-500 hover:text-indigo-600 dark:text-gray-400 dark:hover:text-indigo-400 transition cursor-pointer py-1.5 px-3 rounded-lg hover:bg-gray-100 dark:hover:bg-slate-800"
                        >
                            <span>🎟️</span>
                            <span>{t("billing.have_coupon", "Hast du einen Gutscheincode?")}</span>
                        </button>
                    </div>
                ) : (
                    <div className="max-w-md mx-auto p-4 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-2xl shadow-xs animate-in fade-in space-y-3">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <span className="text-base">🎟️</span>
                                <span className="font-bold text-xs text-gray-900 dark:text-white">
                                    {t("billing.coupon_title", "Gutscheincode einlösen")}
                                </span>
                            </div>
                            <button
                                type="button"
                                onClick={() => {
                                    setShowCouponInput(false);
                                    setCouponMsg(null);
                                    setValidatedCoupon(null);
                                }}
                                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 text-xs font-bold px-1.5 py-0.5 rounded-md hover:bg-gray-100 dark:hover:bg-slate-800 cursor-pointer"
                                title={t("common.close", "Schließen")}
                            >
                                ✕
                            </button>
                        </div>

                        <form onSubmit={handleValidateCoupon} className="flex items-center gap-2">
                            <input
                                type="text"
                                placeholder="z. B. PRO100"
                                value={couponCode}
                                onChange={(e) => setCouponCode(e.target.value.toUpperCase())}
                                className="flex-1 bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl px-3.5 py-2 text-xs font-mono font-bold text-gray-900 dark:text-white placeholder-gray-400 focus:outline-hidden focus:ring-2 focus:ring-indigo-500 uppercase"
                                autoFocus
                            />
                            <button
                                type="submit"
                                disabled={couponLoading || !couponCode.trim()}
                                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl text-xs font-bold transition shadow-xs cursor-pointer shrink-0"
                            >
                                {couponLoading ? "..." : t("billing.check_code", "Prüfen")}
                            </button>
                        </form>

                        {/* Validierungs-Ergebnis */}
                        {validatedCoupon && (
                            <div className="p-3 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 animate-in fade-in">
                                <div className="text-xs">
                                    <div className="font-bold text-emerald-800 dark:text-emerald-300 flex items-center gap-1.5">
                                        <span>🎉</span>
                                        <span>{validatedCoupon.description}</span>
                                    </div>
                                    <div className="text-emerald-700 dark:text-emerald-400 text-[11px] mt-0.5">
                                        Code <span className="font-mono font-bold">{validatedCoupon.code}</span> schaltet deinen Tarif sofort frei.
                                    </div>
                                </div>
                                <button
                                    type="button"
                                    onClick={handleRedeemCoupon}
                                    disabled={couponLoading}
                                    className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs rounded-xl transition shadow-xs cursor-pointer shrink-0"
                                >
                                    {couponLoading ? "Wird aktiviert..." : "Jetzt aktivieren →"}
                                </button>
                            </div>
                        )}

                        {couponMsg && (
                            <div className={`text-xs font-semibold px-3 py-2 rounded-xl border ${
                                couponMsg.type === "success"
                                    ? "bg-emerald-50 text-emerald-800 border-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800"
                                    : "bg-rose-50 text-rose-800 border-rose-200 dark:bg-rose-950/60 dark:text-rose-300 dark:border-rose-800"
                            }`}>
                                {couponMsg.text}
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* AGB & DATENSCHUTZ ZUSTIMMUNG (AUDIT-PROOF) */}
            <div className="p-4 bg-slate-50 dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-2xl flex items-start gap-3">
                <input
                    type="checkbox"
                    id="terms_consent_checkbox"
                    checked={termsAccepted}
                    onChange={(e) => setTermsAccepted(e.target.checked)}
                    className="mt-0.5 w-4 h-4 rounded text-indigo-600 border-gray-300 focus:ring-indigo-500 cursor-pointer"
                />
                <label htmlFor="terms_consent_checkbox" className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed cursor-pointer">
                    Ich erkläre mich mit den <span className="font-semibold text-gray-900 dark:text-white">Allgemeinen Geschäftsbedingungen (AGB)</span>, der Widerrufsbelehrung für digitale Dienstleistungen und der <span className="font-semibold text-gray-900 dark:text-white">Datenschutzerklärung</span> von Sharegy einverstanden. Die Zustimmung wird revisionssicher dokumentiert.
                </label>
            </div>
        </div>
    );
}
