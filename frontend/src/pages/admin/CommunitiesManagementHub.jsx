/*
# src/pages/admin/CommunitiesManagementHub.jsx
# Zentrales Multi-Community Management Hub für Energiegemeinschaften & Allokationsmodelle
*/

import { useEffect, useState, useMemo } from "react";
import { apiFetch } from "../../api/client";

export default function CommunitiesManagementHub() {
    const [portfolioData, setPortfolioData] = useState(null);
    const [selectedTenantId, setSelectedTenantId] = useState(null);
    const [drilldownData, setDrilldownData] = useState(null);
    const [drilldownTab, setDrilldownTab] = useState("members"); // 'members' | 'tariffs' | 'shares' | 'announcements' | 'settings'
    const [loading, setLoading] = useState(true);
    const [drilldownLoading, setDrilldownLoading] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");
    const [modelFilter, setModelFilter] = useState("all"); // 'all' | 'mieterstrom' | 'ggv' | 'energy_sharing'
    const [announcementModal, setAnnouncementModal] = useState(false);
    const [newAnnouncement, setNewAnnouncement] = useState({ title: "", message: "", category: "info" });
    const [settingsForm, setSettingsForm] = useState({ name: "", primary_color: "#10b981", is_public: true });
    const [savingSettings, setSavingSettings] = useState(false);
    const [exportingFormat, setExportingFormat] = useState(null);

    // ⚖️ Hilfsfunktion: Rechtliche & fachliche Metadaten pro Modelltyp
    function getModelMetadata(modelType) {
        switch (modelType) {
            case "mieterstrom":
                return {
                    id: "mieterstrom",
                    label: "Mieterstrom (§ 42a EnWG)",
                    shortLabel: "Mieterstrom",
                    badgeText: "🏢 Mieterstrom (§ 42a)",
                    icon: "🏢",
                    badgeClass: "bg-sky-50 dark:bg-sky-950/50 text-sky-700 dark:text-sky-300 border-sky-200 dark:border-sky-800",
                    description: "Vollversorgung: PV-Strom & Reststrom in einer Monatsabrechnung für Mieter",
                    membersTitle: "Mieter & Wohneinheiten",
                    sharesTitle: "Mieterstrom-Zuteilungsquoten",
                    tariffTitle: "Mieterstrom-Vollversorgertarif",
                    meterTitle: "Summenzähler & Wohnungszähler",
                    alertText: "🏢 Mieterstrom-Modell (§ 42a EnWG): Der Vermieter/Contractor übernimmt die Vollversorgung der Mieter mit PV- und Reststrom. Die Abrechnung erfolgt als Gesamtstromrechnung inklusive Mieterstromzuschlag.",
                };
            case "ggv":
                return {
                    id: "ggv",
                    label: "Gebäudeversorgung (GGV § 42b EnWG)",
                    shortLabel: "GGV (§ 42b)",
                    badgeText: "⚖️ GGV (§ 42b)",
                    icon: "⚖️",
                    badgeClass: "bg-purple-50 dark:bg-purple-950/50 text-purple-700 dark:text-purple-300 border-purple-200 dark:border-purple-800",
                    description: "Vor-Ort-Solaraufteilung nach Miteigentumsanteilen (MEA /1000) ohne Reststrompflicht",
                    membersTitle: "Wohnungseigentümer & Parteien",
                    sharesTitle: "Miteigentumsanteile (MEA /1000)",
                    tariffTitle: "Solar-Nutzungsentgelt (ohne Reststrom)",
                    meterTitle: "Wohnungs- & Erzeugungszähler",
                    alertText: "⚖️ Gemeinschaftliche Gebäudeversorgung (§ 42b EnWG): Reine Vor-Ort-Aufteilung des Solarstroms nach Miteigentumsanteilen (MEA). Es besteht keine Reststromlieferpflicht; jeder Nutzer hat seinen eigenen Reststromvertrag.",
                };
            case "energy_sharing":
            default:
                return {
                    id: "energy_sharing",
                    label: "Energy Sharing (Genossenschaft)",
                    shortLabel: "Energy Sharing",
                    badgeText: "⚡ Energy Sharing",
                    icon: "⚡",
                    badgeClass: "bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800",
                    description: "15-Minuten Smart-Meter-Bilanzierung & Verteilnetz-Allokation für Bürgerenergie",
                    membersTitle: "Genossenschaftsmitglieder",
                    sharesTitle: "15m-Allokationsschlüssel",
                    tariffTitle: "Bürgerenergie-Sharingtarif",
                    meterTitle: "Smart Meter (iMSys / RLM)",
                    alertText: "⚡ Regionales Energy Sharing: 15-minütige Bilanzierung über das öffentliche Netz gemäß EU-Richtlinie / § 42c EnWG mit Netzentgelt-Rabatt und automatisiertem BNetzA MSCONS EDIFACT Export.",
                };
        }
    }

    // ⚖️ Beteiligungsquoten & Allokation State
    const [sharesData, setSharesData] = useState(null);
    const [sharesLoading, setSharesLoading] = useState(false);
    const [editingShares, setEditingShares] = useState([]);
    const [savingShares, setSavingShares] = useState(false);
    const [selectedAllocationModel, setSelectedAllocationModel] = useState("dynamic");
    const [savingModel, setSavingModel] = useState(false);
    const [previewData, setPreviewData] = useState(null);
    const [previewLoading, setPreviewLoading] = useState(false);

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
            if (data.active_tariff) {
                setSelectedAllocationModel(data.active_tariff.allocation_model || "dynamic");
            }
            loadShares(tenantId);
        } catch (err) {
            alert("Fehler beim Laden der Community-Details: " + (err.message || "Unbekannt"));
        } finally {
            setDrilldownLoading(false);
        }
    }

    // ⚖️ Beteiligungsquoten laden
    async function loadShares(tenantId) {
        setSharesLoading(true);
        try {
            const data = await apiFetch(`/api/billing/community/shares/?tenant_id=${tenantId}`);
            setSharesData(data);
            setEditingShares(
                data.shares.map((s) => ({
                    membership_id: s.membership_id,
                    user_email: s.user_email,
                    share_percent: s.share_percent,
                    mea_numerator: s.mea_numerator || "",
                    mea_denominator: s.mea_denominator || 1000,
                    assigned_kwp: s.assigned_kwp || "",
                    is_active: s.is_active,
                }))
            );
        } catch (err) {
            console.error("Failed to load shares:", err);
        } finally {
            setSharesLoading(false);
        }
    }

    // ⚖️ Quoten ändern (Prozent oder MEA)
    function handleShareChange(index, field, value) {
        const updated = [...editingShares];
        updated[index][field] = value;

        // Falls MEA-Zähler geändert wird, Prozentwert automatisch live berechnen
        if (field === "mea_numerator") {
            const num = parseFloat(value);
            const den = parseFloat(updated[index].mea_denominator || 1000);
            if (!isNaN(num) && den > 0) {
                updated[index].share_percent = parseFloat(((num / den) * 100).toFixed(4));
            }
        }
        setEditingShares(updated);
    }

    // ⚖️ Quoten im Bulk speichern
    async function saveShares(normalize = false) {
        setSavingShares(true);
        try {
            await apiFetch("/api/billing/community/shares/bulk/", {
                method: "POST",
                body: JSON.stringify({
                    tenant_id: selectedTenantId,
                    normalize_to_100: normalize,
                    shares: editingShares.map((s) => ({
                        membership_id: s.membership_id,
                        share_percent: parseFloat(s.share_percent) || 0,
                        mea_numerator: s.mea_numerator ? parseInt(s.mea_numerator) : null,
                        mea_denominator: parseInt(s.mea_denominator) || 1000,
                        assigned_kwp: s.assigned_kwp ? parseFloat(s.assigned_kwp) : null,
                        is_active: s.is_active,
                    })),
                }),
            });
            alert(normalize ? "Quoten erfolgreich auf 100% normiert und gespeichert!" : "Beteiligungsquoten erfolgreich gespeichert.");
            loadShares(selectedTenantId);
        } catch (err) {
            alert("Fehler beim Speichern der Quoten: " + (err.message || "Unbekannt"));
        } finally {
            setSavingShares(false);
        }
    }

    // ⚖️ Allokationsmodell im Tarif aktualisieren
    async function saveAllocationModel() {
        if (!drilldownData || !drilldownData.active_tariff) return;
        setSavingModel(true);
        try {
            await apiFetch("/api/billing/community/tariffs/", {
                method: "POST",
                body: JSON.stringify({
                    tenant_id: selectedTenantId,
                    name: drilldownData.active_tariff.name,
                    allocation_model: selectedAllocationModel,
                    sharing_price_ct_kwh: drilldownData.active_tariff.sharing_price_ct_kwh,
                    producer_payout_ct_kwh: drilldownData.active_tariff.producer_payout_ct_kwh,
                    community_fee_ct_kwh: drilldownData.active_tariff.community_fee_ct_kwh,
                    grid_fee_saved_ct_kwh: drilldownData.active_tariff.grid_fee_saved_ct_kwh,
                    set_active: true,
                }),
            });
            alert(`Allokationsmodell erfolgreich auf "${selectedAllocationModel.toUpperCase()}" umgestellt!`);
            const updated = await apiFetch(`/api/billing/communities/${selectedTenantId}/drilldown/`);
            setDrilldownData(updated);
        } catch (err) {
            alert("Fehler beim Aktualisieren des Allokationsmodells: " + (err.message || "Unbekannt"));
        } finally {
            setSavingModel(false);
        }
    }

    // 🔍 3-Modelle Simulation laden
    async function loadSimulationPreview() {
        setPreviewLoading(true);
        try {
            const now = new Date();
            const data = await apiFetch(`/api/billing/community/allocation-preview/?tenant_id=${selectedTenantId}&year=${now.getFullYear()}&month=${now.getMonth() + 1}`);
            setPreviewData(data);
        } catch (err) {
            alert("Fehler bei der Simulationsberechnung: " + (err.message || "Unbekannt"));
        } finally {
            setPreviewLoading(false);
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

    // 📄 BNetzA MSCONS EDIFACT Export
    async function exportMscons(tenantId) {
        setExportingFormat("mscons");
        try {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            const response = await fetch(`/api/billing/community/mscons/export/?tenant_id=${tenantId || ""}`, {
                headers: {
                    Authorization: token ? `Bearer ${token}` : "",
                }
            });
            if (!response.ok) throw new Error("MSCONS Export fehlgeschlagen.");
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `Sharegy_MSCONS_${drilldownData?.community?.slug || "community"}_${new Date().toISOString().slice(0, 10)}.edi`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error("MSCONS export error:", err);
            alert("Fehler beim MSCONS EDIFACT Export.");
        } finally {
            setExportingFormat(null);
        }
    }

    // 🔍 Filterung nach Suche und Rechtsmodell
    const filteredCommunities = useMemo(() => {
        if (!portfolioData || !portfolioData.communities) return [];
        return portfolioData.communities.filter((c) => {
            const matchesSearch = !searchQuery.trim() ||
                c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                c.slug.toLowerCase().includes(searchQuery.toLowerCase());
            const cModel = c.model_type || "energy_sharing";
            const matchesModel = modelFilter === "all" || cModel === modelFilter;
            return matchesSearch && matchesModel;
        });
    }, [portfolioData, searchQuery, modelFilter]);

    // Live-Summe der editierten Quoten
    const currentSharesSum = useMemo(() => {
        return editingShares.reduce((acc, s) => acc + (parseFloat(s.share_percent) || 0), 0);
    }, [editingShares]);

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
        <div className="p-6 max-w-7xl mx-auto space-y-8">

            {/* TOP BAR / TITEL */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-200 dark:border-slate-800">
                <div>
                    <div className="flex items-center gap-3">
                        <span className="text-3xl">🏛️</span>
                        <div>
                            <h1 className="text-2xl font-black tracking-tight text-slate-900 dark:text-white">
                                Multi-Community Management Hub
                            </h1>
                            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                                Zentrale Portfolio-Steuerung, Beteiligungsquoten & 15-Minuten Energy Sharing Clearing
                            </p>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <div className="relative">
                        <input
                            type="text"
                            placeholder="Gemeinschaft suchen..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-white placeholder-slate-400 w-64 focus:outline-hidden focus:ring-2 focus:ring-indigo-500/40"
                        />
                        {searchQuery && (
                            <button
                                onClick={() => setSearchQuery("")}
                                className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600 text-xs"
                            >
                                ✕
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {/* ======================================================== */}
            {/* 1. PORTFOLIO HERO STATS */}
            {/* ======================================================== */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-2xs">
                    <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Communities</span>
                    <div className="text-2xl font-black text-slate-900 dark:text-white mt-1">
                        🏛️ {portfolio.total_communities}
                    </div>
                </div>

                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-2xs">
                    <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Teilnehmer</span>
                    <div className="text-2xl font-black text-indigo-600 dark:text-indigo-400 mt-1">
                        👥 {portfolio.total_members}
                    </div>
                </div>

                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-2xs">
                    <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Zähler (iMSys)</span>
                    <div className="text-2xl font-black text-slate-700 dark:text-slate-300 mt-1">
                        🔌 {portfolio.total_meters}
                    </div>
                </div>

                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-2xs">
                    <span className="text-[11px] font-bold text-amber-600 dark:text-amber-400 uppercase tracking-wider">Erzeugung</span>
                    <div className="text-2xl font-black text-amber-600 dark:text-amber-400 mt-1">
                        ☀️ {Number(portfolio?.total_produced_kwh ?? 0).toFixed(0)} <span className="text-xs font-semibold">kWh</span>
                    </div>
                </div>

                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-2xs">
                    <span className="text-[11px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">Autarkiegrad</span>
                    <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-1">
                        ⚡ {Number(portfolio?.portfolio_autarky_pct ?? 0).toFixed(1)}%
                    </div>
                </div>

                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-2xs">
                    <span className="text-[11px] font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-wider">Ersparnis</span>
                    <div className="text-2xl font-black text-cyan-600 dark:text-cyan-400 mt-1">
                        💶 {Number(portfolio?.total_savings_eur ?? 0).toFixed(0)} €
                    </div>
                </div>
            </div>

            {/* ======================================================== */}
            {/* 2. COMMUNITIES GRID WITH MODEL FILTER PILLS */}
            {/* ======================================================== */}
            <div className="space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <h2 className="text-sm font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider">
                        Verwaltete Einheiten & Modelle ({filteredCommunities.length})
                    </h2>

                    {/* MODEL FILTER BUTTON GROUP */}
                    <div className="flex flex-wrap items-center gap-1.5 bg-slate-100 dark:bg-slate-800/80 p-1 rounded-xl text-xs font-semibold">
                        <button
                            type="button"
                            onClick={() => setModelFilter("all")}
                            className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                                modelFilter === "all"
                                    ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs"
                                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                            }`}
                        >
                            Alle ({portfolioData?.communities?.length || 0})
                        </button>
                        <button
                            type="button"
                            onClick={() => setModelFilter("mieterstrom")}
                            className={`px-3 py-1.5 rounded-lg transition cursor-pointer flex items-center gap-1.5 ${
                                modelFilter === "mieterstrom"
                                    ? "bg-sky-50 dark:bg-sky-950/60 text-sky-700 dark:text-sky-300 shadow-xs border border-sky-200 dark:border-sky-800"
                                    : "text-slate-600 dark:text-slate-400 hover:text-sky-600"
                            }`}
                        >
                            <span>🏢</span> Mieterstrom (§ 42a)
                        </button>
                        <button
                            type="button"
                            onClick={() => setModelFilter("ggv")}
                            className={`px-3 py-1.5 rounded-lg transition cursor-pointer flex items-center gap-1.5 ${
                                modelFilter === "ggv"
                                    ? "bg-purple-50 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300 shadow-xs border border-purple-200 dark:border-purple-800"
                                    : "text-slate-600 dark:text-slate-400 hover:text-purple-600"
                            }`}
                        >
                            <span>⚖️</span> GGV (§ 42b)
                        </button>
                        <button
                            type="button"
                            onClick={() => setModelFilter("energy_sharing")}
                            className={`px-3 py-1.5 rounded-lg transition cursor-pointer flex items-center gap-1.5 ${
                                modelFilter === "energy_sharing"
                                    ? "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 shadow-xs border border-emerald-200 dark:border-emerald-800"
                                    : "text-slate-600 dark:text-slate-400 hover:text-emerald-600"
                            }`}
                        >
                            <span>⚡</span> Energy Sharing
                        </button>
                    </div>
                </div>

                {filteredCommunities.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {filteredCommunities.map((c) => {
                            const meta = getModelMetadata(c.model_type || "energy_sharing");
                            return (
                                <div
                                    key={c.id}
                                    className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 hover:border-indigo-500/40 transition shadow-2xs flex flex-col justify-between"
                                >
                                    <div className="space-y-3">
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
                                            <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${meta.badgeClass}`}>
                                                {meta.badgeText}
                                            </span>
                                        </div>

                                        {/* Autarkie Progress */}
                                        <div className="space-y-1 pt-1">
                                            <div className="flex justify-between text-xs font-semibold">
                                                <span className="text-slate-500 dark:text-slate-400">Autarkiegrad</span>
                                                <span className="text-emerald-600 dark:text-emerald-400">{Number(c.autarky_pct ?? 0).toFixed(1)}%</span>
                                            </div>
                                            <div className="w-full bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                                                <div
                                                    className="bg-emerald-500 h-full rounded-full transition-all"
                                                    style={{ width: `${Math.min(c.autarky_pct ?? 0, 100)}%` }}
                                                ></div>
                                            </div>
                                        </div>

                                        {/* Kennzahlen */}
                                        <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-100 dark:border-slate-800 text-xs">
                                            <div>
                                                <span className="text-slate-400 text-[10px]">Monat Erzeugung</span>
                                                <div className="font-bold text-amber-600 dark:text-amber-400">
                                                    ☀️ {Number(c.month_produced_kwh ?? 0).toFixed(1)} kWh
                                                </div>
                                            </div>
                                            <div>
                                                <span className="text-slate-400 text-[10px]">Vor-Ort / Sharing</span>
                                                <div className="font-bold text-emerald-600 dark:text-emerald-400">
                                                    🤝 {Number(c.month_shared_kwh ?? 0).toFixed(1)} kWh
                                                </div>
                                            </div>
                                            <div>
                                                <span className="text-slate-400 text-[10px]">{meta.membersTitle}</span>
                                                <div className="font-semibold text-slate-700 dark:text-slate-300">
                                                    👥 {c.members_count ?? 0} / 🔌 {c.meters_count ?? 0}
                                                </div>
                                            </div>
                                            <div>
                                                <span className="text-slate-400 text-[10px]">Aktiver Tarif</span>
                                                <div className="font-semibold text-indigo-600 dark:text-indigo-400 truncate">
                                                    {c.tariff ? `${Number(c.tariff.sharing_price_ct_kwh ?? 0).toFixed(1)} Ct/kWh` : "Standard"}
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="pt-4 mt-3 border-t border-slate-100 dark:border-slate-800">
                                        <button
                                            onClick={() => openDrilldown(c.id)}
                                            className="w-full py-2 bg-slate-100 hover:bg-indigo-50 dark:bg-slate-800 dark:hover:bg-slate-700/60 text-slate-800 hover:text-indigo-600 dark:text-slate-200 dark:hover:text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 cursor-pointer"
                                        >
                                            <span>🔍</span> Drill-Down & Verwalten
                                        </button>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                ) : (
                    <div className="text-center py-12 text-slate-400 text-xs bg-slate-50 dark:bg-slate-900 rounded-2xl border border-dashed border-slate-200 dark:border-slate-800">
                        Keine Energiegemeinschaften oder Objekte in diesem Filter gefunden.
                    </div>
                )}
            </div>

            {/* ======================================================== */}
            {/* 3. DRILLDOWN MODAL / PANEL */}
            {/* ======================================================== */}
            {selectedTenantId && drilldownData && (() => {
                const drilldownMeta = getModelMetadata(drilldownData.community.model_type || "energy_sharing");
                return (
                <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl max-w-5xl w-full p-6 space-y-6 shadow-2xl my-8">
                        
                        {/* Modal Header */}
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4 gap-3">
                            <div className="flex items-center gap-3">
                                <div
                                    className="w-4 h-4 rounded-full shrink-0"
                                    style={{ backgroundColor: drilldownData.community.primary_color || "#10b981" }}
                                ></div>
                                <div>
                                    <div className="flex items-center gap-2 flex-wrap">
                                        <h2 className="text-lg font-black text-slate-900 dark:text-white">
                                            {drilldownData.community.name}
                                        </h2>
                                        <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${drilldownMeta.badgeClass}`}>
                                            {drilldownMeta.badgeText}
                                        </span>
                                    </div>
                                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                                        {drilldownMeta.description}
                                    </p>
                                </div>
                            </div>

                            <button
                                onClick={() => setSelectedTenantId(null)}
                                className="text-slate-400 hover:text-slate-600 dark:hover:text-white text-lg p-1 rounded-lg cursor-pointer self-start sm:self-center"
                            >
                                ✕
                            </button>
                        </div>

                        {/* Model Legal Context Alert */}
                        <div className="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/80 rounded-2xl p-3.5 text-xs text-slate-700 dark:text-slate-300 flex items-start gap-2.5">
                            <span className="text-lg shrink-0 mt-0.5">{drilldownMeta.icon}</span>
                            <div className="flex-1 leading-relaxed">
                                {drilldownMeta.alertText}
                            </div>
                        </div>

                        {/* TAB NAVIGATION */}
                        <div className="flex flex-wrap bg-slate-100 dark:bg-slate-800/70 p-1 rounded-xl text-xs font-semibold gap-1">
                            <button
                                onClick={() => setDrilldownTab("members")}
                                className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                                    drilldownTab === "members"
                                        ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs"
                                        : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                                }`}
                            >
                                👥 {drilldownMeta.membersTitle} ({drilldownData.members.length})
                            </button>
                            <button
                                onClick={() => setDrilldownTab("shares")}
                                className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                                    drilldownTab === "shares"
                                        ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs"
                                        : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                                }`}
                            >
                                ⚖️ {drilldownMeta.sharesTitle}
                            </button>
                            <button
                                onClick={() => setDrilldownTab("tariffs")}
                                className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                                    drilldownTab === "tariffs"
                                        ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs"
                                        : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                                }`}
                            >
                                💰 {drilldownMeta.tariffTitle}
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
                                                    ☀️ {Number(m.month_produced_kwh ?? 0).toFixed(1)} kWh
                                                </div>
                                            </div>
                                            <div>
                                                <div className="text-[10px] text-slate-400">Verbraucht (Mtl.)</div>
                                                <div className="font-bold text-sky-600 dark:text-sky-400">
                                                    🏠 {Number(m.month_consumed_kwh ?? 0).toFixed(1)} kWh
                                                </div>
                                            </div>
                                            {m.last_statement && (
                                                <div className="pl-3 border-l border-slate-200 dark:border-slate-700">
                                                    <div className="text-[10px] text-slate-400">Letzter Saldo</div>
                                                    <div className={`font-bold ${Number(m.last_statement.net_balance_eur ?? 0) >= 0 ? "text-emerald-600" : "text-rose-600"}`}>
                                                        {Number(m.last_statement.net_balance_eur ?? 0) >= 0 ? "+" : ""}{Number(m.last_statement.net_balance_eur ?? 0).toFixed(2)} €
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}

                        {/* ======================================================== */}
                        {/* 2. ⚖️ BETEILIGUNGSQUOTEN & ALLOKATIONSMODELL */}
                        {/* ======================================================== */}
                        {drilldownTab === "shares" && (
                            <div className="space-y-6">
                                
                                {/* A. Allokationsmodell-Auswahl */}
                                <div className="bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 space-y-4">
                                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                                        <div>
                                            <h3 className="font-bold text-sm text-slate-900 dark:text-white">
                                                Allokationsmodell für Solarstrom-Verteilung
                                            </h3>
                                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                                Bestimmt die mathematische Zuweisung von Gemeinschafts-Solarstrom im 15-Minuten-Raster
                                            </p>
                                        </div>
                                        <button
                                            onClick={saveAllocationModel}
                                            disabled={savingModel}
                                            className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl text-xs font-bold transition cursor-pointer"
                                        >
                                            {savingModel ? "Speichere..." : "Modell im Tarif aktivieren"}
                                        </button>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                                        <label
                                            className={`p-3.5 rounded-xl border cursor-pointer transition flex flex-col justify-between ${
                                                selectedAllocationModel === "dynamic"
                                                    ? "bg-emerald-500/10 border-emerald-500 text-emerald-950 dark:text-emerald-200"
                                                    : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
                                            }`}
                                        >
                                            <div className="flex items-center gap-2">
                                                <input
                                                    type="radio"
                                                    name="alloc_model"
                                                    value="dynamic"
                                                    checked={selectedAllocationModel === "dynamic"}
                                                    onChange={(e) => setSelectedAllocationModel(e.target.value)}
                                                    className="text-emerald-600"
                                                />
                                                <span className="font-bold text-xs">🟢 Dynamisch (Lastgang)</span>
                                            </div>
                                            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">
                                                Solarstrom wird proportional zum zeitgleichen Echtzeit-Verbrauch im 15-Minuten-Raster aufgeteilt.
                                            </p>
                                        </label>

                                        <label
                                            className={`p-3.5 rounded-xl border cursor-pointer transition flex flex-col justify-between ${
                                                selectedAllocationModel === "static"
                                                    ? "bg-blue-500/10 border-blue-500 text-blue-950 dark:text-blue-200"
                                                    : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
                                            }`}
                                        >
                                            <div className="flex items-center gap-2">
                                                <input
                                                    type="radio"
                                                    name="alloc_model"
                                                    value="static"
                                                    checked={selectedAllocationModel === "static"}
                                                    onChange={(e) => setSelectedAllocationModel(e.target.value)}
                                                    className="text-blue-600"
                                                />
                                                <span className="font-bold text-xs">🔵 Statisch (MEA-Quote)</span>
                                            </div>
                                            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">
                                                Jedes Mitglied erhält eine feste Quote (z. B. nach Miteigentumsanteilen). Ungenutzter Strom geht ins Netz.
                                            </p>
                                        </label>

                                        <label
                                            className={`p-3.5 rounded-xl border cursor-pointer transition flex flex-col justify-between ${
                                                selectedAllocationModel === "hybrid"
                                                    ? "bg-purple-500/10 border-purple-500 text-purple-950 dark:text-purple-200"
                                                    : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
                                            }`}
                                        >
                                            <div className="flex items-center gap-2">
                                                <input
                                                    type="radio"
                                                    name="alloc_model"
                                                    value="hybrid"
                                                    checked={selectedAllocationModel === "hybrid"}
                                                    onChange={(e) => setSelectedAllocationModel(e.target.value)}
                                                    className="text-purple-600"
                                                />
                                                <span className="font-bold text-xs">🟣 Hybrid (Vorrang + Überlauf)</span>
                                            </div>
                                            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">
                                                Stufe 1: Vorrangige Quote. Stufe 2: Ungenutzte Überschüsse werden dynamisch auf Restbedarf verteilt.
                                            </p>
                                        </label>
                                    </div>
                                </div>

                                {/* B. Quoten-Tabelle & Validierungsbalken */}
                                <div className="space-y-4">
                                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                                        <div className="flex items-center gap-3">
                                            <h4 className="font-bold text-xs text-slate-900 dark:text-white">
                                                Mitglieder-Beteiligungsquoten & MEA-Schlüssel
                                            </h4>
                                            <span
                                                className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                                                    Math.abs(currentSharesSum - 100) < 0.1
                                                        ? "bg-emerald-500/10 text-emerald-600 border-emerald-500/20"
                                                        : "bg-amber-500/10 text-amber-600 border-amber-500/20"
                                                }`}
                                            >
                                                Summe: {currentSharesSum.toFixed(2)} % {Math.abs(currentSharesSum - 100) < 0.1 ? "🟢 Ausgeglichen" : "⚠️ Nicht 100%"}
                                            </span>
                                        </div>

                                        <div className="flex items-center gap-2">
                                            <button
                                                onClick={() => saveShares(true)}
                                                disabled={savingShares || editingShares.length === 0}
                                                className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-semibold transition cursor-pointer"
                                            >
                                                ⚖️ Auf 100% normieren
                                            </button>
                                            <button
                                                onClick={() => saveShares(false)}
                                                disabled={savingShares || editingShares.length === 0}
                                                className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl text-xs font-bold transition cursor-pointer"
                                            >
                                                {savingShares ? "Speichere..." : "Quoten speichern"}
                                            </button>
                                        </div>
                                    </div>

                                    {/* Quoten Progressbar */}
                                    <div className="w-full bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden flex">
                                        <div
                                            className={`h-full transition-all ${
                                                Math.abs(currentSharesSum - 100) < 0.1 ? "bg-emerald-500" : currentSharesSum > 100 ? "bg-rose-500" : "bg-amber-500"
                                            }`}
                                            style={{ width: `${Math.min(currentSharesSum, 100)}%` }}
                                        ></div>
                                    </div>

                                    {/* Quoten Eingabetabelle */}
                                    <div className="border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden text-xs">
                                        <table className="w-full text-left border-collapse">
                                            <thead>
                                                <tr className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 font-semibold">
                                                    <th className="p-3">Mitglied / E-Mail</th>
                                                    <th className="p-3">Quote (%)</th>
                                                    <th className="p-3">Miteigentumsanteil (MEA)</th>
                                                    <th className="p-3">kWp Zuweisung</th>
                                                </tr>
                                            </thead>
                                            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                                                {editingShares.map((s, idx) => (
                                                    <tr key={s.membership_id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30">
                                                        <td className="p-3 font-semibold text-slate-900 dark:text-white">
                                                            {s.user_email}
                                                        </td>
                                                        <td className="p-3">
                                                            <div className="flex items-center gap-1.5">
                                                                <input
                                                                    type="number"
                                                                    step="0.0001"
                                                                    value={s.share_percent}
                                                                    onChange={(e) => handleShareChange(idx, "share_percent", e.target.value)}
                                                                    className="w-24 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-2.5 py-1 text-slate-900 dark:text-white font-bold"
                                                                />
                                                                <span className="text-slate-400 font-bold">%</span>
                                                            </div>
                                                        </td>
                                                        <td className="p-3">
                                                            <div className="flex items-center gap-1.5">
                                                                <input
                                                                    type="number"
                                                                    placeholder="z. B. 250"
                                                                    value={s.mea_numerator}
                                                                    onChange={(e) => handleShareChange(idx, "mea_numerator", e.target.value)}
                                                                    className="w-20 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-2.5 py-1 text-slate-900 dark:text-white"
                                                                />
                                                                <span className="text-slate-400">/</span>
                                                                <span className="text-slate-500 font-mono">1000 MEA</span>
                                                            </div>
                                                        </td>
                                                        <td className="p-3">
                                                            <div className="flex items-center gap-1.5">
                                                                <input
                                                                    type="number"
                                                                    step="0.1"
                                                                    placeholder="z. B. 3.5"
                                                                    value={s.assigned_kwp}
                                                                    onChange={(e) => handleShareChange(idx, "assigned_kwp", e.target.value)}
                                                                    className="w-20 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-2.5 py-1 text-slate-900 dark:text-white"
                                                                />
                                                                <span className="text-slate-400">kWp</span>
                                                            </div>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>

                                {/* C. 3-Modelle Simulation & Vergleich */}
                                <div className="bg-gradient-to-br from-slate-900 to-indigo-950 text-white rounded-2xl p-5 space-y-4">
                                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                                        <div>
                                            <h4 className="font-bold text-sm">
                                                📊 3-Modelle Simulations- & Ertragsvergleich
                                            </h4>
                                            <p className="text-xs text-indigo-300">
                                                Vergleicht für diesen Abrechnungsmonat den Ertrag und die Deckungsquoten aller 3 Allokationsmethoden
                                            </p>
                                        </div>
                                        <button
                                            onClick={loadSimulationPreview}
                                            disabled={previewLoading}
                                            className="px-3.5 py-1.5 bg-indigo-500 hover:bg-indigo-600 disabled:opacity-50 text-white rounded-xl text-xs font-bold transition cursor-pointer"
                                        >
                                            {previewLoading ? "Simuliere..." : "🔍 Vergleich jetzt berechnen"}
                                        </button>
                                    </div>

                                    {previewData && previewData.comparison && (
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2">
                                            {Object.values(previewData.comparison).map((comp) => (
                                                <div
                                                    key={comp.key}
                                                    className={`p-3.5 rounded-xl border ${
                                                        comp.key === selectedAllocationModel
                                                            ? "bg-indigo-500/20 border-indigo-400"
                                                            : "bg-white/5 border-white/10"
                                                    }`}
                                                >
                                                    <div className="flex justify-between items-start">
                                                        <span className="font-bold text-xs text-white">{comp.label}</span>
                                                        {comp.key === selectedAllocationModel && (
                                                            <span className="bg-indigo-500 text-[9px] font-black px-1.5 py-0.5 rounded">AKTIV</span>
                                                        )}
                                                    </div>
                                                    <div className="mt-3 space-y-1.5 text-xs">
                                                        <div className="flex justify-between text-indigo-200">
                                                            <span>Geteilter Strom:</span>
                                                            <span className="font-bold text-white">{comp.total_shared_kwh} kWh</span>
                                                        </div>
                                                        <div className="flex justify-between text-indigo-200">
                                                            <span>Gesamtersparnis:</span>
                                                            <span className="font-bold text-emerald-300">{comp.total_savings_eur.toFixed(2)} €</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>

                            </div>
                        )}

                        {/* 3. TARIFFS DRILLDOWN */}
                        {drilldownTab === "tariffs" && drilldownData.active_tariff && (
                            <div className="space-y-4">
                                <div className="bg-gradient-to-br from-indigo-900 to-slate-900 text-white rounded-2xl p-5">
                                    <div className="flex justify-between items-center">
                                        <h3 className="font-bold text-sm">{drilldownData.active_tariff.name}</h3>
                                        <span className="bg-white/10 text-indigo-200 text-xs font-semibold px-2.5 py-1 rounded-lg">
                                            Modell: {(drilldownData.active_tariff.allocation_model || "dynamic").toUpperCase()}
                                        </span>
                                    </div>
                                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4 text-xs">
                                        <div>
                                            <span className="text-indigo-300 text-[10px]">Bezugspreis (Sharing)</span>
                                            <div className="text-lg font-black">{Number(drilldownData.active_tariff.sharing_price_ct_kwh || 0).toFixed(2)} Ct/kWh</div>
                                        </div>
                                        <div>
                                            <span className="text-indigo-300 text-[10px]">Einspeisevergütung</span>
                                            <div className="text-lg font-black text-emerald-300">{Number(drilldownData.active_tariff.producer_payout_ct_kwh || 0).toFixed(2)} Ct/kWh</div>
                                        </div>
                                        <div>
                                            <span className="text-indigo-300 text-[10px]">Community-Umlage</span>
                                            <div className="text-lg font-black text-amber-300">{Number(drilldownData.active_tariff.community_fee_ct_kwh || 0).toFixed(2)} Ct/kWh</div>
                                        </div>
                                        <div>
                                            <span className="text-indigo-300 text-[10px]">Netzentgelt-Reduktion</span>
                                            <div className="text-lg font-black text-cyan-300">{Number(drilldownData.active_tariff.grid_fee_saved_ct_kwh || 0).toFixed(2)} Ct/kWh</div>
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
                                        <button
                                            onClick={() => exportMscons(selectedTenantId)}
                                            disabled={exportingFormat === "mscons"}
                                            className="px-3 py-1.5 bg-white dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-semibold transition cursor-pointer flex items-center gap-1.5 shadow-2xs"
                                        >
                                            <span>📄</span> {exportingFormat === "mscons" ? "Exportiere..." : "MSCONS (EDI)"}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* 4. ANNOUNCEMENTS DRILLDOWN */}
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

                        {/* 5. SETTINGS DRILLDOWN */}
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
                );
            })()}

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
