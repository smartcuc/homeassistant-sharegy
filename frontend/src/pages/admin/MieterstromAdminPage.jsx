/*
# src/pages/admin/MieterstromAdminPage.jsx
# Dedicated Admin Page for Mieterstrom (§ 42a EnWG)
# Commercial Full-Supply Model (Vollversorgung = Solar + Residual Grid Power)
*/

import { useEffect, useState, useMemo } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { apiFetch } from "../../api/client";
import { useTranslation } from "react-i18next";
import { QRCodeSVG } from "qrcode.react";
import { useUser } from "../../hooks/useUser";
import MsbSmartMeterHub from "../../features/community/components/MsbSmartMeterHub";
import CommunityShareModal from "../../features/community/components/CommunityShareModal";
import CommunityInviteModal from "../../features/community/components/CommunityInviteModal";
import VirtualMasterMeterHub from "../../features/community/components/VirtualMasterMeterHub";
import VppAggregatorCockpit from "../../features/energy/components/VppAggregatorCockpit";
import TenantSetupWizardModal from "../../features/community/components/TenantSetupWizardModal";
import WhitelabelSettingsModal from "../../features/tenant/components/WhitelabelSettingsModal";
import MarketCommunicationModal from "../../features/billing/components/MarketCommunicationModal";

export default function MieterstromAdminPage() {
    const { t } = useTranslation();
    const { isStaffOrAdmin, hasCommunityAdminAccess } = useUser();
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
    const [timeRange, setTimeRange] = useState("today");

    const allowedTabs = ["cockpit", "apartments", "settlement", "meters", "vpp", "msb", "audit"];
    const [activeTab, setActiveTab] = useState(
        allowedTabs.includes(initialTab) ? initialTab : "cockpit"
    );

    const [loading, setLoading] = useState(true);
    const [shareModalOpen, setShareModalOpen] = useState(false);
    const [inviteModalOpen, setInviteModalOpen] = useState(false);
    const [wizardOpen, setWizardOpen] = useState(false);
    const [whitelabelModalOpen, setWhitelabelModalOpen] = useState(false);
    const [makoModalOpen, setMakoModalOpen] = useState(false);
    const [settling, setSettling] = useState(false);
    const [downloadingId, setDownloadingId] = useState(null);
    const [exportingFormat, setExportingFormat] = useState(null);
    const [activeQrToken, setActiveQrToken] = useState(null);
    const [copiedToken, setCopiedToken] = useState(null);

    async function loadData() {
        setLoading(true);
        try {
            const data = await apiFetch("/api/my-tenant/");
            setTenant(data.tenant);
            setMembers(data.members || []);
            setInvites(data.invites || []);

            if (data.tenant) {
                const [cockpitRes, tariffsRes, statementsRes, sharesRes, logRes] = await Promise.all([
                    apiFetch("/api/billing/community/cockpit/").catch(() => null),
                    apiFetch("/api/billing/community/tariffs/").catch(() => null),
                    apiFetch("/api/billing/community/statements/").catch(() => null),
                    apiFetch("/api/billing/community/shares/").catch(() => null),
                    apiFetch("/api/audit-log/").catch(() => []),
                ]);

                setCockpit(cockpitRes);
                setTariffData(tariffsRes);
                setStatementsData(statementsRes);
                setSharesData(sharesRes);
                setLogs(logRes || []);
            }
        } catch (err) {
            console.error("Mieterstrom Admin load failed:", err);
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
        }
    }, [searchParams]);

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
            alert(res.message || "Mieterstrom-Monatsabrechnung erfolgreich generiert.");
            const statementsRes = await apiFetch("/api/billing/community/statements/").catch(() => null);
            setStatementsData(statementsRes);
        } catch (err) {
            alert("Abrechnungsfehler: " + (err.message || "Unbekannter Fehler"));
        } finally {
            setSettling(false);
        }
    }

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
            alert("Fehler beim Erstellen des Mieter-Einladungslinks: " + (err.message || ""));
            throw err;
        }
    }

    async function downloadStatementPdf(statementId, statementNumber) {
        setDownloadingId(statementId);
        try {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            const response = await fetch(`/api/billing/community/statements/${statementId}/pdf/`, {
                headers: {
                    Authorization: token ? `Bearer ${token}` : "",
                    "X-Tenant-ID": tenant?.id || "",
                },
            });
            if (!response.ok) throw new Error("Download fehlgeschlagen.");
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `Mieterstromabrechnung_${statementNumber}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (err) {
            alert("Fehler beim Herunterladen des Mieterstrom-PDFs.");
        } finally {
            setDownloadingId(null);
        }
    }

    async function exportStatements(format = "xlsx") {
        setExportingFormat(format);
        try {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            const response = await fetch(`/api/billing/community/statements/export/?export_format=${format}&tenant_id=${tenant?.id || ""}`, {
                headers: {
                    Authorization: token ? `Bearer ${token}` : "",
                    "X-Tenant-ID": tenant?.id || "",
                },
            });
            if (!response.ok) throw new Error("Export fehlgeschlagen.");
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            const ext = format === "xlsx" ? "xlsx" : format === "csv" ? "csv" : "xml";
            a.download = `Sharegy_Mieterstrom_${tenant?.slug || "objekt"}_${new Date().toISOString().slice(0, 10)}.${ext}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (err) {
            alert(`Fehler beim ${format.toUpperCase()}-Export.`);
        } finally {
            setExportingFormat(null);
        }
    }

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

    async function removeMember(userId) {
        if (!confirm("Möchtest du diesen Mieter wirklich aus dem Mieterstrom-Objekt entfernen?")) return;
        await apiFetch("/api/remove-member/", {
            method: "POST",
            body: JSON.stringify({
                tenant_id: tenant.id,
                user_id: userId,
            }),
        });
        loadData();
    }

    async function deactivateInvite(token) {
        if (!window.confirm("Möchtest du diesen Mieter-Einladungslink widerrufen?")) return;
        try {
            await apiFetch("/api/deactivate-invite/", {
                method: "POST",
                body: JSON.stringify({ token }),
            });
            setInvites((prev) => prev.filter((i) => i.token !== token));
            await loadData();
        } catch (err) {
            alert("Fehler beim Deaktivieren des Links.");
        }
    }

    if (loading) {
        return (
            <div className="p-12 text-center text-slate-400 text-sm animate-pulse">
                Lade Mieterstrom-Verwaltung (§ 42a EnWG)...
            </div>
        );
    }

    if (!tenant) {
        return (
            <div className="p-8 max-w-xl mx-auto text-center space-y-4 my-8 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl">
                <div className="text-4xl">🏢</div>
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">{t("admin_mieterstrom.no_tenant_assigned_title", "Kein Mieterstrom-Objekt zugewiesen")}</h2>
                <p className="text-xs text-slate-500">{t("admin_mieterstrom.no_tenant_assigned_desc", "Du bist aktuell keinem Mieterstrom-Objekt zugeordnet.")}</p>
                <Link to="/app/dashboard" className="inline-block px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-xs font-semibold">
                    {t("tenant_dashboard.back_to_dashboard", "Zum Dashboard")}
                </Link>
            </div>
        );
    }

    const currentStats = cockpit ? (timeRange === "today" ? cockpit.today : cockpit.month) : null;
    const activeTariff = tariffData ? tariffData.active_tariff : null;
    const statements = statementsData ? statementsData.statements : [];

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            {/* HEADER */}
            <div className="space-y-4 pb-4 border-b border-slate-200 dark:border-slate-800">
                <div className="flex items-start gap-3.5">
                    <div className="w-10 h-10 rounded-2xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-xl shrink-0 mt-0.5">
                        🏢
                    </div>
                    <div className="flex-1 min-w-0">
                        <div className="flex flex-wrap items-center gap-2.5">
                            <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white truncate">
                                {tenant.name}
                            </h1>
                            <span className="shrink-0 text-xs font-bold px-3 py-1 rounded-full border flex items-center gap-1.5 bg-sky-50 dark:bg-sky-950/50 text-sky-700 dark:text-sky-300 border-sky-200 dark:border-sky-800">
                                <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse"></span>
                                {t("admin_mieterstrom.title", "🏢 Mieterstrom (§ 42a EnWG)")}
                            </span>
                            <span className="shrink-0 text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800/60">
                                {t("admin_mieterstrom.badge_model", "Vollversorgungsmodell (AGB)")}
                            </span>
                        </div>
                        <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
                            {t("admin_mieterstrom.subtitle", "Vollversorgungs-Modell: Vor-Ort-Solarstrom & Reststrom in einer gemeinsamen Monatsabrechnung mit Mieterstromzuschlag gem. § 21 Abs. 3 EEG")}
                        </p>
                    </div>
                </div>

                {/* ACTION BUTTONS */}
                <div className="flex flex-wrap items-center gap-2.5 pt-1">
                    <button
                        type="button"
                        onClick={() => setWhitelabelModalOpen(true)}
                        className="px-3.5 py-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-900 hover:bg-sky-50 dark:hover:bg-sky-950/40 text-slate-700 dark:text-slate-200 hover:text-sky-600 dark:hover:text-sky-400 border border-slate-200 dark:border-slate-800 hover:border-sky-300 transition-all shadow-xs flex items-center gap-2 cursor-pointer"
                    >
                        <span>🎨</span>
                        <span>{t("tenant.whitelabel_btn", "Whitelabel & Branding")}</span>
                    </button>
                    <button
                        type="button"
                        onClick={() => setMakoModalOpen(true)}
                        className="px-3.5 py-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-900 hover:bg-teal-50 dark:hover:bg-teal-950/40 text-slate-700 dark:text-slate-200 hover:text-teal-600 dark:hover:text-teal-400 border border-slate-200 dark:border-slate-800 hover:border-teal-300 transition-all shadow-xs flex items-center gap-2 cursor-pointer"
                    >
                        <span>📄</span>
                        <span>{t("admin_mieterstrom.btn_mako", "Zählerdaten-Export (MSCONS)")}</span>
                    </button>
                    <button
                        type="button"
                        onClick={() => setWizardOpen(true)}
                        className="px-3.5 py-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-900 hover:bg-sky-50 dark:hover:bg-sky-950/40 text-slate-700 dark:text-slate-200 hover:text-sky-600 dark:hover:text-sky-400 border border-slate-200 dark:border-slate-800 hover:border-sky-300 transition-all shadow-xs flex items-center gap-2 cursor-pointer"
                    >
                        <span>✨</span>
                        <span>{t("admin_mieterstrom.btn_wizard", "Mieterstrom-Assistent (3 Schritte)")}</span>
                    </button>
                    <button
                        type="button"
                        onClick={() => setShareModalOpen(true)}
                        className="px-3.5 py-2 rounded-xl text-xs font-bold bg-sky-50 dark:bg-sky-950/40 hover:bg-sky-100 dark:hover:bg-sky-900/60 text-sky-800 dark:text-sky-300 border border-sky-200 dark:border-sky-800/80 transition-all shadow-xs flex items-center gap-2 cursor-pointer"
                    >
                        <span>📢</span>
                        <span>{t("admin_mieterstrom.btn_share", "Quartier teilen")}</span>
                    </button>
                </div>
            </div>

            {/* TAB SWITCHER */}
            <div className="flex flex-wrap bg-slate-100 dark:bg-slate-800/70 p-1 rounded-xl text-xs font-semibold gap-1">
                <button
                    onClick={() => handleTabChange("cockpit")}
                    className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                        activeTab === "cockpit" ? "bg-white dark:bg-slate-900 text-sky-600 dark:text-sky-400 font-bold shadow-xs" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    }`}
                >
                    {t("admin_mieterstrom.tab_cockpit", "🏢 Mieterstrom-Cockpit")}
                </button>
                <button
                    onClick={() => handleTabChange("apartments")}
                    className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                        activeTab === "apartments" ? "bg-white dark:bg-slate-900 text-sky-600 dark:text-sky-400 font-bold shadow-xs" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    }`}
                >
                    {t("admin_mieterstrom.tab_apartments_count", { count: members.length, defaultValue: `🏠 Wohnungen & Mieter (${members.length})` })}
                </button>
                <button
                    onClick={() => handleTabChange("settlement")}
                    className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                        activeTab === "settlement" ? "bg-white dark:bg-slate-900 text-sky-600 dark:text-sky-400 font-bold shadow-xs" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    }`}
                >
                    {t("admin_mieterstrom.tab_settlement", "💰 Vollversorger-Abrechnung")}
                </button>
                <button
                    onClick={() => handleTabChange("meters")}
                    className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                        activeTab === "meters" ? "bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 font-bold shadow-xs" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    }`}
                >
                    {t("admin_mieterstrom.tab_meters", "⚡ Summen- & Unterzähler")}
                </button>
                <button
                    onClick={() => handleTabChange("vpp")}
                    className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                        activeTab === "vpp" ? "bg-white dark:bg-slate-900 text-amber-600 dark:text-amber-400 font-bold shadow-xs" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    }`}
                >
                    {t("admin_mieterstrom.tab_vpp", "🔌 Quartiers-Flexibilität")}
                </button>
                <button
                    onClick={() => handleTabChange("msb")}
                    className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                        activeTab === "msb" ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs font-bold" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    }`}
                >
                    {t("admin_mieterstrom.tab_msb", "⚡ wMSB & Gateways")}
                </button>
                <button
                    onClick={() => handleTabChange("audit")}
                    className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                        activeTab === "audit" ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
                    }`}
                >
                    {t("admin_mieterstrom.tab_audit", "📜 Audit-Protokoll")}
                </button>
            </div>

            {/* TAB 1: COCKPIT */}
            {activeTab === "cockpit" && cockpit && (
                <div className="space-y-6">
                    <div className="flex items-center justify-between">
                        <h2 className="text-sm font-bold text-slate-800 dark:text-slate-200">
                            {t("admin_mieterstrom.balance_title", "Mieterstrom Bilanzen & Vollversorger-Strommix")}
                        </h2>
                        <div className="flex bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg text-xs font-semibold">
                            <button
                                onClick={() => setTimeRange("today")}
                                className={`px-2.5 py-1 rounded-md transition ${timeRange === "today" ? "bg-white dark:bg-slate-900 text-sky-600 dark:text-sky-400 shadow-xs" : "text-slate-500"}`}
                            >
                                {t("common.today", "Heute")}
                            </button>
                            <button
                                onClick={() => setTimeRange("month")}
                                className={`px-2.5 py-1 rounded-md transition ${timeRange === "month" ? "bg-white dark:bg-slate-900 text-sky-600 dark:text-sky-400 shadow-xs" : "text-slate-500"}`}
                            >
                                {t("common.this_month", "Dieser Monat")}
                            </button>
                        </div>
                    </div>

                    {/* KPI CARDS */}
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
                        <div className="bg-amber-500/5 dark:bg-amber-500/10 border border-amber-500/20 rounded-2xl p-4">
                            <div className="flex items-center justify-between text-amber-700 dark:text-amber-300 text-xs font-bold uppercase">
                                <span>{t("admin_mieterstrom.kpi_solar_title", "Solarerzeugung")}</span>
                                <span>☀️</span>
                            </div>
                            <div className="mt-3 text-2xl font-black text-amber-900 dark:text-amber-100">
                                {Number(currentStats?.produced_kwh ?? 0).toFixed(1)} <span className="text-xs font-normal">kWh</span>
                            </div>
                            <div className="text-[11px] text-amber-700/80 dark:text-amber-300/80 mt-0.5">{t("admin_mieterstrom.kpi_solar_desc", "PV-Dachanlage")}</div>
                        </div>

                        <div className="bg-sky-500/5 dark:bg-sky-500/10 border border-sky-500/20 rounded-2xl p-4">
                            <div className="flex items-center justify-between text-sky-700 dark:text-sky-300 text-xs font-bold uppercase">
                                <span>{t("admin_mieterstrom.kpi_demand_title", "Mieterbedarf")}</span>
                                <span>🏠</span>
                            </div>
                            <div className="mt-3 text-2xl font-black text-sky-900 dark:text-sky-100">
                                {Number(currentStats?.consumed_kwh ?? 0).toFixed(1)} <span className="text-xs font-normal">kWh</span>
                            </div>
                            <div className="text-[11px] text-sky-700/80 dark:text-sky-300/80 mt-0.5">{t("admin_mieterstrom.kpi_demand_desc", "Alle Wohneinheiten")}</div>
                        </div>

                        <div className="bg-emerald-500/5 dark:bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-4">
                            <div className="flex items-center justify-between text-emerald-700 dark:text-emerald-300 text-xs font-bold uppercase">
                                <span>{t("admin_mieterstrom.kpi_onsite_solar_title", "Solar vor Ort")}</span>
                                <span>⚡</span>
                            </div>
                            <div className="mt-3 text-2xl font-black text-emerald-900 dark:text-emerald-100">
                                {Number(currentStats?.shared_kwh ?? 0).toFixed(1)} <span className="text-xs font-normal">kWh</span>
                            </div>
                            <div className="text-[11px] text-emerald-700/80 dark:text-emerald-300/80 mt-0.5 font-semibold">
                                {t("admin_mieterstrom.kpi_onsite_solar_desc", { pct: currentStats?.autarky_pct ?? 0, defaultValue: `Solarquote: ${currentStats?.autarky_pct ?? 0}%` })}
                            </div>
                        </div>

                        <div className="bg-rose-500/5 dark:bg-rose-500/10 border border-rose-500/20 rounded-2xl p-4">
                            <div className="flex items-center justify-between text-rose-700 dark:text-rose-300 text-xs font-bold uppercase">
                                <span>{t("admin_mieterstrom.kpi_grid_title", "Reststromnetz")}</span>
                                <span>🔌</span>
                            </div>
                            <div className="mt-3 text-2xl font-black text-rose-900 dark:text-rose-100">
                                {Number(currentStats?.grid_import_kwh ?? 0).toFixed(1)} <span className="text-xs font-normal">kWh</span>
                            </div>
                            <div className="text-[11px] text-rose-700/80 dark:text-rose-300/80 mt-0.5">{t("admin_mieterstrom.kpi_grid_desc", "Zugekaufter Reststrom")}</div>
                        </div>

                        <div className="bg-indigo-500/5 dark:bg-indigo-500/10 border border-indigo-500/20 rounded-2xl p-4 col-span-2 sm:col-span-1">
                            <div className="flex items-center justify-between text-indigo-700 dark:text-indigo-300 text-xs font-bold uppercase">
                                <span>{t("admin_mieterstrom.kpi_savings_title", "Mieterersparnis")}</span>
                                <span>💰</span>
                            </div>
                            <div className="mt-3 text-2xl font-black text-indigo-900 dark:text-indigo-100">
                                {Number(currentStats?.savings_eur ?? 0).toFixed(2)} <span className="text-xs font-normal">€</span>
                            </div>
                            <div className="text-[11px] text-indigo-700/80 dark:text-indigo-300/80 mt-0.5 font-semibold">
                                {t("admin_mieterstrom.kpi_savings_desc", "vs. Grundversorgung")}
                            </div>
                        </div>
                    </div>

                    {/* 48H KI PROGNOSE */}
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs">
                        <div className="flex items-center justify-between mb-4">
                            <div>
                                <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                                    {t("admin_mieterstrom.forecast_title", "🔮 48-Stunden KI-Erzeugungsprognose & Lastverschiebung")}
                                </h3>
                                <p className="text-xs text-slate-500">
                                    {t("admin_mieterstrom.forecast_desc", "Prädiktive Optimierung für Wärmepumpen und Batteriespeicher im Mieterstrom-Quartier")}
                                </p>
                            </div>
                            <div className="text-right">
                                <div className="text-xs font-bold text-sky-600">
                                    +{cockpit.forecast_48h?.total_predicted_kwh?.toFixed(1) || 0} kWh
                                </div>
                                <div className="text-[10px] text-slate-400">{t("admin_mieterstrom.expected_yield", "erwarteter Ertrag")}</div>
                            </div>
                        </div>

                        {cockpit.forecast_48h?.hours?.length > 0 && (
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
                                        <span className="text-[10px] font-mono">{new Date(h.timestamp).getHours()}:00</span>
                                        <span className="text-xs font-black my-1">{h.power_kw} <span className="text-[9px] font-normal">kW</span></span>
                                        {h.is_peak_window && <span className="text-[9px] font-bold text-emerald-600">{t("admin_mieterstrom.peak_solar_badge", "⚡ Solar")}</span>}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* TAB 2: APARTMENTS & TENANTS */}
            {activeTab === "apartments" && (
                <div className="space-y-6">
                    <section className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-xs space-y-5">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100 dark:border-slate-800">
                            <div>
                                <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                    <span>🏠</span>
                                    <span>{t("admin_mieterstrom.tab_apartments_count", { count: members.length, defaultValue: `Mieter & Wohneinheiten (${members.length})` })}</span>
                                </h2>
                                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                                    {t("admin_mieterstrom.apartments_subtitle", "Verwalte die Wohneinheiten, Zählerzuweisungen und AGB-Vollversorgungsverträge der Mieter.")}
                                </p>
                            </div>
                            <button
                                type="button"
                                onClick={() => setInviteModalOpen(true)}
                                className="px-4 py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-bold shadow-xs transition-all flex items-center gap-2 cursor-pointer"
                            >
                                <span>+</span>
                                <span>{t("admin_mieterstrom.btn_invite_tenant", "Neuen Mieter einladen")}</span>
                            </button>
                        </div>

                        {/* ACTIVE INVITES */}
                        <div className="space-y-3">
                            <div className="text-xs font-bold text-slate-700 dark:text-slate-300">
                                {t("admin_mieterstrom.open_invites_count", { count: invites.length, defaultValue: `Offene Einladungslinks für Mieter: (${invites.length})` })}
                            </div>
                            {invites.length === 0 ? (
                                <div className="p-4 text-center rounded-2xl bg-slate-50 dark:bg-slate-800/30 border border-dashed border-slate-200 dark:border-slate-800 text-xs text-slate-400">
                                    {t("admin_mieterstrom.no_open_invites", "Keine offenen Mieter-Einladungslinks. Erstelle oben einen neuen Link für den Hausfluraushang oder direkten Versand.")}
                                </div>
                            ) : (
                                invites.map((i) => {
                                    const fullInviteUrl = `${window.location.origin}/onboarding?invite=${i.token}`;
                                    const isCopied = copiedToken === i.token;
                                    const isQrOpen = activeQrToken === i.token;
                                    return (
                                        <div key={i.token} className="border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-800/40 p-4 rounded-2xl flex flex-col gap-3">
                                            <div className="flex items-center justify-between">
                                                <span className="text-xs font-bold text-slate-900 dark:text-white">🏢 {t("admin_mieterstrom.invite_label", "Mieter-Einladung")}</span>
                                                <div className="flex items-center gap-2">
                                                    <button
                                                        type="button"
                                                        onClick={() => {
                                                            navigator.clipboard.writeText(fullInviteUrl);
                                                            setCopiedToken(i.token);
                                                            setTimeout(() => setCopiedToken(null), 2500);
                                                        }}
                                                        className="px-3 py-1.5 rounded-xl text-xs font-bold bg-white dark:bg-slate-800 text-sky-600 border border-slate-200 dark:border-slate-700 cursor-pointer"
                                                    >
                                                        {isCopied ? t("common.copied", "✓ Kopiert") : t("common.copy_link", "📋 Link kopieren")}
                                                    </button>
                                                    <button
                                                        type="button"
                                                        onClick={() => setActiveQrToken(isQrOpen ? null : i.token)}
                                                        className="px-3 py-1.5 rounded-xl text-xs font-bold bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 cursor-pointer"
                                                    >
                                                        📱 QR-Code
                                                    </button>
                                                    <button
                                                        type="button"
                                                        onClick={() => deactivateInvite(i.token)}
                                                        className="px-2.5 py-1.5 text-xs text-rose-600 hover:bg-rose-50 rounded-lg cursor-pointer"
                                                    >
                                                        {t("common.revoke", "Widerrufen")}
                                                    </button>
                                                </div>
                                            </div>
                                            {isQrOpen && (
                                                <div className="p-4 bg-white dark:bg-slate-900 rounded-2xl border flex items-center gap-4">
                                                    <QRCodeSVG value={fullInviteUrl} size={110} level="M" />
                                                    <div className="text-xs">
                                                        <h5 className="font-bold">{t("admin_mieterstrom.qr_title", "QR-Code für Hausflur-Aushang")}</h5>
                                                        <p className="text-slate-500 text-[11px]">{t("admin_mieterstrom.qr_desc", "Mieter können den Code scannen, um ihren Mieterstromvertrag digital zu aktivieren.")}</p>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    );
                                })
                            )}
                        </div>

                        {/* MEMBERS LIST */}
                        <div className="space-y-2.5 pt-4 border-t border-slate-100 dark:border-slate-800">
                            <div className="text-xs font-bold text-slate-700 dark:text-slate-300">{t("admin_mieterstrom.registered_tenants", "Registrierte Mieter:")}</div>
                            {members.map((m) => (
                                <div key={m.id} className="border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-800/40 p-3.5 rounded-2xl flex items-center justify-between">
                                    <div className="flex items-center gap-2.5">
                                        <div className="w-8 h-8 rounded-full bg-sky-500/10 text-sky-600 font-bold text-xs flex items-center justify-center">
                                            {m.email?.slice(0, 2).toUpperCase()}
                                        </div>
                                        <div>
                                            <div className="text-xs font-semibold text-slate-900 dark:text-white">{m.email}</div>
                                            <div className="text-[10px] text-slate-400">{t("admin_mieterstrom.contract_active_badge", "Vollversorgungsvertrag (AGB) aktiv")}</div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <select
                                            value={m.role}
                                            onChange={(e) => updateRole(m.id, e.target.value)}
                                            className="text-xs border rounded-xl px-3 py-1.5 bg-white dark:bg-slate-800 cursor-pointer"
                                        >
                                            <option value="member">🏢 {t("roles.member", "Mieter")}</option>
                                            <option value="user_admin">👥 {t("roles.user_admin", "Hausverwaltung")}</option>
                                            <option value="auditor">📊 {t("roles.auditor", "Rechnungsprüfer")}</option>
                                            <option value="admin">🏛️ {t("roles.admin", "Eigentümer / Betreiber")}</option>
                                        </select>
                                        <button onClick={() => removeMember(m.id)} className="text-rose-600 text-xs px-2.5 py-1.5 cursor-pointer">
                                            {t("common.delete", "Entfernen")}
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>
                </div>
            )}

            {/* TAB 3: SETTLEMENT */}
            {activeTab === "settlement" && (
                <div className="space-y-6">
                    {/* TARIFF BANNER */}
                    {activeTariff && (
                        <div className="bg-gradient-to-br from-slate-900 to-sky-950 text-white rounded-2xl p-6 border border-sky-800/50 shadow-md space-y-6">
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                                <div>
                                    <div className="flex items-center gap-2">
                                        <span className="text-xl">🏢</span>
                                        <h2 className="text-lg font-black">{activeTariff.name}</h2>
                                        <span className="bg-emerald-400/20 text-emerald-300 text-[10px] font-bold px-2 py-0.5 rounded-full border border-emerald-400/30">
                                            {t("common.active", "Aktiv")}
                                        </span>
                                    </div>
                                    <p className="text-xs text-sky-200/80 mt-1">
                                        {t("admin_mieterstrom.tariff_banner_sub", "Mieterstrom-Vollversorgung gem. § 42a EnWG (Solarstrom + Reststrom in einer Gesamtrechnung)")}
                                    </p>
                                </div>
                                <button
                                    onClick={triggerSettlement}
                                    disabled={settling}
                                    className="px-4 py-2 bg-sky-500 hover:bg-sky-600 disabled:opacity-50 text-white rounded-xl text-xs font-bold cursor-pointer"
                                >
                                    {settling ? t("admin_mieterstrom.calculating", "Berechne...") : t("admin_mieterstrom.trigger_settlement_btn", "Monatsabrechnung anstoßen")}
                                </button>
                            </div>

                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-sky-800/60">
                                <div>
                                    <div className="text-[11px] text-sky-300 font-semibold uppercase">{t("admin_mieterstrom.solar_working_price", "Solar-Arbeitspreis")}</div>
                                    <div className="text-2xl font-black mt-1 text-white">
                                        {Number(activeTariff?.sharing_price_ct_kwh ?? 0).toFixed(2)} <span className="text-xs font-normal">Ct/kWh</span>
                                    </div>
                                    <div className="text-[10px] text-sky-300/70 mt-0.5">{t("admin_mieterstrom.onsite_pv_electricity", "Vor-Ort PV-Strom")}</div>
                                </div>
                                <div>
                                    <div className="text-[11px] text-sky-300 font-semibold uppercase">{t("admin_mieterstrom.residual_price", "Reststrompreis")}</div>
                                    <div className="text-2xl font-black mt-1 text-amber-300">
                                        ~32,50 <span className="text-xs font-normal">Ct/kWh</span>
                                    </div>
                                    <div className="text-[10px] text-sky-300/70 mt-0.5">{t("admin_mieterstrom.residual_grid_supply", "Netzbezug (Vollversorger)")}</div>
                                </div>
                                <div>
                                    <div className="text-[11px] text-sky-300 font-semibold uppercase">{t("admin_mieterstrom.base_price", "Grundpreis")}</div>
                                    <div className="text-2xl font-black mt-1 text-emerald-300">
                                        8,50 <span className="text-xs font-normal">€/{t("common.month", "Monat")}</span>
                                    </div>
                                    <div className="text-[10px] text-sky-300/70 mt-0.5">{t("admin_mieterstrom.meter_and_billing", "Zähler & Abrechnung")}</div>
                                </div>
                                <div>
                                    <div className="text-[11px] text-sky-300 font-semibold uppercase">{t("admin_mieterstrom.tenant_subsidy", "Mieterstromzuschlag")}</div>
                                    <div className="text-2xl font-black mt-1 text-cyan-300">
                                        § 21 (3) EEG
                                    </div>
                                    <div className="text-[10px] text-sky-300/70 mt-0.5">{t("admin_mieterstrom.subsidy_for_operator", "Förderung für Betreiber")}</div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* STATEMENTS LIST */}
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs">
                        <div className="flex items-center justify-between mb-4">
                            <div>
                                <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                                    {t("admin_mieterstrom.statements_title", "Monatliche Mieterstrom-Abrechnungsnachweise")}
                                </h3>
                                <p className="text-xs text-slate-500">
                                    {t("admin_mieterstrom.statements_desc", "Eichrechtskonforme Vollversorgungsabrechnungen aller Mieter")}
                                </p>
                            </div>
                            <div className="flex items-center gap-1.5">
                                <button onClick={() => exportStatements("xlsx")} className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 text-xs rounded-lg border">
                                    Excel
                                </button>
                                <button onClick={() => exportStatements("csv")} className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 text-xs rounded-lg border">
                                    CSV
                                </button>
                            </div>
                        </div>

                        {statements.length > 0 ? (
                            <div className="space-y-3">
                                {statements.map((stmt) => (
                                    <div key={stmt.id} className="border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40 p-4 rounded-xl flex flex-col sm:flex-row items-center justify-between gap-4">
                                        <div>
                                            <div className="flex items-center gap-2">
                                                <span className="font-mono font-bold text-xs">{stmt.statement_number}</span>
                                                <span className="text-[10px] bg-slate-200 dark:bg-slate-700 px-2 py-0.5 rounded">{stmt.period_start} {t("common.to", "bis")} {stmt.period_end}</span>
                                            </div>
                                            <div className="text-xs text-slate-500 mt-1">{t("roles.member", "Mieter")}: <span className="font-medium text-slate-700 dark:text-slate-300">{stmt.user_email}</span></div>
                                        </div>
                                        <div className="flex items-center gap-4">
                                            <div className="text-right">
                                                <div className="text-xs text-slate-400">{t("admin_mieterstrom.invoice_amount", "Rechnungsbetrag")}</div>
                                                <div className="text-lg font-black text-slate-900 dark:text-white">{Number(stmt.net_balance_eur ?? 0).toFixed(2)} €</div>
                                            </div>
                                            <button
                                                onClick={() => downloadStatementPdf(stmt.id, stmt.statement_number)}
                                                disabled={downloadingId === stmt.id}
                                                className="px-3 py-1.5 bg-white dark:bg-slate-900 text-sky-600 border border-sky-200 dark:border-sky-800 rounded-lg text-xs font-bold cursor-pointer"
                                            >
                                                📄 PDF
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-xs text-slate-400 bg-slate-50 dark:bg-slate-800/30 rounded-xl border border-dashed">
                                {t("admin_mieterstrom.no_statements", "Noch keine Mieterstromabrechnungen generiert. Klicke auf 'Monatsabrechnung anstoßen'.")}
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* TAB 4: METERS & KASKADE */}
            {activeTab === "meters" && <VirtualMasterMeterHub tenant={tenant} />}

            {/* TAB 5: VPP */}
            {activeTab === "vpp" && <VppAggregatorCockpit />}

            {/* TAB 6: MSB & GATEWAYS */}
            {activeTab === "msb" && <MsbSmartMeterHub tenant={tenant} />}

            {/* TAB 7: AUDIT */}
            {activeTab === "audit" && (
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xs">
                    <h2 className="text-sm font-bold text-slate-900 dark:text-white mb-3">{t("admin_mieterstrom.audit_title", "Rechtssicheres Mieterstrom-Auditprotokoll")}</h2>
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                        {logs.slice(0, 30).map((log, idx) => (
                            <div key={idx} className="border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/30 p-3 rounded-xl text-xs flex justify-between">
                                <div>
                                    <span className="font-semibold">{log.action}</span>
                                    <div className="text-slate-500 mt-0.5">{log.user} → {log.target || "-"}</div>
                                </div>
                                <span className="text-slate-400">{new Date(log.created_at).toLocaleString()}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* MODALS */}
            <TenantSetupWizardModal isOpen={wizardOpen} onClose={() => setWizardOpen(false)} onComplete={() => loadData()} existingTenant={tenant} />
            <CommunityShareModal isOpen={shareModalOpen} onClose={() => setShareModalOpen(false)} kpis={{ autarky_pct: cockpit?.autarky_pct || 85, community_shared_kwh: cockpit?.shared_kwh || 120, self_consumption_pct: cockpit?.self_consumption_pct || 90 }} />
            <WhitelabelSettingsModal isOpen={whitelabelModalOpen} onClose={() => setWhitelabelModalOpen(false)} />
            <MarketCommunicationModal isOpen={makoModalOpen} onClose={() => setMakoModalOpen(false)} tenantId={tenant?.id} />
            <CommunityInviteModal isOpen={inviteModalOpen} onClose={() => setInviteModalOpen(false)} tenant={tenant} initialRole="member" onInviteCreated={createInvite} />
        </div>
    );
}
