import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { Zap, Clock, ChevronRight, Info, Sparkles } from "lucide-react";
import { apiFetch } from "../../../api/client";
import SpotPriceModal from "./SpotPriceModal";

export default function SpotPriceHeatmapCard({ onOpenDetails }) {
  const { t } = useTranslation();
  const [modalOpen, setModalOpen] = useState(false);
  const [, setSelectedHour] = useState(null);

  const { data, isLoading } = useQuery({
    queryKey: ["spot-price-chart", "2d"],
    queryFn: () => apiFetch("/api/market/chart/?range=2d"),
    staleTime: 1000 * 60 * 15,
  });

  const now = new Date();
  const currentHour = now.getHours();

  // Parse and organize timeline data
  const heatmapData = useMemo(() => {
    if (!data || !data.timestamps || !data.effective_values) return { today: [], tomorrow: [], hasTomorrow: false, min: 0, max: 0, avg: 0, bestWindow: null };

    const items = data.timestamps.map((ts, idx) => {
      const date = new Date(ts);
      const price = data.effective_values[idx] !== undefined ? data.effective_values[idx] : (data.values?.[idx] || 0);
      return {
        timestamp: ts,
        date,
        hour: date.getHours(),
        isToday: date.toDateString() === now.toDateString(),
        price: Number(price),
      };
    });

    // Group into today and tomorrow by hour (averaging if 15-min intervals)
    const groupByHour = (list) => {
      const hoursMap = {};
      list.forEach(item => {
        if (!hoursMap[item.hour]) {
          hoursMap[item.hour] = [];
        }
        hoursMap[item.hour].push(item.price);
      });
      return Object.keys(hoursMap).map(h => {
        const hourNum = parseInt(h, 10);
        const prices = hoursMap[hourNum];
        const avgPrice = prices.reduce((a, b) => a + b, 0) / prices.length;
        return {
          hour: hourNum,
          price: Math.round(avgPrice * 10) / 10,
          label: `${String(hourNum).padStart(2, "0")}:00`,
        };
      }).sort((a, b) => a.hour - b.hour);
    };

    const todayItems = items.filter(i => i.isToday);
    const tomorrowDate = new Date();
    tomorrowDate.setDate(now.getDate() + 1);
    const tomorrowItems = items.filter(i => i.date.toDateString() === tomorrowDate.toDateString());

    const todayHourly = groupByHour(todayItems);
    const tomorrowHourly = groupByHour(tomorrowItems);

    const allHourly = [...todayHourly, ...tomorrowHourly];
    const pricesList = allHourly.map(h => h.price);
    const min = pricesList.length ? Math.min(...pricesList) : 0;
    const max = pricesList.length ? Math.max(...pricesList) : 0;
    const avg = pricesList.length ? Math.round((pricesList.reduce((a, b) => a + b, 0) / pricesList.length) * 10) / 10 : 0;

    // Find best consecutive 2-hour charging window in the next 24h
    let bestWindow = null;
    let lowestWindowAvg = Infinity;
    const futureSlots = [
      ...todayHourly.filter(h => h.hour >= currentHour).map(h => ({ ...h, dayLabel: t("spot_heatmap.today", "Heute") })),
      ...tomorrowHourly.map(h => ({ ...h, dayLabel: t("spot_heatmap.tomorrow", "Morgen") })),
    ];

    for (let i = 0; i < futureSlots.length - 1; i++) {
      const windowAvg = (futureSlots[i].price + futureSlots[i + 1].price) / 2;
      if (windowAvg < lowestWindowAvg) {
        lowestWindowAvg = windowAvg;
        bestWindow = {
          startDay: futureSlots[i].dayLabel,
          startHour: futureSlots[i].label,
          endHour: `${String((futureSlots[i + 1].hour + 1) % 24).padStart(2, "0")}:00`,
          avgPrice: Math.round(windowAvg * 10) / 10,
        };
      }
    }

    return {
      today: todayHourly,
      tomorrow: tomorrowHourly,
      hasTomorrow: tomorrowHourly.length > 0,
      min,
      max,
      avg,
      bestWindow,
    };
  }, [data, now, currentHour, t]);

  // Color mapper based on price
  const getCellColor = (price) => {
    if (price <= 12.0) {
      return "bg-emerald-500 text-white font-bold shadow-xs hover:bg-emerald-600";
    }
    if (price <= 19.0) {
      return "bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border border-emerald-300/60 dark:border-emerald-700/60 hover:bg-emerald-200 dark:hover:bg-emerald-900/60";
    }
    if (price <= 27.0) {
      return "bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border border-amber-300/60 dark:border-amber-700/60 hover:bg-amber-200 dark:hover:bg-amber-900/60";
    }
    return "bg-rose-100 dark:bg-rose-950/60 text-rose-800 dark:text-rose-300 border border-rose-300/60 dark:border-rose-700/60 hover:bg-rose-200 dark:hover:bg-rose-900/60";
  };

  const handleCardClick = () => {
    if (onOpenDetails) {
      onOpenDetails();
    } else {
      setModalOpen(true);
    }
  };

  if (isLoading) {
    return (
      <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-xs animate-pulse">
        <div className="h-5 bg-slate-200 dark:bg-slate-700 rounded w-1/3 mb-4"></div>
        <div className="h-28 bg-slate-100 dark:bg-slate-800 rounded-2xl"></div>
      </div>
    );
  }

  const currentSlot = heatmapData.today.find(h => h.hour === currentHour) || { price: heatmapData.avg || 0 };

  return (
    <>
      <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-xs hover:border-slate-300 dark:hover:border-slate-700 transition-all space-y-5">
        
        {/* Header with Title & Current Price */}
        <div className="flex flex-wrap items-start justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200/60 dark:border-amber-800/60 flex items-center justify-center text-amber-600 dark:text-amber-400 shrink-0 shadow-2xs">
              <Zap className="w-5 h-5 fill-amber-500/20" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-slate-900 dark:text-white">
                  {t("spot_heatmap.title", "Dynamische Börsenstrom-Heatmap (EPEX Spot)")}
                </h2>
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span>
                  Day-Ahead
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                {t("spot_heatmap.subtitle", "Stündliche Strompreis-Trends für kostenoptimiertes Laden und Speichern.")}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                {t("spot_heatmap.current_price", "Aktueller Preis")}
              </div>
              <div className="text-lg font-black text-slate-900 dark:text-white font-mono">
                {currentSlot.price.toFixed(1)} <span className="text-xs font-normal text-slate-500">ct/kWh</span>
              </div>
            </div>

            <button
              onClick={handleCardClick}
              className="p-2 rounded-xl bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 transition-colors cursor-pointer"
              title={t("spot_heatmap.open_details", "Großansicht & Analyse")}
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Smart Best Window Recommendation Banner */}
        {heatmapData.bestWindow && (
          <div className="p-3.5 rounded-2xl bg-gradient-to-r from-emerald-500/10 via-teal-500/10 to-blue-500/10 dark:from-emerald-950/30 dark:to-blue-950/30 border border-emerald-200/80 dark:border-emerald-800/60 flex items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2.5 min-w-0">
              <Sparkles className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
              <span className="text-slate-700 dark:text-slate-200 font-medium truncate">
                <strong className="text-emerald-700 dark:text-emerald-400 font-bold">
                  {t("spot_heatmap.best_charging_window", "Günstigstes Ladefenster:")}
                </strong>{" "}
                {heatmapData.bestWindow.startDay} {heatmapData.bestWindow.startHour} – {heatmapData.bestWindow.endHour} ({heatmapData.bestWindow.avgPrice.toFixed(1)} ct/kWh)
              </span>
            </div>
            <span className="px-2 py-0.5 rounded-lg bg-emerald-100 dark:bg-emerald-900/60 text-emerald-800 dark:text-emerald-300 font-bold text-[10px] shrink-0">
              {t("spot_heatmap.save_recommended", "Optimal")}
            </span>
          </div>
        )}

        {/* Heatmap Section: Today */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              {t("spot_heatmap.today_timeline", "Heute (00:00 – 24:00 Uhr)")}
            </span>
            <span className="text-[11px] text-slate-400">
              Min: <strong className="text-emerald-600 dark:text-emerald-400">{heatmapData.min.toFixed(1)}</strong> | Max: <strong className="text-rose-600 dark:text-rose-400">{heatmapData.max.toFixed(1)}</strong> ct/kWh
            </span>
          </div>

          <div className="grid grid-cols-12 gap-1 sm:gap-1.5">
            {heatmapData.today.map((slot) => {
              const isCurrent = slot.hour === currentHour;
              return (
                <div
                  key={`today-${slot.hour}`}
                  onClick={() => setSelectedHour(slot)}
                  className={`relative p-1.5 sm:p-2 rounded-xl text-center cursor-pointer transition-all duration-150 ${getCellColor(slot.price)} ${
                    isCurrent ? "ring-2 ring-amber-500 ring-offset-2 dark:ring-offset-slate-900 scale-105 z-10" : ""
                  }`}
                >
                  <div className="text-[9px] sm:text-[10px] opacity-80 leading-tight">{slot.label}</div>
                  <div className="text-[10px] sm:text-xs font-black font-mono mt-0.5 leading-none">
                    {slot.price.toFixed(0)}
                  </div>
                  {isCurrent && (
                    <span className="absolute -top-1.5 -right-1 w-2.5 h-2.5 bg-amber-500 border-2 border-white dark:border-slate-900 rounded-full"></span>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Heatmap Section: Tomorrow (or Day-Ahead Notice) */}
        <div className="space-y-2 pt-2 border-t border-slate-100 dark:border-slate-800">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              {t("spot_heatmap.tomorrow_timeline", "Morgen (Folgetag)")}
            </span>
            {heatmapData.hasTomorrow ? (
              <span className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800">
                {t("spot_heatmap.auction_cleared", "✓ Auktionspreise bestätigt")}
              </span>
            ) : (
              <span className="text-[10px] text-slate-400 flex items-center gap-1">
                <Info className="w-3 h-3" />
                {t("spot_heatmap.auction_pending", "Täglich ab 12:45 Uhr verfügbar")}
              </span>
            )}
          </div>

          {heatmapData.hasTomorrow ? (
            <div className="grid grid-cols-12 gap-1 sm:gap-1.5">
              {heatmapData.tomorrow.map((slot) => (
                <div
                  key={`tomorrow-${slot.hour}`}
                  onClick={() => setSelectedHour(slot)}
                  className={`p-1.5 sm:p-2 rounded-xl text-center cursor-pointer transition-all duration-150 ${getCellColor(slot.price)}`}
                >
                  <div className="text-[9px] sm:text-[10px] opacity-80 leading-tight">{slot.label}</div>
                  <div className="text-[10px] sm:text-xs font-black font-mono mt-0.5 leading-none">
                    {slot.price.toFixed(0)}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-dashed border-slate-200 dark:border-slate-700/60 text-center text-xs text-slate-500 dark:text-slate-400">
              {t("spot_heatmap.tomorrow_notice", "Die Day-Ahead Börsenstrompreise für morgen werden gegen 12:45 Uhr an der EPEX Spot auktioniert und hier vollautomatisch eingespielt.")}
            </div>
          )}
        </div>

        {/* Legend */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-2 text-[11px] text-slate-500 dark:text-slate-400 border-t border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-md bg-emerald-500"></span>
              {t("spot_heatmap.legend_super_cheap", "Sehr günstig (<12 ct)")}
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-md bg-emerald-100 dark:bg-emerald-900 border border-emerald-300 dark:border-emerald-700"></span>
              {t("spot_heatmap.legend_cheap", "Günstig (12–19 ct)")}
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-md bg-amber-100 dark:bg-amber-900 border border-amber-300 dark:border-amber-700"></span>
              {t("spot_heatmap.legend_medium", "Normal (19–27 ct)")}
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-md bg-rose-100 dark:bg-rose-900 border border-rose-300 dark:border-rose-700"></span>
              {t("spot_heatmap.legend_peak", "Spitze (>27 ct)")}
            </span>
          </div>

          <button
            onClick={handleCardClick}
            className="text-xs font-bold text-amber-600 dark:text-amber-400 hover:underline flex items-center gap-1 cursor-pointer"
          >
            {t("spot_heatmap.open_chart", "Detaillierte Analyse öffnen")} →
          </button>
        </div>

      </div>

      {modalOpen && (
        <SpotPriceModal open={modalOpen} onClose={() => setModalOpen(false)} />
      )}
    </>
  );
}
