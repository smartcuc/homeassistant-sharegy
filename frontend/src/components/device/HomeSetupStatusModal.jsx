/*
# src/components/device/HomeSetupStatusModal.jsx
*/

import React from "react";
import SystemReadinessCard from "../../features/energy/components/SystemReadinessCard";

export default function HomeSetupStatusModal({ open, onClose, onOpenAddDevice }) {
    if (!open) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-fade-in">
            <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden">
                {/* Header */}
                <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/70">
                    <div className="flex items-center gap-3">
                        <span className="text-3xl p-2.5 bg-white rounded-2xl shadow-xs border border-slate-200">🩺</span>
                        <div>
                            <h2 className="text-xl font-black text-gray-900 tracking-tight">
                                Installations- & Haushaltsstatus
                            </h2>
                            <p className="text-xs text-gray-500">
                                Detaillierte Prüfung der 4 Energiesäulen (PV, Netz, Speicher, Last) und Hardware-Alarme.
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="w-9 h-9 rounded-full bg-white border border-slate-200 text-gray-400 hover:text-gray-700 hover:bg-gray-100 flex items-center justify-center text-lg font-bold transition cursor-pointer"
                    >
                        ✕
                    </button>
                </div>

                {/* Body */}
                <div className="flex-1 overflow-y-auto p-6">
                    <SystemReadinessCard
                        onOpenAddDevice={() => {
                            if (onClose) onClose();
                            if (onOpenAddDevice) onOpenAddDevice();
                        }}
                    />
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-slate-100 bg-slate-50 flex items-center justify-end">
                    <button
                        onClick={onClose}
                        className="px-5 py-2 rounded-xl font-bold text-xs bg-gray-900 text-white hover:bg-black transition cursor-pointer shadow-xs"
                    >
                        Schließen
                    </button>
                </div>
            </div>
        </div>
    );
}
