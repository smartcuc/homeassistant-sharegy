import { NavLink, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useEffect } from "react";
import FlagIcon from "../common/FlagIcon";

export default function AdminLayout({ children }) {
    const { t, i18n } = useTranslation();

    const currentLang = (i18n.resolvedLanguage || i18n.language || "de").substring(0, 2);

    useEffect(() => {
        if (currentLang !== "de" && currentLang !== "en") {
            i18n.changeLanguage("de");
        }
    }, [currentLang, i18n]);

    const handleLanguageToggle = (lang) => {
        i18n.changeLanguage(lang);
        localStorage.setItem("i18nextLng", lang);
    };

    return (
        <div className="flex h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
            {/* Admin Sidebar */}
            <aside className="w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 p-5 flex flex-col justify-between hidden md:flex shrink-0">
                <div className="space-y-6">
                    <div className="flex items-center justify-between px-2">
                        <div className="flex items-center gap-2.5">
                            <span className="text-2xl">🛡️</span>
                            <div>
                                <div className="font-black text-sm text-slate-900 dark:text-white tracking-tight">Staff Portal</div>
                                <div className="text-[10px] text-slate-400 dark:text-slate-500 font-medium">Administration & Control</div>
                            </div>
                        </div>

                        {/* DE / EN Flag Toggle */}
                        <div className="flex items-center bg-slate-100 dark:bg-slate-800 rounded-xl p-1 gap-1">
                            <button
                                type="button"
                                onClick={() => handleLanguageToggle("de")}
                                className={`p-1 rounded-lg transition cursor-pointer flex items-center justify-center ${
                                    currentLang === "de"
                                        ? "bg-white dark:bg-slate-700 shadow-xs ring-1 ring-indigo-500/20"
                                        : "opacity-60 hover:opacity-100"
                                }`}
                                title="Deutsch"
                            >
                                <FlagIcon code="de" className="w-4 h-4" />
                            </button>
                            <button
                                type="button"
                                onClick={() => handleLanguageToggle("en")}
                                className={`p-1 rounded-lg transition cursor-pointer flex items-center justify-center ${
                                    currentLang === "en"
                                        ? "bg-white dark:bg-slate-700 shadow-xs ring-1 ring-indigo-500/20"
                                        : "opacity-60 hover:opacity-100"
                                }`}
                                title="English"
                            >
                                <FlagIcon code="en" className="w-4 h-4" />
                            </button>
                        </div>
                    </div>

                    <nav className="space-y-1">
                        <NavLink
                            to="/app/admin/communities"
                            className={({ isActive }) =>
                                `flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold transition ${
                                    isActive
                                        ? "bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 font-bold"
                                        : "text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60"
                                }`
                            }
                        >
                            <span className="text-sm">🏘️</span> {t("nav.communities_hub", "Quartiere & Gemeinschaften")}
                        </NavLink>

                        <NavLink
                            to="/app/admin/mieterstrom"
                            className={({ isActive }) =>
                                `flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold transition ${
                                    isActive
                                        ? "bg-sky-50 dark:bg-sky-950/60 text-sky-700 dark:text-sky-300 font-bold"
                                        : "text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60"
                                }`
                            }
                        >
                            <span className="text-sm">🏢</span> {t("nav.tenant_management_mieterstrom", "Mieterstrom (§ 42a)")}
                        </NavLink>

                        <NavLink
                            to="/app/admin/ggv"
                            className={({ isActive }) =>
                                `flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold transition ${
                                    isActive
                                        ? "bg-purple-50 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300 font-bold"
                                        : "text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60"
                                }`
                            }
                        >
                            <span className="text-sm">⚖️</span> {t("nav.tenant_management_ggv", "GGV-Gebäude (§ 42b)")}
                        </NavLink>

                        <NavLink
                            to="/app/admin/sharing"
                            className={({ isActive }) =>
                                `flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold transition ${
                                    isActive
                                        ? "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 font-bold"
                                        : "text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60"
                                }`
                            }
                        >
                            <span className="text-sm">👥</span> {t("nav.tenant_management_sharing", "Energy Sharing (eG)")}
                        </NavLink>

                        <NavLink
                            to="/app/admin/vpp"
                            className={({ isActive }) =>
                                `flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold transition ${
                                    isActive
                                        ? "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 font-bold"
                                        : "text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60"
                                }`
                            }
                        >
                            <span className="text-sm">⚡</span> {t("nav.admin_vpp", "VPP & Flex-Zentrale")}
                        </NavLink>

                        <NavLink
                            to="/app/partner"
                            className={({ isActive }) =>
                                `flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold transition ${
                                    isActive
                                        ? "bg-sky-50 dark:bg-sky-950/60 text-sky-700 dark:text-sky-300 font-bold"
                                        : "text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60"
                                }`
                            }
                        >
                            <span className="text-sm">🔧</span> {t("nav.partner_fleet", "Partner-Flotten")}
                        </NavLink>

                        <NavLink
                            to="/app/admin/dashboard"
                            end
                            className={({ isActive }) =>
                                `flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold transition ${
                                    isActive
                                        ? "bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 font-bold"
                                        : "text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60"
                                }`
                            }
                        >
                            <span className="text-sm">📊</span> {t("admin.title", "Conversion & Funnel")}
                        </NavLink>

                        <NavLink
                            to="/app/admin/tracking"
                            className={({ isActive }) =>
                                `flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold transition ${
                                    isActive
                                        ? "bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 font-bold"
                                        : "text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60"
                                }`
                            }
                        >
                            <span className="text-sm">📈</span> {t("admin.event_tracking", "Event-Tracking")}
                        </NavLink>

                        <NavLink
                            to="/app/admin/audit-logs"
                            className={({ isActive }) =>
                                `flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold transition ${
                                    isActive
                                        ? "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 font-bold"
                                        : "text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60"
                                }`
                            }
                        >
                            <span className="text-sm">🔒</span> {t("admin.audit_trail", "Audit Trail & Revision")}
                        </NavLink>

                        <NavLink
                            to="/app/help"
                            className={({ isActive }) =>
                                `flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold transition ${
                                    isActive
                                        ? "bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 font-bold"
                                        : "text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60"
                                }`
                            }
                        >
                            <span className="text-sm">📖</span> {t("nav.manual", "Handbuch")}
                        </NavLink>

                        <a
                            href="/admin/"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60 transition"
                        >
                            <div className="flex items-center gap-2.5">
                                <span className="text-sm">⚙️</span> Django Admin
                            </div>
                            <span className="text-[10px] text-slate-400">↗</span>
                        </a>
                    </nav>
                </div>

                <div className="pt-4 border-t border-slate-200 dark:border-slate-800">
                    <Link
                        to="/app/dashboard"
                        className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/50 hover:bg-indigo-100 dark:hover:bg-indigo-900/70 transition shadow-2xs"
                    >
                        <span>←</span> {t("admin.back_to_portal", "Zurück zum Hauptportal")}
                    </Link>
                </div>
            </aside>

            {/* Content Area */}
            <main className="flex-1 flex flex-col overflow-hidden bg-slate-50 dark:bg-slate-950">
                <div className="flex-1 overflow-auto">
                    {children}
                </div>
            </main>
        </div>
    );
}
