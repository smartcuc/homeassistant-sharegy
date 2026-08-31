/*
# src/components/common/ProBadge.jsx
*/

import React from "react";

export default function ProBadge({ className = "", size = "sm" }) {
    const sizeClasses =
        size === "xs"
            ? "text-[9px] px-1.5 py-0.2"
            : size === "lg"
            ? "text-xs px-2.5 py-1"
            : "text-[10px] px-2 py-0.5";

    return (
        <span
            className={`inline-flex items-center gap-1 font-extrabold tracking-wide uppercase rounded-full bg-gradient-to-r from-amber-500 to-indigo-600 text-white shadow-2xs ${sizeClasses} ${className}`}
            title="Exklusives Sharegy Pro Feature"
        >
            <span>⭐</span>
            <span>PRO</span>
        </span>
    );
}
