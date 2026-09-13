/*
# frontend/src/components/layout/ContextSwitcher.jsx
# Diskretes Dropdown zur nahtlosen Umschaltung des Navigations- & Arbeitskontexts
*/

import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useUserNavigation } from "../../hooks/useUserNavigation";
import { NAV_MODES } from "../../config/navigationConfig";
import { ChevronDown, Check, Sparkles } from "lucide-react";

export default function ContextSwitcher({ compact = false }) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { activeMode, availableModes, switchMode, activeMetadata, allMetadata, isMultiMode } = useUserNavigation();
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef(null);

    // Outside click listener
    useEffect(() => {
        function handleClickOutside(e) {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const handleSelectMode = (modeKey) => {
        switchMode(modeKey);
        setIsOpen(false);
        if (modeKey === NAV_MODES.PARTNER) {
            navigate("/app/partner/dashboard");
        } else if (modeKey === NAV_MODES.ADMIN) {
            navigate("/app/admin/communities");
        } else if (modeKey === NAV_MODES.SHARING_ONLY) {
            navigate("/app/tenants");
        } else if (modeKey === NAV_MODES.EMS_ONLY || modeKey === NAV_MODES.HYBRID) {
            navigate("/app/energy");
        }
    };

    // Wenn der Nutzer nur 1 Modus hat, zeigen wir nur ein dezentes Label oder gar kein Dropdown
    if (!isMultiMode) {
        return (
            <div className="flex items-center gap-1.5 px-2.5 py-1 bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/60 rounded-xl text-xs font-medium text-slate-700 dark:text-slate-300">
                <span>{activeMetadata.icon}</span>
                <span className="hidden sm:inline">{t(activeMetadata.labelKey, activeMetadata.defaultLabel)}</span>
            </div>
        );
    }

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                type="button"
                onClick={() => setIsOpen(!isOpen)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs font-semibold transition-all shadow-sm ${
                    isOpen
                        ? "bg-indigo-50 dark:bg-indigo-950/50 border-indigo-300 dark:border-indigo-600 text-indigo-700 dark:text-indigo-300 ring-2 ring-indigo-500/20"
                        : "bg-white/90 dark:bg-slate-850/90 border-slate-200 dark:border-slate-700/80 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800"
                }`}
                title={t("nav.switch_context_hint", "Arbeitsbereich umschalten")}
            >
                <span className="text-sm">{activeMetadata.icon}</span>
                {!compact && (
                    <div className="flex flex-col items-start text-left leading-tight hidden sm:flex">
                        <span className="text-[9px] uppercase tracking-wider text-slate-600 dark:text-slate-300 font-bold">
                            {t("nav.context_label", "Bereich")}
                        </span>
                        <span className="truncate max-w-[120px] text-slate-900 dark:text-white">
                            {t(activeMetadata.labelKey, activeMetadata.defaultLabel)}
                        </span>
                    </div>
                )}
                <ChevronDown className={`w-3.5 h-3.5 text-slate-600 dark:text-slate-300 transition-transform ${isOpen ? "rotate-180" : ""}`} />
            </button>

            {isOpen && (
                <div className="absolute left-0 sm:right-0 sm:left-auto mt-2 w-64 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-xl z-50 p-1.5 animate-in fade-in zoom-in-95 duration-100">
                    <div className="px-3 py-2 border-b border-slate-100 dark:border-slate-800/80 mb-1">
                        <div className="flex items-center gap-1.5 text-xs font-bold text-slate-900 dark:text-white">
                            <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
                            <span>{t("nav.select_context", "Ansicht wählen")}</span>
                        </div>
                        <p className="text-[11px] text-slate-600 dark:text-slate-300 mt-0.5">
                            {t("nav.select_context_desc", "Menüführung an Rolle anpassen")}
                        </p>
                    </div>

                    <div className="space-y-1">
                        {availableModes.map((modeKey) => {
                            const meta = allMetadata[modeKey];
                            if (!meta) return null;
                            const isCurrent = modeKey === activeMode;

                            return (
                                <button
                                    key={modeKey}
                                    type="button"
                                    onClick={() => handleSelectMode(modeKey)}
                                    className={`w-full flex items-start gap-2.5 p-2 rounded-xl text-left transition-colors cursor-pointer ${
                                        isCurrent
                                            ? "bg-indigo-50 dark:bg-indigo-950/60 text-indigo-900 dark:text-indigo-200 border border-indigo-200 dark:border-indigo-800"
                                            : "hover:bg-slate-100 dark:hover:bg-slate-800/80 text-slate-700 dark:text-slate-300 border border-transparent"
                                    }`}
                                >
                                    <span className="text-base mt-0.5">{meta.icon}</span>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center justify-between">
                                            <span className="text-xs font-bold truncate">
                                                {t(meta.labelKey, meta.defaultLabel)}
                                            </span>
                                            {isCurrent && <Check className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />}
                                        </div>
                                        <p className="text-[10px] text-slate-600 dark:text-slate-300 leading-snug line-clamp-2 mt-0.5">
                                            {meta.description}
                                        </p>
                                    </div>
                                </button>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
}
