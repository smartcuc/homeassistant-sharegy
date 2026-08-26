/*
# components/admin/AdminLayout.jsx
*/

import { NavLink, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

export default function AdminLayout({ children }) {
    const { t } = useTranslation();

    return (
        <div className="flex h-screen bg-slate-50/50">
            {/* Admin Sidebar */}
            <aside className="w-64 bg-white border-r border-gray-200 p-5 flex flex-col justify-between hidden md:flex">
                <div className="space-y-6">
                    <div className="flex items-center gap-2.5 px-2">
                        <span className="text-2xl">🛡️</span>
                        <div>
                            <div className="font-black text-sm text-gray-900 tracking-tight">Staff Portal</div>
                            <div className="text-[10px] text-gray-400 font-medium">Administration & Control</div>
                        </div>
                    </div>

                    <nav className="space-y-1">
                        <NavLink
                            to="/app/admin/dashboard"
                            end
                            className={({ isActive }) =>
                                `flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold transition ${isActive ? "bg-indigo-50 text-indigo-700 shadow-2xs" : "text-gray-600 hover:bg-gray-50"
                                }`
                            }
                        >
                            <span className="text-sm">📊</span> {t("admin.title", "Dashboard")}
                        </NavLink>

                        <NavLink
                            to="/app/admin/tracking"
                            className={({ isActive }) =>
                                `flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold transition ${isActive ? "bg-indigo-50 text-indigo-700 shadow-2xs" : "text-gray-600 hover:bg-gray-50"
                                }`
                            }
                        >
                            <span className="text-sm">📈</span> {t("admin.event_tracking", "Event-Tracking")}
                        </NavLink>

                        <NavLink
                            to="/app/tenant"
                            className={({ isActive }) =>
                                `flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold transition ${isActive ? "bg-indigo-50 text-indigo-700 shadow-2xs" : "text-gray-600 hover:bg-gray-50"
                                }`
                            }
                        >
                            <span className="text-sm">👥</span> {t("admin.tenants", "Mandanten & Mieter")}
                        </NavLink>

                        <a
                            href="/admin/"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold text-gray-600 hover:bg-gray-50 transition"
                        >
                            <div className="flex items-center gap-2.5">
                                <span className="text-sm">⚙️</span> Django Admin
                            </div>
                            <span className="text-[10px] text-gray-400">↗</span>
                        </a>
                    </nav>
                </div>

                <div className="pt-4 border-t border-gray-100">
                    <Link
                        to="/app/dashboard"
                        className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 transition shadow-2xs"
                    >
                        <span>←</span> {t("admin.back_to_portal", "Zurück zum Hauptportal")}
                    </Link>
                </div>
            </aside>

            {/* Content Area */}
            <main className="flex-1 flex flex-col overflow-hidden">
                <div className="flex-1 overflow-auto">
                    {children}
                </div>
            </main>
        </div>
    );
}
