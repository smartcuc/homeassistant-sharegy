/*
# src/features/energy/components/SystemReadinessCard.jsx
*/

import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function SystemReadinessCard({ onOpenAddDevice, className = "", inModal = false }) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const [collapsed, setCollapsed] = useState(!inModal);
    const [isSubmittingTz, setIsSubmittingTz] = useState(false);

    const detectedTimezone = useMemo(
        () => Intl.DateTimeFormat().resolvedOptions().timeZone,
        []
    );

    const handleAcceptTimezone = async () => {
        setIsSubmittingTz(true);
        try {
            await apiFetch("/api/timezone/", {
                method: "POST",
                body: JSON.stringify({ timezone: detectedTimezone }),
            });
            await queryClient.invalidateQueries({ queryKey: ["system-setup-status"] });
            await queryClient.invalidateQueries({ queryKey: ["settings"] });
        } catch (e) {
            console.error("Failed to set timezone:", e);
        } finally {
            setIsSubmittingTz(false);
        }
    };

    const { data, isLoading } = useQuery({
        queryKey: ["system-setup-status"],
        queryFn: () => apiFetch("/api/energy/setup-status/"),
        refetchInterval: 60000,
    });

    if (isLoading) {
        return (
            <div className={`p-3 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl shadow-2xs animate-pulse flex items-center justify-between ${className}`}>
                <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-1/4"></div>
                <div className="h-4 bg-slate-100 dark:bg-slate-800 rounded w-1/3"></div>
            </div>
        );
    }

    if (!data) return null;

    const score = Number(data.score ?? 0);
    const pillars = data.pillars || {};
    const recommendations = data.recommendations || [];
    const submeters = data.submeters || { count: 0, rooms_count: 0, floors_count: 0 };

    const scoreColor =
        score >= 90
            ? "text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800"
            : score >= 60
            ? "text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800"
            : "text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800";

    const scoreBarColor =
        score >= 90
            ? "bg-emerald-500"
            : score >= 60
            ? "bg-amber-500"
            : "bg-rose-500";

    const pillarConfigs = [
        {
            key: "generation",
            icon: "☀️",
            label: t("system_health.pillar_pv", "PV"),
            pillar: pillars.generation || pillars.pv || pillars.producer,
            missingHint: "Kein Wechselrichter / BKW",
        },
        {
            key: "grid",
            icon: "⚡",
            label: t("system_health.pillar_grid", "Netz"),
            pillar: pillars.grid || pillars.meter,
            missingHint: "Kein Haupt-/Zweirichtungszähler",
        },
        {
            key: "battery",
            icon: "🔋",
            label: t("system_health.pillar_battery", "Speicher"),
            pillar: pillars.battery || pillars.storage,
            missingHint: "Kein Heimspeicher",
            optional: true,
        },
        {
            key: "load",
            icon: "🏠",
            label: t("system_health.pillar_load", "Last"),
            pillar: pillars.load || pillars.consumption,
            missingHint: "Last wird berechnet",
        },
    ];

    return (
        <div className={`bg-white dark:bg-slate-900 ${inModal ? "" : "border border-slate-200/90 dark:border-slate-800 rounded-2xl shadow-2xs"} overflow-hidden transition-all ${className}`}>
            {/* COMPACT SUMMARY STRIP (Nur auf Dashboard / wenn nicht im Modal) */}
            {!inModal && (
                <div className="px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 text-xs">
                    {/* Left: Omi-Check Badge & 4 Mini Status Chips */}
                    <div className="flex flex-wrap items-center gap-2.5 min-w-0">
                        <div className="flex items-center gap-1.5 shrink-0 font-bold text-slate-900 dark:text-white">
                            <span className="text-base">🩺</span>
                            <span>{t("system_health.title_short", "Omi-Check")}:</span>
                            <span className={`px-2 py-0.5 rounded-full text-[11px] font-extrabold border ${scoreColor}`}>
                                {score}% {score >= 90 ? "Optimal" : score >= 60 ? "Bereit" : "Unvollständig"}
                            </span>
                        </div>

                        {/* 4 Mini Pillar Badges */}
                        <div className="flex items-center gap-1.5 overflow-x-auto py-0.5">
                            {pillarConfigs.map((item) => {
                                const isOk = Boolean(
                                    item.pillar?.installed ||
                                    (item.pillar?.configured && item.pillar?.status === "ok") ||
                                    item.pillar?.status === "ok"
                                );
                                return (
                                    <span
                                        key={item.key}
                                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-[11px] font-semibold border ${
                                            isOk
                                                ? "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800"
                                                : item.optional
                                                ? "bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-700"
                                                : "bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800"
                                        }`}
                                        title={`${item.label}: ${isOk ? "Aktiv" : item.optional ? "Optional (nicht angebunden)" : item.missingHint}`}
                                    >
                                        <span>{item.icon}</span>
                                        <span className="hidden sm:inline">{item.label}</span>
                                        <span>{isOk ? "✓" : item.optional ? "—" : "!"}</span>
                                    </span>
                                );
                            })}
                        </div>
                    </div>

                    {/* Right: Actions */}
                    <div className="flex items-center gap-2 shrink-0">
                        {score < 100 && onOpenAddDevice && (
                            <button
                                type="button"
                                onClick={onOpenAddDevice}
                                className="px-2.5 py-1 bg-indigo-600 hover:bg-indigo-700 text-white text-[11px] font-bold rounded-lg shadow-2xs transition flex items-center gap-1 cursor-pointer"
                            >
                                <span>➕</span>
                                <span className="hidden sm:inline">Anbinden</span>
                            </button>
                        )}
                        <button
                            type="button"
                            onClick={() => setCollapsed(!collapsed)}
                            className="px-2.5 py-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg text-slate-600 dark:text-slate-300 transition text-[11px] font-semibold border border-slate-200 dark:border-slate-700 cursor-pointer flex items-center gap-1"
                            title={collapsed ? "Details anzeigen" : "Einklappen"}
                        >
                            <span>{collapsed ? "▼ Details" : "▲ Schließen"}</span>
                        </button>
                    </div>
                </div>
            )}

            {/* PROGRESS BAR (Nur wenn ausgeklappt oder Score < 100) */}
            {!inModal && !collapsed && (
                <div className="w-full h-1 bg-slate-100 dark:bg-slate-800 overflow-hidden">
                    <div
                        className={`h-full transition-all duration-700 ${scoreBarColor}`}
                        style={{ width: `${Math.max(5, score)}%` }}
                    />
                </div>
            )}

            {/* EXPANDABLE / MODAL BODY */}
            {(!collapsed || inModal) && (
                <div className="p-5 space-y-5 animate-fade-in border-t border-slate-100 dark:border-slate-800">
                    {/* 4 PILLARS STATUS CARDS */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                        {pillarConfigs.map((item) => {
                            const isOk = Boolean(
                                item.pillar?.installed ||
                                (item.pillar?.configured && item.pillar?.status === "ok") ||
                                item.pillar?.status === "ok"
                            );
                            const deviceName = item.pillar?.device_name;
                            const statusText = item.pillar?.status_text;
                            const isCalculated = item.pillar?.method === "calculated";

                            return (
                                <div
                                    key={item.key}
                                    className={`p-3.5 rounded-2xl border transition-all flex flex-col justify-between space-y-2 ${
                                        isOk
                                            ? "bg-emerald-50/40 dark:bg-emerald-950/20 border-emerald-200/80 dark:border-emerald-800/60 text-emerald-950 dark:text-emerald-200"
                                            : item.optional
                                            ? "bg-slate-50 dark:bg-slate-800/60 border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200"
                                            : "bg-amber-50/50 dark:bg-amber-950/20 border-amber-200/80 dark:border-amber-800/60 text-amber-950 dark:text-amber-200"
                                    }`}
                                >
                                    <div className="flex items-center justify-between">
                                        <span className="text-xl">{item.icon}</span>
                                        <span
                                            className={`text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full ${
                                                isOk
                                                    ? "bg-emerald-500 text-white"
                                                    : item.optional
                                                    ? "bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300"
                                                    : "bg-amber-500 text-white"
                                            }`}
                                        >
                                            {isOk ? "Aktiv ✓" : item.optional ? "Optional" : "Fehlt"}
                                        </span>
                                    </div>

                                    <div>
                                        <div className="font-bold text-xs text-slate-900 dark:text-white">{item.label}</div>
                                        <div className="text-[11px] text-gray-500 dark:text-slate-400 truncate mt-0.5">
                                            {deviceName
                                                ? deviceName
                                                : isCalculated
                                                ? "Berechnet (PV + Netz)"
                                                : statusText
                                                ? statusText
                                                : item.missingHint}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {/* SUBMETERING METRIC BAR */}
                    <div className="p-3 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-2xl flex flex-wrap items-center justify-between gap-3 text-xs text-gray-600 dark:text-slate-300">
                        <div className="flex items-center gap-2">
                            <span className="text-base">🔌</span>
                            <span>
                                <strong>{submeters.count || 0} Einzelgeräte</strong> ({submeters.rooms_count || 0} Räume, {submeters.floors_count || 0} Etagen) im Sub-Metering angebunden.
                            </span>
                        </div>
                        <a
                            href="/app/devices"
                            className="text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 transition flex items-center gap-1"
                        >
                            <span>Geräte & Räume verwalten</span>
                            <span>→</span>
                        </a>
                    </div>

                    {/* RECOMMENDATIONS (IF ANY) */}
                    {recommendations.length > 0 && (
                        <div className="space-y-2 pt-1 border-t border-slate-100 dark:border-slate-800">
                            <div className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-slate-400">
                                💡 Handlungsempfehlungen:
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                                {recommendations.map((rec, idx) => (
                                    <div
                                        key={idx}
                                        className="p-3 rounded-xl bg-amber-50/70 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800/60 text-xs flex flex-col justify-between gap-2 text-amber-950 dark:text-amber-200"
                                    >
                                        <div className="flex items-start gap-2.5">
                                            <span className="text-base leading-none">⚠️</span>
                                            <div className="space-y-0.5">
                                                <div className="font-bold">{rec.title}</div>
                                                <div className="text-amber-900/80 dark:text-amber-300/80 leading-relaxed text-[11px]">{rec.text}</div>
                                            </div>
                                        </div>

                                        {/* Action Buttons for specific recommendations */}
                                        <div className="flex items-center justify-end gap-2 pt-1">
                                            {rec.action === "set_timezone" && (
                                                <button
                                                    type="button"
                                                    disabled={isSubmittingTz}
                                                    onClick={handleAcceptTimezone}
                                                    className="px-2.5 py-1 bg-amber-600 hover:bg-amber-700 text-white font-bold text-[11px] rounded-lg shadow-2xs transition cursor-pointer flex items-center gap-1"
                                                >
                                                    <span>🌐</span>
                                                    <span>{detectedTimezone} übernehmen</span>
                                                </button>
                                            )}
                                            {rec.action === "configure_devices" && (
                                                <button
                                                    type="button"
                                                    onClick={() => navigate("/app/devices")}
                                                    className="px-2.5 py-1 bg-amber-600 hover:bg-amber-700 text-white font-bold text-[11px] rounded-lg shadow-2xs transition cursor-pointer flex items-center gap-1"
                                                >
                                                    <span>📟</span>
                                                    <span>Geräte zuweisen →</span>
                                                </button>
                                            )}
                                            {["connect_inverter_or_meter", "connect_grid_meter", "connect_pv", "add_submeter"].includes(rec.action) && onOpenAddDevice && (
                                                <button
                                                    type="button"
                                                    onClick={onOpenAddDevice}
                                                    className="px-2.5 py-1 bg-amber-600 hover:bg-amber-700 text-white font-bold text-[11px] rounded-lg shadow-2xs transition cursor-pointer flex items-center gap-1"
                                                >
                                                    <span>➕</span>
                                                    <span>Gerät anbinden</span>
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
