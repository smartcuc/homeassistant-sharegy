import useModalDismiss from "../../../hooks/useModalDismiss";
import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../../api/client";
import {
  Palette,
  Globe,
  Upload,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  X,
  Sparkles,
  Eye,
  Building,
  Mail,
  ExternalLink,
  ShieldCheck,
  Zap
} from "lucide-react";
import { useTenantTheming } from "../../../context/TenantThemingContext";

const PRESET_THEMES = [
  {
    name: "Azure Cloud (Standard)",
    primary: "#0284c7",
    secondary: "#0f172a",
    accent: "#38bdf8",
    button: "#0284c7",
  },
  {
    name: "Clean Emerald (Green Energy)",
    primary: "#059669",
    secondary: "#064e3b",
    accent: "#34d399",
    button: "#059669",
  },
  {
    name: "Solar Amber (PV Pro)",
    primary: "#d97706",
    secondary: "#1c1917",
    accent: "#fbbf24",
    button: "#d97706",
  },
  {
    name: "Royal Indigo (Stadtwerke)",
    primary: "#4f46e5",
    secondary: "#1e1b4b",
    accent: "#818cf8",
    button: "#4f46e5",
  },
];

export default function WhitelabelSettingsModal({ isOpen, onClose }) {
  const { t } = useTranslation();
  useModalDismiss(isOpen, onClose);
  const { theming, updatePreviewTheme, reloadTheming } = useTenantTheming();

  const [formData, setFormData] = useState({
    company_legal_name: "",
    support_email: "",
    custom_domain: "",
    primary_color: "#0284c7",
    secondary_color: "#0f172a",
    accent_color: "#38bdf8",
    button_color: "#0284c7",
    logo_url: "",
    favicon_url: "",
    is_whitelabel_active: false,
  });

  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    if (theming && isOpen) {
      setFormData({
        company_legal_name: theming.companyLegalName || "",
        support_email: theming.supportEmail || "",
        custom_domain: theming.customDomain || "",
        primary_color: theming.primaryColor || "#0284c7",
        secondary_color: theming.secondaryColor || "#0f172a",
        accent_color: theming.accentColor || "#38bdf8",
        button_color: theming.buttonColor || "#0284c7",
        logo_url: theming.logoUrl || "",
        favicon_url: theming.faviconUrl || "",
        is_whitelabel_active: theming.isWhitelabelActive || false,
      });
    }
  }, [theming, isOpen]);

  if (!isOpen) return null;

  const handleColorChange = (key, value) => {
    const updated = { ...formData, [key]: value };
    setFormData(updated);
    updatePreviewTheme({
      primaryColor: updated.primary_color,
      secondaryColor: updated.secondary_color,
      accentColor: updated.accent_color,
      buttonColor: updated.button_color,
      companyLegalName: updated.company_legal_name,
      supportEmail: updated.support_email,
      logoUrl: updated.logo_url,
    });
  };

  const applyPreset = (preset) => {
    const updated = {
      ...formData,
      primary_color: preset.primary,
      secondary_color: preset.secondary,
      accent_color: preset.accent,
      button_color: preset.button,
    };
    setFormData(updated);
    updatePreviewTheme({
      primaryColor: preset.primary,
      secondaryColor: preset.secondary,
      accentColor: preset.accent,
      buttonColor: preset.button,
    });
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      setSaving(true);
      setErrorMsg(null);
      setSuccessMsg(null);
      await apiFetch("/api/core/tenant/theming/", {
        method: "PATCH",
        body: JSON.stringify(formData),
      });
      setSuccessMsg(t("whitelabel.success_msg", "Branding & Whitelabel-Einstellungen erfolgreich gespeichert!"));
      await reloadTheming();
    } catch (err) {
      setErrorMsg(err?.message || t("whitelabel.error_msg", "Speichern fehlgeschlagen."));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/75 backdrop-blur-md animate-fade-in" onClick={onClose}>
      <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden" onClick={(e) => e.stopPropagation()}>
        
        {/* Header (Fixed) */}
        <div className="p-6 md:p-8 pb-4 border-b border-slate-800 shrink-0 flex justify-between items-start">
          <div className="space-y-1">
            <div className="flex items-center gap-2.5">
              <div className="p-2 bg-sky-500/10 border border-sky-500/30 rounded-xl text-sky-400">
                <Palette className="w-5 h-5" />
              </div>
              <h2 className="text-xl md:text-2xl font-bold text-white">
                {t("whitelabel.modal_title", "B2B Whitelabel & Dynamic Theming Engine")}
              </h2>
            </div>
            <p className="text-xs md:text-sm text-slate-400">
              {t("whitelabel.modal_subtitle", "Passen Sie Farben, Logos, Firmennamen und Custom-Domains für Ihre EVU-, WEG- oder Stadtwerke-Kunden an.")}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSave} className="flex-1 flex flex-col overflow-hidden">
          
          {/* Scrollable Form Body */}
          <div className="p-6 md:p-8 overflow-y-auto space-y-6 flex-1">
            {errorMsg && (
              <div className="p-3.5 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            {successMsg && (
              <div className="p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                <span>{successMsg}</span>
              </div>
            )}
          
          {/* Preset Palettes */}
          <div className="space-y-2">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              {t("whitelabel.presets_title", "Schnell-Farbprofile")}
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
              {PRESET_THEMES.map((p) => (
                <button
                  key={p.name}
                  type="button"
                  onClick={() => applyPreset(p)}
                  className="p-2.5 rounded-xl border border-slate-800 bg-slate-950/60 hover:border-slate-700 text-left transition flex items-center gap-2.5 cursor-pointer"
                >
                  <div className="flex -space-x-1.5">
                    <span className="w-4 h-4 rounded-full border border-slate-900" style={{ backgroundColor: p.primary }} />
                    <span className="w-4 h-4 rounded-full border border-slate-900" style={{ backgroundColor: p.accent }} />
                  </div>
                  <span className="text-xs font-medium text-slate-300 truncate">{p.name.split(" ")[0]}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Left Column: Theme Details */}
            <div className="space-y-4">
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                {t("whitelabel.branding_section", "Markenauftritt & Corporate Design")}
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">{t("whitelabel.company_name", "Unternehmensname (EVU / Stadtwerk)")}</label>
                <div className="relative">
                  <Building className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type="text"
                    value={formData.company_legal_name}
                    onChange={(e) => setFormData({ ...formData, company_legal_name: e.target.value })}
                    placeholder="z.B. Stadtwerke Sonnenstadt GmbH"
                    className="w-full bg-slate-950 border border-slate-800 pl-9 pr-3.5 py-2 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">{t("whitelabel.support_email", "Support E-Mail-Adresse")}</label>
                <div className="relative">
                  <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type="email"
                    value={formData.support_email}
                    onChange={(e) => setFormData({ ...formData, support_email: e.target.value })}
                    placeholder="kundenservice@stadtwerke-sonnenstadt.de"
                    className="w-full bg-slate-950 border border-slate-800 pl-9 pr-3.5 py-2 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">{t("whitelabel.primary_color", "Primärfarbe")}</label>
                  <div className="flex items-center gap-2 bg-slate-950 border border-slate-800 p-1.5 rounded-xl">
                    <input
                      type="color"
                      value={formData.primary_color}
                      onChange={(e) => handleColorChange("primary_color", e.target.value)}
                      className="w-7 h-7 rounded-lg cursor-pointer bg-transparent border-0"
                    />
                    <span className="text-xs font-mono text-slate-300">{formData.primary_color}</span>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">{t("whitelabel.accent_color", "Akzentfarbe")}</label>
                  <div className="flex items-center gap-2 bg-slate-950 border border-slate-800 p-1.5 rounded-xl">
                    <input
                      type="color"
                      value={formData.accent_color}
                      onChange={(e) => handleColorChange("accent_color", e.target.value)}
                      className="w-7 h-7 rounded-lg cursor-pointer bg-transparent border-0"
                    />
                    <span className="text-xs font-mono text-slate-300">{formData.accent_color}</span>
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">{t("whitelabel.logo_url", "Logo URL (SVG / PNG)")}</label>
                <input
                  type="url"
                  value={formData.logo_url}
                  onChange={(e) => handleColorChange("logo_url", e.target.value)}
                  placeholder="https://cdn.ihredomain.de/logo.svg"
                  className="w-full bg-slate-950 border border-slate-800 px-3.5 py-2 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">{t("whitelabel.domain_cname", "Eigene Subdomain / Domain (CNAME)")}</label>
                <div className="relative">
                  <Globe className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type="text"
                    value={formData.custom_domain}
                    onChange={(e) => setFormData({ ...formData, custom_domain: e.target.value })}
                    placeholder="portal.stadtwerke-sonnenstadt.de"
                    className="w-full bg-slate-950 border border-slate-800 pl-9 pr-3.5 py-2 rounded-xl text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                  />
                </div>
                <p className="text-[11px] text-slate-500 mt-1">
                  {t("whitelabel.cname_hint", "Setzen Sie bei Ihrem DNS-Provider einen CNAME-Eintrag auf")} <span className="font-mono text-sky-400">cname.sharegy.de</span>.
                </p>
              </div>

              <div className="flex items-center justify-between p-3.5 bg-slate-950 border border-slate-800 rounded-2xl">
                <div>
                  <div className="text-xs font-semibold text-slate-200">{t("whitelabel.enable_mode", "Whitelabel-Modus aktivieren")}</div>
                  <div className="text-[11px] text-slate-400">{t("whitelabel.hide_branding", "Sharegy-Branding in Kopf- & Fußzeile ausblenden")}</div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.is_whitelabel_active}
                    onChange={(e) => setFormData({ ...formData, is_whitelabel_active: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-sky-500"></div>
                </label>
              </div>
            </div>

            {/* Right Column: Live Card Preview */}
            <div className="space-y-4">
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                {t("whitelabel.preview_title", "Live-Vorschau")}
              </div>

              <div className="p-5 rounded-2xl border border-slate-800 bg-slate-950/80 space-y-4">
                {/* Header Preview */}
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    {formData.logo_url ? (
                      <img src={formData.logo_url} alt="Logo" className="h-6 max-w-[120px] object-contain" />
                    ) : (
                      <div className="flex items-center gap-1.5 font-bold text-sm text-white">
                        <span style={{ color: formData.primary_color }}>⚡</span>
                        <span>{formData.company_legal_name || "Stadtwerke Sonnenstadt"}</span>
                      </div>
                    )}
                  </div>
                  <span
                    className="text-[10px] font-bold px-2 py-0.5 rounded-full text-white"
                    style={{ backgroundColor: formData.accent_color }}
                  >
                    PRO Live
                  </span>
                </div>

                {/* Card Preview */}
                <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-xl space-y-3">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400">{t("whitelabel.preview_ggv_title", "Gemeinschaftliche Gebäudeversorgung")}</span>
                    <span className="text-emerald-400 font-semibold">{t("whitelabel.preview_badge", "GGV")}</span>
                  </div>
                  <div className="text-xl font-extrabold text-white">4.820 kWh</div>
                  <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-300"
                      style={{ width: "72%", backgroundColor: formData.primary_color }}
                    />
                  </div>
                  <button
                    type="button"
                    className="w-full py-2 rounded-lg text-xs font-semibold text-white shadow transition"
                    style={{ backgroundColor: formData.button_color }}
                  >
                    {t("whitelabel.preview_btn_billing", "Monatsabrechnung einsehen")}
                  </button>
                </div>

                <div className="text-[11px] text-slate-500 text-center">
                  {t("whitelabel.support_label", "Support:")} {formData.support_email || "support@sharegy.de"}
                </div>
              </div>
            </div>

          </div>
          </div>

          {/* Footer Actions (Fixed at bottom) */}
          <div className="p-4 md:p-6 border-t border-slate-800 shrink-0 flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium rounded-xl transition cursor-pointer"
            >
              {t("common.cancel", "Abbrechen")}
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex items-center gap-2 px-6 py-2.5 bg-sky-500 hover:bg-sky-400 text-white text-sm font-semibold rounded-xl shadow-lg shadow-sky-500/25 transition cursor-pointer"
            >
              {saving && <RefreshCw className="w-4 h-4 animate-spin" />}
              <span>{t("whitelabel.save_branding", "Branding übernehmen")}</span>
            </button>
          </div>

        </form>

      </div>
    </div>
  );
}
