/*
# src/features/energy/components/SystemReadinessCard.jsx
*/

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function SystemReadinessCard({ onOpenAddDevice, className = "" }) {
    const { t } = useTranslation();
    const [collapsed, setCollapsed] = useState(false);

    const { data, isLoading } = useQuery({
        queryKey: ["system-setup-status"],
        queryFn: () => apiFetch("/api/energy/setup-status/"),
        refetchInterval: 60000,
    });

    if (isLoading) {
        return (
            <div className={`p-5 bg-white border border-slate-200/80 rounded-3xl shadow-xs animate-pulse ${className}`}>
                <div className="h-5 bg-slate-200 rounded w-1/3 mb-3"></div>
                <div className="h-16 bg-slate-100 rounded-2xl"></div>
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
            ? "text-emerald-600 bg-emerald-50 border-emerald-200"
            : score >= 60
            ? "text-amber-600 bg-amber-50 border-amber-200"
            : "text-rose-600 bg-rose-50 border-rose-200";

    const scoreBarColor =
        score >= 90
            ? "bg-emerald-500"
            : score >= 60
            ? "bg-amber-500"
            : "bg-rose-500";

    const pillarConfigs = [
        {
            key: "pv",
            icon: "☀️",
            label: t("system_health.pillar_pv", "Solar-Erzeugung"),
            pillar: pillars.pv,
            missingHint: "Keine Solaranlage / BKW eingerichtet",
        },
        {
            key: "grid",
            icon: "⚡",
            label: t("system_health.pillar_grid", "Netzanschluss / Zähler"),
            pillar: pillars.grid,
            missingHint: "Kein Smart Meter / Netzbezug erfasst",
        },
        {
            key: "battery",
            icon: "🔋",
            label: t("system_health.pillar_battery", "Batteriespeicher"),
            pillar: pillars.battery,
            missingHint: "Kein Heimspeicher angebunden",
            optional: true,
        },
        {
            key: "load",
            icon: "🏠",
            label: t("system_health.pillar_load", "Hausverbrauch"),
            pillar: pillars.load,
            missingHint: "Hauslast wird berechnet / geschätzt",
        },
    ];

    return (
        <div className={`bg-white border border-slate-200/90 rounded-3xl shadow-xs overflow-hidden transition-all ${className}`}>
            {/* CARD HEADER */}
            <div className="p-5 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-xl shadow-2xs shrink-0">
                        🩺
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h2 className="text-base font-bold text-gray-900">
                                {t("system_health.title", "System-Check & Einrichtungsgrad (Omi-Check)")}
                            </h2>
                            <span className={`px-2.5 py-0.5 rounded-full text-xs font-black border ${scoreColor}`}>
                                {score}% {score >= 90 ? "Optimal" : score >= 60 ? "Bereit" : "Unvollständig"}
                            </span>
                        </div>
                        <p className="text-xs text-gray-500 mt-0.5">
                            {data.description || t("system_health.subtitle", "Automatische Prüfung der 4 Kernsäulen für ein fehlerfreies Energiemanagement.")}
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-auto">
                    {score < 100 && onOpenAddDevice && (
                        <button
                            type="button"
                            onClick={onOpenAddDevice}
                            className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl shadow-xs transition flex items-center gap-1.5 cursor-pointer"
                        >
                            <span>➕</span>
                            <span>Gerät hinzufügen</span>
                        </button>
                    )}
                    <button
                        type="button"
                        onClick={() => setCollapsed(!collapsed)}
                        className="p-1.5 hover:bg-slate-100 rounded-xl text-gray-400 hover:text-gray-700 transition text-xs font-semibold cursor-pointer"
                        title={collapsed ? "Aufklappen" : "Einklappen"}
                    >
                        {collapsed ? "▼ Details" : "▲ Schließen"}
                    </button>
                </div>
            </div>

            {/* PROGRESS BAR */}
            <div className="w-full h-1.5 bg-slate-100 overflow-hidden">
                <div
                    className={`h-full transition-all duration-700 ${scoreBarColor}`}
                    style={{ width: `${Math.max(5, score)}%` }}
                />
            </div>

            {/* EXPANDABLE BODY */}
            {!collapsed && (
                <div className="p-5 space-y-5 animate-fade-in">
                    {/* 4 PILLARS STATUS CARDS */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                        {pillarConfigs.map((item) => {
                            const isOk = item.pillar?.configured && item.pillar?.status === "ok";
                            const deviceName = item.pillar?.device_name;
                            const isCalculated = item.pillar?.method === "calculated";

                            return (
                                <div
                                    key={item.key}
                                    className={`p-3.5 rounded-2xl border transition-all flex flex-col justify-between space-y-2 ${
                                        isOk
                                            ? "bg-emerald-50/40 border-emerald-200/80 text-emerald-950"
                                            : item.optional
                                            ? "bg-slate-50 border-slate-200 text-slate-800"
                                            : "bg-amber-50/50 border-amber-200/80 text-amber-950"
                                    }`}
                                >
                                    <div className="flex items-center justify-between">
                                        <span className="text-xl">{item.icon}</span>
                                        <span
                                            className={`text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full ${
                                                isOk
                                                    ? "bg-emerald-500 text-white"
                                                    : item.optional
                                                    ? "bg-slate-200 text-slate-700"
                                                    : "bg-amber-500 text-white"
                                            }`}
                                        >
                                            {isOk ? "Aktiv ✓" : item.optional ? "Optional" : "Fehlt"}
                                        </span>
                                    </div>

                                    <div>
                                        <div className="font-bold text-xs">{item.label}</div>
                                        <div className="text-[11px] text-gray-500 truncate mt-0.5">
                                            {deviceName
                                                ? deviceName
                                                : isCalculated
                                                ? "Berechnet (PV - Netz)"
                                                : item.missingHint}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {/* SUBMETERING METRIC BAR */}
                    <div className="p-3 bg-slate-50 border border-slate-200 rounded-2xl flex flex-wrap items-center justify-between gap-3 text-xs text-gray-600">
                        <div className="flex items-center gap-2">
                            <span className="text-base">🔌</span>
                            <span>
                                <strong>{submeters.count || 0} Einzelgeräte</strong> ({submeters.rooms_count || 0} Räume, {submeters.floors_count || 0} Etagen) im Sub-Metering angebunden.
                            </span>
                        </div>
                        <a
                            href="/app/devices"
                            className="text-xs font-bold text-indigo-600 hover:text-indigo-800 transition flex items-center gap-1"
                        >
                            <span>Geräte & Räume verwalten</span>
                            <span>→</span>
                        </a>
                    </div>

                    {/* RECOMMENDATIONS (IF ANY) */}
                    {recommendations.length > 0 && (
                        <div className="space-y-2 pt-1 border-t border-slate-100">
                            <div className="text-xs font-bold uppercase tracking-wider text-gray-500">
                                💡 Handlungsempfehlungen:
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                                {recommendations.map((rec, idx) => (
                                    <div
                                        key={idx}
                                        className="p-3 rounded-xl bg-amber-50/70 border border-amber-200 text-xs flex items-start gap-2.5 text-amber-950"
                                    >
                                        <span className="text-base leading-none">⚠️</span>
                                        <div className="space-y-0.5">
                                            <div className="font-bold">{rec.title}</div>
                                            <div className="text-amber-900/80 leading-relaxed text-[11px]">{rec.text}</div>
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
