/*
# src/features/energy/components/VppCustomerParticipationCard.jsx
# Endkunden-Cockpit: VPP-Teilnahme, Flexibilitäts-Bonus, Reserve-SoC & Auszahlungshistorie
*/

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function VppCustomerParticipationCard() {
    const { t } = useTranslation();
    const queryClient = useQueryClient();

    const [isOptingIn, setIsOptingIn] = useState(false);
    const [selectedDevice, setSelectedDevice] = useState("");
    const [reserveSoc, setReserveSoc] = useState(25);
    const [autoSpot, setAutoSpot] = useState(true);
    const [autoAfrr, setAutoAfrr] = useState(true);
    const [activeTab, setActiveTab] = useState("overview"); // "overview" | "dispatches" | "statements"

    // 1. User Earnings & Participation Query
    const earningsQuery = useQuery({
        queryKey: ["vpp-user-earnings"],
        queryFn: () => {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            return apiFetch("/api/vpp/earnings/", {
                headers: { Authorization: token ? `Bearer ${token}` : "" },
            });
        },
        refetchInterval: 15000,
    });

    // 2. User Devices Query (for enrolling new batteries)
    const devicesQuery = useQuery({
        queryKey: ["user-battery-devices"],
        queryFn: () => {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            return apiFetch("/api/devices/", {
                headers: { Authorization: token ? `Bearer ${token}` : "" },
            });
        },
    });

    // 3. Enroll Mutation
    const enrollMutation = useMutation({
        mutationFn: async () => {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            return apiFetch("/api/vpp/enrollments/", {
                method: "POST",
                headers: {
                    Authorization: token ? `Bearer ${token}` : "",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    device_id: Number(selectedDevice),
                    min_soc_reserve_pct: Number(reserveSoc),
                    auto_spot_arbitrage: autoSpot,
                    auto_afrr_frequency: autoAfrr,
                }),
            });
        },
        onSuccess: () => {
            setIsOptingIn(false);
            queryClient.invalidateQueries(["vpp-user-earnings"]);
        },
    });

    // 4. Update Status Mutation
    const updateStatusMutation = useMutation({
        mutationFn: async ({ enrollmentId, status, min_soc_reserve_pct }) => {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            return apiFetch(`/api/vpp/enrollments/${enrollmentId}/`, {
                method: "PATCH",
                headers: {
                    Authorization: token ? `Bearer ${token}` : "",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ status, min_soc_reserve_pct }),
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries(["vpp-user-earnings"]);
        },
    });

    const data = earningsQuery.data || {
        is_participating: false,
        enrolled_devices_count: 0,
        active_devices_count: 0,
        total_earned_eur: 0,
        estimated_annual_eur: 0,
        total_dispatches_count: 0,
        co2_saved_kg: 0,
        enrollments: [],
        recent_dispatches: [],
        statements: [],
    };

    const batteryDevices = (devicesQuery.data || []).filter(
        (d) => d.role?.key === "battery" || d.config?.role?.key === "battery" || d.name?.toLowerCase().includes("speicher") || d.name?.toLowerCase().includes("battery")
    );

    return (
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden transition-all">
            {/* CARD HEADER */}
            <div className="p-5 border-b border-slate-100 dark:border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gradient-to-r from-emerald-500/5 via-teal-500/5 to-transparent">
                <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold text-xl shrink-0">
                        ⚡
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h3 className="text-base font-black text-slate-900 dark:text-white">
                                Virtuelles Kraftwerk (VPP) Flexibilitäts-Bonus
                            </h3>
                            {data.is_participating && (
                                <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
                                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                                    Aktiv vergütet (80 % Split)
                                </span>
                            )}
                        </div>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                            Stelle freie Speicherkapazität zur Netzstabilisierung bereit und erhalte automatische Gutschriften auf deine Stromrechnung.
                        </p>
                    </div>
                </div>

                {/* ACTION CTA */}
                {!data.is_participating && !isOptingIn && (
                    <button
                        onClick={() => {
                            if (batteryDevices.length > 0) setSelectedDevice(batteryDevices[0].id);
                            setIsOptingIn(true);
                        }}
                        className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl shadow-xs transition-all flex items-center justify-center gap-1.5 shrink-0"
                    >
                        <span>✨</span>
                        <span>Jetzt teilnehmen & bis zu 250 €/Jahr sichern</span>
                    </button>
                )}
            </div>

            {/* OPT-IN MODAL / FORM INLINE */}
            {isOptingIn && (
                <div className="p-5 bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800 space-y-4">
                    <div className="flex items-center justify-between">
                        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                            Speicher für VPP-Regelenergie freischalten
                        </h4>
                        <button
                            onClick={() => setIsOptingIn(false)}
                            className="text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                        >
                            ✕ Abbrechen
                        </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-1">
                                Batteriespeicher auswählen
                            </label>
                            <select
                                value={selectedDevice}
                                onChange={(e) => setSelectedDevice(e.target.value)}
                                className="w-full text-xs font-semibold px-3 py-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-xl"
                            >
                                {batteryDevices.length > 0 ? (
                                    batteryDevices.map((d) => (
                                        <option key={d.id} value={d.id}>
                                            {d.name || `Speicher #${d.id}`}
                                        </option>
                                    ))
                                ) : (
                                    <option value="">Kein Heimspeicher gefunden</option>
                                )}
                            </select>
                        </div>

                        <div>
                            <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-1">
                                Haus-Reserve SoC: <span className="text-emerald-600 font-extrabold">{reserveSoc} %</span>
                            </label>
                            <input
                                type="range"
                                min="10"
                                max="50"
                                step="5"
                                value={reserveSoc}
                                onChange={(e) => setReserveSoc(Number(e.target.value))}
                                className="w-full accent-emerald-600 cursor-pointer mt-2"
                            />
                            <p className="text-[10px] text-slate-400 mt-1">
                                Dieser Ladestand bleibt garantiert immer für deinen Eigenverbrauch geschützt.
                            </p>
                        </div>

                        <div className="space-y-2">
                            <label className="flex items-center gap-2 text-xs text-slate-700 dark:text-slate-300 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={autoSpot}
                                    onChange={(e) => setAutoSpot(e.target.checked)}
                                    className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                                />
                                <span>Börsenpreis-Arbitrage (Preistiefststände)</span>
                            </label>
                            <label className="flex items-center gap-2 text-xs text-slate-700 dark:text-slate-300 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={autoAfrr}
                                    onChange={(e) => setAutoAfrr(e.target.checked)}
                                    className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                                />
                                <span>Sekundärregelleistung (aFRR Frequenz)</span>
                            </label>
                        </div>
                    </div>

                    <div className="flex justify-end pt-2">
                        <button
                            onClick={() => enrollMutation.mutate()}
                            disabled={enrollMutation.isPending || !selectedDevice}
                            className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl shadow-xs transition-all disabled:opacity-50"
                        >
                            {enrollMutation.isPending ? "Wird aktiviert..." : "Kostenfrei aktivieren & Prämie sichern"}
                        </button>
                    </div>
                </div>
            )}

            {/* KPIS OVERVIEW */}
            <div className="p-5 grid grid-cols-2 lg:grid-cols-4 gap-4 bg-slate-50/50 dark:bg-slate-900/40">
                <div className="bg-white dark:bg-slate-800/80 p-4 rounded-xl border border-slate-200/80 dark:border-slate-700/80 shadow-2xs">
                    <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                        Bisherige Erlöse
                    </span>
                    <div className="flex items-baseline gap-1 mt-1">
                        <span className="text-2xl font-black text-emerald-600 dark:text-emerald-400">
                            {data.total_earned_eur.toFixed(2)}
                        </span>
                        <span className="text-xs font-bold text-slate-400">€</span>
                    </div>
                    <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-semibold block mt-0.5">
                        ✓ Direkt gutgeschrieben
                    </span>
                </div>

                <div className="bg-white dark:bg-slate-800/80 p-4 rounded-xl border border-slate-200/80 dark:border-slate-700/80 shadow-2xs">
                    <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                        Prognose / Jahr
                    </span>
                    <div className="flex items-baseline gap-1 mt-1">
                        <span className="text-2xl font-black text-slate-900 dark:text-white">
                            ~{data.estimated_annual_eur.toFixed(0)}
                        </span>
                        <span className="text-xs font-bold text-slate-400">€/a</span>
                    </div>
                    <span className="text-[10px] text-slate-400 font-medium block mt-0.5">
                        Basierend auf Marktprämien
                    </span>
                </div>

                <div className="bg-white dark:bg-slate-800/80 p-4 rounded-xl border border-slate-200/80 dark:border-slate-700/80 shadow-2xs">
                    <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                        Erfolgreiche Abrufe
                    </span>
                    <div className="flex items-baseline gap-1 mt-1">
                        <span className="text-2xl font-black text-slate-900 dark:text-white">
                            {data.total_dispatches_count}
                        </span>
                        <span className="text-xs font-bold text-slate-400">Events</span>
                    </div>
                    <span className="text-[10px] text-slate-400 font-medium block mt-0.5">
                        Sekundärregelleistung & Arbitrage
                    </span>
                </div>

                <div className="bg-white dark:bg-slate-800/80 p-4 rounded-xl border border-slate-200/80 dark:border-slate-700/80 shadow-2xs">
                    <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                        Eingeschriebene Geräte
                    </span>
                    <div className="flex items-baseline gap-1 mt-1">
                        <span className="text-2xl font-black text-slate-900 dark:text-white">
                            {data.active_devices_count}
                        </span>
                        <span className="text-xs font-bold text-slate-400">von {data.enrolled_devices_count}</span>
                    </div>
                    <span className="text-[10px] text-emerald-600 font-semibold block mt-0.5">
                        🌱 {data.co2_saved_kg} kg CO₂ vermieden
                    </span>
                </div>
            </div>

            {/* TAB NAVIGATION */}
            {data.is_participating && (
                <div className="border-t border-slate-200 dark:border-slate-800">
                    <div className="flex items-center gap-2 px-5 pt-3 bg-white dark:bg-slate-900 border-b border-slate-100 dark:border-slate-800">
                        <button
                            onClick={() => setActiveTab("overview")}
                            className={`pb-2.5 text-xs font-bold transition-all border-b-2 ${
                                activeTab === "overview"
                                    ? "border-emerald-600 text-emerald-600 dark:text-emerald-400"
                                    : "border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
                            }`}
                        >
                            Meine VPP-Assets ({data.enrollments.length})
                        </button>
                        <button
                            onClick={() => setActiveTab("dispatches")}
                            className={`pb-2.5 text-xs font-bold transition-all border-b-2 ${
                                activeTab === "dispatches"
                                    ? "border-emerald-600 text-emerald-600 dark:text-emerald-400"
                                    : "border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
                            }`}
                        >
                            Letzte Abrufe & Vergütung
                        </button>
                        <button
                            onClick={() => setActiveTab("statements")}
                            className={`pb-2.5 text-xs font-bold transition-all border-b-2 ${
                                activeTab === "statements"
                                    ? "border-emerald-600 text-emerald-600 dark:text-emerald-400"
                                    : "border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
                            }`}
                        >
                            Monatliche Abrechnungen ({data.statements.length})
                        </button>
                    </div>

                    <div className="p-5">
                        {/* TAB 1: ASSETS */}
                        {activeTab === "overview" && (
                            <div className="space-y-3">
                                {data.enrollments.map((e) => (
                                    <div
                                        key={e.id}
                                        className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700/60"
                                    >
                                        <div>
                                            <div className="flex items-center gap-2">
                                                <span className="text-sm font-bold text-slate-900 dark:text-white">
                                                    {e.device_name}
                                                </span>
                                                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                                                    e.status === "active"
                                                        ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
                                                        : "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300"
                                                }`}>
                                                    {e.status === "active" ? "Bereit für Regelenergie" : "Pausiert"}
                                                </span>
                                            </div>
                                            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                                                Pool: <strong className="text-slate-700 dark:text-slate-300">{e.pool_name}</strong> | Mindest-Reserve: <strong className="text-emerald-600">{e.min_soc_reserve_pct} %</strong> | Erlös-Split: <strong className="text-slate-700 dark:text-slate-300">{e.payout_share_pct} %</strong>
                                            </p>
                                        </div>

                                        <div className="flex items-center gap-2 shrink-0">
                                            <span className="text-xs font-black text-emerald-600 dark:text-emerald-400 mr-2">
                                                +{e.total_earned_eur.toFixed(2)} €
                                            </span>
                                            {e.status === "active" ? (
                                                <button
                                                    onClick={() => updateStatusMutation.mutate({ enrollmentId: e.id, status: "paused" })}
                                                    className="px-3 py-1.5 text-xs font-semibold bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-600 transition-all"
                                                >
                                                    Pausieren
                                                </button>
                                            ) : (
                                                <button
                                                    onClick={() => updateStatusMutation.mutate({ enrollmentId: e.id, status: "active" })}
                                                    className="px-3 py-1.5 text-xs font-semibold bg-emerald-600 text-white rounded-lg hover:bg-emerald-500 transition-all"
                                                >
                                                    Aktivieren
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}

                        {/* TAB 2: DISPATCHES */}
                        {activeTab === "dispatches" && (
                            <div className="overflow-x-auto">
                                <table className="w-full text-left text-xs">
                                    <thead>
                                        <tr className="border-b border-slate-200 dark:border-slate-700 text-slate-400 uppercase text-[10px] font-bold">
                                            <th className="pb-2">Zeitpunkt</th>
                                            <th className="pb-2">Gerät</th>
                                            <th className="pb-2">Abruf-Typ</th>
                                            <th className="pb-2">Leistung</th>
                                            <th className="pb-2">Energie</th>
                                            <th className="pb-2 text-right">Vergütung (80%)</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                                        {data.recent_dispatches.length > 0 ? (
                                            data.recent_dispatches.map((d) => (
                                                <tr key={d.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                                                    <td className="py-2.5 text-slate-500">
                                                        {new Date(d.timestamp).toLocaleString("de-DE", {
                                                            day: "2-digit",
                                                            month: "2-digit",
                                                            hour: "2-digit",
                                                            minute: "2-digit",
                                                        })}
                                                    </td>
                                                    <td className="py-2.5 font-bold text-slate-900 dark:text-white">
                                                        {d.device_name}
                                                    </td>
                                                    <td className="py-2.5 text-slate-600 dark:text-slate-300">
                                                        {d.dispatch_type}
                                                    </td>
                                                    <td className="py-2.5 font-mono text-slate-700 dark:text-slate-300">
                                                        {d.delivered_power_kw.toFixed(1)} kW
                                                    </td>
                                                    <td className="py-2.5 font-mono text-slate-700 dark:text-slate-300">
                                                        {d.energy_kwh.toFixed(3)} kWh
                                                    </td>
                                                    <td className="py-2.5 text-right font-black text-emerald-600 dark:text-emerald-400">
                                                        +{d.customer_payout_eur.toFixed(2)} €
                                                    </td>
                                                </tr>
                                            ))
                                        ) : (
                                            <tr>
                                                <td colSpan="6" className="py-4 text-center text-slate-400">
                                                    Noch keine Abrufe für diesen Speicher verzeichnet.
                                                </td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        )}

                        {/* TAB 3: STATEMENTS */}
                        {activeTab === "statements" && (
                            <div className="space-y-3">
                                {data.statements.length > 0 ? (
                                    data.statements.map((s) => (
                                        <div
                                            key={s.id}
                                            className="flex items-center justify-between p-3.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700/60"
                                        >
                                            <div>
                                                <span className="text-xs font-bold text-slate-900 dark:text-white block">
                                                    Abrechnung {s.period}
                                                </span>
                                                <span className="text-[11px] text-slate-500 dark:text-slate-400 font-mono">
                                                    Ref: {s.payment_reference} • {s.dispatches_count} Events • {s.total_energy_kwh.toFixed(2)} kWh
                                                </span>
                                            </div>
                                            <div className="text-right">
                                                <span className="text-sm font-black text-emerald-600 dark:text-emerald-400 block">
                                                    +{s.customer_payout_eur.toFixed(2)} €
                                                </span>
                                                <span className="text-[10px] font-bold text-slate-400">
                                                    ✓ {s.status}
                                                </span>
                                            </div>
                                        </div>
                                    ))
                                ) : (
                                    <p className="text-xs text-slate-400 text-center py-4">
                                        Die erste Monatsabrechnung wird zum Monatsende automatisch generiert.
                                    </p>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
