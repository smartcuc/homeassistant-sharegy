/*
# src/pages/admin/CommunitiesManagementHub.jsx
# Zentrales Multi-Community Management Hub für Energiegemeinschaften
*/

import { useEffect, useState, useMemo } from "react";
import { apiFetch } from "../../api/client";

export default function CommunitiesManagementHub() {
    const [portfolioData, setPortfolioData] = useState(null);
    const [selectedTenantId, setSelectedTenantId] = useState(null);
    const [drilldownData, setDrilldownData] = useState(null);
    const [drilldownTab, setDrilldownTab] = useState("members"); // 'members' | 'tariffs' | 'announcements' | 'settings'
    const [loading, setLoading] = useState(true);
    const [drilldownLoading, setDrilldownLoading] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");
    const [announcementModal, setAnnouncementModal] = useState(false);
    const [settingsForm, setSettingsForm] = useState({ name: "", primary_color: "#10b981", is_public: true });
    const [savingSettings, setSavingSettings] = useState(false);
    const [exportingFormat, setExportingFormat] = useState(null);


    // ✅ Portfolio-Daten laden
    async function loadPortfolio() {
        setLoading(true);
        try {
            const data = await apiFetch("/api/billing/communities/overview/");
            setPortfolioData(data);
        } catch (err) {
            console.error("Failed to load portfolio:", err);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadPortfolio();
    }, []);

    // ✅ Drilldown für eine Community laden
    async function openDrilldown(tenantId) {
        setSelectedTenantId(tenantId);
        setDrilldownLoading(true);
        try {
            const data = await apiFetch(`/api/billing/communities/${tenantId}/drilldown/`);
            setDrilldownData(data);
            setSettingsForm({
                name: data.community.name,
                primary_color: data.community.primary_color || "#10b981",
                is_public: data.community.is_public,
            });
        } catch (err) {
            alert("Fehler beim Laden der Community-Details: " + (err.message || "Unbekannt"));
        } finally {
            setDrilldownLoading(false);
        }
    }

    // ✅ Ankündigung posten
    async function submitAnnouncement(e) {
        e.preventDefault();
        if (!newAnnouncement.title || !newAnnouncement.message) return;
        try {
            await apiFetch(`/api/billing/communities/${selectedTenantId}/announcements/`, {
                method: "POST",
                body: JSON.stringify(newAnnouncement),
            });
            alert("Mitteilung erfolgreich an die Community übermittelt!");
            setAnnouncementModal(false);
            setNewAnnouncement({ title: "", message: "", category: "info" });
            // Drilldown aktualisieren
            const updated = await apiFetch(`/api/billing/communities/${selectedTenantId}/drilldown/`);
            setDrilldownData(updated);
        } catch (err) {
            alert("Fehler: " + (err.message || "Konnte Mitteilung nicht senden."));
        }
    }

    // ✅ Einstellungen speichern
    async function saveSettings(e) {
        e.preventDefault();
        setSavingSettings(true);
        try {
            await apiFetch(`/api/billing/communities/${selectedTenantId}/settings/`, {
                method: "POST",
                body: JSON.stringify(settingsForm),
            });
            alert("Einstellungen erfolgreich gespeichert.");
            loadPortfolio();
            const updated = await apiFetch(`/api/billing/communities/${selectedTenantId}/drilldown/`);
            setDrilldownData(updated);
        } catch (err) {
            alert("Fehler beim Speichern: " + (err.message || "Unbekannt"));
        } finally {
            setSavingSettings(false);
        }
    }

    // 📥 Multi-Format Abrechnungsexport
    async function exportStatements(tenantId, format = "xlsx") {
        setExportingFormat(format);
        try {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            const response = await fetch(`/api/billing/community/statements/export/?export_format=${format}&tenant_id=${tenantId || ""}`, {
                headers: {
                    Authorization: token ? `Bearer ${token}` : "",
                }
            });
            if (!response.ok) throw new Error("Export fehlgeschlagen.");
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            const ext = format === "xlsx" ? "xlsx" : format === "csv" ? "csv" : "xml";
            a.download = `Sharegy_Abrechnungsdaten_${drilldownData?.community?.slug || "community"}_${new Date().toISOString().slice(0, 10)}.${ext}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error("Export error:", err);
            alert(`Fehler beim ${format.toUpperCase()}-Export.`);
        } finally {
            setExportingFormat(null);
        }
    }

    // 🔍 Filterung nach Suche

    const filteredCommunities = useMemo(() => {
        if (!portfolioData || !portfolioData.communities) return [];
        if (!searchQuery.trim()) return portfolioData.communities;
        const q = searchQuery.toLowerCase();
        return portfolioData.communities.filter(
            (c) => c.name.toLowerCase().includes(q) || c.slug.toLowerCase().includes(q)
        );
    }, [portfolioData, searchQuery]);

    if (loading) {
        return (
            <div className="p-12 text-center text-slate-400 text-sm animate-pulse">
                Lade Multi-Community Portfolio & Performance-Zentralen...
            </div>
        );
    }

    const portfolio = portfolioData?.portfolio || {
        total_communities: 0,
        total_members: 0,
        total_meters: 0,
        total_produced_kwh: 0,
        total_consumed_kwh: 0,
        total_shared_kwh: 0,
        portfolio_autarky_pct: 0,
        total_savings_eur: 0,
    };

    return (
        <div className="p-4 sm:p-8 max-w-7xl mx-auto space-y-8">

            {/* ======================================================== */}
            {/* 1. HEADER & HERO PORTFOLIO METRICS */}
            {/* ======================================================== */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
                <div>
                    <div className="flex items-center gap-3">
                        <span className="text-3xl">🏘️</span>
                        <div>
                            <h1 className="text-2xl font-black tracking-tight text-slate-900 dark:text-white">
                                Energiegemeinschaften & Quartiere
                            </h1>
                            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                                Zentrales Multi-Tenant Management: Performance, Tarife, Mitglieder & Abrechnungen
                            </p>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <span className="bg-indigo-500/10 text-indigo-700 dark:text-indigo-400 text-xs font-bold px-3 py-1.5 rounded-xl border border-indigo-500/20">
                        {portfolio.total_communities} Aktive Gemeinschaften
                    </span>
                </div>
            </div>

            {/* 5 HERO KPI CARDS */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
                
                {/* 1. COMMUNITIES & MITGLIEDER */}
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-xs">
                    <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-semibold">
                        <span>Netzwerk</span>
                        <span className="text-base">👥</span>
                    </div>
                    <div className="mt-2">
                        <div className="text-2xl font-black text-slate-900 dark:text-white">
                            {portfolio.total_members} <span className="text-xs font-medium text-slate-400">Nutzer</span>
                        </div>
                        <div className="text-[11px] text-slate-500 mt-0.5">
                            in {portfolio.total_communities} Gemeinschaften ({portfolio.total_meters} Zähler)
                        </div>
                    </div>
                </div>

                {/* 2. GESAMTERZEUGUNG */}
                <div className="bg-amber-500/5 dark:bg-amber-500/10 border border-amber-500/20 rounded-2xl p-4 shadow-xs">
                    <div className="flex items-center justify-between text-amber-700 dark:text-amber-300 text-xs font-bold">
                        <span>Solar-Erzeugung (Mtl.)</span>
                        <span className="text-base">☀️</span>
                    </div>
                    <div className="mt-2">
                        <div className="text-2xl font-black text-amber-900 dark:text-amber-100">
                            {portfolio.total_produced_kwh.toLocaleString()} <span className="text-xs font-normal">kWh</span>
                        </div>
                        <div className="text-[11px] text-amber-700/80 dark:text-amber-300/80 mt-0.5">
                            über alle Einspeiser
                        </div>
                    </div>
                </div>

                {/* 3. GESAMTVERBRAUCH */}
                <div className="bg-sky-500/5 dark:bg-sky-500/10 border border-sky-500/20 rounded-2xl p-4 shadow-xs">
                    <div className="flex items-center justify-between text-sky-700 dark:text-sky-300 text-xs font-bold">
                        <span>Gesamtverbrauch (Mtl.)</span>
                        <span className="text-base">🏠</span>
                    </div>
                    <div className="mt-2">
                        <div className="text-2xl font-black text-sky-900 dark:text-sky-100">
                            {portfolio.total_consumed_kwh.toLocaleString()} <span className="text-xs font-normal">kWh</span>
                        </div>
                        <div className="text-[11px] text-sky-700/80 dark:text-sky-300/80 mt-0.5">
                            Gesamtlast der Mitglieder
                        </div>
                    </div>
                </div>

                {/* 4. GETEILTE ENERGIE & AUTARKIE */}
                <div className="bg-emerald-500/5 dark:bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-4 shadow-xs">
                    <div className="flex items-center justify-between text-emerald-700 dark:text-emerald-300 text-xs font-bold">
                        <span>Geteilt (Sharing)</span>
                        <span className="text-base">🤝</span>
                    </div>
                    <div className="mt-2">
                        <div className="text-2xl font-black text-emerald-900 dark:text-emerald-100">
                            {portfolio.total_shared_kwh.toLocaleString()} <span className="text-xs font-normal">kWh</span>
                        </div>
                        <div className="text-[11px] text-emerald-700/80 dark:text-emerald-300/80 mt-0.5 font-bold">
                            Ø Autarkie: {portfolio.portfolio_autarky_pct}%
                        </div>
                    </div>
                </div>

                {/* 5. FINANZIELLE ERSPARNIS */}
                <div className="bg-indigo-500/5 dark:bg-indigo-500/10 border border-indigo-500/20 rounded-2xl p-4 shadow-xs col-span-2 sm:col-span-1">
                    <div className="flex items-center justify-between text-indigo-700 dark:text-indigo-300 text-xs font-bold">
                        <span>Portfolio Ersparnis</span>
                        <span className="text-base">💰</span>
                    </div>
                    <div className="mt-2">
                        <div className="text-2xl font-black text-indigo-900 dark:text-indigo-100">
                            {portfolio.total_savings_eur.toLocaleString(undefined, { minimumFractionDigits: 2 })} <span className="text-xs font-normal">€</span>
                        </div>
                        <div className="text-[11px] text-indigo-700/80 dark:text-indigo-300/80 mt-0.5">
                            ggü. Grundversorgung
                        </div>
                    </div>
                </div>

            </div>

            {/* ======================================================== */}
            {/* 2. COMMUNITIES PORTFOLIO LISTE & FILTER */}
            {/* ======================================================== */}
            <div className="space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <h2 className="text-base font-bold text-slate-900 dark:text-white">
                        Alle Energiegemeinschaften ({filteredCommunities.length})
                    </h2>

                    {/* SUCHE */}
                    <div className="relative">
                        <input
                            type="text"
                            placeholder="Gemeinschaft suchen (Name, Slug)..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full sm:w-72 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3.5 py-1.5 text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
                        />
                        <span className="absolute right-3 top-2 text-slate-400 text-xs">🔍</span>
                    </div>
                </div>

                {filteredCommunities.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                        {filteredCommunities.map((c) => (
                            <div
                                key={c.id}
                                className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs hover:shadow-md transition flex flex-col justify-between"
                            >
                                <div className="space-y-3">
                                    {/* Header */}
                                    <div className="flex items-start justify-between gap-2">
                                        <div className="flex items-center gap-2.5">
                                            <div
                                                className="w-3.5 h-3.5 rounded-full"
                                                style={{ backgroundColor: c.primary_color || "#10b981" }}
                                            ></div>
                                            <div>
                                                <h3 className="font-bold text-sm text-slate-900 dark:text-white">
                                                    {c.name}
                                                </h3>
                                                <span className="text-[11px] font-mono text-slate-400">
                                                    /{c.slug}
                                                </span>
                                            </div>
                                        </div>
                                        <span className="bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-[10px] font-bold px-2 py-0.5 rounded-full border border-emerald-500/20">
                                            Aktiv
                                        </span>
                                    </div>

                                    {/* Autarkie Progress */}
                                    <div className="space-y-1 pt-1">
                                        <div className="flex justify-between text-xs font-semibold">
                                            <span className="text-slate-500 dark:text-slate-400">Autarkiegrad</span>
                                            <span className="text-emerald-600 dark:text-emerald-400">{c.autarky_pct}%</span>
                                        </div>
                                        <div className="w-full bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                                            <div
                                                className="bg-emerald-500 h-full rounded-full transition-all"
                                                style={{ width: `${Math.min(c.autarky_pct, 100)}%` }}
                                            ></div>
                                        </div>
                                    </div>

                                    {/* Kennzahlen */}
                                    <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-100 dark:border-slate-800 text-xs">
                                        <div>
                                            <span className="text-slate-400 text-[10px]">Monat Erzeugung</span>
                                            <div className="font-bold text-amber-600 dark:text-amber-400">
                                                ☀️ {c.month_produced_kwh.toFixed(1)} kWh
                                            </div>
                                        </div>
                                        <div>
                                            <span className="text-slate-400 text-[10px]">Geteilt (Sharing)</span>
                                            <div className="font-bold text-emerald-600 dark:text-emerald-400">
                                                🤝 {c.month_shared_kwh.toFixed(1)} kWh
                                            </div>
                                        </div>
                                        <div>
                                            <span className="text-slate-400 text-[10px]">Mitglieder & Zähler</span>
                                            <div className="font-semibold text-slate-700 dark:text-slate-300">
                                                👥 {c.members_count} / 🔌 {c.meters_count}
                                            </div>
                                        </div>
                                        <div>
                                            <span className="text-slate-400 text-[10px]">Aktiver Tarif</span>
                                            <div className="font-semibold text-indigo-600 dark:text-indigo-400">
                                                {c.tariff ? `${c.tariff.sharing_price_ct_kwh.toFixed(1)} Ct/kWh` : "Standard"}
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Action */}
                                <div className="pt-4 mt-3 border-t border-slate-100 dark:border-slate-800">
                                    <button
                                        onClick={() => openDrilldown(c.id)}
                                        className="w-full py-2 bg-slate-100 hover:bg-indigo-50 dark:bg-slate-800 dark:hover:bg-slate-700/60 text-slate-800 hover:text-indigo-600 dark:text-slate-200 dark:hover:text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 cursor-pointer"
                                    >
                                        <span>🔍</span> Drill-Down & Verwalten
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-12 text-slate-400 text-xs bg-slate-50 dark:bg-slate-900 rounded-2xl border border-dashed border-slate-200 dark:border-slate-800">
                        Keine Energiegemeinschaften gefunden.
                    </div>
                )}
            </div>

            {/* ======================================================== */}
            {/* 3. DRILLDOWN MODAL / PANEL */}
            {/* ======================================================== */}
            {selectedTenantId && drilldownData && (
                <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl max-w-4xl w-full p-6 space-y-6 shadow-2xl my-8">
                        
                        {/* Modal Header */}
                        <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
                            <div className="flex items-center gap-3">
                                <div
                                    className="w-4 h-4 rounded-full"
                                    style={{ backgroundColor: drilldownData.community.primary_color || "#10b981" }}
                                ></div>
                                <div>
                                    <h2 className="text-lg font-black text-slate-900 dark:text-white">
                                        {drilldownData.community.name}
                                    </h2>
                                    <span className="text-xs text-slate-400">
                                        Community-ID: {drilldownData.community.id}
                                    </span>
                                </div>
                            </div>

                            <button
                                onClick={() => setSelectedTenantId(null)}
                                className="text-slate-400 hover:text-slate-600 dark:hover:text-white text-lg p-1 rounded-lg cursor-pointer"
                            >
                                ✕
                            </button>
                        </div>

                        {/* TAB NAVIGATION */}
                        <div className="flex bg-slate-100 dark:bg-slate-800/70 p-1 rounded-xl text-xs font-semibold">
                            <button
                                onClick={() => setDrilldownTab("members")}
                                className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                                    drilldownTab === "members"
                                        ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs"
                                        : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                                }`}
                            >
                                👥 Teilnehmer & Zähler ({drilldownData.members.length})
                            </button>
                            <button
                                onClick={() => setDrilldownTab("tariffs")}
                                className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                                    drilldownTab === "tariffs"
                                        ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs"
                                        : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                                }`}
                            >
                                💰 Tarife & Konditionen
                            </button>
                            <button
                                onClick={() => setDrilldownTab("announcements")}
                                className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                                    drilldownTab === "announcements"
                                        ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs"
                                        : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                                }`}
                            >
                                📢 Mitteilungen ({drilldownData.announcements.length})
                            </button>
                            <button
                                onClick={() => setDrilldownTab("settings")}
                                className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                                    drilldownTab === "settings"
                                        ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs"
                                        : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                                }`}
                            >
                                ⚙️ Einstellungen
                            </button>
                        </div>

                        {/* 1. MEMBERS DRILLDOWN */}
                        {drilldownTab === "members" && (
                            <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
                                {drilldownData.members.map((m) => (
                                    <div
                                        key={m.membership_id}
                                        className="border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40 p-3.5 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
                                    >
                                        <div className="space-y-1">
                                            <div className="flex items-center gap-2">
                                                <span className="font-bold text-slate-900 dark:text-white">
                                                    {m.email}
                                                </span>
                                                <span className="bg-indigo-50 dark:bg-indigo-950/30 text-indigo-600 dark:text-indigo-400 text-[10px] font-bold px-2 py-0.5 rounded-md">
                                                    {m.role}
                                                </span>
                                            </div>
                                            <div className="text-slate-400 text-[11px]">
                                                Zähler: {m.meters.length > 0 ? m.meters.map((mtr) => mtr.serial_number).join(", ") : "Kein Zähler zugewiesen"}
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-4 text-right">
                                            <div>
                                                <div className="text-[10px] text-slate-400">Erzeugt (Mtl.)</div>
                                                <div className="font-bold text-amber-600 dark:text-amber-400">
                                                    ☀️ {m.month_produced_kwh} kWh
                                                </div>
                                            </div>
                                            <div>
                                                <div className="text-[10px] text-slate-400">Verbraucht (Mtl.)</div>
                                                <div className="font-bold text-sky-600 dark:text-sky-400">
                                                    🏠 {m.month_consumed_kwh} kWh
                                                </div>
                                            </div>
                                            {m.last_statement && (
                                                <div className="pl-3 border-l border-slate-200 dark:border-slate-700">
                                                    <div className="text-[10px] text-slate-400">Letzter Saldo</div>
                                                    <div className={`font-bold ${m.last_statement.net_balance_eur >= 0 ? "text-emerald-600" : "text-rose-600"}`}>
                                                        {m.last_statement.net_balance_eur >= 0 ? "+" : ""}{m.last_statement.net_balance_eur.toFixed(2)} €
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}

                        {/* 2. TARIFFS DRILLDOWN */}
                        {drilldownTab === "tariffs" && drilldownData.active_tariff && (
                            <div className="space-y-4">
                                <div className="bg-gradient-to-br from-indigo-900 to-slate-900 text-white rounded-2xl p-5">
                                    <h3 className="font-bold text-sm">{drilldownData.active_tariff.name}</h3>
                                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4 text-xs">
                                        <div>
                                            <span className="text-indigo-300 text-[10px]">Bezugspreis (Sharing)</span>
                                            <div className="text-lg font-black">{drilldownData.active_tariff.sharing_price_ct_kwh.toFixed(2)} Ct/kWh</div>
                                        </div>
                                        <div>
                                            <span className="text-indigo-300 text-[10px]">Einspeisevergütung</span>
                                            <div className="text-lg font-black text-emerald-300">{drilldownData.active_tariff.producer_payout_ct_kwh.toFixed(2)} Ct/kWh</div>
                                        </div>
                                        <div>
                                            <span className="text-indigo-300 text-[10px]">Community-Umlage</span>
                                            <div className="text-lg font-black text-amber-300">{drilldownData.active_tariff.community_fee_ct_kwh.toFixed(2)} Ct/kWh</div>
                                        </div>
                                        <div>
                                            <span className="text-indigo-300 text-[10px]">Netzentgelt-Reduktion</span>
                                            <div className="text-lg font-black text-cyan-300">{drilldownData.active_tariff.grid_fee_saved_ct_kwh.toFixed(2)} Ct/kWh</div>
                                        </div>
                                    </div>
                                </div>

                                {/* Export & Clearing Box */}
                                <div className="bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                                    <div>
                                        <h4 className="text-xs font-bold text-slate-900 dark:text-white">
                                            Abrechnungs- & Clearing-Exporte
                                        </h4>
                                        <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                                            Export aller Monatsabrechnungen dieses Quartiers für ERP, DATEV und Buchhaltung
                                        </p>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={() => exportStatements(selectedTenantId, "xlsx")}
                                            disabled={exportingFormat === "xlsx"}
                                            className="px-3 py-1.5 bg-white dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-semibold transition cursor-pointer flex items-center gap-1.5 shadow-2xs"
                                        >
                                            <span>📗</span> {exportingFormat === "xlsx" ? "Exportiere..." : "Excel (.xlsx)"}
                                        </button>
                                        <button
                                            onClick={() => exportStatements(selectedTenantId, "csv")}
                                            disabled={exportingFormat === "csv"}
                                            className="px-3 py-1.5 bg-white dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-semibold transition cursor-pointer flex items-center gap-1.5 shadow-2xs"
                                        >
                                            <span>📊</span> {exportingFormat === "csv" ? "Exportiere..." : "CSV"}
                                        </button>
                                        <button
                                            onClick={() => exportStatements(selectedTenantId, "xml")}
                                            disabled={exportingFormat === "xml"}
                                            className="px-3 py-1.5 bg-white dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-semibold transition cursor-pointer flex items-center gap-1.5 shadow-2xs"
                                        >
                                            <span>📦</span> {exportingFormat === "xml" ? "Exportiere..." : "XML / ERP"}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )}


                        {/* 3. ANNOUNCEMENTS DRILLDOWN */}
                        {drilldownTab === "announcements" && (
                            <div className="space-y-4">
                                <div className="flex justify-between items-center">
                                    <h4 className="text-xs font-bold text-slate-800 dark:text-slate-200">
                                        Community-Rundschreiben & Statusmeldungen
                                    </h4>
                                    <button
                                        onClick={() => setAnnouncementModal(true)}
                                        className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition cursor-pointer"
                                    >
                                        + Neue Mitteilung posten
                                    </button>
                                </div>

                                <div className="space-y-2 max-h-72 overflow-y-auto">
                                    {drilldownData.announcements.map((a) => (
                                        <div
                                            key={a.id}
                                            className="border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/30 p-3.5 rounded-xl space-y-1 text-xs"
                                        >
                                            <div className="flex justify-between items-center">
                                                <span className="font-bold text-slate-900 dark:text-white">
                                                    {a.title}
                                                </span>
                                                <span className="text-[10px] text-slate-400">
                                                    {new Date(a.created_at).toLocaleDateString()}
                                                </span>
                                            </div>
                                            <p className="text-slate-600 dark:text-slate-300 text-[11px] leading-relaxed">
                                                {a.message}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* 4. SETTINGS DRILLDOWN */}
                        {drilldownTab === "settings" && (
                            <form onSubmit={saveSettings} className="space-y-4 text-xs">
                                <div>
                                    <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                                        Name der Energiegemeinschaft
                                    </label>
                                    <input
                                        type="text"
                                        value={settingsForm.name}
                                        onChange={(e) => setSettingsForm({ ...settingsForm, name: e.target.value })}
                                        className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-slate-900 dark:text-white"
                                    />
                                </div>

                                <div>
                                    <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                                        Branding / Primärfarbe
                                    </label>
                                    <div className="flex items-center gap-3">
                                        <input
                                            type="color"
                                            value={settingsForm.primary_color}
                                            onChange={(e) => setSettingsForm({ ...settingsForm, primary_color: e.target.value })}
                                            className="w-10 h-10 rounded-lg cursor-pointer border-0"
                                        />
                                        <span className="font-mono text-slate-500">{settingsForm.primary_color}</span>
                                    </div>
                                </div>

                                <div className="pt-2">
                                    <button
                                        type="submit"
                                        disabled={savingSettings}
                                        className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl font-bold transition cursor-pointer"
                                    >
                                        {savingSettings ? "Speichere..." : "Einstellungen übernehmen"}
                                    </button>
                                </div>
                            </form>
                        )}

                    </div>
                </div>
            )}

            {/* ANNOUNCEMENT CREATE MODAL */}
            {announcementModal && (
                <div className="fixed inset-0 z-60 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl max-w-md w-full p-6 space-y-4 shadow-2xl">
                        <div className="flex justify-between items-center">
                            <h3 className="font-bold text-sm text-slate-900 dark:text-white">
                                Neue Community-Mitteilung
                            </h3>
                            <button
                                onClick={() => setAnnouncementModal(false)}
                                className="text-slate-400 hover:text-slate-600 text-sm cursor-pointer"
                            >
                                ✕
                            </button>
                        </div>

                        <form onSubmit={submitAnnouncement} className="space-y-3 text-xs">
                            <div>
                                <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                                    Titel / Betreff
                                </label>
                                <input
                                    type="text"
                                    placeholder="z. B. Neuer Zählerwechsel-Termin"
                                    value={newAnnouncement.title}
                                    onChange={(e) => setNewAnnouncement({ ...newAnnouncement, title: e.target.value })}
                                    className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-slate-900 dark:text-white"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                                    Kategorie
                                </label>
                                <select
                                    value={newAnnouncement.category}
                                    onChange={(e) => setNewAnnouncement({ ...newAnnouncement, category: e.target.value })}
                                    className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-slate-900 dark:text-white"
                                >
                                    <option value="info">ℹ️ Information</option>
                                    <option value="tariff">💰 Tarif & Abrechnung</option>
                                    <option value="maintenance">🔧 Wartung & Zähler</option>
                                    <option value="important">⚠️ Wichtig / Dringend</option>
                                </select>
                            </div>

                            <div>
                                <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                                    Nachrichtentext
                                </label>
                                <textarea
                                    rows="4"
                                    placeholder="Text der Mitteilung an alle Teilnehmer dieser Energiegemeinschaft..."
                                    value={newAnnouncement.message}
                                    onChange={(e) => setNewAnnouncement({ ...newAnnouncement, message: e.target.value })}
                                    className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-slate-900 dark:text-white"
                                    required
                                ></textarea>
                            </div>

                            <div className="pt-2 flex justify-end gap-2">
                                <button
                                    type="button"
                                    onClick={() => setAnnouncementModal(false)}
                                    className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-semibold cursor-pointer"
                                >
                                    Abbrechen
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold cursor-pointer"
                                >
                                    Veröffentlichen
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

        </div>
    );
}
