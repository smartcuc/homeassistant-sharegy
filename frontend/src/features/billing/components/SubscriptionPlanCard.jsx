import React, { useState } from "react";
import Card from "../../../components/ui/Card";
import { apiFetch } from "../../../api/client";

export default function SubscriptionPlanCard({ subscriptionData, onRefresh }) {
    const [interval, setInterval] = useState("month");
    const [loadingPlan, setLoadingPlan] = useState(null);
    const [actionMsg, setActionMsg] = useState(null);

    const currentPlan = subscriptionData?.subscription?.plan || "free";
    const isPro = subscriptionData?.subscription?.is_pro;
    const isLandlord = subscriptionData?.subscription?.is_landlord;
    const currentPeriodEnd = subscriptionData?.subscription?.current_period_end;
    const cancelAtEnd = subscriptionData?.subscription?.cancel_at_period_end;

    const handlePlanChange = async (targetPlan) => {
        setLoadingPlan(targetPlan);
        setActionMsg(null);
        try {
            const res = await apiFetch("/api/billing/subscription/change-plan/", {
                method: "POST",
                body: JSON.stringify({ plan: targetPlan }),
            });
            if (res.status === "success") {
                setActionMsg({ type: "success", text: res.message });
                if (onRefresh) onRefresh();
            } else {
                setActionMsg({ type: "error", text: res.message || "Fehler beim Wechseln des Plans." });
            }
        } catch (err) {
            setActionMsg({ type: "error", text: "Netzwerkfehler beim Planwechsel." });
        } finally {
            setLoadingPlan(null);
        }
    };

    const handleCancel = async () => {
        if (!window.confirm("Möchtest du dein Abonnement wirklich zum Ende des Abrechnungszeitraums kündigen?")) return;
        try {
            await apiFetch("/api/billing/subscription/cancel/", {
                method: "POST",
                body: JSON.stringify({ at_period_end: true }),
            });
            if (onRefresh) onRefresh();
        } catch (err) {
            alert("Fehler beim Kündigen.");
        }
    };

    const handleReactivate = async () => {
        try {
            await apiFetch("/api/billing/subscription/reactivate/", {
                method: "POST",
            });
            if (onRefresh) onRefresh();
        } catch (err) {
            alert("Fehler beim Reaktivieren.");
        }
    };

    const plans = [
        {
            id: "free",
            name: "Sharegy Free",
            badge: "Basis",
            iconEmoji: "🛡️",
            priceMonthly: "0 €",
            priceYearly: "0 €",
            priceSub: "Dauerhaft kostenlos",
            desc: "Ideal für den Einstieg und die reine Live-Visualisierung deines Zuhauses.",
            features: [
                "Live-Sankey Energiefluss & 24h-Historie",
                "Basis-Wetter- & Solarprognose (24h)",
                "Matter 1.3 Energy Management Hub",
                "Home Assistant & Grafana Bridge",
                "Residual-Zähler & Grundlastmessung",
            ],
            current: currentPlan === "free",
        },
        {
            id: interval === "month" ? "pro_monthly" : "pro_yearly",
            name: "Sharegy Pro",
            badge: "⭐ Beliebteste Wahl",
            badgeColor: "bg-emerald-100 text-emerald-800 border-emerald-300",
            iconEmoji: "⚡",
            priceMonthly: "4,99 €",
            priceYearly: "49,99 €",
            priceSub: interval === "year" ? "entspricht 4,17 € / Monat" : "monatlich kündbar",
            desc: "Volle KI-Power, Speicher-Arbitrage und automatische Börsenpreis-Optimierung.",
            highlight: true,
            features: [
                "48h-Prognose-Trio (PV + Last + Speicher-SoC)",
                "Multi-Dauer Börsenstrom-Optimizer (1h, 2h, 4h)",
                "Batterie-Arbitrage Simulator (Netzladen)",
                "Live CO₂-Grid-Signal & Grünstrom-Index (36h)",
                "Proaktive AI-Alarmzentrale (8 Schutzregeln)",
                "Unbegrenzte Historie & Submeter-Trends",
                "Multi-Format Daten-Export (Excel, PDF, CSV)",
            ],
            current: isPro && !isLandlord,
        },
        {
            id: interval === "month" ? "landlord_monthly" : "landlord_yearly",
            name: "Vermieter & Quartiere",
            badge: "Multi-Unit",
            badgeColor: "bg-indigo-100 text-indigo-800 border-indigo-300",
            iconEmoji: "🏢",
            priceMonthly: "14,99 €",
            priceYearly: "149,99 €",
            priceSub: interval === "year" ? "entspricht 12,50 € / Monat" : "monatlich kündbar",
            desc: "Für Mehrfamilienhäuser, Vermieter und Mieterstrom-Gemeinschaften.",
            features: [
                "Alle Pro-Funktionen inklusive",
                "Multi-Home & Mehrparteien-Verwaltung",
                "Unterzähler-Abrechnungsberichte",
                "Mieterstrom-Abrechnungs-PDFs für Steuer",
                "Quartiers-Clearing & P2P-Bilanzen",
                "Prioritäts-Support mit SLA",
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
                        <div className="font-bold text-sm">Abonnement zum Periodenende gekündigt</div>
                        <div className="text-xs text-amber-700 mt-0.5">
                            Dein Zugang bleibt bis zum {currentPeriodEnd ? new Date(currentPeriodEnd).toLocaleDateString("de-DE") : "Ende der Laufzeit"} vollständig aktiv.
                        </div>
                    </div>
                    <button
                        onClick={handleReactivate}
                        className="px-3.5 py-1.5 bg-white border border-amber-300 text-amber-900 rounded-xl text-xs font-bold shadow-xs hover:bg-amber-100 transition"
                    >
                        Kündigung widerrufen
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
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-gray-200 shadow-xs">
                <div>
                    <h3 className="font-bold text-gray-900 text-base flex items-center gap-2">
                        <span>✨</span>
                        Verfügbare Tarife & Abonnement-Pläne
                    </h3>
                    <p className="text-xs text-gray-500 mt-0.5">
                        Wähle das passende Leistungspaket für dein Smart Home oder Mehrparteienhaus.
                    </p>
                </div>

                <div className="flex items-center bg-gray-100 p-1 rounded-xl self-start sm:self-auto border border-gray-200">
                    <button
                        type="button"
                        onClick={() => setInterval("month")}
                        className={`px-4 py-1.5 rounded-lg text-xs font-bold transition ${
                            interval === "month" ? "bg-white text-gray-900 shadow-xs" : "text-gray-500 hover:text-gray-900"
                        }`}
                    >
                        Monatlich
                    </button>
                    <button
                        type="button"
                        onClick={() => setInterval("year")}
                        className={`px-4 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
                            interval === "year" ? "bg-white text-emerald-800 shadow-xs" : "text-gray-500 hover:text-gray-900"
                        }`}
                    >
                        <span>Jährlich</span>
                        <span className="bg-emerald-600 text-white text-[10px] px-1.5 py-0.5 rounded-full font-extrabold uppercase">
                            -17% Rabatt
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
                                    ? "bg-gradient-to-b from-emerald-50/50 to-white border-emerald-400 ring-2 ring-emerald-500/20 shadow-md"
                                    : "bg-white border-gray-200 hover:border-gray-300 shadow-xs"
                            }`}
                        >
                            {p.badge && (
                                <span className={`absolute -top-3 right-5 text-[11px] font-extrabold px-2.5 py-0.5 rounded-full border shadow-xs ${
                                    p.badgeColor || "bg-gray-100 text-gray-700 border-gray-300"
                                }`}>
                                    {p.badge}
                                </span>
                            )}

                            <div>
                                <div className="flex items-center gap-3 mb-3">
                                    <div className="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center text-lg">
                                        {p.iconEmoji}
                                    </div>
                                    <div>
                                        <h4 className="font-bold text-gray-900 text-base">{p.name}</h4>
                                        <div className="text-[11px] text-gray-400 font-medium">SaaS Cloud</div>
                                    </div>
                                </div>

                                <div className="my-4">
                                    <div className="flex items-baseline gap-1">
                                        <span className="text-3xl font-extrabold text-gray-900">{price}</span>
                                        <span className="text-xs text-gray-500 font-semibold">/ {interval === "year" ? "Jahr" : "Monat"}</span>
                                    </div>
                                    <div className="text-[11px] text-emerald-700 font-semibold mt-0.5">{p.priceSub}</div>
                                    <p className="text-xs text-gray-500 mt-2">{p.desc}</p>
                                </div>

                                <hr className="my-4 border-gray-100" />

                                <div className="space-y-2.5 mb-6">
                                    <div className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">Enthaltene Features</div>
                                    {p.features.map((feat, idx) => (
                                        <div key={idx} className="flex items-start gap-2 text-xs text-gray-700">
                                            <span className="text-emerald-600 font-bold">✓</span>
                                            <span>{feat}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div>
                                {isCurrent ? (
                                    <div className="space-y-2">
                                        <div className="w-full py-2.5 rounded-xl bg-emerald-100 text-emerald-800 text-xs font-bold text-center border border-emerald-200">
                                            ✅ Dein aktueller Plan
                                        </div>
                                        {p.id !== "free" && !cancelAtEnd && (
                                            <button
                                                type="button"
                                                onClick={handleCancel}
                                                className="w-full text-center text-[11px] text-gray-400 hover:text-rose-600 transition pt-1"
                                            >
                                                Abonnement kündigen
                                            </button>
                                        )}
                                    </div>
                                ) : (
                                    <button
                                        type="button"
                                        disabled={loadingPlan !== null}
                                        onClick={() => handlePlanChange(p.id)}
                                        className={`w-full py-2.5 px-4 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition shadow-xs ${
                                            p.highlight
                                                ? "bg-emerald-600 hover:bg-emerald-700 text-white"
                                                : "bg-gray-900 hover:bg-black text-white"
                                        }`}
                                    >
                                        {loadingPlan === p.id ? (
                                            <span>Wird umgestellt...</span>
                                        ) : (
                                            <>
                                                <span>{p.id === "free" ? "Auf Free wechseln" : "Diesen Plan wählen"}</span>
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
        </div>
    );
}
