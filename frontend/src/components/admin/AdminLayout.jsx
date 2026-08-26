/*
# components/admin/AdminLayout.jsx
*/

import { Link, NavLink } from "react-router-dom";

export default function AdminLayout({ children }) {
    return (
        <div className="flex h-screen bg-slate-50">
            {/* Sidebar */}
            <aside className="w-64 bg-white border-r border-gray-200 p-4 flex flex-col justify-between shrink-0">
                <div className="space-y-6">
                    {/* Brand */}
                    <div className="flex items-center gap-2.5 px-2">
                        <span className="text-2xl">🛡️</span>
                        <div>
                            <div className="font-black text-base bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                                Sharegy Admin
                            </div>
                            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">
                                Staff Portal
                            </span>
                        </div>
                    </div>

                    {/* Navigation */}
                    <nav className="space-y-1">
                        <NavLink
                            to="/admin/dashboard"
                            className={({ isActive }) =>
                                `flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold transition ${
                                    isActive ? "bg-indigo-50 text-indigo-700 shadow-2xs" : "text-gray-600 hover:bg-gray-50"
                                }`
                            }
                        >
                            <span className="text-sm">📊</span> Onboarding Funnel
                        </NavLink>

                        <NavLink
                            to="/admin/tracking"
                            className={({ isActive }) =>
                                `flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold transition ${
                                    isActive ? "bg-indigo-50 text-indigo-700 shadow-2xs" : "text-gray-600 hover:bg-gray-50"
                                }`
                            }
                        >
                            <span className="text-sm">📈</span> Event & Telemetrie
                        </NavLink>

                        <NavLink
                            to="/admin/tenants"
                            className={({ isActive }) =>
                                `flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold transition ${
                                    isActive ? "bg-indigo-50 text-indigo-700 shadow-2xs" : "text-gray-600 hover:bg-gray-50"
                                }`
                            }
                        >
                            <span className="text-sm">👥</span> Mandanten & Mieter
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
                        <span>←</span> Zurück zum Hauptportal
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
