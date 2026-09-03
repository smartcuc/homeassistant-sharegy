import React, { useState, useEffect } from "react";
import { 
  Activity, 
  CheckCircle2, 
  AlertTriangle, 
  RefreshCw, 
  Zap, 
  Wifi, 
  ShieldCheck, 
  Clock, 
  ArrowRight, 
  X, 
  Sparkles,
  Gauge
} from "lucide-react";
import { useTranslation } from "react-i18next";

export default function DeviceSelfTestModal({ open, onClose, deviceId = null, deviceName = "Wechselrichter / Wallbox", profileId = null }) {
  const { t } = useTranslation();
  const [running, setRunning] = useState(false);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const startTest = async () => {
    setRunning(true);
    setResult(null);
    setError(null);
    setCurrentStepIndex(0);

    // Step-by-step UI animation
    const stepInterval = setInterval(() => {
      setCurrentStepIndex((prev) => {
        if (prev < 2) return prev + 1;
        clearInterval(stepInterval);
        return prev;
      });
    }, 700);

    try {
      const url = deviceId 
        ? `/api/devices/${deviceId}/self-test/` 
        : `/api/devices/self-test/simulate/?profile_id=${profileId || "sungrow_isolarcloud"}`;

      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });

      if (!res.ok) throw new Error("Selbsttest-Service nicht erreichbar");
      const data = await res.json();
      
      // Allow user to experience the animated sequence
      setTimeout(() => {
        setResult(data);
        setCurrentStepIndex(3);
        setRunning(false);
      }, 2100);

    } catch (err) {
      clearInterval(stepInterval);
      setError(err.message || "Fehler bei der Diagnose");
      setRunning(false);
    }
  };

  useEffect(() => {
    if (open) {
      startTest();
    } else {
      setResult(null);
      setRunning(false);
      setCurrentStepIndex(0);
    }
  }, [open, deviceId]);

  if (!open) return null;

  const testSteps = [
    { key: "connectivity", title: t("selftest.step1", "Verbindung & Latenz-Prüfung"), icon: Wifi, desc: "Ping, TLS/WSS Handshake & Cloud-Erreichbarkeit" },
    { key: "telemetry", title: t("selftest.step2", "Live-Telemetrie Ingestion"), icon: Activity, desc: "Wirkleistung (W), Zählerstand & SoC-Plausibilität" },
    { key: "control_loop", title: t("selftest.step3", "Steuerungs-Rückkanal & Heartbeat"), icon: Zap, desc: "Bidirektionale Regelung (OpenAPI / OCPP / WSS)" }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 max-w-xl w-full overflow-hidden transition-all">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-emerald-500/10 via-teal-500/10 to-emerald-500/10 dark:from-emerald-950/40 dark:to-slate-900 p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-emerald-500 text-white flex items-center justify-center shadow-lg shadow-emerald-500/30">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                {t("selftest.title", "1-Klick Hardware-Selbsttest")}
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-300">
                  Live Check
                </span>
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {deviceName}
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="w-8 h-8 rounded-full flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6">
          
          {/* Progress / Step List */}
          <div className="space-y-3">
            {testSteps.map((s, idx) => {
              const Icon = s.icon;
              const isDone = currentStepIndex > idx || (result && !running);
              const isActive = running && currentStepIndex === idx;

              return (
                <div 
                  key={s.key}
                  className={`p-4 rounded-2xl border transition-all flex items-start gap-4 ${
                    isDone 
                      ? "bg-emerald-50/50 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800/40"
                      : isActive 
                        ? "bg-blue-50/50 dark:bg-blue-950/20 border-blue-300 dark:border-blue-700 shadow-sm"
                        : "bg-slate-50 dark:bg-slate-800/40 border-slate-200 dark:border-slate-800 opacity-60"
                  }`}
                >
                  <div className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 mt-0.5 ${
                    isDone 
                      ? "bg-emerald-500 text-white" 
                      : isActive 
                        ? "bg-blue-500 text-white animate-pulse" 
                        : "bg-slate-200 dark:bg-slate-700 text-slate-400"
                  }`}>
                    {isDone ? (
                      <CheckCircle2 className="w-5 h-5" />
                    ) : isActive ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <Icon className="w-4 h-4" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-bold text-slate-800 dark:text-slate-200">
                        {s.title}
                      </span>
                      {isDone && result?.steps?.[idx]?.latency_ms && (
                        <span className="text-[11px] font-mono font-semibold px-2 py-0.5 rounded-md bg-emerald-100 dark:bg-emerald-900/60 text-emerald-700 dark:text-emerald-300">
                          {result.steps[idx].latency_ms} ms
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                      {isDone && result?.steps?.[idx]?.message 
                        ? result.steps[idx].message 
                        : s.desc}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Test Certificate & Result Box */}
          {result && (
            <div className="p-4 rounded-2xl bg-gradient-to-br from-emerald-500/10 via-teal-500/5 to-transparent dark:from-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 space-y-3 animate-fade-in">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                  <span className="text-xs font-bold uppercase tracking-wider text-emerald-800 dark:text-emerald-300">
                    Diagnose-Zertifikat
                  </span>
                </div>
                <div className="flex items-center gap-1.5 bg-emerald-500 text-white px-3 py-1 rounded-full text-xs font-extrabold shadow-sm">
                  <Gauge className="w-3.5 h-3.5" />
                  <span>Score {result.health_score} / 100</span>
                </div>
              </div>

              <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed font-medium">
                {result.summary}
              </p>

              {/* Detail Metrics Preview */}
              {result.steps?.[1]?.live_metrics && (
                <div className="grid grid-cols-3 gap-2 pt-2 border-t border-emerald-200/60 dark:border-emerald-800/40">
                  <div className="p-2 rounded-xl bg-white/80 dark:bg-slate-800/80 text-center">
                    <span className="text-[10px] text-slate-400 font-semibold block">Live Leistung</span>
                    <span className="text-xs font-bold text-slate-900 dark:text-white font-mono">
                      {result.steps[1].live_metrics.power_w || 0} W
                    </span>
                  </div>
                  <div className="p-2 rounded-xl bg-white/80 dark:bg-slate-800/80 text-center">
                    <span className="text-[10px] text-slate-400 font-semibold block">Netzspannung</span>
                    <span className="text-xs font-bold text-slate-900 dark:text-white font-mono">
                      {result.steps[1].live_metrics.voltage_v || 230.1} V
                    </span>
                  </div>
                  <div className="p-2 rounded-xl bg-white/80 dark:bg-slate-800/80 text-center">
                    <span className="text-[10px] text-slate-400 font-semibold block">Latenz</span>
                    <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 font-mono">
                      {result.latency_ms} ms
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="p-4 rounded-2xl bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 text-xs text-red-600 dark:text-red-400 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

        </div>

        {/* Footer Actions */}
        <div className="p-4 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <button
            onClick={startTest}
            disabled={running}
            className="px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-white dark:hover:bg-slate-700 text-xs font-bold text-slate-700 dark:text-slate-300 flex items-center gap-1.5 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${running ? "animate-spin" : ""}`} />
            {t("selftest.retry", "Erneut prüfen")}
          </button>

          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-md shadow-emerald-500/20 transition-all"
          >
            {t("selftest.done", "Fertig")}
          </button>
        </div>

      </div>
    </div>
  );
}
