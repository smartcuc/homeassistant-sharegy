/*
# Sidebar.jsx
*/

import { NavLink, useParams } from "react-router-dom";

export default function Sidebar({ theme }) {
    const { tenantSlug } = useParams();

    const primary = theme?.primary || "#f97316";
    const secondary = theme?.secondary || "#7c3aed";

    return (
        <aside className="w-64 border-r shadow-sm flex flex-col"
            style={{
                background: `linear-gradient(to bottom, ${primary}, ${secondary})`,
                color: "white"
            }}
        >

            {/* Logo */}
            <div className="p-6 text-2xl font-bold tracking-tight lowercase">
                sharegy
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 space-y-2">

                <NavLink
                    to="/dashboard"
                    className="block px-3 py-2 rounded-lg hover:bg-white/20"
                >
                    Dashboard
                </NavLink>

                <NavLink
                    to={`/tenant/${tenantSlug}/home`}
                    className="block px-3 py-2 rounded-lg hover:bg-white/20"
                >
                    Community
                </NavLink>

                <NavLink
                    to="/dashboard"
                    className="block px-3 py-2 rounded-lg hover:bg-white/20"
                >
                    Energiefluss
                </NavLink>

            </nav>
        </aside>
    );
}

