import useModalDismiss from "../../hooks/useModalDismiss";
/*
# frontend/src/components/layout/MobileMenuDrawer.jsx
*/

import { NavLink, Link, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useUser } from "../../hooks/useUser";
import { useUserNavigation } from "../../hooks/useUserNavigation";
import { getNavigationSections } from "../../config/navigationConfig";
import { useSubscription } from "../../hooks/useSubscription";
import { useTheme } from "../../theme/ThemeContext";
import { X, Sun, Moon, LogOut, User, CreditCard, LifeBuoy } from "lucide-react";
import ProBadge from "../common/ProBadge";
import ContextSwitcher from "./ContextSwitcher";
import { useMemo } from "react";

export default function MobileMenuDrawer({ isOpen, onClose }) {
    const { t } = useTranslation();
    useModalDismiss(isOpen, onClose);
    const location = useLocation();
    const { user, isStaffOrAdmin, hasCommunityAdminAccess } = useUser();
    const { isPro } = useSubscription();
    const { isDark, toggleTheme } = useTheme();
    const { activeMode, isMultiMode } = useUserNavigation();

    const sections = useMemo(() => {
        return getNavigationSections({
            activeMode,
            t,
            isPro,
            isStaffOrAdmin,
            hasCommunityAdminAccess,
        });
    }, [activeMode, t, isPro, isStaffOrAdmin, hasCommunityAdminAccess]);

    if (!isOpen) return null;

    const handleLogout = () => {
        onClose();
        localStorage.clear();
        sessionStorage.clear();
        window.location.href = "/login";
    };

    return (
        <div className="fixed inset-0 z-50 flex lg:hidden">
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
                        className="p-2 rounded-xl text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition cursor-pointer"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* User Info & Role Switcher */}
                <div className="p-4 border-b border-slate-200 dark:border-slate-800 bg-indigo-50/40 dark:bg-indigo-950/20 space-y-3">
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
                                        ⭐ {t("common.pro_active", "Pro Aktiv")}
                                    </span>
                                ) : (
                                    <span className="text-[10px] font-medium px-2 py-0.2 rounded-full bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                                        {t("common.free_plan", "Free Plan")}
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>

                    {isMultiMode && (
                        <div className="pt-1">
                            <ContextSwitcher />
                        </div>
                    )}
                </div>

                {/* Dynamic Grouped Navigation List */}
                <div className="flex-1 overflow-y-auto p-3 space-y-4">
                    {sections.map((section, sIdx) => (
                        <div key={sIdx}>
                            {section.title && (
                                <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 px-3 mb-1">
                                    {section.title}
                                </div>
                            )}
                            <div className="space-y-1">
                                {section.items.map((link, idx) => {
                                    if (link.isExternal) {
                                        return (
                                            <a
                                                key={link.path || idx}
                                                href={link.path}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                onClick={onClose}
                                                className="flex items-center justify-between px-3 py-2 rounded-xl text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
                                            >
                                                <div className="flex items-center gap-3">
                                                    <span className="text-base">{link.icon}</span>
                                                    <span>{link.name}</span>
                                                </div>
                                                <span className="text-xs text-slate-400">↗</span>
                                            </a>
                                        );
                                    }

                                    const isCurrentActive = link.path?.includes("?")
                                        ? (location.pathname + location.search) === link.path
                                        : location.pathname === link.path && (!location.search || location.pathname !== "/app/tenant");

                                    return (
                                        <NavLink
                                            key={link.path}
                                            to={link.path}
                                            onClick={onClose}
                                            className={
                                                `flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition ${
                                                    isCurrentActive
                                                        ? "bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 font-bold border border-indigo-100 dark:border-indigo-900/50"
                                                        : "text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                                                }`
                                            }
                                        >
                                            <div className="flex items-center gap-3">
                                                <span className="text-base">{link.icon}</span>
                                                <span>{link.name}</span>
                                                {link.isProGated && !isPro && <ProBadge size="xs" />}
                                            </div>
                                        </NavLink>
                                    );
                                })}
                            </div>
                        </div>
                    ))}
                </div>

                {/* Footer Controls */}
                <div className="p-4 border-t border-slate-200 dark:border-slate-800 space-y-2 bg-slate-50 dark:bg-slate-950/50">
                    <div className="flex items-center justify-between">
                        <span className="text-xs font-medium text-slate-500 dark:text-slate-400">{t("nav.theme", "Design")}</span>
                        <button
                            type="button"
                            onClick={toggleTheme}
                            className="flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-200 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-2xs cursor-pointer"
                        >
                            {isDark ? <Sun className="w-3.5 h-3.5 text-amber-400" /> : <Moon className="w-3.5 h-3.5 text-slate-600" />}
                            <span>{isDark ? t("common.light", "Hell") : t("common.dark", "Dunkel")}</span>
                        </button>
                    </div>

                    <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-200 dark:border-slate-800">
                        <Link
                            to="/app/profile"
                            onClick={onClose}
                            className="flex flex-col items-center justify-center p-2 rounded-xl text-slate-600 dark:text-slate-400 hover:bg-white dark:hover:bg-slate-800 transition"
                        >
                            <User className="w-4 h-4 mb-1" />
                            <span className="text-[10px] font-medium">{t("nav.profile", "Profil")}</span>
                        </Link>
                        <Link
                            to="/app/billing"
                            onClick={onClose}
                            className="flex flex-col items-center justify-center p-2 rounded-xl text-slate-600 dark:text-slate-400 hover:bg-white dark:hover:bg-slate-800 transition"
                        >
                            <CreditCard className="w-4 h-4 mb-1" />
                            <span className="text-[10px] font-medium">{t("nav.billing", "Tarif")}</span>
                        </Link>
                        <Link
                            to="/app/support-hub"
                            onClick={onClose}
                            className="flex flex-col items-center justify-center p-2 rounded-xl text-slate-600 dark:text-slate-400 hover:bg-white dark:hover:bg-slate-800 transition"
                        >
                            <LifeBuoy className="w-4 h-4 mb-1" />
                            <span className="text-[10px] font-medium">{t("nav.help", "Hilfe")}</span>
                        </Link>
                    </div>

                    <button
                        type="button"
                        onClick={handleLogout}
                        className="w-full flex items-center justify-center gap-2 p-2.5 mt-2 rounded-xl text-xs font-bold text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/40 hover:bg-rose-100 transition cursor-pointer"
                    >
                        <LogOut className="w-4 h-4" />
                        <span>{t("common.logout", "Abmelden")}</span>
                    </button>
                </div>
            </div>
        </div>
    );
}
