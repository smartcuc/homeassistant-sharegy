/*
# src/pages/TenantDashboard.jsx
*/

import { useEffect, useState, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import { apiFetch } from "../api/client";
import { useTranslation } from "react-i18next";
import { QRCodeSVG } from "qrcode.react";
import { useUser } from "../hooks/useUser";
import MsbSmartMeterHub from "../features/community/components/MsbSmartMeterHub";
import CommunityShareModal from "../features/community/components/CommunityShareModal";
import CommunityInviteModal from "../features/community/components/CommunityInviteModal";
import VirtualMasterMeterHub from "../features/community/components/VirtualMasterMeterHub";
import VppAggregatorCockpit from "../features/energy/components/VppAggregatorCockpit";
import TenantSetupWizardModal from "../features/community/components/TenantSetupWizardModal";
import WhitelabelSettingsModal from "../features/tenant/components/WhitelabelSettingsModal";
import MarketCommunicationModal from "../features/billing/components/MarketCommunicationModal";

const ALL_TABS = ["cockpit", "virtual_meter", "vpp", "settlement", "members", "msb", "audit"];
const MEMBER_TABS = ["cockpit", "settlement"];

export default function TenantDashboard() {
    const { t } = useTranslation();
    const { user, isStaffOrAdmin, hasCommunityAdminAccess } = useUser();
    const [searchParams, setSearchParams] = useSearchParams();
    const initialTab = searchParams.get("tab");
    const [tenant, setTenant] = useState(null);
    const [members, setMembers] = useState([]);
    const [invites, setInvites] = useState([]);
    const [logs, setLogs] = useState([]);
    const [cockpit, setCockpit] = useState(null);
    const [tariffData, setTariffData] = useState(null);
    const [statementsData, setStatementsData] = useState(null);
    const [sharesData, setSharesData] = useState(null);
    const [timeRange, setTimeRange] = useState("today"); // 'today' | 'month'

    const isCommunityAdmin = useMemo(() => {
        return Boolean(
            isStaffOrAdmin ||
            hasCommunityAdminAccess ||
            tenant?.is_admin ||
            statementsData?.is_admin ||
            ["admin", "owner", "auditor"].includes(tenant?.user_role)
        );
    }, [isStaffOrAdmin, hasCommunityAdminAccess, tenant, statementsData]);

    const allowedTabs = isCommunityAdmin ? ALL_TABS : MEMBER_TABS;

    const [activeTab, setActiveTab] = useState(
        allowedTabs.includes(initialTab) ? initialTab : "cockpit"
    );
    const [loading, setLoading] = useState(true);
    const [shareModalOpen, setShareModalOpen] = useState(false);
    const [inviteModalOpen, setInviteModalOpen] = useState(false);
    const [inviteInitialRole, setInviteInitialRole] = useState("member");
    const [wizardOpen, setWizardOpen] = useState(false);
    const [whitelabelModalOpen, setWhitelabelModalOpen] = useState(false);
    const [makoModalOpen, setMakoModalOpen] = useState(false);
    const [settling, setSettling] = useState(false);
    const [downloadingId, setDownloadingId] = useState(null);
    const [exportingFormat, setExportingFormat] = useState(null);
    const [activeQrToken, setActiveQrToken] = useState(null);
    const [copiedToken, setCopiedToken] = useState(null);

    // ✅ Daten laden
    async function loadData() {
        setLoading(true);
        try {
            const data = await apiFetch("/api/my-tenant/");
            setTenant(data.tenant);
            setMembers(data.members || []);
            setInvites(data.invites || []);

            if (data.tenant) {
                const isUserAdmin = data.tenant.is_admin || isStaffOrAdmin || hasCommunityAdminAccess;

                const fetchPromises = [
                    apiFetch("/api/billing/community/cockpit/").catch(() => null),
                    apiFetch("/api/billing/community/tariffs/").catch(() => null),
                    apiFetch("/api/billing/community/statements/").catch(() => null),
                    apiFetch("/api/billing/community/shares/").catch(() => null),
                ];

                if (isUserAdmin) {
                    fetchPromises.push(apiFetch("/api/audit-log/").catch(() => []));
                }

                const [cockpitData, tariffsRes, statementsRes, sharesRes, logData] = await Promise.all(fetchPromises);

                setLogs(logData || []);
                setCockpit(cockpitData);
                setTariffData(tariffsRes);
                setStatementsData(statementsRes);
                setSharesData(sharesRes);
            } else {
                setLogs([]);
                setCockpit(null);
                setTariffData(null);
                setStatementsData(null);
                setSharesData(null);
            }
        } catch (err) {
            console.error("Load failed:", err);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadData();
    }, []);

    useEffect(() => {
        const tab = searchParams.get("tab");
        if (tab && allowedTabs.includes(tab) && tab !== activeTab) {
            setActiveTab(tab);
        } else if (tab && !allowedTabs.includes(tab)) {
            setActiveTab("cockpit");
        }
    }, [searchParams, allowedTabs]);

    function handleTabChange(newTab) {
        const targetTab = allowedTabs.includes(newTab) ? newTab : "cockpit";
        setActiveTab(targetTab);
        setSearchParams(
            (prev) => {
                const next = new URLSearchParams(prev);
                if (targetTab === "cockpit") {
                    next.delete("tab");
                } else {
                    next.set("tab", targetTab);
                }
                return next;
            },
            { replace: true }
        );
    }

    // ✅ MONATLICHE ABRECHNUNG ANSTOSSEN
    async function triggerSettlement() {
        setSettling(true);
        try {
            const now = new Date();
            const res = await apiFetch("/api/billing/community/statements/generate/", {
                method: "POST",
                body: JSON.stringify({
                    tenant_id: tenant.id,
                    year: now.getFullYear(),
                    month: now.getMonth() + 1,
                }),
            });
            alert(res.message || "Abrechnung erfolgreich generiert.");
            const statementsRes = await apiFetch("/api/billing/community/statements/").catch(() => null);
            setStatementsData(statementsRes);
        } catch (err) {
            alert("Abrechnungsfehler: " + (err.message || "Unbekannter Fehler"));
        } finally {
            setSettling(false);
        }
    }

    // ✅ INVITE ERSTELLEN
    async function createInvite(role) {
        try {
            const data = await apiFetch("/api/create-invite/", {
                method: "POST",
                body: JSON.stringify({
                    tenant_id: tenant.id,
                    role: role,
                }),
            });
            await loadData();
            return data;
        } catch (err) {
            console.error("Invite error:", err);
            alert("Fehler beim Erstellen des Einladungslinks: " + (err.message || ""));
            throw err;
        }
    }

    // ✅ PDF STATEMENT DOWNLOAD
    async function downloadStatementPdf(statementId, statementNumber) {
        setDownloadingId(statementId);
        try {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            const response = await fetch(`/api/billing/community/statements/${statementId}/pdf/`, {
                headers: {
                    Authorization: token ? `Bearer ${token}` : "",
                    "X-Tenant-ID": tenant?.id || "",
                }
            });
            if (!response.ok) throw new Error("Download fehlgeschlagen.");
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `Abrechnungsnachweis_${statementNumber}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error("PDF Download error:", err);
            alert("Fehler beim Herunterladen des PDF-Abrechnungsnachweises.");
        } finally {
            setDownloadingId(null);
        }
    }

    // ✅ MULTI-FORMAT EXPORT (XLSX, CSV, XML)
    async function exportCommunityStatements(format = "xlsx") {
        setExportingFormat(format);
        try {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            const response = await fetch(`/api/billing/community/statements/export/?export_format=${format}&tenant_id=${tenant?.id || ""}`, {
                headers: {
                    Authorization: token ? `Bearer ${token}` : "",
                    "X-Tenant-ID": tenant?.id || "",
                }
            });
            if (!response.ok) throw new Error("Export fehlgeschlagen.");
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            const ext = format === "xlsx" ? "xlsx" : format === "csv" ? "csv" : "xml";
            a.download = `Sharegy_Abrechnungsdaten_${tenant?.slug || "community"}_${new Date().toISOString().slice(0, 10)}.${ext}`;
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

    // ✅ ROLE UPDATE

    async function updateRole(userId, role) {
        await apiFetch("/api/update-role/", {
            method: "POST",
            body: JSON.stringify({
                tenant_id: tenant.id,
                user_id: userId,
                role: role,
            }),
        });
        loadData();
    }

    // ✅ MEMBER ENTFERNEN
    async function removeMember(userId) {
        if (!confirm("Möchtest du dieses Mitglied wirklich aus der Community entfernen?")) return;
        await apiFetch("/api/remove-member/", {
            method: "POST",
            body: JSON.stringify({
                tenant_id: tenant.id,
                user_id: userId,
            }),
        });
        loadData();
    }

    // ✅ INVITE DEAKTIVIEREN / WIDERRUFEN
    async function deactivateInvite(token) {
        if (!window.confirm("Möchtest du diesen Einladungslink wirklich widerrufen und dauerhaft löschen?")) {
            return;
        }
        try {
            await apiFetch("/api/deactivate-invite/", {
                method: "POST",
                body: JSON.stringify({ token }),
            });
            // Sofort aus der Liste entfernen
            setInvites((prev) => prev.filter((i) => i.token !== token));
            await loadData();
        } catch (err) {
            console.error("Deactivate error:", err);
            alert("Fehler beim Widerrufen des Einladungslinks: " + (err.message || ""));
        }
    }

    function formatAction(log) {
        switch (log.action) {
            case "member_removed":
                return t.member_removed || "Mitglied entfernt";
            case "role_updated":
                return t.role_updated || "Rolle geändert";
            case "invite_created":
                return t.invite_created || "Invite erstellt";
            case "invite_deactivated":
                return t.invite_deactivated || "Invite deaktiviert";
            default:
                return log.action;
        }
    }

    function formatDate(date) {
        return new Date(date).toLocaleString();
    }

    if (loading) {
        return (
            <div className="p-12 text-center text-slate-400 text-sm animate-pulse">
                Lade Energy Community Dashboard & Bilanzen...
            </div>
        );
    }

    if (!tenant) {
        return (
            <div className="p-8 max-w-xl mx-auto text-center space-y-4 my-8 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-xs">
                <div className="text-4xl">🏛️</div>
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                    Keine aktive Energy Community
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                    Du bist aktuell noch keiner Energy Community zugewiesen oder hast noch keinen Einladungslink eingelöst.
                </p>
                <div className="pt-2">
                    <button
                        onClick={() => window.location.href = "/app/dashboard"}
                        className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-xs transition cursor-pointer"
                    >
                        Zurück zum Dashboard
                    </button>
                </div>
            </div>
        );
    }

    const currentStats = cockpit ? (timeRange === "today" ? cockpit.today : cockpit.month) : null;
    const activeTariff = tariffData ? tariffData.active_tariff : null;
    const statements = statementsData ? statementsData.statements : [];

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">

            {/* ✅ TITLE & HEADER (FULL WIDTH WITH ACTION BADGES UNDERNEATH) */}
            <div className="space-y-4 pb-4 border-b border-slate-200 dark:border-slate-800">
                <div className="flex items-start gap-3.5">
                    <div className="w-10 h-10 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-xl shrink-0 mt-0.5">
                        ⚡
                    </div>
                    <div className="flex-1 min-w-0">
                        <div className="flex flex-wrap items-center gap-2.5">
                            <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white truncate">
                                {tenant.name}
                            </h1>
                            <span className="shrink-0 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-xs font-bold px-3 py-1 rounded-full border border-emerald-500/20 flex items-center gap-1.5">
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                                {t("tenant.community_active", "Community Aktiv")}
                            </span>
                        </div>
                        <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
                            {t("tenant.subtitle", "Eichrechtskonformes 15-Minuten Energy Sharing & Prädiktive KI-Steuerung")}
                        </p>
                    </div>
                </div>

                {/* Quick Action Badges Bar */}
                <div className="flex flex-wrap items-center gap-2.5 pt-1">
                    {isCommunityAdmin && (
                        <>
                            <button
                                type="button"
                                onClick={() => setWhitelabelModalOpen(true)}
                                className="px-3.5 py-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-900 hover:bg-sky-50 dark:hover:bg-sky-950/40 text-slate-700 dark:text-slate-200 hover:text-sky-600 dark:hover:text-sky-400 border border-slate-200 dark:border-slate-800 hover:border-sky-300 dark:hover:border-sky-800 transition-all shadow-xs flex items-center gap-2 hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
                            >
                                <span className="text-sm">🎨</span>
                                <span>{t("tenant.whitelabel_btn", "Whitelabel & Branding")}</span>
                            </button>
                            <button
                                type="button"
                                onClick={() => setMakoModalOpen(true)}
                                className="px-3.5 py-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-900 hover:bg-teal-50 dark:hover:bg-teal-950/40 text-slate-700 dark:text-slate-200 hover:text-teal-600 dark:hover:text-teal-400 border border-slate-200 dark:border-slate-800 hover:border-teal-300 dark:hover:border-teal-800 transition-all shadow-xs flex items-center gap-2 hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
                            >
                                <span className="text-sm">📄</span>
                                <span>{t("tenant.mako_btn", "Marktkommunikation (AS4)")}</span>
                            </button>
                            <button
                                type="button"
                                onClick={() => setWizardOpen(true)}
                                className="px-3.5 py-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-900 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 text-slate-700 dark:text-slate-200 hover:text-indigo-600 dark:hover:text-indigo-400 border border-slate-200 dark:border-slate-800 hover:border-indigo-300 dark:hover:border-indigo-800 transition-all shadow-xs flex items-center gap-2 hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
                            >
                                <span className="text-sm">✨</span>
                                <span>{t("tenant.wizard_btn", "Gebäude-Assistent (3 Schritte)")}</span>
                            </button>
                        </>
                    )}
                    <button
                        type="button"
                        onClick={() => setShareModalOpen(true)}
                        className="px-3.5 py-2 rounded-xl text-xs font-bold bg-emerald-50 dark:bg-emerald-950/40 hover:bg-emerald-100 dark:hover:bg-emerald-900/60 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800/80 hover:border-emerald-300 transition-all shadow-xs flex items-center gap-2 hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
                    >
                        <span className="text-sm">📢</span>
                        <span>{t("tenant.share_btn", "Erfolge teilen")}</span>
                    </button>
                </div>
            </div>

                {/* TAB SWITCHER */}
                <div className="flex flex-wrap bg-slate-100 dark:bg-slate-800/70 p-1 rounded-xl text-xs font-semibold gap-1">
                    <button
                        onClick={() => handleTabChange("cockpit")}
                        className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                            activeTab === "cockpit"
                                ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs"
                                : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                        }`}
                    >
                        ⚡ {isCommunityAdmin ? "Cockpit" : "Mein Verbrauch & Bilanzen"}
                    </button>

                    {isCommunityAdmin && (
                        <>
                            <button
                                onClick={() => handleTabChange("virtual_meter")}
                                className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                                    activeTab === "virtual_meter"
                                        ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 font-bold shadow-xs"
                                        : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                                }`}
                            >
                                🏢 Virtueller Summenzähler
                            </button>
                            <button
                                onClick={() => handleTabChange("vpp")}
                                className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                                    activeTab === "vpp"
                                        ? "bg-white dark:bg-slate-900 text-amber-600 dark:text-amber-400 font-bold shadow-xs"
                                        : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                                }`}
                            >
                                🔌 VPP Kraftwerk
                            </button>
                        </>
                    )}

                    <button
                        onClick={() => handleTabChange("settlement")}
                        className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                            activeTab === "settlement"
                                ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs"
                                : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                        }`}
                    >
                        💰 {isCommunityAdmin ? "Tarife & Abrechnungen" : "Meine Abrechnungen & Tarife"}
                    </button>

                    {isCommunityAdmin && (
                        <>
                            <button
                                onClick={() => handleTabChange("members")}
                                className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                                    activeTab === "members"
                                        ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs"
                                        : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                                }`}
                            >
                                👥 Mitglieder ({members.length})
                            </button>
                            <button
                                onClick={() => handleTabChange("msb")}
                                className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                                    activeTab === "msb"
                                        ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs font-bold"
                                        : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                                }`}
                            >
                                ⚡ wMSB Hub
                            </button>
                            <button
                                onClick={() => handleTabChange("audit")}
                                className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                                    activeTab === "audit"
                                        ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs"
                                        : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                                }`}
                            >
                                📜 Audit
                            </button>
                        </>
                    )}
                </div>

            {/* ======================================================== */}
            {/* 1. COCKPIT TAB */}
            {/* ======================================================== */}
            {activeTab === "cockpit" && cockpit && (
                <div className="space-y-6">

                    {/* ZEITRAUM FILTER */}
                    <div className="flex items-center justify-between">
                        <h2 className="text-sm font-bold text-slate-800 dark:text-slate-200">
                            Community Bilanzen & Kennzahlen
                        </h2>
                        <div className="flex bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg text-xs font-semibold">
                            <button
                                onClick={() => setTimeRange("today")}
                                className={`px-2.5 py-1 rounded-md transition ${
                                    timeRange === "today"
                                        ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs"
                                        : "text-slate-500"
                                }`}
                            >
                                Heute
                            </button>
                            <button
                                onClick={() => setTimeRange("month")}
                                className={`px-2.5 py-1 rounded-md transition ${
                                    timeRange === "month"
                                        ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs"
                                        : "text-slate-500"
                                }`}
                            >
                                Dieser Monat
                            </button>
                        </div>
                    </div>

                    {/* 5 HERO KPI CARDS */}
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
                        
                        {/* 1. PRODUZIERT */}
                        <div className="bg-amber-500/5 dark:bg-amber-500/10 border border-amber-500/20 rounded-2xl p-4 flex flex-col justify-between">
                            <div className="flex items-center justify-between">
                                <span className="text-[11px] font-bold text-amber-700 dark:text-amber-300 uppercase tracking-wider">
                                    Produziert (2.8.0)
                                </span>
                                <span className="text-lg">☀️</span>
                            </div>
                            <div className="mt-3">
                                <div className="text-2xl font-black text-amber-900 dark:text-amber-100">
                                    {Number(currentStats?.produced_kwh ?? 0).toFixed(1)} <span className="text-xs font-normal">kWh</span>
                                </div>
                                <div className="text-[11px] text-amber-700/80 dark:text-amber-300/80 mt-0.5">
                                    Gesamte Solar-Erzeugung
                                </div>
                            </div>
                        </div>

                        {/* 2. VERBRAUCHT */}
                        <div className="bg-sky-500/5 dark:bg-sky-500/10 border border-sky-500/20 rounded-2xl p-4 flex flex-col justify-between">
                            <div className="flex items-center justify-between">
                                <span className="text-[11px] font-bold text-sky-700 dark:text-sky-300 uppercase tracking-wider">
                                    Verbraucht (1.8.0)
                                </span>
                                <span className="text-lg">🏠</span>
                            </div>
                            <div className="mt-3">
                                <div className="text-2xl font-black text-sky-900 dark:text-sky-100">
                                    {Number(currentStats?.consumed_kwh ?? 0).toFixed(1)} <span className="text-xs font-normal">kWh</span>
                                </div>
                                <div className="text-[11px] text-sky-700/80 dark:text-sky-300/80 mt-0.5">
                                    Bedarf aller Mitglieder
                                </div>
                            </div>
                        </div>

                        {/* 3. GETEILT (SHARING) */}
                        <div className="bg-emerald-500/5 dark:bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-4 flex flex-col justify-between">
                            <div className="flex items-center justify-between">
                                <span className="text-[11px] font-bold text-emerald-700 dark:text-emerald-300 uppercase tracking-wider">
                                    Geteilt (Sharing)
                                </span>
                                <span className="text-lg">🤝</span>
                            </div>
                            <div className="mt-3">
                                <div className="text-2xl font-black text-emerald-900 dark:text-emerald-100">
                                    {Number(currentStats?.shared_kwh ?? 0).toFixed(1)} <span className="text-xs font-normal">kWh</span>
                                </div>
                                <div className="text-[11px] text-emerald-700/80 dark:text-emerald-300/80 mt-0.5 font-semibold">
                                    Autarkiegrad: {currentStats?.autarky_pct ?? 0}%
                                </div>
                            </div>
                        </div>

                        {/* 4. RESTSTROM VOM NETZ */}
                        <div className="bg-rose-500/5 dark:bg-rose-500/10 border border-rose-500/20 rounded-2xl p-4 flex flex-col justify-between">
                            <div className="flex items-center justify-between">
                                <span className="text-[11px] font-bold text-rose-700 dark:text-rose-300 uppercase tracking-wider">
                                    Zugekauft (Rest)
                                </span>
                                <span className="text-lg">🔌</span>
                            </div>
                            <div className="mt-3">
                                <div className="text-2xl font-black text-rose-900 dark:text-rose-100">
                                    {Number(currentStats?.grid_import_kwh ?? 0).toFixed(1)} <span className="text-xs font-normal">kWh</span>
                                </div>
                                <div className="text-[11px] text-rose-700/80 dark:text-rose-300/80 mt-0.5">
                                    Über Restversorger bezogen
                                </div>
                            </div>
                        </div>

                        {/* 5. FINANZIELLE ERSPARNIS */}
                        <div className="bg-indigo-500/5 dark:bg-indigo-500/10 border border-indigo-500/20 rounded-2xl p-4 flex flex-col justify-between col-span-2 sm:col-span-1">
                            <div className="flex items-center justify-between">
                                <span className="text-[11px] font-bold text-indigo-700 dark:text-indigo-300 uppercase tracking-wider">
                                    Ersparnis
                                </span>
                                <span className="text-lg">💰</span>
                            </div>
                            <div className="mt-3">
                                <div className="text-2xl font-black text-indigo-900 dark:text-indigo-100">
                                    {Number(currentStats?.savings_eur ?? 0).toFixed(2)} <span className="text-xs font-normal">€</span>
                                </div>
                                <div className="text-[11px] text-indigo-700/80 dark:text-indigo-300/80 mt-0.5 font-semibold">
                                    vs. Grundversorger
                                </div>
                            </div>
                        </div>

                    </div>

                    {/* 48H KI-PROGNOSE BLOCK */}
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs">
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-2">
                                <span className="text-xl">🔮</span>
                                <div>
                                    <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                                        48-Stunden KI-Erzeugungsprognose & Ladefenster
                                    </h3>
                                    <p className="text-xs text-slate-500 dark:text-slate-400">
                                        Prädiktive Lastoptimierung auf Basis von Wettermodellen & historischen Community-Mustern
                                    </p>
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="text-xs font-bold text-indigo-600 dark:text-indigo-400">
                                    +{cockpit.forecast_48h.total_predicted_kwh.toFixed(1)} kWh
                                </div>
                                <div className="text-[10px] text-slate-400">erwarteter Ertrag</div>
                            </div>
                        </div>

                        {cockpit.forecast_48h.hours.length > 0 ? (
                            <div className="space-y-2">
                                <div className="grid grid-cols-6 sm:grid-cols-12 gap-1.5 pt-2">
                                    {cockpit.forecast_48h.hours.slice(0, 24).map((h, i) => (
                                        <div
                                            key={i}
                                            className={`p-2 rounded-xl text-center flex flex-col justify-between border transition ${
                                                h.is_peak_window
                                                    ? "bg-amber-500/10 border-amber-500/30 text-amber-800 dark:text-amber-200"
                                                    : "bg-slate-50 dark:bg-slate-800/40 border-slate-200/60 dark:border-slate-800 text-slate-600 dark:text-slate-400"
                                            }`}
                                        >
                                            <span className="text-[10px] font-mono">
                                                {new Date(h.timestamp).getHours()}:00
                                            </span>
                                            <span className="text-xs font-black my-1">
                                                {h.power_kw} <span className="text-[9px] font-normal">kW</span>
                                            </span>
                                            {h.is_peak_window && (
                                                <span className="text-[9px] font-bold text-emerald-600 dark:text-emerald-400">
                                                    ⚡ Günstig
                                                </span>
                                            )}
                                        </div>
                                    ))}
                                </div>
                                <div className="text-[11px] text-slate-500 dark:text-slate-400 flex items-center gap-2 pt-2">
                                    <span className="w-2 h-2 rounded-full bg-amber-500"></span>
                                    <span>Gelb hinterlegte Zeitfenster: Hohe Solarverfügbarkeit in der Community – ideal für E-Auto & Heimspeicher.</span>
                                </div>
                            </div>
                        ) : (
                            <div className="text-center py-6 text-xs text-slate-400 bg-slate-50 dark:bg-slate-800/30 rounded-xl border border-dashed border-slate-200 dark:border-slate-800">
                                ☀️ Keine 48h-Wetterdaten hinterlegt. Die KI-Prognose wird automatisch nach Synchronisation der Solaranlagen berechnet.
                            </div>
                        )}
                    </div>

                    {/* 15-MINUTEN LASTGANG ZEITREIHE */}
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs">
                        <div className="flex items-center justify-between mb-4">
                            <div>
                                <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                                    15-Minuten Lastgang & Sharing-Verlauf (Letzte 24 Stunden)
                                </h3>
                                <p className="text-xs text-slate-500 dark:text-slate-400">
                                    Eichrechtskonforme Erfassung aller 15m-Slots aus OBIS 1.8.0 & 2.8.0
                                </p>
                            </div>
                            <div className="flex items-center gap-3 text-xs">
                                <span className="flex items-center gap-1.5 text-amber-600 font-semibold">
                                    <span className="w-2.5 h-2.5 rounded-sm bg-amber-500"></span> Erzeugung
                                </span>
                                <span className="flex items-center gap-1.5 text-sky-600 font-semibold">
                                    <span className="w-2.5 h-2.5 rounded-sm bg-sky-500"></span> Verbrauch
                                </span>
                                <span className="flex items-center gap-1.5 text-emerald-600 font-semibold">
                                    <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500"></span> Geteilt
                                </span>
                            </div>
                        </div>

                        {cockpit.timeseries_24h.length > 0 ? (
                            <div className="space-y-1 max-h-72 overflow-y-auto pr-1">
                                {cockpit.timeseries_24h.slice(-16).reverse().map((slot, idx) => (
                                    <div
                                        key={idx}
                                        className="flex items-center justify-between p-2.5 bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800 rounded-xl text-xs"
                                    >
                                        <span className="font-mono text-slate-500 dark:text-slate-400">
                                            {new Date(slot.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} Uhr
                                        </span>
                                        <div className="flex items-center gap-4">
                                            <span className="text-amber-600 dark:text-amber-400 font-bold">
                                                ☀️ {slot.produced_kwh.toFixed(2)} kWh
                                            </span>
                                            <span className="text-sky-600 dark:text-sky-400 font-bold">
                                                🏠 {slot.consumed_kwh.toFixed(2)} kWh
                                            </span>
                                            <span className="text-emerald-600 dark:text-emerald-400 font-black">
                                                🤝 {slot.shared_kwh.toFixed(2)} kWh
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-xs text-slate-400 bg-slate-50 dark:bg-slate-800/30 rounded-xl border border-dashed border-slate-200 dark:border-slate-800">
                                📊 Noch keine 15-Minuten-Slots für diesen Tag vorhanden. Messwerte des MSB werden alle 15 Minuten automatisch eingelesen.
                            </div>
                        )}
                    </div>

                </div>
            )}

            {/* ======================================================== */}
            {/* 2. TARIFE & ABRECHNUNGEN TAB */}
            {/* ======================================================== */}
            {activeTab === "settlement" && (
                <div className="space-y-6">

                    {/* AKTIVER SHARING TARIF */}
                    {activeTariff && (
                        <div className="bg-gradient-to-br from-indigo-900 to-slate-900 text-white rounded-2xl p-6 border border-indigo-700/50 shadow-md space-y-6">
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                                <div>
                                    <div className="flex items-center gap-2">
                                        <span className="text-xl shrink-0">🏷️</span>
                                        <h2 className="text-lg font-black tracking-tight">{activeTariff.name}</h2>
                                        <span className="shrink-0 bg-emerald-400/20 text-emerald-300 text-[10px] font-bold px-2 py-0.5 rounded-full border border-emerald-400/30">
                                            Aktiv
                                        </span>
                                    </div>
                                    <div className="mt-1.5 flex flex-wrap items-center gap-2">
                                        <span className="shrink-0 bg-indigo-400/20 text-indigo-200 text-[10px] font-bold px-2.5 py-0.5 rounded-full border border-indigo-400/30">
                                            Allokation: {activeTariff.allocation_model === "dynamic" ? "🟢 Dynamisch (15m Lastgang)" : activeTariff.allocation_model === "static" ? "🔵 Statisch (MEA-Quote)" : "🟣 Hybrid (Vorrang + Überlauf)"}
                                        </span>
                                        <span className="text-xs text-indigo-200/80">
                                            Gültige Konditionen für alle Teilnehmer gem. § 42b EnWG
                                        </span>
                                    </div>
                                </div>

                                {statementsData?.is_admin && (
                                    <button
                                        onClick={triggerSettlement}
                                        disabled={settling}
                                        className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-white rounded-xl text-xs font-bold shadow-xs transition cursor-pointer flex items-center gap-1.5"
                                    >
                                        <span>⚡</span> {settling ? "Berechne..." : "Monatsabrechnung anstoßen"}
                                    </button>
                                )}
                            </div>

                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-indigo-800/60">
                                <div>
                                    <div className="text-[11px] text-indigo-300 font-semibold uppercase">Bezugspreis (Sharing)</div>
                                    <div className="text-2xl font-black mt-1 text-white">
                                        {Number(activeTariff?.sharing_price_ct_kwh ?? 0).toFixed(2)} <span className="text-xs font-normal">Ct/kWh</span>
                                    </div>
                                    <div className="text-[10px] text-indigo-300/70 mt-0.5">für Solar-Abnehmer</div>
                                </div>

                                <div>
                                    <div className="text-[11px] text-indigo-300 font-semibold uppercase">Einspeisevergütung</div>
                                    <div className="text-2xl font-black mt-1 text-emerald-300">
                                        {Number(activeTariff?.producer_payout_ct_kwh ?? 0).toFixed(2)} <span className="text-xs font-normal">Ct/kWh</span>
                                    </div>
                                    <div className="text-[10px] text-indigo-300/70 mt-0.5">Gutschrift an Einspeiser</div>
                                </div>

                                <div>
                                    <div className="text-[11px] text-indigo-300 font-semibold uppercase">Community-Umlage</div>
                                    <div className="text-2xl font-black mt-1 text-amber-300">
                                        {Number(activeTariff?.community_fee_ct_kwh ?? 0).toFixed(2)} <span className="text-xs font-normal">Ct/kWh</span>
                                    </div>
                                    <div className="text-[10px] text-indigo-300/70 mt-0.5">Betrieb & Software</div>
                                </div>

                                <div>
                                    <div className="text-[11px] text-indigo-300 font-semibold uppercase">Ersparnis vs. Netz</div>
                                    <div className="text-2xl font-black mt-1 text-cyan-300">
                                        ~22,00 <span className="text-xs font-normal">Ct/kWh</span>
                                    </div>
                                    <div className="text-[10px] text-indigo-300/70 mt-0.5">ggü. Grundversorger</div>
                                </div>
                            </div>

                            {/* Quoten-Hinweis falls Quoten konfiguriert */}
                            {sharesData && sharesData.shares && sharesData.shares.length > 0 && (
                                <div className="bg-white/5 border border-white/10 rounded-xl p-3 text-xs flex items-center justify-between gap-2">
                                    <div className="flex items-center gap-2">
                                        <span>⚖️</span>
                                        <span className="text-indigo-200">
                                            Konfigurierte Beteiligungsquoten: <strong>{sharesData.shares.length} Mitglieder</strong> (Gesamt: {Number(sharesData.total_allocated_percent ?? sharesData.total_configured_share_percent ?? 0).toFixed(1)} %)
                                        </span>
                                    </div>
                                    <span className="text-[11px] text-indigo-300 font-mono">
                                        Modell: {(activeTariff?.allocation_model || "DYNAMIC").toUpperCase()}
                                    </span>
                                </div>
                            )}
                        </div>
                    )}

                    {/* MONATLICHE ABRECHNUNGSNACHWEISE */}
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                            <div>
                                <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                                    {isCommunityAdmin
                                        ? "Monatliche Abrechnungsnachweise (Gesamte Community)"
                                        : "Meine monatlichen Abrechnungsnachweise"}
                                </h3>
                                <p className="text-xs text-slate-500 dark:text-slate-400">
                                    {isCommunityAdmin
                                        ? "15-Minuten-scharfe Verrechnung von Erzeugung, Bezug und internen Gutschriften aller Mitglieder"
                                        : "Eichrechtskonforme Abrechnung deines Solarstrombezugs und deiner Einspeisevergütung"}
                                </p>
                            </div>
                            <div className="flex flex-wrap items-center gap-2">
                                <span className="text-xs font-semibold text-slate-500 mr-1">
                                    {statements.length} {statements.length === 1 ? "Nachweis" : "Nachweise"}
                                </span>
                                {isCommunityAdmin && statements.length > 0 && (
                                    <div className="flex items-center gap-1.5">
                                        <button
                                            onClick={() => exportCommunityStatements("xlsx")}
                                            disabled={exportingFormat === "xlsx"}
                                            className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-semibold transition cursor-pointer flex items-center gap-1 border border-slate-200 dark:border-slate-700"
                                            title="Als formatierte Excel-Arbeitsmappe exportieren"
                                        >
                                            <span>📗</span> {exportingFormat === "xlsx" ? "Exportiere..." : "Excel"}
                                        </button>
                                        <button
                                            onClick={() => exportCommunityStatements("csv")}
                                            disabled={exportingFormat === "csv"}
                                            className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-semibold transition cursor-pointer flex items-center gap-1 border border-slate-200 dark:border-slate-700"
                                            title="Als CSV für DATEV/ERP exportieren"
                                        >
                                            <span>📊</span> {exportingFormat === "csv" ? "Exportiere..." : "CSV"}
                                        </button>
                                        <button
                                            onClick={() => exportCommunityStatements("xml")}
                                            disabled={exportingFormat === "xml"}
                                            className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-semibold transition cursor-pointer flex items-center gap-1 border border-slate-200 dark:border-slate-700"
                                            title="Als standardisiertes ERP XML exportieren"
                                        >
                                            <span>📦</span> {exportingFormat === "xml" ? "Exportiere..." : "XML"}
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>

                        {statements.length > 0 ? (
                            <div className="space-y-3">
                                {statements.map(stmt => (
                                    <div
                                        key={stmt.id}
                                        className="border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40 p-4 rounded-xl shadow-xs space-y-3"
                                    >
                                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
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
                                                {isCommunityAdmin && (
                                                    <div className="text-xs text-slate-500 dark:text-slate-400">
                                                        Mitglied: <span className="font-medium text-slate-700 dark:text-slate-300">{stmt.user_email}</span>
                                                    </div>
                                                )}
                                                <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs pt-1 text-slate-600 dark:text-slate-400">
                                                    <span>☀️ Erzeugt: <strong>{Number(stmt.produced_total_kwh ?? 0).toFixed(1)} kWh</strong></span>
                                                    <span>🏠 Verbraucht: <strong>{Number(stmt.consumed_total_kwh ?? 0).toFixed(1)} kWh</strong></span>
                                                    <span>🤝 Geteilt: <strong>{(Number(stmt.shared_imported_kwh ?? 0) + Number(stmt.shared_exported_kwh ?? 0)).toFixed(1)} kWh</strong></span>
                                                </div>
                                            </div>

                                            <div className="text-right sm:border-l sm:border-slate-200 dark:sm:border-slate-700 sm:pl-6">
                                                <div className="text-[11px] text-slate-500 dark:text-slate-400">
                                                    {stmt.is_payout ? "Gutschrift / Auszahlung" : "Forderung / Nachzahlung"}
                                                </div>
                                                <div className={`text-xl font-black mt-0.5 ${
                                                    stmt.is_payout
                                                        ? "text-emerald-600 dark:text-emerald-400"
                                                        : "text-rose-600 dark:text-rose-400"
                                                }`}>
                                                    {stmt.is_payout ? "+" : ""}{Number(stmt.net_balance_eur ?? 0).toFixed(2)} €
                                                </div>
                                                <div className="text-[10px] text-slate-400 mt-0.5">
                                                    Gutschrift: {Number(stmt.credit_shared_export_eur ?? 0).toFixed(2)} € | Bezug: {Number(stmt.charge_shared_import_eur ?? 0).toFixed(2)} €
                                                </div>
                                            </div>
                                        </div>

                                        <div className="pt-2.5 border-t border-slate-200/70 dark:border-slate-700/70 flex justify-end">
                                            <button
                                                onClick={() => downloadStatementPdf(stmt.id, stmt.statement_number)}
                                                disabled={downloadingId === stmt.id}
                                                className="px-3 py-1.5 bg-white dark:bg-slate-900 hover:bg-indigo-50 dark:hover:bg-slate-800 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800/80 rounded-lg text-xs font-bold transition cursor-pointer flex items-center gap-1.5 shadow-2xs"
                                            >
                                                <span>📄</span> {downloadingId === stmt.id ? "Erzeuge PDF..." : "PDF-Nachweis herunterladen"}
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-10 text-xs text-slate-400 bg-slate-50 dark:bg-slate-800/30 rounded-xl border border-dashed border-slate-200 dark:border-slate-800">
                                {isCommunityAdmin
                                    ? "📜 Noch keine Monatsabrechnungen erstellt. Klicke auf 'Monatsabrechnung anstoßen', um den aktuellen Monat abzurechnen."
                                    : "📜 Für deinen Account liegen aktuell noch keine abgeschlossenen Monatsabrechnungen vor. Sobald der Abrechnungslauf zum Monatsende abgeschlossen ist, kannst du deinen PDF-Nachweis hier direkt herunterladen."}
                            </div>
                        )}
                    </div>


                </div>
            )}

            {/* ======================================================== */}
            {/* 3. MEMBERS & INVITES TAB */}
            {/* ======================================================== */}
            {activeTab === "members" && (
                <div className="space-y-6">

                    {/* INVITES SECTION */}
                    <section className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-xs space-y-5">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100 dark:border-slate-800">
                            <div>
                                <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                    <span>🤝</span>
                                    <span>{t("tenant.invites_title", "Einladungslinks für Mitglieder & Mieter")}</span>
                                </h2>
                                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                                    {t("tenant.invites_subtitle", "Lade Teilnehmer für das gemeinschaftliche Energy Sharing (§ 42b EnWG) oder Mieterstrom ein.")}
                                </p>
                            </div>

                            <button
                                type="button"
                                onClick={() => {
                                    setInviteInitialRole("member");
                                    setInviteModalOpen(true);
                                }}
                                className="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold shadow-xs transition-all flex items-center gap-2 hover:scale-[1.02] active:scale-[0.98] cursor-pointer self-start sm:self-auto"
                            >
                                <span>+</span>
                                <span>{t("tenant.btn_invite_member", "Mitglied oder Mieter einladen")}</span>
                            </button>
                        </div>

                        {/* ROLE SHORTCUT PILLS */}
                        <div>
                            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                                {t("tenant.quick_invite_role", "Schnellauswahl nach Rolle:")}
                            </div>
                            <div className="flex flex-wrap gap-2">
                                <button
                                    type="button"
                                    onClick={() => {
                                        setInviteInitialRole("member");
                                        setInviteModalOpen(true);
                                    }}
                                    className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-800 dark:text-emerald-300 border border-emerald-500/20 transition flex items-center gap-1.5 cursor-pointer"
                                >
                                    <span>⚡</span>
                                    <span>Mitglied / Mieter</span>
                                </button>
                                <button
                                    type="button"
                                    onClick={() => {
                                        setInviteInitialRole("user_admin");
                                        setInviteModalOpen(true);
                                    }}
                                    className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-800 dark:text-indigo-300 border border-indigo-500/20 transition flex items-center gap-1.5 cursor-pointer"
                                >
                                    <span>👥</span>
                                    <span>Mitglieder- & Mieterbetreuung</span>
                                </button>
                                <button
                                    type="button"
                                    onClick={() => {
                                        setInviteInitialRole("helpdesk");
                                        setInviteModalOpen(true);
                                    }}
                                    className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-sky-500/10 hover:bg-sky-500/20 text-sky-800 dark:text-sky-300 border border-sky-500/20 transition flex items-center gap-1.5 cursor-pointer"
                                >
                                    <span>🛟</span>
                                    <span>Support vor Ort</span>
                                </button>
                                <button
                                    type="button"
                                    onClick={() => {
                                        setInviteInitialRole("auditor");
                                        setInviteModalOpen(true);
                                    }}
                                    className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-amber-500/10 hover:bg-amber-500/20 text-amber-800 dark:text-amber-300 border border-amber-500/20 transition flex items-center gap-1.5 cursor-pointer"
                                >
                                    <span>📊</span>
                                    <span>Kassenprüfer / Beirat</span>
                                </button>
                                <button
                                    type="button"
                                    onClick={() => {
                                        setInviteInitialRole("admin");
                                        setInviteModalOpen(true);
                                    }}
                                    className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-rose-500/10 hover:bg-rose-500/20 text-rose-800 dark:text-rose-300 border border-rose-500/20 transition flex items-center gap-1.5 cursor-pointer"
                                >
                                    <span>🏛️</span>
                                    <span>Gemeinschafts-Leitung</span>
                                </button>
                            </div>
                        </div>

                        {/* INVITES LIST */}
                        <div className="space-y-3 pt-2">
                            <div className="text-xs font-bold text-slate-700 dark:text-slate-300">
                                {t("tenant.active_invites", "Aktive Einladungslinks:")} ({invites.length})
                            </div>

                            {invites.length === 0 ? (
                                <div className="p-6 text-center rounded-2xl bg-slate-50 dark:bg-slate-800/30 border border-dashed border-slate-200 dark:border-slate-800 text-xs text-slate-400">
                                    Aktuell sind keine offenen Einladungslinks vorhanden. Erstelle oben einen neuen Link für Nachbarn oder Mieter.
                                </div>
                            ) : (
                                invites.map((i) => {
                                    const fullInviteUrl = `${window.location.origin}/onboarding?invite=${i.token}`;
                                    const isCopied = copiedToken === i.token;
                                    const isQrOpen = activeQrToken === i.token;

                                    const roleLabels = {
                                        member: "⚡ Mitglied / Mieter",
                                        user_admin: "👥 Mitglieder- & Mieterbetreuung",
                                        helpdesk: "🛟 Support vor Ort",
                                        auditor: "📊 Kassenprüfer / Beirat",
                                        admin: "🏛️ Gemeinschafts-Leitung",
                                    };

                                    return (
                                        <div
                                            key={i.token}
                                            className="border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-800/40 p-4 rounded-2xl flex flex-col gap-3 shadow-xs"
                                        >
                                            <div className="flex flex-wrap items-center justify-between gap-2">
                                                <div className="flex items-center gap-2">
                                                    <span className="text-xs font-bold text-slate-900 dark:text-white">
                                                        {roleLabels[i.role] || i.role_display || i.role}
                                                    </span>
                                                    <span className="text-[10px] bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 px-2 py-0.5 rounded-full font-bold">
                                                        Verwendet: {i.used || 0}
                                                    </span>
                                                </div>

                                                <div className="flex items-center gap-2">
                                                    <button
                                                        type="button"
                                                        onClick={() => {
                                                            navigator.clipboard.writeText(fullInviteUrl);
                                                            setCopiedToken(i.token);
                                                            setTimeout(() => setCopiedToken(null), 2500);
                                                        }}
                                                        className={`px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 cursor-pointer ${
                                                            isCopied
                                                                ? "bg-emerald-600 text-white"
                                                                : "bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 border border-slate-200 dark:border-slate-700 hover:border-indigo-300"
                                                        }`}
                                                    >
                                                        <span>{isCopied ? "✓" : "📋"}</span>
                                                        <span>{isCopied ? "Kopiert!" : "Link kopieren"}</span>
                                                    </button>

                                                    <button
                                                        type="button"
                                                        onClick={() => setActiveQrToken(isQrOpen ? null : i.token)}
                                                        className="px-3 py-1.5 rounded-xl text-xs font-bold bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:border-slate-400 transition flex items-center gap-1.5 cursor-pointer"
                                                    >
                                                        <span>📱</span>
                                                        <span>{isQrOpen ? "QR schließen" : "QR-Code"}</span>
                                                    </button>

                                                    <button
                                                        type="button"
                                                        onClick={() => deactivateInvite(i.token)}
                                                        className="px-2.5 py-1.5 text-xs text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/30 rounded-lg transition cursor-pointer font-semibold"
                                                    >
                                                        Widerrufen
                                                    </button>
                                                </div>
                                            </div>

                                            <div className="text-[11px] font-mono text-slate-500 dark:text-slate-400 break-all bg-white dark:bg-slate-900 p-2 rounded-xl border border-slate-200 dark:border-slate-700 select-all">
                                                {fullInviteUrl}
                                            </div>

                                            {/* INLINE QR CODE PREVIEW */}
                                            {isQrOpen && (
                                                <div className="p-4 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-700 flex flex-col sm:flex-row items-center gap-4 animate-fade-in">
                                                    <div className="p-2 bg-white rounded-xl shadow-xs border border-slate-100 shrink-0">
                                                        <QRCodeSVG value={fullInviteUrl} size={120} level="M" />
                                                    </div>
                                                    <div className="text-center sm:text-left text-xs">
                                                        <h5 className="font-bold text-slate-800 dark:text-white">
                                                            QR-Code für Hausflur-Aushang
                                                        </h5>
                                                        <p className="text-slate-500 dark:text-slate-400 text-[11px] mt-0.5">
                                                            Bewohner können diesen Code direkt scannen, um der Community beizutreten.
                                                        </p>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    );
                                })
                            )}
                        </div>
                    </section>

                    {/* MEMBERS SECTION */}
                    <section className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-xs space-y-4">
                        <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
                            <div>
                                <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                    <span>👥</span>
                                    <span>{t("tenant.members_title", "Aktive Mitglieder & Mieter")} ({members.length})</span>
                                </h2>
                                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                                    Zugewiesene Berechtigungen und Rollen in {tenant?.name}
                                </p>
                            </div>
                        </div>

                        <div className="space-y-2.5">
                            {members.map(m => (
                                <div
                                    key={m.id}
                                    className="border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-800/40 p-3.5 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xs"
                                >
                                    <div className="flex items-center gap-2.5">
                                        <div className="w-8 h-8 rounded-full bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 font-bold text-xs flex items-center justify-center">
                                            {m.email?.slice(0, 2).toUpperCase()}
                                        </div>
                                        <span className="text-xs font-semibold text-slate-900 dark:text-slate-100">{m.email}</span>
                                    </div>
                                    <div className="flex gap-2 items-center self-end sm:self-auto">
                                        <select
                                            value={m.role}
                                            onChange={(e) => updateRole(m.id, e.target.value)}
                                            className="text-xs font-semibold border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 rounded-xl px-3 py-1.5 text-slate-800 dark:text-white cursor-pointer"
                                        >
                                            <option value="member">⚡ Mitglied / Mieter</option>
                                            <option value="user_admin">👥 Mitglieder- & Mieterbetreuung</option>
                                            <option value="helpdesk">🛟 Support vor Ort</option>
                                            <option value="auditor">📊 Kassenprüfer / Beirat</option>
                                            <option value="admin">🏛️ Gemeinschafts-Leitung</option>
                                        </select>
                                        <button
                                            onClick={() => removeMember(m.id)}
                                            className="text-rose-600 hover:text-rose-700 text-xs font-semibold px-2.5 py-1.5 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950/30 transition cursor-pointer"
                                        >
                                            Entfernen
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>

                </div>
            )}

            {/* ======================================================== */}
            {/* 2. VIRTUALE SUMMENZÄHLER TAB */}
            {/* ======================================================== */}
            {activeTab === "virtual_meter" && (
                <VirtualMasterMeterHub tenant={tenant} />
            )}

            {/* ======================================================== */}
            {/* 3. VIRTUAL POWER PLANT (VPP) COCKPIT TAB */}
            {/* ======================================================== */}
            {activeTab === "vpp" && (
                <VppAggregatorCockpit />
            )}

            {/* ======================================================== */}
            {/* 4. ZÄHLER & wMSB HUB TAB */}
            {/* ======================================================== */}
            {activeTab === "msb" && (
                <MsbSmartMeterHub tenant={tenant} />
            )}

            {/* ======================================================== */}
            {/* 5. AUDIT TAB */}
            {/* ======================================================== */}
            {activeTab === "audit" && (
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs">
                    <h2 className="text-sm font-bold text-slate-900 dark:text-white mb-3">
                        {t.audit_log || "Aktivitäts- & Audit-Protokoll"}
                    </h2>

                    <div className="space-y-2 max-h-96 overflow-y-auto">
                        {logs
                            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                            .slice(0, 30)
                            .map((log, idx) => (
                                <div
                                    key={idx}
                                    className={`border p-3 rounded-xl text-sm ${
                                        log.action === "member_removed"
                                            ? "border-red-400 bg-red-50/50 dark:bg-red-950/20"
                                            : "border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/30"
                                    }`}
                                >
                                    <div className="flex justify-between items-center">
                                        <span className="font-semibold text-xs text-slate-800 dark:text-slate-200">
                                            {formatAction(log)}
                                        </span>
                                        <span className="text-slate-400 text-xs">
                                            {formatDate(log.created_at)}
                                        </span>
                                    </div>
                                    <div className="text-xs text-slate-500 mt-1">
                                        {log.user} → {log.target || "-"}
                                    </div>
                                </div>
                            ))}
                    </div>
                </div>
            )}

            {/* TENANT SETUP WIZARD MODAL */}
            <TenantSetupWizardModal
                isOpen={wizardOpen}
                onClose={() => setWizardOpen(false)}
                onComplete={() => loadData()}
                existingTenant={tenant}
            />

            {/* COMMUNITY SHARE MODAL */}
            <CommunityShareModal
                isOpen={shareModalOpen}
                onClose={() => setShareModalOpen(false)}
                kpis={{
                    autarky_pct: cockpit?.autarky_pct || 88,
                    community_shared_kwh: cockpit?.shared_kwh || 160,
                    self_consumption_pct: cockpit?.self_consumption_pct || 94,
                }}
            />

            {/* WHITELABEL & BRANDING MODAL */}
            <WhitelabelSettingsModal
                isOpen={whitelabelModalOpen}
                onClose={() => setWhitelabelModalOpen(false)}
            />

            {/* MARKTKOMMUNIKATION AS4 / EDIFACT MODAL */}
            <MarketCommunicationModal
                isOpen={makoModalOpen}
                onClose={() => setMakoModalOpen(false)}
                tenantId={tenant?.id}
            />

            {/* COMMUNITY INVITE MODAL */}
            <CommunityInviteModal
                isOpen={inviteModalOpen}
                onClose={() => setInviteModalOpen(false)}
                tenant={tenant}
                initialRole={inviteInitialRole}
                onInviteCreated={createInvite}
            />
        </div>
    );
}



