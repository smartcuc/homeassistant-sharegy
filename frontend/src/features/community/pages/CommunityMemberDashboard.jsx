/*
# src/features/community/pages/CommunityMemberDashboard.jsx
# Dediziertes Endnutzer-Cockpit für Teilnehmer einer Energiegemeinschaft / Mieterstrom
*/

import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";
import { useUser } from "../../../hooks/useUser";
import CommunityShareModal from "../components/CommunityShareModal";

export default function CommunityMemberDashboard() {
    const { t } = useTranslation();
    const { user } = useUser();

    const [loading, setLoading] = useState(true);
    const [tenant, setTenant] = useState(null);
    const [cockpit, setCockpit] = useState(null);
    const [tariffData, setTariffData] = useState(null);
    const [statementsData, setStatementsData] = useState(null);
    const [timeRange, setTimeRange] = useState("today"); // 'today' | 'month'
    const [shareModalOpen, setShareModalOpen] = useState(false);
    const [downloadingId, setDownloadingId] = useState(null);

    async function loadData() {
        setLoading(true);
        try {
            const data = await apiFetch("/api/my-tenant/");
            setTenant(data?.tenant || null);

            if (data?.tenant) {
                const [cockpitRes, tariffsRes, statementsRes] = await Promise.all([
                    apiFetch("/api/billing/community/cockpit/").catch(() => null),
                    apiFetch("/api/billing/community/tariffs/").catch(() => null),
                    apiFetch("/api/billing/community/statements/").catch(() => null),
                ]);

                setCockpit(cockpitRes);
                setTariffData(tariffsRes);
                setStatementsData(statementsRes);
            }
        } catch (err) {
            console.error("Failed to load community member data:", err);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadData();
    }, []);

    // PDF Download
    async function downloadStatementPdf(statementId, statementNumber) {
        setDownloadingId(statementId);
        try {
            const response = await fetch(`/api/billing/community/statements/${statementId}/pdf/`, {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("token") || sessionStorage.getItem("token") || ""}`,
                },
            });

            if (!response.ok) {
                throw new Error("Download fehlgeschlagen");
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `Abrechnungsnachweis_${statementNumber || statementId}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error("PDF Download error:", err);
            alert("Fehler beim Herunterladen des Abrechnungsnachweises als PDF.");
        } finally {
            setDownloadingId(null);
        }
    }

    if (loading) {
        return (
            <div className="p-12 text-center text-slate-400 text-sm animate-pulse max-w-7xl mx-auto">
                <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
                Lade dein Community Sharing Cockpit...
            </div>
        );
    }

    if (!tenant) {
        return (
            <div className="p-8 max-w-xl mx-auto text-center space-y-4 my-12 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl shadow-sm">
                <div className="w-16 h-16 rounded-3xl bg-amber-500/10 text-amber-600 flex items-center justify-center text-3xl mx-auto">
                    🏛️
                </div>
                <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                    Keine aktive Energiegemeinschaft
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                    Du bist aktuell noch keiner Energiegemeinschaft oder keinem Mieterstrom-Projekt zugewiesen. Sobald du einen Einladungslink einlöst, findest du deine Bilanzen und Nachweise hier.
                </p>
                <div className="pt-2">
                    <button
                        onClick={() => window.location.href = "/app/dashboard"}
                        className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-xs transition cursor-pointer"
                    >
                        Zurück zum Dashboard
                    </button>
                </div>
            </div>
        );
    }

    const currentStats = cockpit ? (timeRange === "today" ? cockpit.today : cockpit.month) : null;
    const activeTariff = tariffData ? tariffData.active_tariff : null;
    const statements = statementsData?.statements || [];

    // Berechne persönliche Summen über alle vorliegenden Nachweise
    const myTotalSharedImportKwh = statements.reduce((acc, s) => acc + Number(s.shared_imported_kwh || 0), 0);
    const myTotalSharedExportKwh = statements.reduce((acc, s) => acc + Number(s.shared_exported_kwh || 0), 0);
    const myTotalGridResidualImportKwh = statements.reduce((acc, s) => acc + Number(s.grid_residual_import_kwh || 0), 0);
    const myTotalProducedKwh = statements.reduce((acc, s) => acc + Number(s.produced_total_kwh || 0), 0);
    const myTotalConsumedKwh = statements.reduce((acc, s) => acc + Number(s.consumed_total_kwh || 0), 0);

    const myTotalExportCreditEur = statements.reduce((acc, s) => acc + Number(s.credit_shared_export_eur || 0), 0);
    const myTotalImportChargeEur = statements.reduce((acc, s) => acc + Number(s.charge_shared_import_eur || 0), 0);
    const myTotalNetBalanceEur = statements.reduce((acc, s) => acc + Number(s.net_balance_eur || 0), 0);

    // Rollenbestimmung im Energy Sharing
    const isProsumer = myTotalSharedExportKwh > 0 || myTotalProducedKwh > 0;
    const isConsumer = myTotalSharedImportKwh > 0 || myTotalConsumedKwh > 0 || !isProsumer;

    const [memberPerspective, setMemberPerspective] = useState(
        isProsumer && !isConsumer ? "prosumer" : isConsumer && !isProsumer ? "consumer" : "all"
    );

    // Ersparnis vs. Grundversorger (~38 Ct/kWh Grundversorger vs ~18 Ct/kWh Sharing)
    const estimatedSavingsEur = myTotalSharedImportKwh * 0.20;
    // Mehrerlös Prosumer vs. reine EEG-Einspeisung (~10 Ct Sharing vs ~7 Ct EEG = 3 Ct Vorteil)
    const estimatedProducerBonusEur = myTotalSharedExportKwh * 0.03;

    return (
        <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-6">

            {/* 1. HEADER MIT GEMEINSCHAFTS-STATUS & MODELL-UNTERSCHEIDUNG */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-6 shadow-2xs space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex items-start gap-3.5">
                        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-amber-400 to-amber-600 text-white flex items-center justify-center text-2xl shadow-sm shrink-0 mt-0.5">
                            ⚡
                        </div>
                        <div>
                            <div className="flex flex-wrap items-center gap-2.5">
                                <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white">
                                    {tenant.name}
                                </h1>
                                <span className="bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-xs font-bold px-3 py-1 rounded-full border border-emerald-500/20 flex items-center gap-1.5">
                                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                                    {t("tenant.community_active", "Energy Sharing Aktiv")}
                                </span>
                                <span className="bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 text-xs font-bold px-3 py-1 rounded-full border border-indigo-500/20">
                                    {isProsumer && isConsumer
                                        ? "⚡ Prosumer & Consumer"
                                        : isProsumer
                                        ? "☀️ Prosumer (Einspeiser)"
                                        : "🔌 Consumer (Abnehmer)"}
                                </span>
                            </div>
                            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
                                Dein persönliches Cockpit für geteilten Solarstrom im regionalen Verteilnetz
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2.5 self-start sm:self-auto">
                        <a
                            href="/app/help/mieterstrom-ggv-und-energy-sharing-unterschiede"
                            className="px-3.5 py-2 rounded-xl text-xs font-bold bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 transition flex items-center gap-1.5"
                        >
                            <span>📖</span>
                            <span>Handbuch: Mieterstrom vs. GGV vs. Sharing</span>
                        </a>

                        <button
                            type="button"
                            onClick={() => setShareModalOpen(true)}
                            className="px-4 py-2 rounded-xl text-xs font-bold bg-emerald-50 dark:bg-emerald-950/40 hover:bg-emerald-100 dark:hover:bg-emerald-900/60 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800/80 transition shadow-xs flex items-center gap-2 cursor-pointer"
                        >
                            <span>📢</span>
                            <span>{t("tenant.share_btn", "Erfolge teilen")}</span>
                        </button>
                    </div>
                </div>

                {/* 🌟 ENERGIE-MODELL ERKLÄRBOX */}
                <div className="p-4 rounded-2xl bg-indigo-50/70 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900/50 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                    <div className="flex items-start gap-3 text-indigo-950 dark:text-indigo-200">
                        <span className="text-xl shrink-0 mt-0.5">⚖️</span>
                        <div className="space-y-0.5">
                            <div className="font-bold flex items-center gap-2">
                                <span>Regionales Energy Sharing (Bürgerenergie & Verteilnetz-Allokation)</span>
                                <span className="text-[10px] bg-indigo-200/60 dark:bg-indigo-800/60 text-indigo-900 dark:text-indigo-200 px-2 py-0.5 rounded-md font-mono font-semibold">
                                    15m Smart-Meter-Bilanzierung
                                </span>
                            </div>
                            <div className="text-indigo-700/80 dark:text-indigo-300/80 text-[11px] leading-relaxed">
                                Prosumer speisen überschüssigen Solarstrom in die Gemeinschaft ein – Consumer beziehen ihn bilanziell vor Ort. Reststrom beziehst du weiterhin unabhängig über deinen bestehenden Stromversorger.
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* 2. DIE GEMEINSCHAFT IM ÜBERBLICK */}
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                            <span>🏘️</span> Die Energiegemeinschaft im Überblick
                        </h2>
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                            Gesamterzeugung der Prosumer-Anlagen und geteilter Strom aller Teilnehmer
                        </p>
                    </div>

                    <div className="flex bg-slate-100 dark:bg-slate-800 p-0.5 rounded-xl text-xs font-semibold">
                        <button
                            onClick={() => setTimeRange("today")}
                            className={`px-3 py-1 rounded-lg transition cursor-pointer ${
                                timeRange === "today"
                                    ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs"
                                    : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                            }`}
                        >
                            Heute
                        </button>
                        <button
                            onClick={() => setTimeRange("month")}
                            className={`px-3 py-1 rounded-lg transition cursor-pointer ${
                                timeRange === "month"
                                    ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs"
                                    : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                            }`}
                        >
                            Dieser Monat
                        </button>
                    </div>
                </div>

                {/* 4 Community KPI Cards */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5">
                    {/* Solar-Erzeugung Prosumer-Pool */}
                    <div className="bg-amber-500/5 dark:bg-amber-500/10 border border-amber-500/20 rounded-2xl p-4 flex flex-col justify-between">
                        <div className="flex items-center justify-between">
                            <span className="text-[11px] font-bold text-amber-700 dark:text-amber-300 uppercase tracking-wider">
                                Prosumer Erzeugung
                            </span>
                            <span className="text-lg">☀️</span>
                        </div>
                        <div className="mt-3">
                            <div className="text-2xl font-black text-amber-900 dark:text-amber-100">
                                {Number(currentStats?.produced_kwh ?? 0).toFixed(1)} <span className="text-xs font-normal">kWh</span>
                            </div>
                            <div className="text-[11px] text-amber-700/80 dark:text-amber-300/80 mt-0.5">
                                Solarertrag aller Erzeuger im Pool
                            </div>
                        </div>
                    </div>

                    {/* Geteilter Strom (Sharing) */}
                    <div className="bg-emerald-500/5 dark:bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-4 flex flex-col justify-between">
                        <div className="flex items-center justify-between">
                            <span className="text-[11px] font-bold text-emerald-700 dark:text-emerald-300 uppercase tracking-wider">
                                Geteilter Strom
                            </span>
                            <span className="text-lg">🤝</span>
                        </div>
                        <div className="mt-3">
                            <div className="text-2xl font-black text-emerald-900 dark:text-emerald-100">
                                {Number(currentStats?.shared_kwh ?? 0).toFixed(1)} <span className="text-xs font-normal">kWh</span>
                            </div>
                            <div className="text-[11px] text-emerald-700/80 dark:text-emerald-300/80 mt-0.5">
                                Bilanziell im Netzgebiet geteilt
                            </div>
                        </div>
                    </div>

                    {/* Gemeinschaftsbedarf */}
                    <div className="bg-sky-500/5 dark:bg-sky-500/10 border border-sky-500/20 rounded-2xl p-4 flex flex-col justify-between">
                        <div className="flex items-center justify-between">
                            <span className="text-[11px] font-bold text-sky-700 dark:text-sky-300 uppercase tracking-wider">
                                Gesamtbedarf
                            </span>
                            <span className="text-lg">🏠</span>
                        </div>
                        <div className="mt-3">
                            <div className="text-2xl font-black text-sky-900 dark:text-sky-100">
                                {Number(currentStats?.consumed_kwh ?? 0).toFixed(1)} <span className="text-xs font-normal">kWh</span>
                            </div>
                            <div className="text-[11px] text-sky-700/80 dark:text-sky-300/80 mt-0.5">
                                Stromverbrauch aller Teilnehmer
                            </div>
                        </div>
                    </div>

                    {/* Community Autarkiegrad */}
                    <div className="bg-purple-500/5 dark:bg-purple-500/10 border border-purple-500/20 rounded-2xl p-4 flex flex-col justify-between">
                        <div className="flex items-center justify-between">
                            <span className="text-[11px] font-bold text-purple-700 dark:text-purple-300 uppercase tracking-wider">
                                Autarkiegrad
                            </span>
                            <span className="text-lg">🌱</span>
                        </div>
                        <div className="mt-3">
                            <div className="text-2xl font-black text-purple-900 dark:text-purple-100">
                                {Number(currentStats?.autarky_pct ?? 0).toFixed(0)} <span className="text-xs font-normal">%</span>
                            </div>
                            <div className="text-[11px] text-purple-700/80 dark:text-purple-300/80 mt-0.5">
                                Deckung aus eigenem Pool
                            </div>
                        </div>
                    </div>
                </div>

                {/* 48H WETTER- & KI-SOLARPROGNOSE */}
                {cockpit?.forecast_48h && cockpit.forecast_48h.length > 0 && (
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-2xs space-y-3">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <span className="text-base">🌤️</span>
                                <h3 className="text-xs font-bold text-slate-800 dark:text-slate-200">
                                    48h Solar-Verfügbarkeit & Wetterprognose
                                </h3>
                            </div>
                            <span className="text-[11px] text-slate-400">
                                Günstigste Fenster für Verbraucher & flexible Lasten
                            </span>
                        </div>

                        <div className="grid grid-cols-4 sm:grid-cols-8 gap-2">
                            {cockpit.forecast_48h.slice(0, 8).map((slot, idx) => {
                                const isPeak = slot.expected_pv_kwh > 2.0;
                                return (
                                    <div
                                        key={idx}
                                        className={`p-2.5 rounded-xl border text-center transition ${
                                            isPeak
                                                ? "bg-amber-50 dark:bg-amber-950/40 border-amber-300 dark:border-amber-700/60 text-amber-900 dark:text-amber-200 font-bold"
                                                : "bg-slate-50 dark:bg-slate-800/40 border-slate-200/60 dark:border-slate-800 text-slate-600 dark:text-slate-300"
                                        }`}
                                    >
                                        <div className="text-[10px] opacity-70">
                                            {new Date(slot.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                        </div>
                                        <div className="text-xs font-extrabold mt-1">
                                            {slot.expected_pv_kwh.toFixed(1)} <span className="text-[9px] font-normal">kW</span>
                                        </div>
                                        {isPeak && <div className="text-[9px] text-amber-600 dark:text-amber-400 mt-0.5">☀️ Solar-Peak</div>}
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}
            </div>

            {/* 3. MEIN PERSÖNLICHER BEITRAG (PROSUMER & CONSUMER PERSPEKTIVE) */}
            <div className="space-y-4 pt-2">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                        <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                            <span>👤</span> Mein persönlicher Beitrag & Nutzen
                        </h2>
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                            Deine Einspeise- und Verbrauchsdaten aus der 15-Minuten-Bilanzierung
                        </p>
                    </div>

                    {/* PERSPEKTIVEN UMSCHALTER */}
                    <div className="flex bg-slate-100 dark:bg-slate-800 p-0.5 rounded-xl text-xs font-semibold gap-1">
                        <button
                            onClick={() => setMemberPerspective("all")}
                            className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                                memberPerspective === "all"
                                    ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs font-bold"
                                    : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                            }`}
                        >
                            ⚡ Gesamtbilanz
                        </button>
                        <button
                            onClick={() => setMemberPerspective("prosumer")}
                            className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                                memberPerspective === "prosumer"
                                    ? "bg-white dark:bg-slate-900 text-amber-600 dark:text-amber-400 shadow-xs font-bold"
                                    : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                            }`}
                        >
                            ☀️ Prosumer (Einspeisung)
                        </button>
                        <button
                            onClick={() => setMemberPerspective("consumer")}
                            className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                                memberPerspective === "consumer"
                                    ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs font-bold"
                                    : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                            }`}
                        >
                            🔌 Consumer (Bezug)
                        </button>
                    </div>
                </div>

                {/* DYNAMISCHE KARTEN JE NACH PERSPEKTIVE */}
                {(memberPerspective === "all" || memberPerspective === "prosumer") && (
                    <div className="space-y-2">
                        <div className="text-xs font-bold text-amber-700 dark:text-amber-300 uppercase tracking-wider flex items-center gap-1.5">
                            <span>☀️</span> Meine Prosumer-Einspeisung in die Community
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                            <div className="bg-gradient-to-br from-amber-500/10 to-amber-600/5 border border-amber-500/20 rounded-2xl p-5">
                                <div className="text-[11px] font-bold text-amber-700 dark:text-amber-300 uppercase">
                                    Geteilter Solarstrom
                                </div>
                                <div className="text-3xl font-black text-amber-900 dark:text-amber-100 mt-2">
                                    {myTotalSharedExportKwh.toFixed(1)} <span className="text-sm font-normal">kWh</span>
                                </div>
                                <div className="text-xs text-amber-600 dark:text-amber-400 mt-1">
                                    Überschuss mit Nachbarn geteilt
                                </div>
                            </div>

                            <div className="bg-gradient-to-br from-emerald-500/10 to-emerald-600/5 border border-emerald-500/20 rounded-2xl p-5">
                                <div className="text-[11px] font-bold text-emerald-700 dark:text-emerald-300 uppercase">
                                    Meine Sharing-Erlöse
                                </div>
                                <div className="text-3xl font-black text-emerald-900 dark:text-emerald-100 mt-2">
                                    {myTotalExportCreditEur.toFixed(2)} <span className="text-sm font-normal">€</span>
                                </div>
                                <div className="text-xs text-emerald-600 dark:text-emerald-400 mt-1">
                                    Gutschrift aus Quartiers-Einspeisung
                                </div>
                            </div>

                            <div className="bg-gradient-to-br from-purple-500/10 to-purple-600/5 border border-purple-500/20 rounded-2xl p-5">
                                <div className="text-[11px] font-bold text-purple-700 dark:text-purple-300 uppercase">
                                    Mehrerlös ggü. EEG
                                </div>
                                <div className="text-3xl font-black text-purple-900 dark:text-purple-100 mt-2">
                                    ~{estimatedProducerBonusEur.toFixed(2)} <span className="text-sm font-normal">€</span>
                                </div>
                                <div className="text-xs text-purple-600 dark:text-purple-400 mt-1">
                                    Mehrertrag gegenüber Standard-Einspeisung
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {(memberPerspective === "all" || memberPerspective === "consumer") && (
                    <div className="space-y-2 pt-2">
                        <div className="text-xs font-bold text-indigo-700 dark:text-indigo-300 uppercase tracking-wider flex items-center gap-1.5">
                            <span>🔌</span> Mein Consumer-Bezug aus der Community
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                            <div className="bg-gradient-to-br from-indigo-500/10 to-indigo-600/5 border border-indigo-500/20 rounded-2xl p-5">
                                <div className="text-[11px] font-bold text-indigo-700 dark:text-indigo-300 uppercase">
                                    Mein Solar-Bezug
                                </div>
                                <div className="text-3xl font-black text-indigo-900 dark:text-indigo-100 mt-2">
                                    {myTotalSharedImportKwh.toFixed(1)} <span className="text-sm font-normal">kWh</span>
                                </div>
                                <div className="text-xs text-indigo-600 dark:text-indigo-400 mt-1">
                                    Günstiger Ökostrom aus dem Verteilnetz
                                </div>
                            </div>

                            <div className="bg-gradient-to-br from-cyan-500/10 to-cyan-600/5 border border-cyan-500/20 rounded-2xl p-5">
                                <div className="text-[11px] font-bold text-cyan-700 dark:text-cyan-300 uppercase">
                                    Meine Ersparnis
                                </div>
                                <div className="text-3xl font-black text-cyan-900 dark:text-cyan-100 mt-2">
                                    ~{estimatedSavingsEur.toFixed(2)} <span className="text-sm font-normal">€</span>
                                </div>
                                <div className="text-xs text-cyan-600 dark:text-cyan-400 mt-1">
                                    Ersparnis ggü. Netz-Grundversorger
                                </div>
                            </div>

                            <div className="bg-gradient-to-br from-slate-500/10 to-slate-600/5 border border-slate-500/20 rounded-2xl p-5">
                                <div className="text-[11px] font-bold text-slate-700 dark:text-slate-300 uppercase">
                                    Reststrom aus Netz
                                </div>
                                <div className="text-3xl font-black text-slate-900 dark:text-slate-100 mt-2">
                                    {myTotalGridResidualImportKwh.toFixed(1)} <span className="text-sm font-normal">kWh</span>
                                </div>
                                <div className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                                    Über externen Lieferanten bezogen
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* 4. SHARING-TARIF & MONATLICHE ABRECHNUNGSNACHWEISE (§ 42b EnWG) */}
            <div className="space-y-4 pt-2">
                <div>
                    <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <span>📄</span> Meine Abrechnungsnachweise & Tarifkonditionen
                    </h2>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                        Monatliche Abrechnungsbelege zur internen Verrechnung und PDF-Nachweise
                    </p>
                </div>

                {/* AKTIVER TARIF BANNER */}
                {activeTariff && (
                    <div className="bg-gradient-to-br from-slate-900 to-indigo-950 text-white rounded-2xl p-5 border border-indigo-800/40 shadow-sm">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-white/10">
                            <div>
                                <div className="text-xs text-indigo-300 font-semibold uppercase">Gültiger Sharing-Tarif</div>
                                <div className="text-lg font-black">{activeTariff.name}</div>
                            </div>
                            <span className="bg-emerald-400/20 text-emerald-300 text-xs font-bold px-3 py-1 rounded-full border border-emerald-400/30 self-start sm:self-auto">
                                Aktiv nach § 42b EnWG
                            </span>
                        </div>

                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-3">
                            <div>
                                <div className="text-[10px] text-indigo-300 uppercase">Bezugspreis Solar</div>
                                <div className="text-xl font-bold text-white mt-0.5">
                                    {Number(activeTariff?.sharing_price_ct_kwh ?? 0).toFixed(2)} <span className="text-xs font-normal">Ct/kWh</span>
                                </div>
                            </div>
                            <div>
                                <div className="text-[10px] text-indigo-300 uppercase">Einspeisevergütung</div>
                                <div className="text-xl font-bold text-emerald-300 mt-0.5">
                                    {Number(activeTariff?.producer_payout_ct_kwh ?? 0).toFixed(2)} <span className="text-xs font-normal">Ct/kWh</span>
                                </div>
                            </div>
                            <div>
                                <div className="text-[10px] text-indigo-300 uppercase">Community-Umlage</div>
                                <div className="text-xl font-bold text-amber-300 mt-0.5">
                                    {Number(activeTariff?.community_fee_ct_kwh ?? 0).toFixed(2)} <span className="text-xs font-normal">Ct/kWh</span>
                                </div>
                            </div>
                            <div>
                                <div className="text-[10px] text-indigo-300 uppercase">Ersparnis vs. Netz</div>
                                <div className="text-xl font-bold text-cyan-300 mt-0.5">
                                    ~20,00 <span className="text-xs font-normal">Ct/kWh</span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* TABELLE DER PERSÖNLICHEN ABRECHNUNGSNACHWEISE */}
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-2xs space-y-3">
                    <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-800">
                        <h3 className="text-xs font-bold text-slate-800 dark:text-slate-200">
                            Persönliche Monatsnachweise ({statements.length})
                        </h3>
                        <span className="text-[11px] text-slate-400">
                            Eichrechtskonform generiert
                        </span>
                    </div>

                    {statements.length > 0 ? (
                        <div className="space-y-3">
                            {statements.map((stmt) => (
                                <div
                                    key={stmt.id}
                                    className="p-4 rounded-xl border border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                                >
                                    <div className="space-y-1">
                                        <div className="flex items-center gap-2">
                                            <span className="font-mono font-bold text-xs text-slate-900 dark:text-white">
                                                {stmt.statement_number}
                                            </span>
                                            <span className="bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 text-[10px] font-semibold px-2 py-0.5 rounded-md">
                                                {stmt.period_start} bis {stmt.period_end}
                                            </span>
                                            <span className="bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-[10px] font-bold px-2 py-0.5 rounded-md border border-emerald-500/20">
                                                {stmt.status === "finalized" ? "Abgerechnet" : stmt.status}
                                            </span>
                                        </div>
                                        <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-600 dark:text-slate-400 pt-1">
                                            {Number(stmt.shared_exported_kwh || 0) > 0 && (
                                                <span className="text-amber-700 dark:text-amber-300">
                                                    ☀️ Solar geteilt: <strong>{Number(stmt.shared_exported_kwh).toFixed(1)} kWh</strong>
                                                </span>
                                            )}
                                            {Number(stmt.shared_imported_kwh || 0) > 0 && (
                                                <span className="text-indigo-700 dark:text-indigo-300">
                                                    🔌 Solar bezogen: <strong>{Number(stmt.shared_imported_kwh).toFixed(1)} kWh</strong>
                                                </span>
                                            )}
                                            {Number(stmt.grid_residual_import_kwh || 0) > 0 && (
                                                <span>
                                                    🏠 Netz bezogen: <strong>{Number(stmt.grid_residual_import_kwh).toFixed(1)} kWh</strong>
                                                </span>
                                            )}
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-4 justify-between sm:justify-end border-t sm:border-t-0 pt-2 sm:pt-0 border-slate-200 dark:border-slate-700">
                                        <div className="text-right">
                                            <div className="text-[10px] text-slate-400">
                                                {stmt.is_payout ? "Gutschrift" : "Zahlbetrag Solarstrom"}
                                            </div>
                                            <div className={`text-lg font-black ${
                                                stmt.is_payout ? "text-emerald-600 dark:text-emerald-400" : "text-slate-900 dark:text-white"
                                            }`}>
                                                {stmt.is_payout ? "+" : ""}{Number(stmt.net_balance_eur ?? 0).toFixed(2)} €
                                            </div>
                                        </div>

                                        <button
                                            onClick={() => downloadStatementPdf(stmt.id, stmt.statement_number)}
                                            disabled={downloadingId === stmt.id}
                                            className="px-3.5 py-2 bg-white dark:bg-slate-900 hover:bg-indigo-50 dark:hover:bg-slate-800 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800 rounded-xl text-xs font-bold transition cursor-pointer flex items-center gap-1.5 shadow-2xs"
                                        >
                                            <span>📄</span>
                                            <span>{downloadingId === stmt.id ? "Lade..." : "PDF"}</span>
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-8 text-xs text-slate-400 bg-slate-50 dark:bg-slate-800/30 rounded-xl border border-dashed border-slate-200 dark:border-slate-800">
                            📜 Für deinen Account liegen für diesen Abrechnungszeitraum noch keine abgeschlossenen Monatsabrechnungen vor. Sobald der Abrechnungslauf zum Monatsende abgeschlossen ist, findest du deinen PDF-Nachweis hier.
                        </div>
                    )}
                </div>
            </div>

            {/* MODAL: SHARE ERFOLGE */}
            {shareModalOpen && (
                <CommunityShareModal
                    open={shareModalOpen}
                    onClose={() => setShareModalOpen(false)}
                    tenant={tenant}
                    cockpit={cockpit}
                />
            )}
        </div>
    );
}
