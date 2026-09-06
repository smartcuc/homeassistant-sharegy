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

    async function handleLanguageSelect(langId) {
        await i18n.changeLanguage(langId);
        localStorage.setItem("i18nextLng", langId);

        queryClient.setQueryData(["settings"], (old) => {
            if (!old) return old;
            return { ...old, language: langId };
        });

        try {
            await apiFetch("/api/language/", {
                method: "POST",
                body: JSON.stringify({ language: langId }),
            });
        } catch {
            // Ignore API fallback
        }
    }

    return (
        <div className="relative" ref={dropdownRef}>
            {/* TRIGGER BUTTON */}
            <button
                onClick={() => setOpen(!open)}
                className="flex items-center gap-2.5 px-2.5 py-1.5 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition cursor-pointer group"
                aria-expanded={open}
            >
                <div
                    className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white shadow-xs shrink-0 ring-2 ring-white dark:ring-slate-700"
                    style={{
                        background: `linear-gradient(135deg, ${theme.colors?.primary || "#4f46e5"}, ${theme.colors?.secondary || "#06b6d4"})`,
                    }}
                >
                    {initials}
                </div>

                <div className="hidden sm:flex flex-col text-left">
                    <span className="text-xs font-semibold text-gray-800 dark:text-gray-200 truncate max-w-[130px]">
                        {displayName}
                    </span>
                    <span className="text-[10px] text-gray-400 font-medium">
                        {isLandlord ? "⭐ Vermieter" : isPro ? "⭐ Pro Plan" : "Free Plan"}
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
                        <div
                            className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold text-white shadow-xs shrink-0"
                            style={{
                                background: `linear-gradient(135deg, ${theme.colors?.primary || "#4f46e5"}, ${theme.colors?.secondary || "#06b6d4"})`,
                            }}
                        >
                            {initials}
                        </div>
                        <div className="min-w-0 flex-1">
                            <div className="text-sm font-bold text-gray-900 dark:text-white truncate">
                                {displayName}
                            </div>
                            <div className="text-xs text-gray-400 truncate">
                                {user.email}
                            </div>
                            <div className="mt-1.5 flex items-center gap-1.5">
                                <span
                                    className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold ${
                                        isPro || isLandlord
                                            ? "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300"
                                            : "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300"
                                    }`}
                                >
                                    {isPro || isLandlord ? "⭐ " : "🌱 "}
                                    {planName}
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


                    {/* SPRACH- & THEME-UMSCHALTER */}
                    <div className="px-4 py-2.5 bg-slate-50/80 dark:bg-slate-800/40 border-t border-gray-100 dark:border-slate-800 space-y-2.5">
                        {/* Theme */}
                        <div className="flex items-center justify-between">
                            <span className="text-[10px] uppercase tracking-wider font-bold text-gray-400">
                                {t("settings.appearance", "Design")}
                            </span>
                            <div className="grid grid-cols-3 gap-1">
                                {[
                                    { id: "light", label: "☀️ Hell" },
                                    { id: "dark", label: "🌙 Dunkel" },
                                    { id: "system", label: "💻 Auto" },
                                ].map((thm) => {
                                    const isActive = (theme?.mode || "light") === thm.id;
                                    return (
                                        <button
                                            key={thm.id}
                                            type="button"
                                            onClick={() => theme?.setThemeMode?.(thm.id)}
                                            className={`py-1 px-1.5 text-[10px] font-bold rounded-md border transition cursor-pointer ${
                                                isActive
                                                    ? "bg-indigo-600 text-white border-indigo-600 shadow-2xs"
                                                    : "bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-slate-700 hover:bg-gray-100"
                                            }`}
                                        >
                                            {thm.label}
                                        </button>
                                    );
                                })}
                            </div>
                        </div>

                        {/* Sprache */}
                        <div className="flex items-center justify-between">
                            <span className="text-[10px] uppercase tracking-wider font-bold text-gray-400">
                                {t("settings.language", "Sprache")}
                            </span>
                            <div className="grid grid-cols-3 gap-1">
                                {[
                                    { id: "de", label: "🇩🇪 DE" },
                                    { id: "en", label: "🇬🇧 EN" },
                                    { id: "pl", label: "🇵🇱 PL" },
                                ].map((lang) => {
                                    const isActive = currentLang === lang.id;
                                    return (
                                        <button
                                            key={lang.id}
                                            type="button"
                                            onClick={() => handleLanguageSelect(lang.id)}
                                            className={`py-1 px-1.5 text-[10px] font-bold rounded-md border transition cursor-pointer ${
                                                isActive
                                                    ? "bg-indigo-600 text-white border-indigo-600 shadow-2xs"
                                                    : "bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-slate-700 hover:bg-gray-100"
                                            }`}
                                        >
                                            {lang.label}
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
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
