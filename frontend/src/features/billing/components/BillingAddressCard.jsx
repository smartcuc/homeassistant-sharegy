import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import Card from "../../../components/ui/Card";
import { apiFetch } from "../../../api/client";

export default function BillingAddressCard({ billingAddress, onSaveSuccess }) {
    const { t } = useTranslation();
    const [formData, setFormData] = useState({
        first_name: "",
        last_name: "",
        billing_name: "",
        customer_type: "private",
        company_name: "",
        vat_id: "",
        street: "",
        house_number: "",
        postal_code: "",
        city: "",
        country: "DE",
    });

    const [saving, setSaving] = useState(false);
    const [saved, setSaved] = useState(false);

    useEffect(() => {
        if (billingAddress) {
            let fName = billingAddress.first_name || "";
            let lName = billingAddress.last_name || "";

            // Falls bisher Vor- & Nachname nicht getrennt hinterlegt waren:
            if (!fName && !lName && billingAddress.billing_name) {
                const parts = billingAddress.billing_name.trim().split(/\s+/);
                if (parts.length > 1) {
                    fName = parts.slice(0, -1).join(" ");
                    lName = parts[parts.length - 1];
                } else if (parts.length === 1 && !parts[0].includes("@")) {
                    fName = parts[0];
                }
            }

            // Sicherstellen, dass keine E-Mail-Adresse in den Namensfeldern landet
            if (fName.includes("@")) fName = "";
            if (lName.includes("@")) lName = "";

            setFormData({
                first_name: fName,
                last_name: lName,
                billing_name: billingAddress.billing_name && !billingAddress.billing_name.includes("@") ? billingAddress.billing_name : "",
                customer_type: billingAddress.customer_type || "private",
                company_name: billingAddress.company_name || "",
                vat_id: billingAddress.vat_id || "",
                street: billingAddress.street || "",
                house_number: billingAddress.house_number || "",
                postal_code: billingAddress.postal_code || "",
                city: billingAddress.city || "",
                country: billingAddress.country || "DE",
            });
        }
    }, [billingAddress]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        setSaved(false);
        try {
            const combinedName = `${formData.first_name || ""} ${formData.last_name || ""}`.trim();
            const payload = {
                ...formData,
                billing_name: combinedName || formData.company_name || "",
            };
            await apiFetch("/api/billing/subscription/update-address/", {
                method: "POST",
                body: JSON.stringify(payload),
            });
            setSaved(true);
            setTimeout(() => setSaved(false), 3000);
            if (onSaveSuccess) onSaveSuccess();
        } catch (err) {
            alert(t("billing.address_error", "Fehler beim Speichern der Rechnungsadresse."));
        } finally {
            setSaving(false);
        }
    };

    return (
        <Card>
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h3 className="font-bold text-gray-900 text-base flex items-center gap-2">
                        <span>🏢</span> {t("billing.address_title", "Rechnungsanschrift & Stammdaten")}
                    </h3>
                    <p className="text-xs text-gray-500 mt-0.5">
                        {t("billing.address_desc", "Wird für monatliche PDF-Rechnungen und Vorsteuerabzug verwendet.")}
                    </p>
                </div>

                {saved && (
                    <span className="flex items-center gap-1.5 text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-xl">
                        {t("billing.address_saved", "✓ Gespeichert")}
                    </span>
                )}
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
                {/* Kundentyp Umschalter */}
                <div className="grid grid-cols-2 gap-3 p-1 bg-gray-100 rounded-xl border border-gray-200 max-w-sm">
                    <button
                        type="button"
                        onClick={() => setFormData({ ...formData, customer_type: "private" })}
                        className={`py-1.5 px-3 rounded-lg text-xs font-bold flex items-center justify-center gap-2 transition ${formData.customer_type === "private" ? "bg-white text-gray-900 shadow-xs" : "text-gray-500"
                            }`}
                    >
                        {t("billing.private_customer", "👤 Privatkunde")}
                    </button>
                    <button
                        type="button"
                        onClick={() => setFormData({ ...formData, customer_type: "business" })}
                        className={`py-1.5 px-3 rounded-lg text-xs font-bold flex items-center justify-center gap-2 transition ${formData.customer_type === "business" ? "bg-white text-indigo-900 shadow-xs" : "text-gray-500"
                            }`}
                    >
                        {t("billing.business_customer", "🏢 Geschäftskunde")}
                    </button>
                </div>

                {/* 1. Vorname & Nachname */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase mb-1">
                            {t("billing.first_name", "Vorname")}
                        </label>
                        <input
                            type="text"
                            value={formData.first_name}
                            onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                            placeholder={t("billing.first_name_placeholder", "z. B. Max")}
                            className="w-full border border-gray-300 rounded-xl px-3 py-2 text-sm bg-white text-gray-900 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                        />
                    </div>

                    <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase mb-1">
                            {t("billing.last_name", "Nachname")}
                        </label>
                        <input
                            type="text"
                            value={formData.last_name}
                            onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                            placeholder={t("billing.last_name_placeholder", "z. B. Mustermann")}
                            className="w-full border border-gray-300 rounded-xl px-3 py-2 text-sm bg-white text-gray-900 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                        />
                    </div>
                </div>

                {/* Geschäftskunde Felder */}
                {formData.customer_type === "business" && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
                        <div>
                            <label className="block text-xs font-bold text-gray-700 uppercase mb-1">
                                {t("billing.company_label", "Firmenname")}
                            </label>
                            <input
                                type="text"
                                value={formData.company_name}
                                onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                                placeholder="z. B. SolarInvest GmbH"
                                className="w-full border border-gray-300 rounded-xl px-3 py-2 text-sm bg-white text-gray-900 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-bold text-gray-700 uppercase mb-1">
                                {t("billing.vat_label", "USt-IdNr. (VAT ID)")}
                            </label>
                            <input
                                type="text"
                                value={formData.vat_id}
                                onChange={(e) => setFormData({ ...formData, vat_id: e.target.value })}
                                placeholder="z. B. DE123456789"
                                className="w-full border border-gray-300 rounded-xl px-3 py-2 text-sm bg-white text-gray-900 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                            />
                        </div>
                    </div>
                )}

                {/* 2. Straße & Hausnummer */}
                <div className="grid grid-cols-3 sm:grid-cols-4 gap-4">
                    <div className="col-span-2 sm:col-span-3">
                        <label className="block text-xs font-bold text-gray-700 uppercase mb-1">
                            {t("billing.street_label", "Straße")}
                        </label>
                        <input
                            type="text"
                            value={formData.street}
                            onChange={(e) => setFormData({ ...formData, street: e.target.value })}
                            placeholder="z. B. Sonnenallee"
                            className="w-full border border-gray-300 rounded-xl px-3 py-2 text-sm bg-white text-gray-900 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                        />
                    </div>

                    <div className="col-span-1">
                        <label className="block text-xs font-bold text-gray-700 uppercase mb-1">
                            {t("billing.house_number", "Hausnr.")}
                        </label>
                        <input
                            type="text"
                            value={formData.house_number}
                            onChange={(e) => setFormData({ ...formData, house_number: e.target.value })}
                            placeholder="z. B. 42a"
                            className="w-full border border-gray-300 rounded-xl px-3 py-2 text-sm bg-white text-gray-900 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                        />
                    </div>
                </div>

                {/* 3. PLZ & Wohnort */}
                <div className="grid grid-cols-3 sm:grid-cols-4 gap-4">
                    <div className="col-span-1">
                        <label className="block text-xs font-bold text-gray-700 uppercase mb-1">
                            {t("billing.zip_label", "PLZ")}
                        </label>
                        <input
                            type="text"
                            value={formData.postal_code}
                            onChange={(e) => setFormData({ ...formData, postal_code: e.target.value })}
                            placeholder="z. B. 10115"
                            className="w-full border border-gray-300 rounded-xl px-3 py-2 text-sm bg-white text-gray-900 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                        />
                    </div>

                    <div className="col-span-2 sm:col-span-3">
                        <label className="block text-xs font-bold text-gray-700 uppercase mb-1">
                            {t("billing.city_label", "Wohnort / Stadt")}
                        </label>
                        <input
                            type="text"
                            value={formData.city}
                            onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                            placeholder="z. B. Berlin"
                            className="w-full border border-gray-300 rounded-xl px-3 py-2 text-sm bg-white text-gray-900 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                        />
                    </div>
                </div>

                <div className="flex justify-end pt-2">
                    <button
                        type="submit"
                        disabled={saving}
                        className="px-5 py-2.5 bg-gray-900 hover:bg-black text-white text-xs font-bold rounded-xl flex items-center gap-2 shadow-xs transition cursor-pointer"
                    >
                        <span>💾</span>
                        <span>{saving ? t("common.saving", "Wird gespeichert...") : t("billing.save_address", "Stammdaten speichern")}</span>
                    </button>
                </div>
            </form>
        </Card>
    );
}
