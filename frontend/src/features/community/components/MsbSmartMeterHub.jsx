/*
# src/features/community/components/MsbSmartMeterHub.jsx
*/

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";

export default function MsbSmartMeterHub({ tenant }) {
    const { t } = useTranslation();
    const queryClient = useQueryClient();

    const [activeTab, setActiveTab] = useState("paths"); // "paths", "meters", "import_export", "switch_guide"
    const [msconsText, setMsconsText] = useState("");
    const [jsonReadingsText, setJsonReadingsText] = useState("");
    const [importResult, setImportResult] = useState(null);
    const [copiedKey, setCopiedKey] = useState(null);

    const webhookUrl = `${window.location.origin}/api/billing/community/obis/ingest/`;
    const msconsUploadUrl = `${window.location.origin}/api/billing/community/mscons/import/`;

    function safeCopy(text, key) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text);
            setCopiedKey(key);
            setTimeout(() => setCopiedKey(null), 2000);
        }
    }

    // 1. Zählerliste der Community abfragen
    const metersQuery = useQuery({
        queryKey: ["community-msb-meters", tenant?.id],
        queryFn: () => {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            return apiFetch(`/api/billing/community/msb-meters/?tenant_id=${tenant?.id || ""}`, {
                headers: {
                    Authorization: token ? `Bearer ${token}` : "",
                    "X-Tenant-ID": tenant?.id || "",
                },
            });
        },
        enabled: !!tenant?.id,
    });

    const meters = metersQuery.data?.meters || [];

    // 2. MSCONS Import Mutation
    const msconsImportMutation = useMutation({
        mutationFn: async (content) => {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            return apiFetch("/api/billing/community/mscons/import/", {
                method: "POST",
                headers: {
                    Authorization: token ? `Bearer ${token}` : "",
                    "X-Tenant-ID": tenant?.id || "",
                },
                body: JSON.stringify({
                    tenant_id: tenant?.id,
                    edi_content: content,
                }),
            });
        },
        onSuccess: (data) => {
            setImportResult(data);
            queryClient.invalidateQueries(["community-msb-meters"]);
            queryClient.invalidateQueries(["community-cockpit"]);
        },
        onError: (err) => {
            alert(err.message || "Fehler beim MSCONS-Import");
        },
    });

    // 3. JSON OBIS Ingest Mutation
    const obisJsonMutation = useMutation({
        mutationFn: async (readings) => {
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            return apiFetch("/api/billing/community/obis/ingest/", {
                method: "POST",
                headers: {
                    Authorization: token ? `Bearer ${token}` : "",
                    "X-Tenant-ID": tenant?.id || "",
                },
                body: JSON.stringify({
                    tenant_id: tenant?.id,
                    readings: readings,
                }),
            });
        },
        onSuccess: (data) => {
            setImportResult(data);
            queryClient.invalidateQueries(["community-msb-meters"]);
            queryClient.invalidateQueries(["community-cockpit"]);
        },
        onError: (err) => {
            alert(err.message || "Fehler beim JSON-OBIS-Import");
        },
    });

    // MSCONS Export herunterladen
    async function downloadMsconsExport() {
        try {
            const now = new Date();
            const year = now.getFullYear();
            const month = now.getMonth() + 1;
            const token = localStorage.getItem("token") || sessionStorage.getItem("token");
            const res = await fetch(`/api/billing/community/mscons/export/?year=${year}&month=${month}&tenant_id=${tenant?.id || ""}`, {
                headers: {
                    Authorization: token ? `Bearer ${token}` : "",
                    "X-Tenant-ID": tenant?.id || "",
                },
            });
            if (!res.ok) throw new Error("Export fehlgeschlagen.");
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `MSCONS_${tenant?.slug || "community"}_${year}_${month.toString().padStart(2, "0")}.edi`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error(err);
            alert("Fehler beim Herunterladen des MSCONS EDIFACT Exports.");
        }
    }

    return (
        <div className="space-y-6">
            {/* HERO HEADER */}
            <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white rounded-3xl p-6 sm:p-8 border border-indigo-800/60 shadow-xl relative overflow-hidden">
                <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div className="space-y-2 max-w-2xl">
                        <div className="flex items-center gap-2">
                            <span className="px-3 py-1 bg-indigo-500/20 border border-indigo-400/30 rounded-full text-indigo-300 text-xs font-black tracking-wider uppercase">
                                § 42b EnWG & MsbG Konform
                            </span>
                            <span className="px-2.5 py-1 bg-emerald-500/20 border border-emerald-400/30 rounded-full text-emerald-300 text-xs font-extrabold">
                                3 Zählerpfade Aktiv
                            </span>
                        </div>
                        <h2 className="text-2xl sm:text-3xl font-black tracking-tight">
                            Zähler-Flexibilität & wMSB Smart Meter Hub ⚡
                        </h2>
                        <p className="text-sm text-slate-300 leading-relaxed">
                            Verbinde zertifizierte Smart Meter Gateways (iMSys), wettbewerbliche Messstellenbetreiber (wMSB) oder MID-Submeter. 
                            Sharegy aggregiert 15-Minuten-Lastgänge für ein eichrechtskonformes Energy Sharing.
                        </p>
                    </div>

                    <div className="flex flex-col sm:flex-row gap-3 shrink-0">
                        <button
                            type="button"
                            onClick={downloadMsconsExport}
                            className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl transition shadow-sm flex items-center justify-center gap-2 cursor-pointer"
                        >
                            <span>📑</span>
                            <span>MSCONS Export (.edi)</span>
                        </button>
                    </div>
                </div>
            </div>

            {/* TAB BAR */}
            <div className="flex border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 rounded-2xl p-1.5 shadow-2xs gap-1">
                {[
                    { id: "paths", label: "🌐 3 Zählerpfade (wMSB / gMSB / Submeter)", icon: "🌐" },
                    { id: "meters", label: `📊 Zählerliste (${meters.length})`, icon: "📊" },
                    { id: "import_export", label: "🔄 MSCONS & 15m-OBIS Ingest", icon: "🔄" },
                    { id: "switch_guide", label: "📄 wMSB Wechselassistent", icon: "📄" },
                ].map((tab) => (
                    <button
                        key={tab.id}
                        type="button"
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex-1 py-2.5 px-3 rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 cursor-pointer ${
                            activeTab === tab.id
                                ? "bg-indigo-600 text-white shadow-xs"
                                : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
                        }`}
                    >
                        <span>{tab.label}</span>
                    </button>
                ))}
            </div>

            {/* TAB 1: DIE 3 ZÄHLERPFADE */}
            {activeTab === "paths" && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                    {/* PFAD 1: wMSB CLOUD-PUSH */}
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-xs flex flex-col justify-between space-y-4">
                        <div className="space-y-3">
                            <div className="w-12 h-12 rounded-2xl bg-indigo-50 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-2xl shadow-2xs">
                                🏢
                            </div>
                            <div>
                                <span className="text-[10px] uppercase tracking-wider font-extrabold px-2 py-0.5 rounded-full bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300">
                                    Pfad 1: Wettbewerblich (wMSB)
                                </span>
                                <h3 className="text-base font-bold text-slate-900 dark:text-white mt-1.5">
                                    wMSB Cloud-Push & Webhooks
                                </h3>
                                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
                                    Für inexogy, Solandeo, Discovergy oder Octopus/Tibber Pulse. Der wMSB pusht 15m-Lastgänge automatisch per HTTPS REST oder MSCONS EDIFACT.
                                </p>
                            </div>

                            <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl space-y-1.5 text-[11px] font-mono text-slate-700 dark:text-slate-300">
                                <div className="text-slate-400 text-[10px] uppercase font-bold">Community Ingest Webhook:</div>
                                <div className="break-all font-semibold text-indigo-600 dark:text-indigo-400">
                                    {webhookUrl}
                                </div>
                            </div>
                        </div>

                        <button
                            type="button"
                            onClick={() => safeCopy(webhookUrl, "webhook")}
                            className="w-full py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 cursor-pointer"
                        >
                            {copiedKey === "webhook" ? "✅ URL kopiert!" : "📋 Webhook-URL kopieren"}
                        </button>
                    </div>

                    {/* PFAD 2: gMSB SMART METER GATEWAY */}
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-xs flex flex-col justify-between space-y-4">
                        <div className="space-y-3">
                            <div className="w-12 h-12 rounded-2xl bg-amber-50 dark:bg-amber-900/40 text-amber-600 dark:text-amber-400 flex items-center justify-center text-2xl shadow-2xs">
                                ⚡
                            </div>
                            <div>
                                <span className="text-[10px] uppercase tracking-wider font-extrabold px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-900/50 text-amber-800 dark:text-amber-300">
                                    Pfad 2: Grundzuständig (gMSB)
                                </span>
                                <h3 className="text-base font-bold text-slate-900 dark:text-white mt-1.5">
                                    gMSB iMSys / HAN-Schnittstelle
                                </h3>
                                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
                                    Für Stadtwerke & Verteilnetzbetreiber (z. B. BonnNetz, Westnetz). Auslesung über die BSI TR-03109-1 HAN-Schnittstelle oder lokales SMGW-Gateway.
                                </p>
                            </div>

                            <div className="space-y-1 text-xs text-slate-600 dark:text-slate-400">
                                <div className="flex items-center gap-1.5">
                                    <span>🔒</span>
                                    <span>BSI TR-03109-1 konform</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span>📡</span>
                                    <span>Lokal & CLS-Kanal Support</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span>⏱️</span>
                                    <span>Echte 15m-Werte (OBIS 1.8.0/2.8.0)</span>
                                </div>
                            </div>
                        </div>

                        <div className="p-2.5 bg-amber-50/60 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/40 rounded-xl text-[11px] text-amber-900 dark:text-amber-300">
                            ℹ️ HAN-PIN beim Netzbetreiber anfordern.
                        </div>
                    </div>

                    {/* PFAD 3: SUB-METERING & MID */}
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-xs flex flex-col justify-between space-y-4">
                        <div className="space-y-3">
                            <div className="w-12 h-12 rounded-2xl bg-emerald-50 dark:bg-emerald-900/40 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-2xl shadow-2xs">
                                🔌
                            </div>
                            <div>
                                <span className="text-[10px] uppercase tracking-wider font-extrabold px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-900/50 text-emerald-800 dark:text-emerald-300">
                                    Pfad 3: Private Quartiere & WEGs
                                </span>
                                <h3 className="text-base font-bold text-slate-900 dark:text-white mt-1.5">
                                    Hardware-Open MID-Submetering
                                </h3>
                                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
                                    Für interne Liegenschaften, Kaltmieter & ZEV. Nutzung von Shelly Pro 3EM, Modbus RTU/TCP oder Eastron MID Zählern über WebSocket / MQTT.
                                </p>
                            </div>

                            <div className="space-y-1 text-xs text-slate-600 dark:text-slate-400">
                                <div className="flex items-center gap-1.5">
                                    <span>⚡</span>
                                    <span>Shelly Pro 3EM / Plus 1PM</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span>🔄</span>
                                    <span>Sekundenschnelle Live-Bilanzierung</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span>💰</span>
                                    <span>Extrem kostengünstig (&lt; 150 €)</span>
                                </div>
                            </div>
                        </div>

                        <a
                            href="/app/devices"
                            className="w-full py-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300 rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5"
                        >
                            <span>➕</span>
                            <span>MID-Submeter anbinden</span>
                        </a>
                    </div>
                </div>
            )}

            {/* TAB 2: ZÄHLERLISTE DER COMMUNITY */}
            {activeTab === "meters" && (
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-xs space-y-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <h3 className="text-base font-bold text-slate-900 dark:text-white">
                                Zählpunkte & Messstellen der Community
                            </h3>
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                Alle registrierten Stromzähler, MaLo-IDs und deren aktueller Ingestion-Status.
                            </p>
                        </div>
                        <span className="text-xs font-bold px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full border border-indigo-200">
                            {meters.length} Zähler registriert
                        </span>
                    </div>

                    {meters.length > 0 ? (
                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-xs text-slate-600 dark:text-slate-400">
                                <thead className="bg-slate-50 dark:bg-slate-800/50 text-[10px] uppercase font-bold text-slate-500">
                                    <tr>
                                        <th className="p-3">Zählernummer / MaLo-ID</th>
                                        <th className="p-3">Mitglied / Zuordnung</th>
                                        <th className="p-3">Rolle</th>
                                        <th className="p-3">15m-Slots</th>
                                        <th className="p-3">Letzter Messwert</th>
                                        <th className="p-3">Status</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100 dark:divide-slate-800 font-medium">
                                    {meters.map((m) => (
                                        <tr key={m.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition">
                                            <td className="p-3 font-mono font-bold text-slate-900 dark:text-white">
                                                {m.serial_number}
                                            </td>
                                            <td className="p-3 text-slate-800 dark:text-slate-200">
                                                {m.member_name}
                                            </td>
                                            <td className="p-3">
                                                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                                                    m.member_role === "producer"
                                                        ? "bg-amber-100 text-amber-800"
                                                        : m.member_role === "prosumer"
                                                        ? "bg-purple-100 text-purple-800"
                                                        : "bg-blue-100 text-blue-800"
                                                }`}>
                                                    {m.member_role}
                                                </span>
                                            </td>
                                            <td className="p-3 font-bold text-slate-800 dark:text-slate-200">
                                                {m.total_15m_readings}
                                            </td>
                                            <td className="p-3 text-slate-500">
                                                {m.last_reading_time
                                                    ? `${new Date(m.last_reading_time).toLocaleDateString()} ${new Date(m.last_reading_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} (${m.last_reading_val} kWh ${m.last_reading_obis || ""})`
                                                    : "Noch keine Messwerte"}
                                            </td>
                                            <td className="p-3">
                                                <span className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold ${
                                                    m.status === "active"
                                                        ? "bg-emerald-100 text-emerald-800"
                                                        : "bg-amber-100 text-amber-800"
                                                }`}>
                                                    {m.status === "active" ? "🟢 Aktiv" : "⏳ Warte auf Daten"}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <div className="p-8 text-center bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-dashed border-slate-200 dark:border-slate-800 text-slate-400 text-xs">
                            Noch keine Zähler in dieser Community angelegt. Lade Mitglieder ein oder importiere eine MSCONS-Datei.
                        </div>
                    )}
                </div>
            )}

            {/* TAB 3: MSCONS & 15m-OBIS INGEST SIMULATOR */}
            {activeTab === "import_export" && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* EDIFACT / MSCONS IMPORT */}
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-xs space-y-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                    <span>📑</span> MSCONS EDIFACT (.edi) Import
                                </h3>
                                <p className="text-xs text-slate-500 dark:text-slate-400">
                                    Standardformat der BNetzA für Zähler-Lastgänge.
                                </p>
                            </div>
                        </div>

                        <textarea
                            value={msconsText}
                            onChange={(e) => setMsconsText(e.target.value)}
                            placeholder="UNA:+.? '&#10;UNB+UNOC:3+9901234567890:500+9909876543210:500...&#10;UNH+1+MSCONS:D:04B:UN:EAN008'&#10;..."
                            rows={7}
                            className="w-full p-3 font-mono text-[11px] bg-slate-900 text-green-400 rounded-xl border border-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        />

                        <button
                            type="button"
                            disabled={!msconsText.trim() || msconsImportMutation.isLoading}
                            onClick={() => msconsImportMutation.mutate(msconsText)}
                            className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl transition shadow-xs disabled:opacity-50 flex items-center justify-center gap-2 cursor-pointer"
                        >
                            {msconsImportMutation.isLoading ? "Importiere..." : "🚀 MSCONS-Datei einlesen & bilanzieren"}
                        </button>
                    </div>

                    {/* JSON OBIS INGEST */}
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-xs space-y-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                    <span>⚡</span> 15m-OBIS JSON Webhook Simulator
                                </h3>
                                <p className="text-xs text-slate-500 dark:text-slate-400">
                                    Direkte REST-Ingestion für wMSBs und Smart Meter Gateways.
                                </p>
                            </div>
                        </div>

                        <textarea
                            value={jsonReadingsText}
                            onChange={(e) => setJsonReadingsText(e.target.value)}
                            placeholder={`[
  {
    "malo_id": "1EMH0012345678",
    "ts_start": "2026-09-01T14:00:00+02:00",
    "obis": "1.8.0",
    "value_kwh": 2.50
  }
]`}
                            rows={7}
                            className="w-full p-3 font-mono text-[11px] bg-slate-900 text-amber-300 rounded-xl border border-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        />

                        <button
                            type="button"
                            disabled={!jsonReadingsText.trim() || obisJsonMutation.isLoading}
                            onClick={() => {
                                try {
                                    const parsed = JSON.parse(jsonReadingsText);
                                    obisJsonMutation.mutate(parsed);
                                } catch {
                                    alert("Ungültiges JSON-Format.");
                                }
                            }}
                            className="w-full py-2.5 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-xl transition shadow-xs disabled:opacity-50 flex items-center justify-center gap-2 cursor-pointer"
                        >
                            {obisJsonMutation.isLoading ? "Sende..." : "⚡ JSON-Messwerte einlesen"}
                        </button>
                    </div>

                    {/* IMPORT RESULT DISPLAY */}
                    {importResult && (
                        <div className="md:col-span-2 p-4 bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800 rounded-2xl text-xs space-y-2">
                            <div className="font-bold text-emerald-900 dark:text-emerald-200 flex items-center gap-2">
                                <span>🎉</span>
                                <span>{importResult.message || "Import erfolgreich durchgeführt!"}</span>
                            </div>
                            <div className="text-[11px] text-emerald-800 dark:text-emerald-300">
                                Eingelesene Messwerte: <strong>{importResult.imported_count || 0}</strong>
                                {importResult.unknown_meters?.length > 0 && (
                                    <span className="block text-amber-700 mt-1">
                                        ⚠️ Unbekannte Zähler in der Datei (nicht zugeordnet): {importResult.unknown_meters.join(", ")}
                                    </span>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* TAB 4: wMSB WECHSELASSISTENT */}
            {activeTab === "switch_guide" && (
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 sm:p-8 shadow-xs space-y-6">
                    <div className="max-w-2xl space-y-2">
                        <span className="text-xs font-bold text-indigo-600 uppercase tracking-wider">
                            Rechtlicher Rahmen nach § 5 MsbG
                        </span>
                        <h3 className="text-xl font-bold text-slate-900 dark:text-white">
                            Freie Messstellenbetreiber-Wahl für Prosumer & Communities
                        </h3>
                        <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                            Jeder Anschlussnutzer in Deutschland hat nach § 5 MsbG das gesetzliche Recht, seinen Messstellenbetreiber frei zu wählen. 
                            Wettbewerbliche MSBs (wMSB) bauen zertifizierte Smart Meter Gateways mit 15-Minuten-Lastgangübertragung ein — ohne jahrelange Wartezeiten beim lokalen Netzbetreiber.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
                        <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-200/80 dark:border-slate-800 space-y-1.5">
                            <div className="text-xl">1️⃣</div>
                            <div className="font-bold text-slate-900 dark:text-white">wMSB auswählen</div>
                            <div className="text-slate-500 text-[11px]">z. B. inexogy, Solandeo oder Discovergy beauftragen.</div>
                        </div>

                        <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-200/80 dark:border-slate-800 space-y-1.5">
                            <div className="text-xl">2️⃣</div>
                            <div className="font-bold text-slate-900 dark:text-white">Zähler-Installation</div>
                            <div className="text-slate-500 text-[11px]">Einbau des iMSys Smart Meter Gateways durch den wMSB.</div>
                        </div>

                        <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-200/80 dark:border-slate-800 space-y-1.5">
                            <div className="text-xl">3️⃣</div>
                            <div className="font-bold text-slate-900 dark:text-white">Sharegy Webhook hinterlegen</div>
                            <div className="text-slate-500 text-[11px]">Automatische 15m-Lastgangübertragung aktivieren.</div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
