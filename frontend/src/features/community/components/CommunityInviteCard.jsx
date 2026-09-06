import { useState } from "react";
import { useTranslation } from "react-i18next";

export default function CommunityInviteCard({ onOpenShareModal, kpis = {} }) {
    const { t } = useTranslation();
    const [copied, setCopied] = useState(false);

    const inviteToken = "solar-community";
    const appUrl = window.location.origin || "https://sharegy.de";
    const inviteUrl = `${appUrl}/join?ref=${inviteToken}`;

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(inviteUrl);
            setCopied(true);
            setTimeout(() => setCopied(false), 3000);
        } catch (e) {
            // fallback
        }
    };

    return (
        <div className="bg-gradient-to-r from-emerald-950/40 via-slate-900/80 to-amber-950/30 backdrop-blur-xl border border-emerald-500/30 rounded-2xl p-5 shadow-xl relative overflow-hidden flex flex-col md:flex-row md:items-center justify-between gap-4">
            {/* Background Glow */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>

            <div className="flex items-start gap-3.5 max-w-xl">
                <div className="p-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-2xl shrink-0 mt-0.5">
                    🤝
                </div>
                <div>
                    <div className="flex items-center gap-2">
                        <h4 className="text-sm font-bold text-white tracking-tight">
                            {t("community.sharing_title", "Quartiers-Energy Sharing (§ 42b EnWG)")}
                        </h4>
                        <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                            {t("community.badge", "Community")}
                        </span>
                    </div>
                    <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                        {t("community.sharing_desc", "Teile deinen überschüssigen Solarstrom mit Nachbarn oder Mietern und spare gemeinsam teure Netzgebühren durch automatisiertes 15-Minuten-Clearing.")}
                    </p>
                </div>
            </div>

            <div className="flex flex-wrap items-center gap-2.5 shrink-0">
                <button
                    type="button"
                    onClick={handleCopy}
                    className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-800/90 hover:bg-slate-750 text-slate-200 border border-slate-700 transition-all flex items-center gap-1.5"
                >
                    <span>{copied ? "✓" : "📋"}</span>
                    <span>{copied ? t("common.copied", "Link kopiert") : t("community.invite_link", "Invite-Link")}</span>
                </button>

                <button
                    type="button"
                    onClick={onOpenShareModal}
                    className="px-4 py-2 rounded-xl text-xs font-bold bg-emerald-500 hover:bg-emerald-400 text-slate-950 transition-all shadow-lg shadow-emerald-500/25 flex items-center gap-1.5 hover:scale-[1.02] active:scale-[0.98]"
                >
                    <span>📢</span>
                    <span>{t("community.share_and_invite", "Erfolge teilen & einladen")}</span>
                </button>
            </div>
        </div>
    );
}
