import useModalDismiss from "../../../hooks/useModalDismiss";
import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { QRCodeSVG } from "qrcode.react";

export const ROLE_DEFINITIONS = [
    {
        key: "member",
        icon: "⚡",
        title: "Mitglied / Mieter (Sharing-Teilnehmer)",
        badge: "Standard",
        badgeColor: "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-500/20",
        description: "Nimmt am gemeinschaftlichen Energy Sharing oder Mieterstrom teil. Sieht den eigenen Solarstrom-Anteil, Live-Verbrauch und Monatsabrechnungen.",
    },
    {
        key: "user_admin",
        icon: "👥",
        title: "Mitglieder- & Mieterbetreuung",
        badge: "Verwaltung",
        badgeColor: "bg-indigo-500/10 text-indigo-700 dark:text-indigo-400 border-indigo-500/20",
        description: "Zuständig für die Betreuung der Hausgemeinschaft: Darf neue Bewohner/Mitglieder einladen, Einladungen verwalten und Daten bei Mieterwechsel pflegen.",
    },
    {
        key: "helpdesk",
        icon: "🛟",
        title: "Gemeinschafts- & Mieter-Support",
        badge: "Support",
        badgeColor: "bg-sky-500/10 text-sky-700 dark:text-sky-400 border-sky-500/20",
        description: "First-Level-Ansprechpartner vor Ort für Bewohner bei Fragen zu Zählern, Geräten oder der Sharegy-App.",
    },
    {
        key: "auditor",
        icon: "📊",
        title: "Kassenprüfer / Beirat",
        badge: "Prüfung",
        badgeColor: "bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/20",
        description: "Reiner Lesezugriff zur transparenten Einsicht in Quartiersbilanzen, Summenzähler und Abrechnungsnachweise nach § 42b EnWG.",
    },
    {
        key: "admin",
        icon: "🏛️",
        title: "Gemeinschafts-Leitung / Energie-Verwalter",
        badge: "Vollzugriff",
        badgeColor: "bg-rose-500/10 text-rose-700 dark:text-rose-400 border-rose-500/20",
        description: "Vollständige administrative Kontrolle über Tarife, Submetering, wMSB-Messstellenbetrieb und § 42b EnWG Abrechnung.",
    },
];

export default function CommunityInviteModal({
    isOpen,
    onClose,
    tenant,
    onInviteCreated,
    initialRole = "member",
}) {
    const { t } = useTranslation();
    useModalDismiss(isOpen, onClose);
    const [selectedRole, setSelectedRole] = useState(initialRole);
    const [createdInvite, setCreatedInvite] = useState(null);
    const [loading, setLoading] = useState(false);
    const [copied, setCopied] = useState(false);
    const [showQr, setShowQr] = useState(false);

    useEffect(() => {
        if (isOpen) {
            setSelectedRole(initialRole || "member");
            setCreatedInvite(null);
            setCopied(false);
            setShowQr(false);
        }
    }, [initialRole, isOpen]);

    if (!isOpen) return null;

    const currentRoleObj = ROLE_DEFINITIONS.find((r) => r.key === selectedRole) || ROLE_DEFINITIONS[0];

    const handleCreate = async () => {
        setLoading(true);
        try {
            const data = await onInviteCreated(selectedRole);
            if (data) {
                const fullUrl = data.link?.startsWith("http")
                    ? data.link
                    : `${window.location.origin}/onboarding?invite=${data.token}`;
                setCreatedInvite({
                    ...data,
                    fullUrl,
                });
            }
        } catch (err) {
            console.error("Invite error:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleCopy = async (url) => {
        try {
            await navigator.clipboard.writeText(url);
            setCopied(true);
            setTimeout(() => setCopied(false), 3000);
        } catch (e) {
            console.error("Copy failed:", e);
        }
    };

    const handleReset = () => {
        setCreatedInvite(null);
        setCopied(false);
        setShowQr(false);
    };

    // Mailto generator
    const getMailtoHref = () => {
        if (!createdInvite) return "#";
        const communityName = tenant?.name || "unserer Energy Community";
        const subject = encodeURIComponent(`Einladung zu ${communityName} auf Sharegy`);
        const body = encodeURIComponent(
            `Hallo,\n\ndu bist herzlich eingeladen, unserer Energie-Gemeinschaft "${communityName}" auf Sharegy beizutreten.\n\nÜber diesen persönlichen Link kannst du dich direkt registrieren und deinen Solarstrom-Anteil sowie deine Verbrauchsdaten einsehen:\n${createdInvite.fullUrl}\n\nViele Grüße,\n${tenant?.name || "Deine Gemeinschaft"}`
        );
        return `mailto:?subject=${subject}&body=${body}`;
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fade-in" onClick={onClose}>
            <div
                className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl w-full max-w-xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
                onClick={(e) => e.stopPropagation()}
            >
                {/* MODAL HEADER */}
                <div className="p-6 border-b border-slate-100 dark:border-slate-800/80 flex items-start justify-between bg-gradient-to-r from-slate-50 via-white to-slate-50 dark:from-slate-900 dark:via-slate-900 dark:to-slate-850">
                    <div className="flex items-start gap-3.5">
                        <div className="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-xl shrink-0 mt-0.5">
                            🤝
                        </div>
                        <div>
                            <h2 className="text-lg font-black text-slate-900 dark:text-white tracking-tight">
                                {t("tenant.invite_modal_title", "Mitglieder & Mieter einladen")}
                            </h2>
                            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                                {tenant?.name} • Sichere Einladung für Energy Sharing & Mieterstrom
                            </p>
                        </div>
                    </div>
                    <button
                        type="button"
                        onClick={onClose}
                        className="w-8 h-8 rounded-full flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition cursor-pointer"
                    >
                        ✕
                    </button>
                </div>

                {/* MODAL BODY */}
                <div className="p-6 overflow-y-auto space-y-5 flex-1">
                    {!createdInvite ? (
                        <>
                            <div>
                                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">
                                    {t("tenant.select_role_label", "1. Rolle & Berechtigung auswählen:")}
                                </label>
                                <div className="space-y-2.5">
                                    {ROLE_DEFINITIONS.map((r) => {
                                        const isSelected = selectedRole === r.key;
                                        return (
                                            <div
                                                key={r.key}
                                                onClick={() => setSelectedRole(r.key)}
                                                className={`p-3.5 rounded-2xl border transition-all cursor-pointer flex items-start gap-3 ${
                                                    isSelected
                                                        ? "border-emerald-500 bg-emerald-500/5 dark:bg-emerald-500/10 shadow-xs ring-1 ring-emerald-500"
                                                        : "border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 hover:border-slate-300 dark:hover:border-slate-700"
                                                }`}
                                            >
                                                <div className="text-2xl shrink-0 mt-0.5">{r.icon}</div>
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center justify-between gap-2">
                                                        <h4 className="text-xs font-bold text-slate-900 dark:text-white">
                                                            {r.title}
                                                        </h4>
                                                        <span
                                                            className={`text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full border shrink-0 ${r.badgeColor}`}
                                                        >
                                                            {r.badge}
                                                        </span>
                                                    </div>
                                                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
                                                        {r.description}
                                                    </p>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        </>
                    ) : (
                        /* SUCCESS STATE WITH GENERATED LINK */
                        <div className="space-y-5">
                            <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-start gap-3">
                                <span className="text-2xl shrink-0">✅</span>
                                <div>
                                    <h4 className="text-xs font-bold text-emerald-800 dark:text-emerald-300">
                                        Einladungslink erfolgreich erstellt!
                                    </h4>
                                    <p className="text-[11px] text-emerald-700 dark:text-emerald-400 mt-0.5">
                                        Rolle: <strong>{currentRoleObj.title}</strong>
                                    </p>
                                </div>
                            </div>

                            {/* LINK DISPLAY BOX */}
                            <div>
                                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5">
                                    Persönlicher Registrierungslink:
                                </label>
                                <div className="flex items-center gap-2 p-2 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 font-mono text-xs text-slate-800 dark:text-slate-200 break-all select-all">
                                    <span className="flex-1 truncate">{createdInvite.fullUrl}</span>
                                </div>
                            </div>

                            {/* ACTION BUTTONS (COPY, MAIL, QR) */}
                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                                <button
                                    type="button"
                                    onClick={() => handleCopy(createdInvite.fullUrl)}
                                    className={`py-2.5 px-3 rounded-xl text-xs font-bold border transition-all flex items-center justify-center gap-2 cursor-pointer shadow-xs ${
                                        copied
                                            ? "bg-emerald-600 text-white border-emerald-600"
                                            : "bg-slate-900 hover:bg-black dark:bg-white dark:hover:bg-slate-100 text-white dark:text-slate-900 border-transparent"
                                    }`}
                                >
                                    <span>{copied ? "✓" : "📋"}</span>
                                    <span>{copied ? "Kopiert!" : "Link kopieren"}</span>
                                </button>

                                <a
                                    href={getMailtoHref()}
                                    className="py-2.5 px-3 rounded-xl text-xs font-bold bg-white dark:bg-slate-800 hover:bg-sky-50 dark:hover:bg-sky-950/40 text-slate-700 dark:text-slate-200 hover:text-sky-600 dark:hover:text-sky-400 border border-slate-200 dark:border-slate-700 hover:border-sky-300 dark:hover:border-sky-800 transition-all flex items-center justify-center gap-2 shadow-xs cursor-pointer text-center"
                                >
                                    <span>✉️</span>
                                    <span>Per E-Mail</span>
                                </a>

                                <button
                                    type="button"
                                    onClick={() => setShowQr(!showQr)}
                                    className="py-2.5 px-3 rounded-xl text-xs font-bold bg-white dark:bg-slate-800 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 text-slate-700 dark:text-slate-200 hover:text-indigo-600 dark:hover:text-indigo-400 border border-slate-200 dark:border-slate-700 hover:border-indigo-300 dark:hover:border-indigo-800 transition-all flex items-center justify-center gap-2 shadow-xs cursor-pointer"
                                >
                                    <span>📱</span>
                                    <span>{showQr ? "QR verbergen" : "QR-Code"}</span>
                                </button>
                            </div>

                            {/* QR CODE DISPLAY BOX */}
                            {showQr && (
                                <div className="p-4 rounded-2xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex flex-col items-center justify-center text-center space-y-3 shadow-inner">
                                    <div className="p-3 bg-white rounded-xl shadow-xs border border-slate-100">
                                        <QRCodeSVG
                                            value={createdInvite.fullUrl}
                                            size={180}
                                            level="M"
                                            includeMargin={false}
                                        />
                                    </div>
                                    <div className="max-w-xs">
                                        <p className="text-xs font-bold text-slate-800 dark:text-slate-200">
                                            Aushang für Schwarzes Brett / Hausflur
                                        </p>
                                        <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                                            Nachbarn und Mieter können diesen Code direkt mit der Smartphone-Kamera scannen, um beizutreten.
                                        </p>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* MODAL FOOTER */}
                <div className="p-4 px-6 border-t border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-900/50 flex items-center justify-between gap-3">
                    {!createdInvite ? (
                        <>
                            <button
                                type="button"
                                onClick={onClose}
                                className="px-4 py-2 text-xs font-bold text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition cursor-pointer"
                            >
                                Abbrechen
                            </button>
                            <button
                                type="button"
                                disabled={loading}
                                onClick={handleCreate}
                                className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl transition shadow-xs flex items-center gap-2 cursor-pointer disabled:opacity-50"
                            >
                                <span>⚡</span>
                                <span>{loading ? "Erstelle Link..." : "Einladungslink generieren →"}</span>
                            </button>
                        </>
                    ) : (
                        <>
                            <button
                                type="button"
                                onClick={handleReset}
                                className="px-4 py-2 text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:underline transition cursor-pointer"
                            >
                                + Weiteren Link erstellen
                            </button>
                            <button
                                type="button"
                                onClick={onClose}
                                className="px-5 py-2.5 bg-slate-900 hover:bg-black dark:bg-slate-800 dark:hover:bg-slate-700 text-white text-xs font-bold rounded-xl transition cursor-pointer"
                            >
                                Fertig
                            </button>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
