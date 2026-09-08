import { NavLink, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useUser } from "../../hooks/useUser";
import { useSubscription } from "../../hooks/useSubscription";
import { useTheme } from "../../theme/ThemeContext";
import { X, Sun, Moon, LogOut, ShieldCheck, User, CreditCard, LifeBuoy, Sparkles } from "lucide-react";
import ProBadge from "../common/ProBadge";

export default function MobileMenuDrawer({ isOpen, onClose }) {
    const { t } = useTranslation();
    const { user, isStaffOrAdmin, hasCommunityAdminAccess } = useUser();
    const { isPro } = useSubscription();
    const { isDark, toggleTheme } = useTheme();

    if (!isOpen) return null;

    const navLinks = [
        { name: t("nav.dashboard", "Dashboard"), path: "/app/dashboard", icon: "🏠" },
        { name: t("energy.energy_balance", "Energiebilanz"), path: "/app/energy", icon: "⚡" },
        { name: t("nav.energy_control", "Energiesteuerung"), path: "/app/control", icon: "🎛️", isProGated: true },
        { name: t("nav.mobility", "E-Mobilität"), path: "/app/mobility", icon: "🚗", isProGated: true },
        { name: t("nav.heating_climate", "Wärme & Klima"), path: "/app/heating", icon: "🌡️", isProGated: true },
        { name: t("nav.alerts", "Alarmzentrale"), path: "/app/alerts", icon: "🚨", isProGated: true },
        { name: t("nav.solar_forecast", "Solar-Prognose"), path: "/app/solarforecast", icon: "☀️" },
        { name: t("nav.metrics", "Messwert-Explorer"), path: "/app/metrics", icon: "📈" },
        { name: t("nav.all_devices", "Geräteübersicht"), path: "/app/devices", icon: "📟" },
        { name: t("nav.producers", "Erzeuger & Speicher"), path: "/app/producers", icon: "🔋" },
        ...(hasCommunityAdminAccess
            ? [{ name: t("nav.tenant_management", "Community & Mieter"), path: "/app/tenant", icon: "👥" }]
            : []),
        { name: t("nav.tariff", "Dynamischer Tarif"), path: "/app/tariff", icon: "💶" },
        { name: t("nav.system_status", "Systemstatus & Live-Sync"), path: "/app/status", icon: "📶" },
        { name: t("nav.help_center", "Hilfe & Knowledge Base"), path: "/app/help", icon: "📚" },
        ...(isStaffOrAdmin
            ? [{ name: t("nav.admin_dashboard", "Admin Dashboard"), path: "/app/admin/dashboard", icon: "🛡️" }]
            : []),
    ];

    const handleLogout = () => {
        onClose();
        localStorage.clear();
        sessionStorage.clear();
        window.location.href = "/login";
    };

    return (
        <div className="fixed inset-0 z-50 flex md:hidden">
            {/* Backdrop */}
            <div 
                className="fixed inset-0 bg-slate-950/70 backdrop-blur-xs animate-fade-in"
                onClick={onClose}
            />

            {/* Slide-over Panel */}
            <div className="relative w-4/5 max-w-sm bg-white dark:bg-slate-900 h-full shadow-2xl flex flex-col z-10 border-r border-slate-200 dark:border-slate-800 animate-slide-in-left">
                {/* Header */}
                <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50 dark:bg-slate-950/50">
                    <Link
                        to="/"
                        onClick={onClose}
                        className="font-bold text-base bg-gradient-to-r from-indigo-500 to-purple-600 text-transparent bg-clip-text flex items-center gap-1.5"
                    >
                        <span>⚡</span>
                        <span className="font-mono tracking-tight lowercase">sharegy</span>
                    </Link>

                    <button
                        type="button"
                        onClick={onClose}
                        className="p-2 rounded-xl text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* User Info & Pro Status */}
                <div className="p-4 border-b border-slate-200 dark:border-slate-800 bg-indigo-50/40 dark:bg-indigo-950/20">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-2xl bg-indigo-600 text-white font-bold flex items-center justify-center text-sm shadow-sm">
                            {user?.first_name ? user.first_name[0].toUpperCase() : user?.email ? user.email[0].toUpperCase() : "U"}
                        </div>
                        <div className="min-w-0 flex-1">
                            <div className="text-sm font-bold text-slate-900 dark:text-white truncate">
                                {user?.first_name ? `${user.first_name} ${user.last_name || ""}` : user?.email}
                            </div>
                            <div className="flex items-center gap-1.5 mt-0.5">
                                {isPro ? (
                                    <span className="text-[10px] font-bold px-2 py-0.2 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
                                        ⭐ Pro Aktiv
                                    </span>
                                ) : (
                                    <span className="text-[10px] font-medium px-2 py-0.2 rounded-full bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                                        Free Plan
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Navigation Items List */}
                <div className="flex-1 overflow-y-auto p-3 space-y-1">
                    {navLinks.map((link) => (
                        <NavLink
                            key={link.path}
                            to={link.path}
                            onClick={onClose}
                            className={({ isActive }) =>
                                `flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition ${
                                    isActive
                                        ? "bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 font-bold border border-indigo-200 dark:border-indigo-900/50 shadow-2xs"
                                        : "text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                                }`
                            }
                        >
                            <div className="flex items-center gap-3">
                                <span className="text-base">{link.icon}</span>
                                <span>{link.name}</span>
                            </div>
                            {link.isProGated && !isPro && <ProBadge size="xs" />}
                        </NavLink>
                    ))}
                </div>

                {/* Footer Controls (Theme, Profile, Logout) */}
                <div className="p-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/60 space-y-2">
                    <div className="flex items-center justify-between px-2 py-1">
                        <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">Design</span>
                        <button
                            type="button"
                            onClick={toggleTheme}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-bold text-slate-700 dark:text-slate-200 shadow-2xs cursor-pointer"
                        >
                            {isDark ? <Moon className="w-3.5 h-3.5 text-indigo-400" /> : <Sun className="w-3.5 h-3.5 text-amber-500" />}
                            <span>{isDark ? "Dark" : "Light"}</span>
                        </button>
                    </div>

                    <div className="grid grid-cols-2 gap-2 pt-1">
                        <Link
                            to="/app/profile"
                            onClick={onClose}
                            className="flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs font-bold text-slate-700 dark:text-slate-200 shadow-2xs"
                        >
                            <User className="w-3.5 h-3.5" />
                            <span>Profil</span>
                        </Link>

                        <button
                            type="button"
                            onClick={handleLogout}
                            className="flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/50 text-xs font-bold text-rose-700 dark:text-rose-300 shadow-2xs cursor-pointer"
                        >
                            <LogOut className="w-3.5 h-3.5" />
                            <span>Abmelden</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
