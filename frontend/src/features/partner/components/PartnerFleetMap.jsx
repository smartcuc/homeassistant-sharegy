import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import {
  MapPin,
  Navigation,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Wrench,
  Eye,
  FileText,
  Battery,
  Sun,
  Zap,
  Car,
  Clock,
  Compass,
  Building,
  Radio,
  ExternalLink
} from "lucide-react";

// Mock coordinate distribution for German hubs if no lat/lng in backend
const CITY_COORDS = {
  münchen: { x: 62, y: 84 },
  munich: { x: 62, y: 84 },
  berlin: { x: 74, y: 28 },
  hamburg: { x: 48, y: 16 },
  köln: { x: 22, y: 52 },
  cologne: { x: 22, y: 52 },
  frankfurt: { x: 36, y: 60 },
  stuttgart: { x: 40, y: 76 },
  leipzig: { x: 68, y: 44 },
  dortmund: { x: 26, y: 44 },
  düsseldorf: { x: 20, y: 46 },
  nürnberg: { x: 58, y: 68 },
  augsburg: { x: 56, y: 82 },
  hannover: { x: 44, y: 32 },
  bremen: { x: 38, y: 22 },
  dresden: { x: 80, y: 48 },
};

export default function PartnerFleetMap({
  homes,
  onSelectAssetForDiagnostics,
  onOpenProtocol
}) {
  const { t } = useTranslation();
  const [selectedHomeId, setSelectedHomeId] = useState(
    homes?.find((h) => h.health === "error")?.id || homes?.[0]?.id || null
  );
  const [filterMapHealth, setFilterMapHealth] = useState("all");

  const selectedHome = homes?.find((h) => h.id === selectedHomeId) || homes?.[0];

  // Helper to determine map coordinates
  const getCoordinates = (home, index) => {
    const addr = (home.address || "").toLowerCase();
    for (const [city, coords] of Object.entries(CITY_COORDS)) {
      if (addr.includes(city)) {
        // slight jitter so overlapping points don't hide each other
        const jitterX = ((index % 5) - 2) * 2;
        const jitterY = (((index * 3) % 5) - 2) * 2;
        return { x: coords.x + jitterX, y: coords.y + jitterY };
      }
    }
    // Default pseudo positions spread across Germany/DACH
    const defaultPositions = [
      { x: 35, y: 58 },
      { x: 60, y: 82 },
      { x: 72, y: 30 },
      { x: 46, y: 18 },
      { x: 56, y: 66 },
      { x: 24, y: 50 },
      { x: 42, y: 74 },
      { x: 66, y: 42 },
    ];
    return defaultPositions[index % defaultPositions.length];
  };

  const filteredMapHomes = (homes || []).filter((h) => {
    if (filterMapHealth === "all") return true;
    return h.health === filterMapHealth;
  });

  // Calculate simulated distances for technician dispatch (sorted with errors first)
  const prioritizedHomes = [...(homes || [])].sort((a, b) => {
    const score = (h) => (h.health === "error" ? 0 : h.health === "warning" ? 1 : 2);
    return score(a) - score(b);
  });

  return (
    <div className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 rounded-3xl p-5 sm:p-6 shadow-xs space-y-6">
      {/* Top Controls & Dispatch Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-100 dark:border-slate-800 pb-4">
        <div>
          <h3 className="text-base font-black text-slate-900 dark:text-white flex items-center gap-2">
            <Compass className="w-5 h-5 text-sky-500" />
            <span>{t("partner.map_title", "Flotten-Radar & Servicetechniker-Routenplanung")}</span>
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            {t("partner.map_subtitle", "Interaktive Liegenschafts-Karte mit Störungs-Priorisierung und 1-Klick-Navigation")}
          </p>
        </div>

        <div className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-800/60 p-1 rounded-xl text-xs font-bold">
          <button
            type="button"
            onClick={() => setFilterMapHealth("all")}
            className={`px-3 py-1 rounded-lg transition cursor-pointer ${
              filterMapHealth === "all" ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-2xs" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            Alle ({homes?.length || 0})
          </button>
          <button
            type="button"
            onClick={() => setFilterMapHealth("error")}
            className={`flex items-center gap-1 px-3 py-1 rounded-lg transition cursor-pointer ${
              filterMapHealth === "error" ? "bg-rose-500 text-white shadow-2xs" : "text-slate-500 hover:text-rose-600"
            }`}
          >
            <XCircle className="w-3.5 h-3.5" />
            <span>Störungen ({homes?.filter((h) => h.health === "error").length || 0})</span>
          </button>
          <button
            type="button"
            onClick={() => setFilterMapHealth("warning")}
            className={`flex items-center gap-1 px-3 py-1 rounded-lg transition cursor-pointer ${
              filterMapHealth === "warning" ? "bg-amber-500 text-white shadow-2xs" : "text-slate-500 hover:text-amber-600"
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Warnungen ({homes?.filter((h) => h.health === "warning").length || 0})</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Map & Dispatch Queue */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left / Center: Interactive SVG Map Container */}
        <div className="lg:col-span-7 bg-slate-950 rounded-3xl p-4 sm:p-6 relative overflow-hidden border border-slate-800 min-h-[360px] sm:min-h-[460px] flex items-center justify-center shadow-inner">
          {/* Background Map Contours */}
          <div className="absolute inset-0 opacity-15 pointer-events-none bg-[radial-gradient(#38bdf8_1px,transparent_1px)] [background-size:16px_16px]"></div>
          
          <svg
            viewBox="0 0 100 100"
            className="w-full h-full max-w-[420px] max-h-[420px] relative z-10 select-none"
          >
            {/* Outline of Germany / Central Europe stylized */}
            <path
              d="M35 12 Q50 8 68 18 Q82 25 80 40 Q84 55 75 75 Q68 88 55 92 Q42 88 34 78 Q22 68 18 52 Q16 34 26 22 Z"
              fill="rgba(30, 41, 59, 0.5)"
              stroke="rgba(56, 189, 248, 0.3)"
              strokeWidth="0.8"
              strokeDasharray="2,2"
            />
            {/* Regional Rings */}
            <circle cx="50" cy="50" r="35" fill="none" stroke="rgba(56, 189, 248, 0.1)" strokeWidth="0.5" />
            <circle cx="50" cy="50" r="20" fill="none" stroke="rgba(56, 189, 248, 0.1)" strokeWidth="0.5" />

            {/* Render Map Pins for Homes */}
            {filteredMapHomes.map((home, idx) => {
              const { x, y } = getCoordinates(home, idx);
              const isSelected = home.id === selectedHomeId;
              const isError = home.health === "error";
              const isWarning = home.health === "warning";
              const pinColor = isError ? "#f43f5e" : isWarning ? "#f59e0b" : "#10b981";

              return (
                <g
                  key={home.id}
                  onClick={() => setSelectedHomeId(home.id)}
                  className="cursor-pointer transition-transform duration-200 hover:scale-125 origin-center"
                  style={{ transformOrigin: `${x}% ${y}%` }}
                >
                  {/* Ping Animation for Selected or Error */}
                  {(isSelected || isError) && (
                    <circle
                      cx={x}
                      cy={y}
                      r={isSelected ? 6 : 4.5}
                      fill="none"
                      stroke={pinColor}
                      strokeWidth="0.8"
                      className="animate-ping opacity-75"
                    />
                  )}

                  {/* Outer glow ring */}
                  <circle
                    cx={x}
                    cy={y}
                    r={isSelected ? 4.5 : 3}
                    fill={pinColor}
                    fillOpacity={isSelected ? 0.35 : 0.2}
                    stroke={pinColor}
                    strokeWidth={isSelected ? 1.2 : 0.6}
                  />

                  {/* Center Dot */}
                  <circle
                    cx={x}
                    cy={y}
                    r={isSelected ? 2.5 : 1.6}
                    fill={pinColor}
                  />

                  {/* Tiny Label on Hover / Selection */}
                  {isSelected && (
                    <g>
                      <rect
                        x={Math.max(5, Math.min(65, x - 15))}
                        y={y - 8}
                        width="30"
                        height="5.5"
                        rx="1.5"
                        fill="rgba(15, 23, 42, 0.9)"
                        stroke={pinColor}
                        strokeWidth="0.4"
                      />
                      <text
                        x={Math.max(5, Math.min(65, x - 15)) + 15}
                        y={y - 4.2}
                        fontSize="2.4"
                        fill="#ffffff"
                        textAnchor="middle"
                        fontWeight="bold"
                        fontFamily="sans-serif"
                      >
                        {home.name.length > 12 ? home.name.slice(0, 11) + "…" : home.name}
                      </text>
                    </g>
                  )}
                </g>
              );
            })}
          </svg>

          {/* Map Overlay Legend */}
          <div className="absolute bottom-3 left-3 bg-slate-900/90 backdrop-blur border border-slate-800 rounded-xl p-2.5 text-[11px] font-bold text-slate-300 space-y-1 z-20">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              <span>Online / Optimal</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-amber-500"></span>
              <span>Warnung / Überprüfung</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
              <span>Störung (Priorität 1)</span>
            </div>
          </div>
        </div>

        {/* Right: Selected Asset Detail & Technician Dispatch Queue */}
        <div className="lg:col-span-5 flex flex-col justify-between space-y-4">
          {selectedHome ? (
            <div className="bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-2xl p-4.5 space-y-4 shadow-xs flex-1 flex flex-col justify-between">
              <div className="space-y-3">
                {/* Header info */}
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xl">🏡</span>
                      <h4 className="font-black text-slate-900 dark:text-white text-base">
                        {selectedHome.name}
                      </h4>
                    </div>
                    <div className="text-xs text-slate-500 mt-0.5">
                      {selectedHome.customer_name} • {selectedHome.customer_email}
                    </div>
                  </div>
                  {selectedHome.health === "ok" ? (
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/20">
                      Online
                    </span>
                  ) : selectedHome.health === "warning" ? (
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-500/20">
                      Warnung
                    </span>
                  ) : (
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-500/10 text-rose-700 dark:text-rose-400 border border-rose-500/20 animate-pulse">
                      Störung
                    </span>
                  )}
                </div>

                {/* Address & Navigation Launch */}
                <div className="p-3 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs">
                  <div className="space-y-0.5">
                    <span className="text-[10px] text-slate-400 block font-bold uppercase">Standort:</span>
                    <strong className="text-slate-900 dark:text-slate-100">
                      {selectedHome.address || "Sonnenstraße 10, 80331 München"}
                    </strong>
                  </div>
                  <a
                    href={`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(
                      selectedHome.address || selectedHome.name
                    )}`}
                    target="_blank"
                    rel="noreferrer"
                    className="px-3 py-1.5 bg-sky-600 hover:bg-sky-500 text-white rounded-lg font-bold flex items-center gap-1.5 transition shadow-xs cursor-pointer text-xs"
                    title="Navigation in Google Maps öffnen"
                  >
                    <Navigation className="w-3.5 h-3.5" />
                    <span>Route</span>
                  </a>
                </div>

                {/* Storage & Live Telemetry */}
                <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                  <div className="p-2.5 rounded-xl bg-emerald-500/5 border border-emerald-500/20">
                    <div className="text-[10px] text-emerald-600 font-bold uppercase">Heimspeicher</div>
                    <div className="text-sm font-black text-emerald-700 dark:text-emerald-300">
                      🔋 {selectedHome.battery_capacity_kwh || 10} kWh
                    </div>
                    <div className="text-[10px] text-slate-400 font-sans mt-0.5">
                      {selectedHome.battery_soc_pct || 74}% Ladestand
                    </div>
                  </div>
                  <div className="p-2.5 rounded-xl bg-amber-500/5 border border-amber-500/20">
                    <div className="text-[10px] text-amber-600 font-bold uppercase">PV-Erzeugung</div>
                    <div className="text-sm font-black text-amber-700 dark:text-amber-300">
                      ☀️ {selectedHome.pv_power_w ?? 0} W
                    </div>
                    <div className="text-[10px] text-slate-400 font-sans mt-0.5">
                      {selectedHome.inverters_count || 1}x Wechselrichter
                    </div>
                  </div>
                </div>

                {/* § 14a Status & Wallbox */}
                <div className="flex items-center justify-between p-2.5 bg-teal-50 dark:bg-teal-950/40 border border-teal-200 dark:border-teal-800/40 rounded-xl text-xs">
                  <span className="font-bold text-teal-800 dark:text-teal-200 flex items-center gap-1.5">
                    <Zap className="w-3.5 h-3.5 text-teal-600" />
                    § 14a Dimm-Status:
                  </span>
                  <span className="font-bold text-teal-700 dark:text-teal-300">
                    Netzdienlich bereit (4,2 kW)
                  </span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-2 pt-2 border-t border-slate-200 dark:border-slate-800">
                <div className="grid grid-cols-2 gap-2">
                  <Link
                    to={`/app/energy?home_id=${selectedHome.id}&partner_view=true&home_name=${encodeURIComponent(selectedHome.name)}&customer=${encodeURIComponent(selectedHome.customer_name || "")}`}
                    className="py-2 bg-white dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-800 rounded-xl text-xs font-bold text-center flex items-center justify-center gap-1.5 transition"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>Live-EMS</span>
                  </Link>
                  <button
                    type="button"
                    onClick={() => onOpenProtocol(selectedHome)}
                    className="py-2 bg-indigo-50 dark:bg-indigo-950/40 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition cursor-pointer"
                  >
                    <FileText className="w-3.5 h-3.5" />
                    <span>IBN-Protokoll</span>
                  </button>
                </div>
                <button
                  type="button"
                  onClick={() => onSelectAssetForDiagnostics(selectedHome)}
                  className="w-full py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-bold flex items-center justify-center gap-2 shadow-xs transition cursor-pointer"
                >
                  <Wrench className="w-4 h-4" />
                  <span>Fernwartung & Diagnose öffnen</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="p-8 text-center text-slate-400">
              Wähle eine Anlage auf der Karte aus
            </div>
          )}

          {/* Servicetechniker Dispatch Queue (Prioritized List) */}
          <div className="p-3.5 bg-slate-100 dark:bg-slate-800/40 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs font-bold text-slate-700 dark:text-slate-300">
              <span className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-sky-500" />
                <span>Einsatz-Warteschlange (Priorität):</span>
              </span>
              <span className="text-[11px] text-slate-400">{prioritizedHomes.length} Liegenschaften</span>
            </div>
            <div className="flex gap-1.5 overflow-x-auto pb-1">
              {prioritizedHomes.slice(0, 5).map((h) => (
                <button
                  key={h.id}
                  type="button"
                  onClick={() => setSelectedHomeId(h.id)}
                  className={`px-2.5 py-1.5 rounded-xl text-[11px] font-bold shrink-0 transition flex items-center gap-1.5 cursor-pointer border ${
                    h.id === selectedHomeId
                      ? "bg-white dark:bg-slate-900 border-sky-500 text-sky-600 dark:text-sky-400 shadow-2xs"
                      : "bg-white/60 dark:bg-slate-900/60 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:bg-white dark:hover:bg-slate-800"
                  }`}
                >
                  <span
                    className={`w-2 h-2 rounded-full ${
                      h.health === "error"
                        ? "bg-rose-500 animate-pulse"
                        : h.health === "warning"
                        ? "bg-amber-500"
                        : "bg-emerald-500"
                    }`}
                  ></span>
                  <span>{h.name}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
