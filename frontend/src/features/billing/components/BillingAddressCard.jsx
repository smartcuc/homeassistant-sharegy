import React, { useState, useEffect } from "react";
import Card from "../../../components/ui/Card";
import { apiFetch } from "../../../api/client";

export default function BillingAddressCard({ billingAddress, onSaveSuccess }) {
    const [formData, setFormData] = useState({
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
            setFormData({
                billing_name: billingAddress.billing_name || "",
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
            await apiFetch("/api/billing/subscription/update-address/", {
                method: "POST",
                body: JSON.stringify(formData),
            });
            setSaved(true);
            setTimeout(() => setSaved(false), 3000);
            if (onSaveSuccess) onSaveSuccess();
        } catch (err) {
            alert("Fehler beim Speichern der Rechnungsadresse.");
        } finally {
            setSaving(false);
        }
    };

    return (
        <Card>
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h3 className="font-bold text-gray-900 text-base flex items-center gap-2">
                        <span>🏢</span> Rechnungsadresse & Firmendaten
                    </h3>
                    <p className="text-xs text-gray-500 mt-0.5">
                        Wird für monatliche PDF-Rechnungen und Vorsteuerabzug verwendet.
                    </p>
                </div>

                {saved && (
                    <span className="flex items-center gap-1.5 text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-xl">
                        ✓ Gespeichert
                    </span>
                )}
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
                {/* Kundentyp Umschalter */}
                <div className="grid grid-cols-2 gap-3 p-1 bg-gray-100 rounded-xl border border-gray-200 max-w-sm">
                    <button
                        type="button"
                        onClick={() => setFormData({ ...formData, customer_type: "private" })}
                        className={`py-1.5 px-3 rounded-lg text-xs font-bold flex items-center justify-center gap-2 transition ${
                            formData.customer_type === "private" ? "bg-white text-gray-900 shadow-xs" : "text-gray-500"
                        }`}
                    >
                        👤 Privatkunde
                    </button>
                    <button
                        type="button"
                        onClick={() => setFormData({ ...formData, customer_type: "business" })}
                        className={`py-1.5 px-3 rounded-lg text-xs font-bold flex items-center justify-center gap-2 transition ${
                            formData.customer_type === "business" ? "bg-white text-indigo-900 shadow-xs" : "text-gray-500"
                        }`}
                    >
                        🏢 Geschäftskunde
                    </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase mb-1">Rechnungsempfänger / Name</label>
                        <input
                            type="text"
                            value={formData.billing_name}
                            onChange={(e) => setFormData({ ...formData, billing_name: e.target.value })}
                            placeholder="z. B. Max Mustermann"
                            className="w-full border rounded-xl px-3 py-2 text-sm bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                        />
                    </div>

                    {formData.customer_type === "business" && (
                        <>
                            <div>
                                <label className="block text-xs font-bold text-gray-700 uppercase mb-1">Firmenname</label>
                                <input
                                    type="text"
                                    value={formData.company_name}
                                    onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                                    placeholder="z. B. SolarInvest GmbH"
                                    className="w-full border rounded-xl px-3 py-2 text-sm bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                                />
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-gray-700 uppercase mb-1">USt-IdNr. (VAT ID)</label>
                                <input
                                    type="text"
                                    value={formData.vat_id}
                                    onChange={(e) => setFormData({ ...formData, vat_id: e.target.value })}
                                    placeholder="z. B. DE123456789"
                                    className="w-full border rounded-xl px-3 py-2 text-sm bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                                />
                            </div>
                        </>
                    )}

                    <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase mb-1">Straße</label>
                        <input
                            type="text"
                            value={formData.street}
                            onChange={(e) => setFormData({ ...formData, street: e.target.value })}
                            placeholder="z. B. Sonnenallee"
                            className="w-full border rounded-xl px-3 py-2 text-sm bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                        />
                    </div>

                    <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase mb-1">Hausnummer</label>
                        <input
                            type="text"
                            value={formData.house_number}
                            onChange={(e) => setFormData({ ...formData, house_number: e.target.value })}
                            placeholder="z. B. 42a"
                            className="w-full border rounded-xl px-3 py-2 text-sm bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                        />
                    </div>

                    <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase mb-1">Postleitzahl</label>
                        <input
                            type="text"
                            value={formData.postal_code}
                            onChange={(e) => setFormData({ ...formData, postal_code: e.target.value })}
                            placeholder="z. B. 10115"
                            className="w-full border rounded-xl px-3 py-2 text-sm bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                        />
                    </div>

                    <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase mb-1">Stadt</label>
                        <input
                            type="text"
                            value={formData.city}
                            onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                            placeholder="z. B. Berlin"
                            className="w-full border rounded-xl px-3 py-2 text-sm bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                        />
                    </div>
                </div>

                <div className="flex justify-end pt-2">
                    <button
                        type="submit"
                        disabled={saving}
                        className="px-5 py-2.5 bg-gray-900 hover:bg-black text-white text-xs font-bold rounded-xl flex items-center gap-2 shadow-xs transition"
                    >
                        <span>💾</span>
                        <span>{saving ? "Wird gespeichert..." : "Rechnungsadresse speichern"}</span>
                    </button>
                </div>
            </form>
        </Card>
    );
}
