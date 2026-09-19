/*
# src/components/ui/Skeleton.jsx
# Wiederverwendbare Skeleton-Ladekomponenten für flüssige Zero-Layout-Shift UX
*/

import React from "react";

/**
 * Basis-Skeleton-Element mit sanftem Pulsieren
 */
export function Skeleton({ className = "", rounded = "rounded-xl", ...props }) {
  return (
    <div
      className={`bg-slate-200/80 dark:bg-slate-800 animate-pulse ${rounded} ${className}`}
      {...props}
    />
  );
}

/**
 * Standardisierte Skeleton-Karte (z.B. für KPIs, Metrik-Boxen)
 */
export function SkeletonCard({ className = "", lines = 2, hasIcon = true }) {
  return (
    <div className={`p-5 sm:p-6 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-3xl space-y-4 shadow-sm ${className}`}>
      <div className="flex items-center justify-between">
        <Skeleton className="h-4 w-1/3" />
        {hasIcon && <Skeleton className="h-8 w-8 rounded-xl shrink-0" />}
      </div>
      <Skeleton className="h-8 w-1/2 rounded-lg" />
      {lines > 0 && (
        <div className="space-y-2 pt-1">
          {Array.from({ length: lines }).map((_, i) => (
            <Skeleton key={i} className={`h-3 ${i === lines - 1 ? "w-2/3" : "w-full"}`} />
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * Standardisiertes 4er / 3er Grid aus Skeleton-Karten
 */
export function SkeletonKpiGrid({ count = 4, className = "" }) {
  return (
    <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-${count} gap-4 sm:gap-6 ${className}`}>
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}

/**
 * Diagramm-Platzhalter mit angedeuteten Balken/Linien
 */
export function SkeletonChart({ className = "", height = "h-72" }) {
  return (
    <div className={`p-6 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-3xl space-y-5 ${className}`}>
      <div className="flex items-center justify-between">
        <div className="space-y-1.5 w-1/3">
          <Skeleton className="h-5 w-full" />
          <Skeleton className="h-3 w-2/3" />
        </div>
        <Skeleton className="h-8 w-24 rounded-xl" />
      </div>

      <div className={`${height} flex items-end justify-between gap-2 pt-6 px-2`}>
        {Array.from({ length: 16 }).map((_, i) => {
          const heights = ["h-1/3", "h-2/3", "h-1/2", "h-3/4", "h-full", "h-2/5", "h-4/5", "h-3/5"];
          const barHeight = heights[i % heights.length];
          return (
            <div key={i} className="flex-1 flex flex-col items-center gap-2 h-full justify-end">
              <Skeleton className={`w-full ${barHeight} rounded-t-lg opacity-70`} />
              <Skeleton className="h-2 w-3/4" />
            </div>
          );
        })}
      </div>
    </div>
  );
}

/**
 * Tabellen-Platzhalter mit Header und konfigurierbaren Zeilen
 */
export function SkeletonTable({ rows = 5, columns = 4, className = "" }) {
  return (
    <div className={`p-5 sm:p-6 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-3xl space-y-4 ${className}`}>
      <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
        <Skeleton className="h-5 w-1/4" />
        <Skeleton className="h-8 w-32 rounded-xl" />
      </div>

      <div className="space-y-3">
        {Array.from({ length: rows }).map((_, r) => (
          <div
            key={r}
            className="flex items-center justify-between gap-4 p-3.5 rounded-2xl bg-slate-50/70 dark:bg-slate-850/60"
          >
            <div className="flex items-center gap-3 w-1/3">
              <Skeleton className="h-8 w-8 rounded-xl shrink-0" />
              <div className="space-y-1 w-full">
                <Skeleton className="h-3.5 w-3/4" />
                <Skeleton className="h-2.5 w-1/2" />
              </div>
            </div>
            <Skeleton className="h-4 w-20 hidden sm:block" />
            <Skeleton className="h-4 w-24 hidden md:block" />
            <Skeleton className="h-7 w-20 rounded-lg shrink-0" />
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Vollständiger Seiten-Ladeplatzhalter für Suspense & Route Transitions
 */
export function SkeletonPageLoader({ className = "" }) {
  return (
    <div className={`p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6 sm:space-y-8 animate-fade-in ${className}`}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200 dark:border-slate-800">
        <div className="space-y-2 w-full max-w-md">
          <Skeleton className="h-4 w-28 rounded-full" />
          <Skeleton className="h-8 w-3/4" />
          <Skeleton className="h-4 w-full" />
        </div>
        <div className="flex items-center gap-3">
          <Skeleton className="h-10 w-28 rounded-2xl" />
          <Skeleton className="h-10 w-32 rounded-2xl" />
        </div>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {Array.from({ length: 4 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>

      {/* Main Chart / Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <SkeletonChart height="h-80" />
        </div>
        <div>
          <SkeletonCard className="h-full" lines={5} />
        </div>
      </div>

      {/* Table Area */}
      <SkeletonTable rows={4} />
    </div>
  );
}

export default Skeleton;
