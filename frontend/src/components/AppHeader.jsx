/*
# src/components/AppHeader.jsx
*/

import { Link, useLocation } from "react-router-dom";
import { useTheme } from "../theme/ThemeContext";
import { useUser } from "../hooks/useUser";

import UserMenu from "./UserMenu";

export default function AppHeader() {

    const theme = useTheme();
    const { user } = useUser();
    const location = useLocation();

    const navItem = (to, label) => {
        const isActive = location.pathname === to;

        return (
            <Link
                to={to}
                className={`text-sm transition-colors duration-150 ${isActive
                    ? "text-black font-medium"
                    : "text-gray-500 hover:text-black"
                    }`}
            >
                {label}
            </Link>
        );
    };

    return (
        <header className="bg-white border-b">
            <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">

                {/* ✅ LOGO */}
                <Link to="/" className="text-2xl font-bold group">
                    <span
                        className="transition-opacity duration-200 group-hover:opacity-80"
                        style={{
                            background: `linear-gradient(
                                to right,
                                ${theme.primary || "#6366f1"},
                                ${theme.secondary || "#9333ea"}
                            )`,
                            WebkitBackgroundClip: "text",
                            color: "transparent",
                        }}
                    >
                        sharegy
                    </span>
                </Link>

                {/* ✅ NAV (nur wenn eingeloggt) */}
                {user && (
                    <div className="flex gap-6">
                        {navItem("/", "Dashboard")}
                        {navItem("/settings", "Settings")}
                    </div>
                )}

                {/* ✅ RIGHT */}
                <div className="flex items-center gap-4">

                    {!user && (
                        <>
                            <Link
                                to="/login"
                                className="text-gray-500 hover:text-black transition"
                            >
                                Login
                            </Link>

                            <Link
                                to="/join"
                                className="px-4 py-2 rounded text-white transition active:scale-95"
                                style={{
                                    background: theme.primary || "#6366f1",
                                }}
                            >
                                Beitreten
                            </Link>
                        </>
                    )}

                    {user && (
                        <UserMenu />
                    )}

                </div>
            </div>
        </header>
    );
}

