/*
# frontend/src/features/community/pages/CooperativeJoinPage.jsx
# Digitaler Beitrittsprozess zu einer Bürgerenergiegenossenschaft (eG) / Energy Sharing Gemeinschaft
# mit rechtssicherer Satzungs-Zustimmung gem. §§ 15b, 30 GenG
*/

import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiFetch } from "../../../api/client";

export default function CooperativeJoinPage() {
    const { slug } = useParams();
    const navigate = useNavigate();

    const [tenant, setTenant] = useState(null);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState("");
    const [submittedData, setSubmittedData] = useState(null);

    const [form, setForm] = useState({
        first_name: "",
        last_name: "",
        email: "",
        phone: "",
        street: "",
        postal_code: "",
        city: "",
        birth_date: "",
        meter_malo_id: "",
        participant_role: "consumer", // 'consumer' | 'prosumer' | 'both'
        shares_count: 1,
        statute_accepted: false,
    });

    useEffect(() => {
        async function loadInfo() {
            setLoading(true);
            try {
                const data = await apiFetch(`/api/cooperative/info/${slug}/`);
                setTenant(data);
                if (data.min_shares_count) {
                    setForm((prev) => ({ ...prev, shares_count: data.min_shares_count }));
                }
            } catch (err) {
                console.error("Failed to load cooperative info:", err);
                setError("Die angeforderte Energiegemeinschaft oder Genossenschaft konnte nicht gefunden werden.");
            } finally {
                setLoading(false);
            }
        }
        if (slug) {
            loadInfo();
        }
    }, [slug]);

    const nominalValue = tenant?.share_nominal_value_eur || 100.0;
    const totalAmount = (Number(form.shares_count) || 1) * nominalValue;

    async function handleSubmit(e) {
        e.preventDefault();
        setError("");

        if (!form.statute_accepted) {
            setError("Bitte bestätige die Anerkennung der Genossenschaftssatzung.");
            return;
        }

        setSubmitting(true);
        try {
            const res = await apiFetch(`/api/cooperative/join/${slug}/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(form),
            });
            setSubmittedData(res);
        } catch (err) {
            console.error("Submission failed:", err);
            setError(err?.data?.error || err?.message || "Fehler beim Absenden des Beitrittsantrags.");
        } finally {
            setSubmitting(false);
        }
    }

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950 p-6">
                <div className="text-center space-y-3">
                    <div className="w-10 h-10 border-3 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                    <p className="text-xs text-slate-500">Lade Beitrittsportal...</p>
                </div>
            </div>
        );
    }

    if (error && !tenant) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950 p-6">
                <div className="max-w-md w-full bg-white dark:bg-slate-900 p-8 rounded-3xl border border-slate-200 dark:border-slate-800 text-center space-y-4 shadow-sm">
                    <div className="w-14 h-14 rounded-2xl bg-rose-500/10 text-rose-600 flex items-center justify-center text-2xl mx-auto">
                        ⚠️
                    </div>
                    <h2 className="text-xl font-bold text-slate-900 dark:text-white">Gemeinschaft nicht gefunden</h2>
                    <p className="text-xs text-slate-500 dark:text-slate-400">{error}</p>
                    <button
                        onClick={() => navigate("/")}
                        className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition cursor-pointer"
                    >
                        Zur Startseite
                    </button>
                </div>
            </div>
        );
    }

    if (submittedData) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950 p-4 sm:p-6">
                <div className="max-w-lg w-full bg-white dark:bg-slate-900 border border-emerald-500/20 rounded-3xl p-8 shadow-sm text-center space-y-5">
                    <div className="w-16 h-16 rounded-3xl bg-emerald-500/10 text-emerald-600 flex items-center justify-center text-3xl mx-auto">
                        ✅
                    </div>
                    <div>
                        <span className="text-[11px] font-bold text-emerald-600 uppercase tracking-wider">
                            Antrag erfolgreich übermittelt
                        </span>
                        <h2 className="text-2xl font-black text-slate-900 dark:text-white mt-1">
                            Willkommen bei {tenant?.name}!
                        </h2>
                    </div>

                    <div className="bg-slate-50 dark:bg-slate-800/40 p-4 rounded-2xl text-left space-y-2 border border-slate-200/60 dark:border-slate-800 text-xs">
                        <div className="flex justify-between py-1 border-b border-slate-200 dark:border-slate-700">
                            <span className="text-slate-500">Antrags-ID:</span>
                            <span className="font-mono font-bold">{submittedData.application_id?.slice(0, 8)}...</span>
                        </div>
                        <div className="flex justify-between py-1 border-b border-slate-200 dark:border-slate-700">
                            <span className="text-slate-500">Gezeichnete Geschäftsanteile:</span>
                            <span className="font-bold">{submittedData.shares_count} Anteil(e) ({submittedData.total_amount_eur?.toFixed(2)} €)</span>
                        </div>
                        <div className="flex justify-between py-1 border-b border-slate-200 dark:border-slate-700">
                            <span className="text-slate-500">Anerkannte Satzungsversion:</span>
                            <span className="font-bold">v{submittedData.statute_version} (§ 15b GenG)</span>
                        </div>
                        <div className="flex justify-between py-1">
                            <span className="text-slate-500">Status:</span>
                            <span className="text-amber-600 font-bold">Wartet auf Vorstandsbeschluss</span>
                        </div>
                    </div>

                    <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                        Dein digitaler Mitgliedsantrag liegt dem Vorstand von <strong>{tenant?.name}</strong> vor. Nach der formalen Beschlussfassung erhältst du deine Mitgliedsnummer und die Bestätigung per E-Mail an <strong>{form.email}</strong>.
                    </p>

                    <div className="pt-2">
                        <button
                            onClick={() => navigate("/login")}
                            className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition shadow-xs cursor-pointer"
                        >
                            Zum Login
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-8 px-4 sm:px-6">
            <div className="max-w-2xl mx-auto space-y-6">

                {/* HEADER BANNER */}
                <div className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-6 shadow-2xs space-y-3">
                    <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 text-emerald-600 flex items-center justify-center text-2xl font-bold">
                            🏛️
                        </div>
                        <div>
                            <div className="text-xs text-emerald-600 font-bold uppercase tracking-wider">
                                Digitaler Genossenschafts-Beitritt gem. § 15b GenG
                            </div>
                            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white">
                                {tenant?.name}
                            </h1>
                        </div>
                    </div>
                    <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                        Werde Teil der regionalen Energiewende. Zeichne deine Genossenschaftsanteile digital und nimm am 15-Minuten-Energy-Sharing im Verteilnetz teil.
                    </p>
                </div>

                {/* BEITRITTS-FORMULAR */}
                <form onSubmit={handleSubmit} className="bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-3xl p-6 shadow-2xs space-y-6">

                    {error && (
                        <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-600 text-xs font-semibold">
                            ⚠️ {error}
                        </div>
                    )}

                    {/* ABSCHNITT 1: PERSÖNLICHE DATEN */}
                    <div className="space-y-3">
                        <h2 className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider flex items-center gap-2">
                            <span>👤</span> 1. Persönliche Angaben des Mitglieds
                        </h2>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                            <div>
                                <label className="block text-slate-600 dark:text-slate-400 mb-1">Vorname *</label>
                                <input
                                    type="text"
                                    required
                                    value={form.first_name}
                                    onChange={(e) => setForm({ ...form, first_name: e.target.value })}
                                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 text-slate-900 dark:text-white"
                                    placeholder="Max"
                                />
                            </div>
                            <div>
                                <label className="block text-slate-600 dark:text-slate-400 mb-1">Nachname *</label>
                                <input
                                    type="text"
                                    required
                                    value={form.last_name}
                                    onChange={(e) => setForm({ ...form, last_name: e.target.value })}
                                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 text-slate-900 dark:text-white"
                                    placeholder="Mustermann"
                                />
                            </div>
                            <div>
                                <label className="block text-slate-600 dark:text-slate-400 mb-1">E-Mail-Adresse *</label>
                                <input
                                    type="email"
                                    required
                                    value={form.email}
                                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 text-slate-900 dark:text-white"
                                    placeholder="max@beispiel.de"
                                />
                            </div>
                            <div>
                                <label className="block text-slate-600 dark:text-slate-400 mb-1">Telefonnummer</label>
                                <input
                                    type="tel"
                                    value={form.phone}
                                    onChange={(e) => setForm({ ...form, phone: e.target.value })}
                                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 text-slate-900 dark:text-white"
                                    placeholder="+49 170 1234567"
                                />
                            </div>
                            <div className="sm:col-span-2">
                                <label className="block text-slate-600 dark:text-slate-400 mb-1">Straße & Hausnummer *</label>
                                <input
                                    type="text"
                                    required
                                    value={form.street}
                                    onChange={(e) => setForm({ ...form, street: e.target.value })}
                                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 text-slate-900 dark:text-white"
                                    placeholder="Sonnenstraße 10"
                                />
                            </div>
                            <div>
                                <label className="block text-slate-600 dark:text-slate-400 mb-1">Postleitzahl *</label>
                                <input
                                    type="text"
                                    required
                                    value={form.postal_code}
                                    onChange={(e) => setForm({ ...form, postal_code: e.target.value })}
                                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 text-slate-900 dark:text-white"
                                    placeholder="10115"
                                />
                            </div>
                            <div>
                                <label className="block text-slate-600 dark:text-slate-400 mb-1">Stadt *</label>
                                <input
                                    type="text"
                                    required
                                    value={form.city}
                                    onChange={(e) => setForm({ ...form, city: e.target.value })}
                                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 text-slate-900 dark:text-white"
                                    placeholder="Berlin"
                                />
                            </div>
                        </div>
                    </div>

                    {/* ABSCHNITT 2: SHARING-ROLLE & ZÄHLER (MALO) */}
                    <div className="space-y-3 pt-3 border-t border-slate-100 dark:border-slate-800">
                        <h2 className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider flex items-center gap-2">
                            <span>⚡</span> 2. Energy Sharing Rolle & Zählpunkt (MaLo)
                        </h2>
                        <div className="space-y-3 text-xs">
                            <div>
                                <label className="block text-slate-600 dark:text-slate-400 mb-1.5 font-semibold">
                                    Wie möchtest du an der Energiegemeinschaft teilnehmen?
                                </label>
                                <div className="grid grid-cols-3 gap-2">
                                    {[
                                        { id: "consumer", label: "🔌 Consumer", desc: "Strom beziehen" },
                                        { id: "prosumer", label: "☀️ Prosumer", desc: "PV einspeisen" },
                                        { id: "both", label: "⚡ Beides", desc: "Erzeugen & Beziehen" },
                                    ].map((r) => (
                                        <button
                                            key={r.id}
                                            type="button"
                                            onClick={() => setForm({ ...form, participant_role: r.id })}
                                            className={`p-3 rounded-xl border text-left transition cursor-pointer ${
                                                form.participant_role === r.id
                                                    ? "bg-indigo-50 dark:bg-indigo-950/40 border-indigo-400 text-indigo-950 dark:text-indigo-200 font-bold"
                                                    : "border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400"
                                            }`}
                                        >
                                            <div className="text-xs">{r.label}</div>
                                            <div className="text-[10px] opacity-75 mt-0.5">{r.desc}</div>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div>
                                <label className="block text-slate-600 dark:text-slate-400 mb-1">
                                    Marktlokations-ID (MaLo) deines Stromzählers (optional / auf der Stromrechnung)
                                </label>
                                <input
                                    type="text"
                                    value={form.meter_malo_id}
                                    onChange={(e) => setForm({ ...form, meter_malo_id: e.target.value })}
                                    className="w-full p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 font-mono text-slate-900 dark:text-white"
                                    placeholder="DE000123456789000000000000000001"
                                />
                                <span className="text-[10px] text-slate-400 mt-1 block">
                                    Wird für die 15-Minuten-Zuteilung im Verteilnetz durch den wMSB benötigt.
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* ABSCHNITT 3: GESCHÄFTSANTEILE & SATZUNG */}
                    <div className="space-y-3 pt-3 border-t border-slate-100 dark:border-slate-800">
                        <h2 className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider flex items-center gap-2">
                            <span>📜</span> 3. Geschäftsanteile & Satzungsanerkennung
                        </h2>

                        {/* ANTEILE BERECHNUNG */}
                        <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                            <div>
                                <div className="font-bold text-emerald-900 dark:text-emerald-200">
                                    Geschäftsanteile nach § 15b GenG
                                </div>
                                <div className="text-[11px] text-emerald-700 dark:text-emerald-300">
                                    Nennwert: {nominalValue.toFixed(2)} € je Anteil (Mindestanzahl: {tenant?.min_shares_count || 1})
                                </div>
                            </div>

                            <div className="flex items-center gap-3">
                                <label className="text-slate-600 dark:text-slate-400 font-semibold">Anzahl:</label>
                                <input
                                    type="number"
                                    min={tenant?.min_shares_count || 1}
                                    max={tenant?.max_shares_count || 100}
                                    value={form.shares_count}
                                    onChange={(e) => setForm({ ...form, shares_count: Math.max(1, parseInt(e.target.value) || 1) })}
                                    className="w-16 p-2 rounded-xl border border-emerald-300 dark:border-emerald-700 bg-white dark:bg-slate-900 text-center font-bold"
                                />
                                <div className="text-right">
                                    <div className="text-[10px] text-slate-400 uppercase">Gesamt</div>
                                    <div className="text-base font-black text-emerald-900 dark:text-emerald-100">
                                        {totalAmount.toFixed(2)} €
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* SATZUNGS-ZUSTIMMUNG */}
                        <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-3 text-xs">
                            <div className="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-slate-700">
                                <span className="font-bold text-slate-800 dark:text-slate-200">
                                    Satzung der {tenant?.name} (Version {tenant?.statute_version || "1.0"})
                                </span>
                                {tenant?.statute_url && (
                                    <a
                                        href={tenant.statute_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-indigo-600 dark:text-indigo-400 underline font-bold flex items-center gap-1"
                                    >
                                        <span>📄</span> Satzungs-PDF öffnen
                                    </a>
                                )}
                            </div>

                            {tenant?.statute_text && (
                                <div className="max-h-32 overflow-y-auto p-3 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 text-[11px] text-slate-600 dark:text-slate-300 leading-relaxed font-mono whitespace-pre-wrap">
                                    {tenant.statute_text}
                                </div>
                            )}

                            <label className="flex items-start gap-3 cursor-pointer pt-1">
                                <input
                                    type="checkbox"
                                    required
                                    checked={form.statute_accepted}
                                    onChange={(e) => setForm({ ...form, statute_accepted: e.target.checked })}
                                    className="mt-1 w-4 h-4 text-emerald-600 rounded cursor-pointer"
                                />
                                <span className="text-[11px] text-slate-700 dark:text-slate-300 leading-relaxed">
                                    Ich habe die <strong>Satzung der {tenant?.name}</strong> (Fassung v{tenant?.statute_version || "1.0"}) sowie die Beitrittsbedingungen vollständig zur Kenntnis genommen und erkenne diese hiermit verbindlich an. Ich beantrage die Aufnahme in die Genossenschaft und verpflichte mich zur Einzahlung der gezeichneten Geschäftsanteile in Höhe von <strong>{totalAmount.toFixed(2)} €</strong> nach Vorstandsgenehmigung.
                                </span>
                            </label>
                        </div>
                    </div>

                    {/* SUBMIT BUTTON */}
                    <div className="pt-3">
                        <button
                            type="submit"
                            disabled={submitting || !form.statute_accepted}
                            className="w-full py-3.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-2xl text-xs font-bold transition shadow-sm cursor-pointer flex items-center justify-center gap-2"
                        >
                            <span>🏛️</span>
                            <span>{submitting ? "Übermittle Beitrittsantrag..." : `Verbindlichen Mitgliedsantrag einreichen (${totalAmount.toFixed(2)} €)`}</span>
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
