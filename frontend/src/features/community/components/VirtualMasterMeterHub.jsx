/*
# src/features/community/components/VirtualMasterMeterHub.jsx
# Virtueller Summenzähler für Mehrfamilienhäuser & Quartiere (NAP-Bilanzierung & 15m-Saldierung)
*/

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function VirtualMasterMeterHub({ tenant }) {
    const { t } = useTranslation();
    const [selectedDate, setSelectedDate] = useState(new Date().toISOString().slice(0, 10));
    const [allocationModel, setAllocationModel] = useState("dynamic");
    const [showGlossary, setShowGlossary] = useState(false);

    const virtualMeterQuery = useQuery({
        queryKey: ["community-virtual-meter", tenant?.id, selectedDate, allocationModel],
        queryFn: () => {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            return apiFetch(
                `/api/billing/community/virtual-meter/?tenant_id=${tenant?.id || ""}&date=${selectedDate}&allocation_model=${allocationModel}`,
                {
                    headers: {
                        Authorization: token ? `Bearer ${token}` : "",
                        "X-Tenant-ID": tenant?.id || "",
                    },
                }
            );
        },
        enabled: !!tenant?.id,
    });

    const data = virtualMeterQuery.data;
    const totals = data?.totals || {
        total_generation_kwh: 0,
        total_consumption_kwh: 0,
        total_shared_kwh: 0,
        total_grid_import_kwh: 0,
        total_grid_export_kwh: 0,
        self_sufficiency_rate_pct: 0,
        self_consumption_rate_pct: 0,
    };
    const members = data?.members || [];
    const timeline = data?.timeline || [];

    return (
        <div className="space-y-6">

            {/* HEADER & FILTER */}
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs">
                {(() => {
                    const isMieterstrom = tenant?.model_type === "mieterstrom";
                    const isGgv = tenant?.model_type === "ggv";
                    const headerIcon = isMieterstrom ? "🏢" : isGgv ? "⚖️" : "⚡";
                    const headerTitle = isMieterstrom 
                        ? t("master_meter.header_mieterstrom", "Gemeinsamer Hausanschluss & Mieterstrom-Summenzähler") 
                        : isGgv 
                        ? t("master_meter.header_ggv", "Messkonzept & Gebäude-Solaraufteilung (GGV)") 
                        : t("master_meter.header_sharing", "15-Minuten Bilanzierung & Virtueller Summenzähler");
                    const badgeLabel = isMieterstrom
                        ? t("master_meter.badge_mieterstrom", "🏢 § 42a EnWG Mieterstrom")
                        : isGgv
                        ? t("master_meter.badge_ggv", "⚖️ § 42b EnWG Gebäudeversorgung")
                        : t("master_meter.badge_sharing", "⚡ Regionales Energy Sharing");
                    const badgeClass = isMieterstrom
                        ? "bg-sky-500/10 text-sky-600 dark:text-sky-400 border-sky-500/20"
                        : isGgv
                        ? "bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20"
                        : "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20";
                    const subtitle = isMieterstrom
                        ? t("master_meter.sub_mieterstrom", "Vollversorgungs-Messkonzept: Viertelstundengenaue Saldierung von PV-Erzeugung, Wohnungszählern und Netz-Reststrom.")
                        : isGgv
                        ? t("master_meter.sub_ggv", "Vor-Ort-Aufteilung des Solarstroms nach Miteigentumsanteilen (MEA) ohne Reststrompflicht.")
                        : t("master_meter.sub_sharing", "Smart-Meter-Matching über das Verteilnetz: 15-Minuten Lastgang-Allokation für alle Erzeuger und Abnehmer.");

                    return (
                        <div className="flex items-start gap-3">
                            <span className="text-2xl shrink-0 mt-0.5">{headerIcon}</span>
                            <div>
                                <div className="flex flex-wrap items-center gap-2">
                                    <h2 className="text-base font-black text-slate-900 dark:text-white">
                                        {headerTitle}
                                    </h2>
                                    <span className={`shrink-0 text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border ${badgeClass}`}>
                                        {badgeLabel}
                                    </span>
                                </div>
                                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                                    {subtitle}
                                </p>
                            </div>
                        </div>
                    );
                })()}

                <div className="flex flex-wrap items-center gap-3">
                    <button
                        onClick={() => setShowGlossary(!showGlossary)}
                        className={`text-xs font-bold px-3 py-1.5 rounded-xl border transition cursor-pointer flex items-center gap-1.5 ${
                            showGlossary
                                ? "bg-amber-500/20 border-amber-500/40 text-amber-700 dark:text-amber-300"
                                : "bg-slate-100 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200"
                        }`}
                    >
                        <span>💡</span>
                        <span>{showGlossary ? t("master_meter.glossary_hide", "Erklärungen ausblenden") : t("master_meter.glossary_show", "Einfache Erklärung")}</span>
                    </button>

                    <div className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700">
                        <span className="text-xs text-slate-500">{t("master_meter.day_label", "📅 Tag:")}</span>
                        <input
                            type="date"
                            value={selectedDate}
                            onChange={(e) => setSelectedDate(e.target.value)}
                            className="bg-transparent text-xs font-semibold text-slate-800 dark:text-slate-200 focus:outline-hidden cursor-pointer"
                        />
                    </div>

                    <div className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700">
                        <span className="text-xs text-slate-500">{t("master_meter.distribution_label", "⚖️ Verteilung:")}</span>
                        <select
                            value={allocationModel}
                            onChange={(e) => setAllocationModel(e.target.value)}
                            className="bg-transparent text-xs font-semibold text-slate-800 dark:text-slate-200 focus:outline-hidden cursor-pointer"
                        >
                            <option value="dynamic">{t("master_meter.opt_dynamic", "⚡ Dynamisch (Wer gerade Strom braucht)")}</option>
                            <option value="static">{t("master_meter.opt_static", "📐 Statisch (Nach Wohnungsgröße MEA)")}</option>
                            <option value="hybrid">{t("master_meter.opt_hybrid", "🤝 Hybrid (Feste Quote + Rest teilen)")}</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* LAIEN-GLOSSAR & BEGRIFFS-ÜBERSETZER */}
            {showGlossary && (
                <div className="bg-amber-500/10 border border-amber-500/20 p-5 rounded-2xl animate-fade-in space-y-3">
                    <div className="flex items-center justify-between">
                        <h3 className="text-xs font-black uppercase tracking-wider text-amber-900 dark:text-amber-200 flex items-center gap-1.5">
                            <span>📖</span> {t("master_meter.glossary_title", "Fachbegriffe einfach erklärt (für Vermieter, WEG-Eigentümer & Mieter)")}
                        </h3>
                        <button
                            onClick={() => setShowGlossary(false)}
                            className="text-amber-700 dark:text-amber-300 text-xs font-bold hover:underline"
                        >
                            {t("master_meter.glossary_close", "Schließen ✕")}
                        </button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                        <div className="p-3 bg-white/80 dark:bg-slate-900/80 rounded-xl border border-amber-500/10">
                            <div className="font-bold text-slate-900 dark:text-white mb-1">{t("master_meter.glossary_nap_title", "🏢 Hausanschluss (NAP) & Virtueller Zähler")}</div>
                            <p className="text-slate-600 dark:text-slate-300 text-[11px] leading-relaxed">
                                {t("master_meter.glossary_nap_desc", "Statt für tausende Euro extra Zählerschränke umzubauen, rechnet Sharegy die Zählerstände der einzelnen Wohnungen alle 15 Minuten digital zusammen. So weiß man genau, ob das Gebäude gerade Solarstrom ins Netz einspeist oder Strom zukaufen muss.")}
                            </p>
                        </div>
                        <div className="p-3 bg-white/80 dark:bg-slate-900/80 rounded-xl border border-amber-500/10">
                            <div className="font-bold text-slate-900 dark:text-white mb-1">{t("master_meter.glossary_15m_title", "⏱️ 15-Minuten-Takt (§ 42b EnWG)")}</div>
                            <p className="text-slate-600 dark:text-slate-300 text-[11px] leading-relaxed">
                                {t("master_meter.glossary_15m_desc", "Das Gesetz schreibt vor, dass Erzeugung und Verbrauch in Viertelstunden-Blöcken verrechnet werden müssen. Wer zur Mittagszeit wäscht oder das E-Auto lädt, bekommt den günstigen Sonnenstrom sofort centgenau gutgeschrieben.")}
                            </p>
                        </div>
                        <div className="p-3 bg-white/80 dark:bg-slate-900/80 rounded-xl border border-amber-500/10">
                            <div className="font-bold text-slate-900 dark:text-white mb-1">{t("master_meter.glossary_models_title", "⚖️ Verteilungs-Modelle (Dynamisch vs. MEA)")}</div>
                            <p className="text-slate-600 dark:text-slate-300 text-[11px] leading-relaxed whitespace-pre-line">
                                {t("master_meter.glossary_models_desc", "Dynamisch: Wer gerade Strom verbraucht, bekommt ihn (höchste Fairness).\nStatisch (MEA): Jeder bekommt einen festen Prozentsatz nach Wohnungsgröße laut Grundbuch.\nHybrid: Fester Grundanteil, Überschüsse gehen an Nachbarn.")}
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* KPI METRICS GRID */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {/* 1. Gesamterzeugung */}
                <div className="bg-amber-500/5 dark:bg-amber-500/10 border border-amber-500/20 p-4 rounded-2xl">
                    <div className="flex items-center justify-between text-amber-600 dark:text-amber-400 text-xs font-bold mb-1">
                        <span>{t("master_meter.kpi_gen", "☀️ PV-Erzeugung")}</span>
                        <span className="text-base">🔋</span>
                    </div>
                    <div className="text-2xl font-black text-slate-900 dark:text-white">
                        {totals.total_generation_kwh.toFixed(1)} <span className="text-xs font-normal text-slate-500">kWh</span>
                    </div>
                    <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                        {t("master_meter.kpi_self_consumption", "Eigenverbrauchsquote:")} <strong className="text-amber-600 dark:text-amber-400">{totals.self_consumption_rate_pct.toFixed(1)}%</strong>
                    </div>
                </div>

                {/* 2. Gesamtverbrauch */}
                <div className="bg-rose-500/5 dark:bg-rose-500/10 border border-rose-500/20 p-4 rounded-2xl">
                    <div className="flex items-center justify-between text-rose-600 dark:text-rose-400 text-xs font-bold mb-1">
                        <span>{t("master_meter.kpi_total_cons", "🔌 Gesamtverbrauch")}</span>
                        <span className="text-base">🏠</span>
                    </div>
                    <div className="text-2xl font-black text-slate-900 dark:text-white">
                        {totals.total_consumption_kwh.toFixed(1)} <span className="text-xs font-normal text-slate-500">kWh</span>
                    </div>
                    <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                        {t("master_meter.kpi_autarky", "Autarkiegrad:")} <strong className="text-emerald-600 dark:text-emerald-400">{totals.self_sufficiency_rate_pct.toFixed(1)}%</strong>
                    </div>
                </div>

                {/* 3. Geteilter Solarstrom */}
                <div className="bg-emerald-500/5 dark:bg-emerald-500/10 border border-emerald-500/20 p-4 rounded-2xl">
                    <div className="flex items-center justify-between text-emerald-600 dark:text-emerald-400 text-xs font-bold mb-1">
                        <span>{t("master_meter.kpi_shared_green", "⚡ Geteilter Ökostrom")}</span>
                        <span className="text-base">🌱</span>
                    </div>
                    <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400">
                        {totals.total_shared_kwh.toFixed(1)} <span className="text-xs font-normal text-slate-500">kWh</span>
                    </div>
                    <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                        {t("master_meter.kpi_shared_sub", "Lokal vor Ort saldiert & verbraucht")}
                    </div>
                </div>

                {/* 4. Restnetzbezug vs. Netzeinspeisung */}
                <div className="bg-blue-500/5 dark:bg-blue-500/10 border border-blue-500/20 p-4 rounded-2xl">
                    <div className="flex items-center justify-between text-blue-600 dark:text-blue-400 text-xs font-bold mb-1">
                        <span>{t("master_meter.kpi_nap", "🌐 Netzanschlusspunkt NAP")}</span>
                        <span className="text-base">⚖️</span>
                    </div>
                    <div className="flex items-baseline gap-2">
                        <div className="text-base font-bold text-slate-900 dark:text-white">
                            +{totals.total_grid_import_kwh.toFixed(1)} <span className="text-[10px] font-normal text-slate-400">{t("common.grid_import", "Bezug")}</span>
                        </div>
                        <span className="text-slate-400">/</span>
                        <div className="text-base font-bold text-emerald-600 dark:text-emerald-400">
                            -{totals.total_grid_export_kwh.toFixed(1)} <span className="text-[10px] font-normal text-slate-400">{t("common.grid_export", "Einspeisung")}</span>
                        </div>
                    </div>
                    <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                        {t("master_meter.kpi_nap_sub", "Reststrom-Saldo über EVU")}
                    </div>
                </div>
            </div>

            {/* 15-MINUTEN NAP ZEITREIHE */}
            <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                        <span className="text-lg">📊</span>
                        <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                            {t("master_meter.timeline_title", "15-Minuten Last- und Erzeugungsprofil am virtuellen Summenzähler ({{count}} Intervalle)", { count: timeline.length })}
                        </h3>
                    </div>
                    <div className="flex items-center gap-3 text-[11px] font-semibold text-slate-500">
                        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block"></span> {t("common.generation", "Erzeugung")}</span>
                        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block"></span> {t("common.consumption", "Verbrauch")}</span>
                        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block"></span> {t("common.shared", "Geteilt")}</span>
                    </div>
                </div>

                {timeline.length === 0 ? (
                    <div className="py-12 text-center text-slate-400 text-xs">
                        {t("common.no_data", "Keine Messwerte für das gewählte Datum vorhanden.")}
                    </div>
                ) : (
                    <div className="space-y-1.5 max-h-80 overflow-y-auto pr-1">
                        {timeline.slice(-24).map((slot, idx) => (
                            <div key={idx} className="flex items-center gap-3 text-xs p-2 rounded-xl bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800 transition">
                                <span className="w-14 font-mono font-bold text-slate-500 text-[11px]">
                                    {new Date(slot.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                                </span>
                                
                                <div className="flex-1 grid grid-cols-4 gap-2 text-right">
                                    <div>
                                        <span className="text-[10px] text-slate-400 block">{t("common.generation", "Erzeugung")}</span>
                                        <span className="font-bold text-amber-600 dark:text-amber-400">{slot.generation_kwh.toFixed(2)} kWh</span>
                                    </div>
                                    <div>
                                        <span className="text-[10px] text-slate-400 block">{t("common.consumption", "Verbrauch")}</span>
                                        <span className="font-bold text-slate-800 dark:text-slate-200">{slot.consumption_kwh.toFixed(2)} kWh</span>
                                    </div>
                                    <div>
                                        <span className="text-[10px] text-slate-400 block">{t("common.shared", "Geteilt")}</span>
                                        <span className="font-bold text-emerald-600 dark:text-emerald-400">{slot.shared_solar_kwh.toFixed(2)} kWh</span>
                                    </div>
                                    <div>
                                        <span className="text-[10px] text-slate-400 block">{t("common.autarky", "Autarkie")}</span>
                                        <span className="font-bold text-indigo-600 dark:text-indigo-400">{slot.self_sufficiency_rate_pct.toFixed(0)}%</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* WOHNUNGS- & MIETER-AUFSCHLÜSSELUNG */}
            <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                        <span className="text-lg">👥</span>
                        <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                            {t("master_meter.breakdown_title", "Mieter- & Parteien-Aufschlüsselung ({{count}} Wohneinheiten)", { count: members.length })}
                        </h3>
                    </div>
                    <span className="text-xs text-slate-400">
                        {t("master_meter.breakdown_subtitle", "Saldierte Zuteilung gem. Modell \"{{model}}\"", { model: allocationModel })}
                    </span>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                        <thead>
                            <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-400 font-semibold">
                                <th className="pb-3">{t("master_meter.th_tenant", "Mieter / Partei")}</th>
                                <th className="pb-3 text-right">{t("master_meter.th_quota", "Beteiligungsquote (MEA)")}</th>
                                <th className="pb-3 text-right">{t("master_meter.th_consumption", "Verbrauch")}</th>
                                <th className="pb-3 text-right">{t("master_meter.th_solar_coverage", "Solar-Deckung")}</th>
                                <th className="pb-3 text-right">{t("master_meter.th_residual_grid", "Restnetzbezug")}</th>
                                <th className="pb-3 text-right">{t("master_meter.th_autarky", "Autarkie")}</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                            {members.map((m) => {
                                const cons = m.totals?.consumption_kwh || 0;
                                const shared = m.totals?.shared_kwh || 0;
                                const gridImp = m.totals?.grid_import_kwh || 0;
                                const autarky = cons > 0 ? (shared / cons) * 100 : 0;

                                return (
                                    <tr key={m.membership_id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition">
                                        <td className="py-3 font-semibold text-slate-900 dark:text-white">
                                            {m.name}
                                            <span className="block text-[10px] font-normal text-slate-400">{m.email}</span>
                                        </td>
                                        <td className="py-3 text-right font-mono font-bold text-slate-600 dark:text-slate-300">
                                            {m.share_percent.toFixed(1)}%
                                        </td>
                                        <td className="py-3 text-right font-mono font-semibold text-slate-800 dark:text-slate-200">
                                            {cons.toFixed(2)} kWh
                                        </td>
                                        <td className="py-3 text-right font-mono font-bold text-emerald-600 dark:text-emerald-400">
                                            {shared.toFixed(2)} kWh
                                        </td>
                                        <td className="py-3 text-right font-mono font-semibold text-rose-600 dark:text-rose-400">
                                            {gridImp.toFixed(2)} kWh
                                        </td>
                                        <td className="py-3 text-right">
                                            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                                                {autarky.toFixed(0)}%
                                            </span>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>

        </div>
    );
}
