/*
# src/components/UserMenu.jsx
*/

import { useState, useRef, useEffect } from "react";
import { useUser } from "../hooks/useUser";
import { useTheme } from "../theme/ThemeContext";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useTranslation } from "react-i18next";
import i18n from "../i18n";
import { apiFetch } from "../api/client";
import { useQueryClient } from "@tanstack/react-query";
import { useHomes } from "../hooks/useHomes";
import { useSubscription } from "../hooks/useSubscription";
import { getAvatarConfig } from "../utils/avatars";

export default function UserMenu() {
    const theme = useTheme();
    const { user } = useUser();
    const { logout } = useAuth();
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const { t } = useTranslation();
    const { homes, primaryHome } = useHomes();
    const { isPro, isLandlord, planName } = useSubscription();

    const [open, setOpen] = useState(false);
    const dropdownRef = useRef(null);

    const currentLang = (i18n.resolvedLanguage || i18n.language || "de").substring(0, 2);

    // Outside-Click Handler
    useEffect(() => {
        function handleClick(e) {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
                setOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClick);
        return () => document.removeEventListener("mousedown", handleClick);
    }, []);

    if (!user) return null;

    // Avatar Konfiguration
    const avatarConfig = getAvatarConfig(user?.avatar || user?.profile?.avatar);

    // Name & Initialen
    const displayName = user?.first_name
        ? `${user.first_name} ${user.last_name || ""}`.trim()
        : user?.email;

    const initials = user?.first_name
        ? `${user.first_name[0]}${user.last_name?.[0] || ""}`.toUpperCase()
        : user?.email?.slice(0, 2).toUpperCase();

    async function handleLogout() {
        setOpen(false);
        await logout();
        navigate("/", { replace: true });
    }

    return (
        <div className="relative" ref={dropdownRef}>
            {/* TRIGGER BUTTON */}
            <button
                onClick={() => setOpen(!open)}
                className="flex items-center gap-2.5 px-2.5 py-1.5 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition cursor-pointer group"
                aria-expanded={open}
            >
                {avatarConfig ? (
                    <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center text-sm shadow-xs shrink-0 ring-2 ring-white dark:ring-slate-700 bg-gradient-to-tr ${avatarConfig.bg}`}
                        title={avatarConfig.label}
                    >
                        <span>{avatarConfig.emoji}</span>
                    </div>
                ) : (
                    <div
                        className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white shadow-xs shrink-0 ring-2 ring-white dark:ring-slate-700"
                        style={{
                            background: `linear-gradient(135deg, ${theme.colors?.primary || "#4f46e5"}, ${theme.colors?.secondary || "#06b6d4"})`,
                        }}
                    >
                        {initials}
                    </div>
                )}

                <div className="hidden sm:flex flex-col text-left">
                    <span className="text-xs font-semibold text-gray-800 dark:text-gray-200 truncate max-w-[130px]">
                        {displayName}
                    </span>
                    <span className="text-[10px] text-gray-400 font-medium">
                        {isLandlord ? "🏢 Vermieter" : isPro ? "⚡ Sharegy Pro" : "🌱 Sharegy Free"}
                    </span>
                </div>

                <span className={`text-[10px] text-gray-400 transition-transform duration-200 ${open ? "rotate-180" : ""}`}>
                    ▼
                </span>
            </button>

            {/* DROPDOWN MENU */}
            {open && (
                <div className="absolute right-0 mt-2 w-72 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-2xl shadow-2xl py-2 z-50 animate-in fade-in zoom-in-95 duration-150">
                    {/* USER HEADER */}
                    <div className="px-4 py-3 bg-slate-50/70 dark:bg-slate-800/40 border-b border-gray-100 dark:border-slate-800 flex items-start gap-3">
                        {avatarConfig ? (
                            <div
                                className={`w-10 h-10 rounded-2xl flex items-center justify-center text-xl shadow-xs shrink-0 bg-gradient-to-tr ${avatarConfig.bg} ring-2 ring-white/20`}
                                title={avatarConfig.label}
                            >
                                <span>{avatarConfig.emoji}</span>
                            </div>
                        ) : (
                            <div
                                className="w-10 h-10 rounded-2xl flex items-center justify-center text-sm font-bold text-white shadow-xs shrink-0"
                                style={{
                                    background: `linear-gradient(135deg, ${theme.colors?.primary || "#4f46e5"}, ${theme.colors?.secondary || "#06b6d4"})`,
                                }}
                            >
                                {initials}
                            </div>
                        )}
                        <div className="min-w-0 flex-1">
                            <div className="text-sm font-bold text-gray-900 dark:text-white truncate">
                                {displayName}
                            </div>
                            <div className="text-xs text-gray-400 truncate">
                                {user.email}
                            </div>
                            <div className="mt-1.5 flex items-center gap-1.5">
                                <span
                                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${
                                        isLandlord
                                            ? "bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 border-indigo-300 dark:border-indigo-800"
                                            : isPro
                                                ? "bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800"
                                                : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-700"
                                    }`}
                                >
                                    {isLandlord ? "🏢 Vermieter & Quartiere" : isPro ? "⚡ Sharegy Pro" : "🌱 Sharegy Free"}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* HAUSHALTS-INFO (FALLS VORHANDEN) */}
                    {primaryHome && (
                        <div className="px-4 py-2 border-b border-gray-100 dark:border-slate-800 flex items-center justify-between text-xs text-gray-600 dark:text-gray-400 bg-white dark:bg-slate-900">
                            <span className="flex items-center gap-1.5 truncate">
                                <span>🏠</span>
                                <span className="font-medium text-gray-800 dark:text-gray-200 truncate">{primaryHome.name}</span>
                            </span>
                            {homes.length > 1 && (
                                <span className="text-[10px] bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded font-mono">
                                    {homes.length} Homes
                                </span>
                            )}
                        </div>
                    )}

                    {/* MENÜPUNKTE */}
                    <div className="py-1">
                        <Link
                            to="/app/profile"
                            onClick={() => setOpen(false)}
                            className="px-4 py-2.5 text-xs text-gray-700 dark:text-gray-300 hover:bg-slate-50 dark:hover:bg-slate-800/60 flex items-center justify-between transition group"
                        >
                            <span className="flex items-center gap-2.5 font-medium">
                                <span className="text-base">👤</span>
                                {t("settings.account", "Benutzerkonto & Einstellungen")}
                            </span>
                            <span className="text-gray-400 group-hover:translate-x-0.5 transition-transform">→</span>
                        </Link>


                        <Link
                            to="/app/billing"
                            onClick={() => setOpen(false)}
                            className="px-4 py-2.5 text-xs text-gray-700 dark:text-gray-300 hover:bg-slate-50 dark:hover:bg-slate-800/60 flex items-center justify-between transition group"
                        >
                            <span className="flex items-center gap-2.5 font-medium">
                                <span className="text-base">⚡</span>
                                {t("billing.nav_title", "Tarife & Abonnement")}
                            </span>
                            {!isPro && !isLandlord ? (
                                <span className="text-[10px] font-bold bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400 px-2 py-0.5 rounded-full border border-indigo-200 dark:border-indigo-800">
                                    Upgrade
                                </span>
                            ) : (
                                <span className="text-gray-400 group-hover:translate-x-0.5 transition-transform">→</span>
                            )}
                        </Link>

                        <Link
                            to="/app/help"
                            onClick={() => setOpen(false)}
                            className="px-4 py-2.5 text-xs text-gray-700 dark:text-gray-300 hover:bg-slate-50 dark:hover:bg-slate-800/60 flex items-center justify-between transition group"
                        >
                            <span className="flex items-center gap-2.5 font-medium">
                                <span className="text-base">❓</span>
                                {t("help.title", "Hilfe & Handbuch")}
                            </span>
                            <span className="text-gray-400 group-hover:translate-x-0.5 transition-transform">→</span>
                        </Link>
                    </div>




                    {/* LOGOUT */}
                    <div className="border-t border-gray-100 dark:border-slate-800 pt-1">
                        <button
                            onClick={handleLogout}
                            className="w-full text-left px-4 py-2.5 text-xs text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition font-bold flex items-center gap-2 cursor-pointer"
                        >
                            <span>🚪</span>
                            <span>{t("nav.logout", "Abmelden")}</span>
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
