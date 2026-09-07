import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useSubscription } from "../../../hooks/useSubscription";
import ProBadge from "../../../components/common/ProBadge";
import ProUpgradeModal from "../../../components/common/ProUpgradeModal";
import WallboxCard from "../../energy/components/WallboxCard";
import FuelRadarCard from "../../control/components/FuelRadarCard";
import AddWallboxModal from "../../devices/components/AddWallboxModal";

export default function MobilityPage() {
    const { t } = useTranslation();
    const { isPro } = useSubscription();
    const [addWallboxOpen, setAddWallboxOpen] = useState(false);
    const [proModalOpen, setProModalOpen] = useState(false);

    return (
        <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-sky-500 to-indigo-600 text-white flex items-center justify-center text-2xl shadow-lg shadow-sky-500/20">
                        🚗
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h1 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white tracking-tight">
                                E-Mobilität & Spritpreis-Radar
                            </h1>
                            <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-sky-50 dark:bg-sky-950/50 text-sky-700 dark:text-sky-300 border border-sky-200 dark:border-sky-800">
                                Smart Mobility Hub
                            </span>
                        </div>
                        <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
                            OCPP-Wallbox-Steuerung, PV-Überschussladung & Echtzeit-Spritpreisvergleich (Tankerkönig MTS-K).
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <button
                        type="button"
                        onClick={() => setAddWallboxOpen(true)}
                        className="px-4 py-2.5 rounded-2xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition shadow-lg shadow-indigo-600/20 flex items-center gap-2 cursor-pointer shrink-0"
                    >
                        <span>⚡</span>
                        <span>Wallbox anbinden</span>
                    </button>
                </div>
            </div>

            {/* Quick Mobility Overview Banner */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center gap-4">
                    <div className="w-11 h-11 rounded-2xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-xl shrink-0">
                        ☀️
                    </div>
                    <div>
                        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">PV-Überschuss Laden</div>
                        <div className="text-base font-black text-slate-900 dark:text-white font-mono">1,44 € <span className="text-xs font-normal text-slate-500">/ 100 km</span></div>
                        <div className="text-[11px] text-emerald-600 dark:text-emerald-400 font-bold">-88% vs. Verbrenner</div>
                    </div>
                </div>

                <div className="p-4 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center gap-4">
                    <div className="w-11 h-11 rounded-2xl bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-xl shrink-0">
                        🌙
                    </div>
                    <div>
                        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Spot-Nachttarif</div>
                        <div className="text-base font-black text-slate-900 dark:text-white font-mono">3,24 € <span className="text-xs font-normal text-slate-500">/ 100 km</span></div>
                        <div className="text-[11px] text-indigo-600 dark:text-indigo-400 font-bold">Günstigste Börsenstunden</div>
                    </div>
                </div>

                <div className="p-4 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center gap-4">
                    <div className="w-11 h-11 rounded-2xl bg-amber-50 dark:bg-amber-950/50 text-amber-600 dark:text-amber-400 flex items-center justify-center text-xl shrink-0">
                        💶
                    </div>
                    <div>
                        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Ersparnis-Potenzial</div>
                        <div className="text-base font-black text-slate-900 dark:text-white font-mono">1.641 € <span className="text-xs font-normal text-slate-500">/ Jahr</span></div>
                        <div className="text-[11px] text-slate-500">bei 15.000 km Fahrleistung</div>
                    </div>
                </div>
            </div>

            {/* Main Cards Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* 🚗 Wallbox / OCPP E-Auto Ladekarte */}
                <div className="space-y-4">
                    <WallboxCard onOpenAddModal={() => setAddWallboxOpen(true)} />
                </div>

                {/* ⛽ Mobilitäts- & Spritpreis-Radar (MTS-K / Tankerkönig) */}
                <div className="space-y-4">
                    <FuelRadarCard />
                </div>
            </div>

            {/* Modal: Wallbox anbinden */}
            {addWallboxOpen && (
                <AddWallboxModal isOpen={addWallboxOpen} onClose={() => setAddWallboxOpen(false)} />
            )}

            {/* Pro Upgrade Modal */}
            {proModalOpen && (
                <ProUpgradeModal isOpen={proModalOpen} onClose={() => setProModalOpen(false)} />
            )}
        </div>
    );
}
