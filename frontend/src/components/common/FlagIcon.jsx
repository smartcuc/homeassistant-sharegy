/*
# src/components/common/FlagIcon.jsx
*/

export default function FlagIcon({ code, className = "w-5 h-5", rounded = "rounded-full" }) {
    const c = (code || "de").toLowerCase();

    // 🇩🇪 Germany
    if (c === "de") {
        return (
            <svg viewBox="0 0 512 512" className={`${className} ${rounded} shadow-2xs overflow-hidden shrink-0 inline-block border border-black/10`}>
                <rect width="512" height="170.7" fill="#262626" />
                <rect y="170.7" width="512" height="170.7" fill="#d00" />
                <rect y="341.3" width="512" height="170.7" fill="#ffce00" />
            </svg>
        );
    }

    // 🇬🇧 United Kingdom (English)
    if (c === "en" || c === "gb") {
        return (
            <svg viewBox="0 0 512 512" className={`${className} ${rounded} shadow-2xs overflow-hidden shrink-0 inline-block border border-black/10`}>
                <rect width="512" height="512" fill="#012169" />
                <path d="M0 0l512 512M512 0L0 512" stroke="#fff" strokeWidth="65" />
                <path d="M0 0l512 512M512 0L0 512" stroke="#c8102e" strokeWidth="40" />
                <path d="M256 0v512M0 256h512" stroke="#fff" strokeWidth="105" />
                <path d="M256 0v512M0 256h512" stroke="#c8102e" strokeWidth="65" />
            </svg>
        );
    }

    // 🇵🇱 Poland
    if (c === "pl") {
        return (
            <svg viewBox="0 0 512 512" className={`${className} ${rounded} shadow-2xs overflow-hidden shrink-0 inline-block border border-black/10`}>
                <rect width="512" height="256" fill="#fff" />
                <rect y="256" width="512" height="256" fill="#dc143c" />
            </svg>
        );
    }

    // 🇹🇷 Turkey
    if (c === "tr") {
        return (
            <svg viewBox="0 0 512 512" className={`${className} ${rounded} shadow-2xs overflow-hidden shrink-0 inline-block border border-black/10`}>
                <rect width="512" height="512" fill="#e30a17" />
                <circle cx="210" cy="256" r="130" fill="#fff" />
                <circle cx="245" cy="256" r="104" fill="#e30a17" />
                <polygon points="320,215 330,245 360,245 336,263 345,295 320,275 295,295 304,263 280,245 310,245" fill="#fff" />
            </svg>
        );
    }

    // 🇷🇺 Russia
    if (c === "ru") {
        return (
            <svg viewBox="0 0 512 512" className={`${className} ${rounded} shadow-2xs overflow-hidden shrink-0 inline-block border border-black/10`}>
                <rect width="512" height="170.7" fill="#fff" />
                <rect y="170.7" width="512" height="170.7" fill="#0039a6" />
                <rect y="341.3" width="512" height="170.7" fill="#d52b1e" />
            </svg>
        );
    }

    // 🇷🇴 Romania
    if (c === "ro") {
        return (
            <svg viewBox="0 0 512 512" className={`${className} ${rounded} shadow-2xs overflow-hidden shrink-0 inline-block border border-black/10`}>
                <rect width="170.7" height="512" fill="#002b7f" />
                <rect x="170.7" width="170.7" height="512" fill="#fcd116" />
                <rect x="341.3" width="170.7" height="512" fill="#ce1126" />
            </svg>
        );
    }

    return null;
}
