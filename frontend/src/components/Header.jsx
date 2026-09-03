/*
# src/components/Header.jsx
*/

import { Link } from "react-router-dom";

export default function Header({ theme, user }) {

    const primary = theme?.primary || "#f97316";
    const secondary = theme?.secondary || "#7c3aed";

    const isLoggedIn = Boolean(user && (user.id || user.email || user.is_authenticated));

    return (
        <header className="bg-white shadow-xs border-b border-gray-100">
            <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">

                {/* LOGO -> Link zur Startseite */}
                <Link
                    to="/"
                    title="sharegy Startseite"
                    className="text-2xl font-bold flex items-center gap-1.5 hover:opacity-90 transition cursor-pointer"
                    style={{
                        background: `linear-gradient(to right, ${primary}, ${secondary})`,
                        WebkitBackgroundClip: "text",
                        color: "transparent",
                    }}
                >
                    <span>⚡</span>
                    <span className="font-mono tracking-tight lowercase">sharegy</span>
                </Link>

                {/* ✅ RECHTE SEITE */}
                <div className="flex items-center gap-3">

                    {/* 🔓 NICHT eingeloggt */}
                    {!isLoggedIn && (
                        <>
                            <Link
                                to="/login"
                                className="text-sm font-semibold text-gray-700 hover:text-indigo-600 px-3 py-2 transition"
                            >
                                Login
                            </Link>

                            <Link
                                to="/join"
                                className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold px-4 py-2 rounded-xl shadow-xs transition"
                            >
                                Beitreten
                            </Link>
                        </>
                    )}

                    {/* 🔐 eingeloggter User */}
                    {isLoggedIn && (
                        <Link
                            to="/app/dashboard"
                            className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold px-4 py-2 rounded-xl shadow-xs transition flex items-center gap-1.5"
                        >
                            <span>Zum Dashboard</span>
                            <span>→</span>
                        </Link>
                    )}

                </div>

            </div>
        </header>
    );
}

