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
    badge,
    badgeColor = "indigo", // 'indigo' | 'sky' | 'purple' | 'emerald' | 'amber' | 'slate'
    manualLink,
    manualLabel,
    actions,
    children,
    className = "",
}) {
    const { t } = useTranslation();

    // Badge styling map
    const badgeColorClasses = {
        indigo: "bg-indigo-50 dark:bg-indigo-950/50 text-indigo-700 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800",
        sky: "bg-sky-50 dark:bg-sky-950/50 text-sky-700 dark:text-sky-300 border-sky-200 dark:border-sky-800",
        purple: "bg-purple-50 dark:bg-purple-950/50 text-purple-700 dark:text-purple-300 border-purple-200 dark:border-purple-800",
        emerald: "bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800",
        amber: "bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800/60",
        slate: "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700",
    };

    const selectedBadgeClass = badgeColorClasses[badgeColor] || badgeColorClasses.indigo;

    return (
        <header className={`space-y-4 pb-5 border-b border-slate-200 dark:border-slate-800 ${className}`}>
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                {/* LEFT: Icon, Title, Badge & Subtitle */}
                <div className="flex items-start gap-3.5 min-w-0">
                    {icon && (
                        <div
                            className={`w-11 h-11 rounded-2xl border flex items-center justify-center text-xl shrink-0 mt-0.5 shadow-2xs ${iconBg}`}
                        >
                            {icon}
                        </div>
                    )}
                    <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2.5">
                            <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white truncate">
                                {title}
                            </h1>
                            {badge && (
                                <span
                                    className={`shrink-0 text-xs font-bold px-2.5 py-0.5 rounded-full border flex items-center gap-1.5 ${selectedBadgeClass}`}
                                >
                                    <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse"></span>
                                    {badge}
                                </span>
                            )}
                        </div>
                        {subtitle && (
                            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1 max-w-3xl leading-relaxed">
                                {subtitle}
                            </p>
                        )}
                    </div>
                </div>

                {/* RIGHT: Actions + Universal Manual Button */}
                <div className="flex flex-wrap items-center gap-2.5 shrink-0 self-start lg:self-center">
                    {/* Optional Custom Action Buttons */}
                    {actions}

                    {/* Standardized Handbook Link Button */}
                    {manualLink && (
                        <Link
                            to={manualLink}
                            className="px-3.5 py-2 rounded-xl text-xs font-bold bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 hover:text-indigo-600 dark:hover:text-indigo-400 border border-slate-200 dark:border-slate-800 hover:border-indigo-300 dark:hover:border-indigo-700 transition-all shadow-xs flex items-center gap-1.5 shrink-0"
                            title={manualLabel || t("nav.manual", "Handbuch")}
                        >
                            <BookOpen className="w-3.5 h-3.5 text-indigo-500" />
                            <span>{manualLabel || t("nav.manual", "Handbuch")}</span>
                        </Link>
                    )}
                </div>
            </div>

            {/* OPTIONAL BOTTOM EXPANSION (e.g. Tabs, Filters, Search) */}
            {children && <div className="pt-1">{children}</div>}
        </header>
    );
}
