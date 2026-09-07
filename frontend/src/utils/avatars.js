/*
# src/utils/avatars.js
# Curated list of energy, smart home and tech avatars
*/

export const AVATAR_PRESETS = [
    { id: "solar_pro", emoji: "☀️", label: "Solar Pro", bg: "from-amber-500 to-orange-500", shadow: "rgba(245, 158, 11, 0.4)" },
    { id: "battery_master", emoji: "🔋", label: "Power Storage", bg: "from-emerald-500 to-teal-600", shadow: "rgba(16, 185, 129, 0.4)" },
    { id: "ev_driver", emoji: "🚗", label: "EV Driver", bg: "from-blue-500 to-indigo-600", shadow: "rgba(59, 130, 246, 0.4)" },
    { id: "eco_pioneer", emoji: "🌿", label: "Eco Pioneer", bg: "from-green-500 to-emerald-700", shadow: "rgba(34, 197, 94, 0.4)" },
    { id: "smart_home", emoji: "🏡", label: "Smart Home", bg: "from-indigo-500 to-purple-600", shadow: "rgba(99, 102, 241, 0.4)" },
    { id: "energy_fox", emoji: "🦊", label: "Energy Fox", bg: "from-orange-500 to-rose-500", shadow: "rgba(249, 115, 22, 0.4)" },
    { id: "autopilot", emoji: "🤖", label: "AI Autopilot", bg: "from-cyan-500 to-blue-600", shadow: "rgba(6, 182, 212, 0.4)" },
    { id: "volt_chief", emoji: "⚡", label: "Volt Chief", bg: "from-amber-400 to-yellow-600", shadow: "rgba(251, 191, 36, 0.4)" },
    { id: "heat_pump", emoji: "♨️", label: "Warmwasser & Heat", bg: "from-rose-500 to-orange-500", shadow: "rgba(244, 63, 94, 0.4)" },
    { id: "efficiency_pro", emoji: "💡", label: "Efficiency Pro", bg: "from-amber-400 to-yellow-500", shadow: "rgba(251, 191, 36, 0.4)" },
    { id: "hydro_pulse", emoji: "🌊", label: "Hydro Pulse", bg: "from-teal-400 to-cyan-600", shadow: "rgba(20, 184, 166, 0.4)" },
    { id: "grid_guardian", emoji: "🛡️", label: "Grid Guardian", bg: "from-purple-600 to-pink-600", shadow: "rgba(147, 51, 234, 0.4)" },
];

export function getAvatarConfig(avatarId) {
    if (!avatarId) return null;
    const found = AVATAR_PRESETS.find((a) => a.id === avatarId);
    if (found) return found;
    // If it's a raw emoji string (e.g. ☀️ or 🚀)
    if (avatarId.length <= 4) {
        return {
            id: "custom_emoji",
            emoji: avatarId,
            label: "Benutzer-Avatar",
            bg: "from-indigo-500 to-cyan-500",
            shadow: "rgba(99, 102, 241, 0.4)",
        };
    }
    return null;
}
