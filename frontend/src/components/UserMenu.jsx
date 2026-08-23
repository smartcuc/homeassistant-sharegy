/*
# src/components/UserMenu.jsx
*/

import { useState, useRef, useEffect } from "react";
import { useUser } from "../hooks/useUser";
import { useTheme } from "../theme/ThemeContext";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../api/client";
import { useQueryClient } from "@tanstack/react-query";

export default function UserMenu() {

    const theme = useTheme();
    const { user } = useUser();
    const { logout } = useAuth();
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const { i18n } = useTranslation();

    const [open, setOpen] = useState(false);
    const dropdownRef = useRef(null);

    const currentLang = (i18n.resolvedLanguage || i18n.language || "de").substring(0, 2);

    // ✅ Outside click schließen
    useEffect(() => {
        function handleClick(e) {
            if (
                dropdownRef.current &&
                !dropdownRef.current.contains(e.target)
            ) {
                setOpen(false);
            }
        }

        document.addEventListener("mousedown", handleClick);
        return () => document.removeEventListener("mousedown", handleClick);
    }, []);

    if (!user) return null;

    // ✅ Name & Initials
    const displayName =
        user?.first_name
            ? `${user.first_name} ${user.last_name || ""}`.trim()
            : user?.email;

    const initials =
        user?.first_name
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

            {/* BUTTON */}
            <button
                onClick={() => setOpen(!open)}
                className="flex items-center gap-3 px-2 py-1 rounded hover:bg-gray-100 transition"
            >
                <div
                    className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium text-white shadow-xs"
                    style={{
                        background: `linear-gradient(
                            to right,
                            ${theme.colors?.primary},
                            ${theme.colors?.secondary}
                        )`,
                    }}
                >
                    {initials}
                </div>

                <span className="text-sm text-gray-700 font-medium">
                    {displayName}
                </span>

                <span className={`text-xs text-gray-400 transition-transform ${open ? "rotate-180" : ""}`}>
                    ▾
                </span>
            </button>

            {/* DROPDOWN */}
            {open && (
                <div className="absolute right-0 mt-2 min-w-[220px] bg-white border border-gray-200 rounded-xl shadow-xl py-2 z-50 animate-in fade-in zoom-in-95 duration-100">

                    <div className="px-4 py-2">
                        <div className="text-xs font-semibold text-gray-900 truncate">
                            {displayName}
                        </div>
                        <div className="text-[11px] text-gray-400 truncate">
                            {user.email}
                        </div>
                    </div>

                    <div className="h-px bg-gray-100 my-1 mx-2" />

                    {/* ✅ User Profile Settings */}
                    <Link
                        to="/app/profile"
                        onClick={() => setOpen(false)}
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center justify-between"
                    >
                        <span>👤 Profil</span>
                        <span className="text-xs text-gray-400">→</span>
                    </Link>

                    <div className="h-px bg-gray-100 my-1 mx-2" />

                    {/* 🌐 Schnell-Sprachumschalter */}
                    <div className="px-4 py-2 bg-slate-50/50">
                        <div className="text-[10px] uppercase tracking-wider font-bold text-gray-400 mb-2">
                            Sprache / Language
                        </div>
                        <div className="grid grid-cols-3 gap-1.5">
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
                                        className={`py-1.5 px-2 text-xs font-semibold rounded-lg border transition ${
                                            isActive
                                                ? "bg-indigo-600 text-white border-indigo-600 shadow-xs"
                                                : "bg-white text-gray-700 border-gray-200 hover:bg-gray-100"
                                        }`}
                                    >
                                        {lang.label}
                                    </button>
                                );
                            })}
                        </div>
                    </div>

                    <div className="h-px bg-gray-100 my-1 mx-2" />

                    {/* ✅ Logout */}
                    <button
                        onClick={handleLogout}
                        className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition font-medium"
                    >
                        🚪 Logout
                    </button>

                </div>
            )}

        </div>
    );
}
