/*
# src/components/admin/AdminPageHeader.jsx
# Unified SaaS Enterprise Page Header for all Admin, Governance, Fleet & Staff Portals
*/

import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { BookOpen } from "lucide-react";

export default function AdminPageHeader({
    icon,
    iconBg = "bg-indigo-500/10 border-indigo-500/20 text-indigo-600 dark:text-indigo-400",
    title,
    subtitle,
    searchSlot,
    manualLink,
    manualLabel,
    actions,
    children,
    className = "",
}) {
    const { t } = useTranslation();

    return (
        <header className={`space-y-3 pb-5 border-b border-slate-200 dark:border-slate-800 ${className}`}>
            {/* ROW 1: Icon + Title (Left/Full Width) | Optional Search (1/5) | Handbook (Right) */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                {/* Title & Icon */}
                <div className="flex items-center gap-3 min-w-0 flex-1">
                    {icon && (
                        <div
                            className={`w-10 h-10 sm:w-11 sm:h-11 rounded-2xl border flex items-center justify-center text-xl shrink-0 shadow-2xs ${iconBg}`}
                        >
                            {icon}
                        </div>
                    )}
                    <h1 className="text-xl sm:text-2xl font-black tracking-tight text-slate-900 dark:text-white truncate">
                        {title}
                    </h1>
                </div>

                {/* Search (approx 1/5 width) & Handbook (Pinned Right) */}
                <div className="flex items-center gap-3 shrink-0 self-end sm:self-center">
                    {searchSlot && (
                        <div className="w-48 sm:w-64">
                            {searchSlot}
                        </div>
                    )}

                    {manualLink && (
                        <Link
                            to={manualLink}
                            className="px-3.5 py-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 hover:text-indigo-600 dark:hover:text-indigo-400 border border-slate-200 dark:border-slate-800 hover:border-indigo-300 dark:hover:border-indigo-700 transition-all shadow-xs flex items-center gap-1.5 shrink-0 cursor-pointer"
                            title={manualLabel || t("nav.manual", "Handbuch")}
                        >
                            <BookOpen className="w-3.5 h-3.5 text-indigo-500" />
                            <span>{manualLabel || t("nav.manual", "Handbuch")}</span>
                        </Link>
                    )}
                </div>
            </div>

            {/* ROW 2: Subtitle (Full width, calm typography, no squishing) */}
            {subtitle && (
                <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 leading-relaxed max-w-4xl">
                    {subtitle}
                </p>
            )}

            {/* ROW 3: Action Buttons / Tools / Filter Pills (Full width flex-wrap) */}
            {actions && (
                <div className="flex flex-wrap items-center gap-2 pt-1">
                    {actions}
                </div>
            )}

            {/* OPTIONAL BOTTOM EXPANSION (Tabs / Sub-Filters) */}
            {children && <div className="pt-2">{children}</div>}
        </header>
    );
}
