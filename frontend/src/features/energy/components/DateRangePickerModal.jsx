import useModalDismiss from "../../../hooks/useModalDismiss";
import { useState } from "react";
import { useTranslation } from "react-i18next";

export default function DateRangePickerModal({ isOpen, onClose, onApply, initialStart, initialEnd }) {
    const { t } = useTranslation();
    useModalDismiss(isOpen, onClose);
    const [startDate, setStartDate] = useState(initialStart || new Date().toISOString().split("T")[0]);
    const [endDate, setEndDate] = useState(initialEnd || new Date().toISOString().split("T")[0]);

    if (!isOpen) return null;

    const setPreset = (daysAgo, label) => {
        const end = new Date();
        const start = new Date();
        start.setDate(end.getDate() - daysAgo);
        setStartDate(start.toISOString().split("T")[0]);
        setEndDate(end.toISOString().split("T")[0]);
    };

    const setMonthPreset = (monthsAgo) => {
        const now = new Date();
        const targetMonth = new Date(now.getFullYear(), now.getMonth() - monthsAgo, 1);
        const lastDay = new Date(targetMonth.getFullYear(), targetMonth.getMonth() + 1, 0);
        setStartDate(targetMonth.toISOString().split("T")[0]);
        setEndDate(lastDay.toISOString().split("T")[0]);
    };

    const handleSave = () => {
        if (!startDate || !endDate) return;
        onApply({
            period: "custom",
            startDate,
            endDate,
            label: `${startDate.split("-").reverse().join(".")} - ${endDate.split("-").reverse().join(".")}`,
        });
        onClose();
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4" onClick={onClose}>
            <div className="bg-white rounded-3xl shadow-2xl max-w-lg w-full p-6 border border-slate-200 animate-in fade-in zoom-in-95 duration-150" onClick={(e) => e.stopPropagation()}>
                <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                    <div className="flex items-center gap-2.5">
                        <span className="text-xl">📅</span>
                        <h3 className="text-lg font-bold text-gray-900">
                            {t("energy.custom_period_title", "Zeitraum frei wählen")}
                        </h3>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600 rounded-full p-1 hover:bg-slate-100 transition cursor-pointer"
                    >
                        ✕
                    </button>
                </div>

                {/* Presets */}
                <div className="mt-4">
                    <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider block mb-2">
                        {t("energy.presets", "Schnellwahl")}
                    </label>
                    <div className="flex flex-wrap gap-2">
                        <button
                            type="button"
                            onClick={() => setPreset(0, t("common.today", "Heute"))}
                            className="px-2.5 py-1 text-xs font-medium rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 transition cursor-pointer"
                        >
                            {t("common.today", "Heute")}
                        </button>
                        <button
                            type="button"
                            onClick={() => setPreset(1, t("common.yesterday", "Gestern"))}
                            className="px-2.5 py-1 text-xs font-medium rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 transition cursor-pointer"
                        >
                            {t("common.yesterday", "Gestern")}
                        </button>
                        <button
                            type="button"
                            onClick={() => setPreset(7, t("energy.last_7_days", "Letzte 7 Tage"))}
                            className="px-2.5 py-1 text-xs font-medium rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 transition cursor-pointer"
                        >
                            {t("energy.last_7_days", "Letzte 7 Tage")}
                        </button>
                        <button
                            type="button"
                            onClick={() => setPreset(30, t("energy.last_30_days", "Letzte 30 Tage"))}
                            className="px-2.5 py-1 text-xs font-medium rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 transition cursor-pointer"
                        >
                            {t("energy.last_30_days", "Letzte 30 Tage")}
                        </button>
                        <button
                            type="button"
                            onClick={() => setMonthPreset(0)}
                            className="px-2.5 py-1 text-xs font-medium rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-700 transition cursor-pointer"
                        >
                            {t("energy.this_month", "Dieser Monat")}
                        </button>
                        <button
                            type="button"
                            onClick={() => setMonthPreset(1)}
                            className="px-2.5 py-1 text-xs font-medium rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 transition cursor-pointer"
                        >
                            {t("energy.last_month", "Letzter Monat")}
                        </button>
                    </div>
                </div>

                {/* Custom Date Pickers */}
                <div className="mt-5 grid grid-cols-2 gap-4">
                    <div>
                        <label className="text-xs font-semibold text-gray-700 block mb-1">
                            {t("energy.start_date", "Startdatum")}
                        </label>
                        <input
                            type="date"
                            value={startDate}
                            onChange={(e) => setStartDate(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-xl text-sm font-medium focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        />
                    </div>
                    <div>
                        <label className="text-xs font-semibold text-gray-700 block mb-1">
                            {t("energy.end_date", "Enddatum")}
                        </label>
                        <input
                            type="date"
                            value={endDate}
                            onChange={(e) => setEndDate(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-xl text-sm font-medium focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        />
                    </div>
                </div>

                {/* Actions */}
                <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-end gap-3">
                    <button
                        type="button"
                        onClick={onClose}
                        className="px-4 py-2 rounded-xl text-sm font-semibold text-gray-600 hover:bg-slate-100 transition cursor-pointer"
                    >
                        {t("common.cancel", "Abbrechen")}
                    </button>
                    <button
                        type="button"
                        onClick={handleSave}
                        className="px-5 py-2 rounded-xl text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 shadow-md shadow-indigo-600/20 transition cursor-pointer"
                    >
                        {t("energy.apply_period", "Zeitraum anwenden")}
                    </button>
                </div>
            </div>
        </div>
    );
}
