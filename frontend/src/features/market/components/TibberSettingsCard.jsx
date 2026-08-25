/*
# src/features/market/components/TibberSettingsCard.jsx
*/

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Card from "../../../components/ui/Card";
import Button from "../../../components/ui/Button";
import { fetchHomeTariff, saveHomeTariff, fetchTibberHomes } from "../api";
import { useTranslation } from "react-i18next";

export default function TibberSettingsCard() {
    const { t } = useTranslation();
    const queryClient = useQueryClient();

    const { data: tariffData, isLoading } = useQuery({
        queryKey: ["home-tariff"],
        queryFn: fetchHomeTariff,
    });

    const [token, setToken] = useState(null);
    const [homeId, setHomeId] = useState(null);
    const [tibberHomes, setTibberHomes] = useState([]);
    const [fetchingHomes, setFetchingHomes] = useState(false);
    const [statusMsg, setStatusMsg] = useState(null);

    const currentToken = token ?? (tariffData?.tibber_token || "");
    const currentHomeId = homeId ?? (tariffData?.tibber_home_id || "");
    const isConnected = tariffData?.tibber_connected;

    const saveMutation = useMutation({
        mutationFn: saveHomeTariff,
        onSuccess: (updatedData) => {
            queryClient.setQueryData(["home-tariff"], updatedData);
            queryClient.invalidateQueries({ queryKey: ["home-tariff"] });
            setToken(null);
            setHomeId(null);
            setStatusMsg({ type: "success", text: t("tariffs.save_tibber_success", "Tibber-Zugangsdaten erfolgreich gespeichert!") });
            setTimeout(() => setStatusMsg(null), 4000);
        },
        onError: (err) => {
            setStatusMsg({ type: "error", text: err?.data?.detail || err?.detail || err?.message || t("tariffs.save_tibber_error", "Fehler beim Speichern.") });
            setTimeout(() => setStatusMsg(null), 5000);
        },
    });

    async function handleFetchHomes() {
        if (!currentToken) {
            setStatusMsg({ type: "error", text: t("tariffs.enter_token", "Bitte zuerst ein Tibber-API-Token eingeben.") });
            return;
        }
        setFetchingHomes(true);
        setStatusMsg(null);
        try {
            const res = await fetchTibberHomes(currentToken);
            if (res.homes && res.homes.length > 0) {
                setTibberHomes(res.homes);
                if (!currentHomeId) {
                    setHomeId(res.homes[0].id);
                }
                setStatusMsg({ type: "success", text: `${res.homes.length} ${t("tariffs.homes_found", "Tibber-Zuhause erfolgreich gefunden!")}` });
            } else {
                setStatusMsg({ type: "error", text: t("tariffs.no_homes_found", "Keine Tibber-Zuhause mit diesem Token gefunden.") });
            }
        } catch (err) {
            setStatusMsg({ type: "error", text: err?.detail || err?.message || t("tariffs.connect_error", "Fehler bei der Tibber-Verbindung.") });
        } finally {
            setFetchingHomes(false);
        }
    }

    function handleSave(e) {
        e.preventDefault();
        saveMutation.mutate({
            tibber_token: currentToken,
            tibber_home_id: currentHomeId,
        });
    }

    if (isLoading) {
        return (
            <Card>
                <div className="p-4 text-sm text-gray-400 animate-pulse">
                    {t("tariffs.loading_tibber", "Lade Tibber-Integration…")}
                </div>
            </Card>
        );
    }

    return (
        <Card>
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <span className="text-2xl">🔌</span>
                    <div>
                        <h2 className="font-semibold text-gray-900 text-base">
                            {t("tariffs.tibber_title", "Tibber API & Smart Meter Integration")}
                        </h2>
                        <p className="text-xs text-gray-500 mt-0.5">
                            {t("tariffs.tibber_desc", "Verbinde deinen Tibber-Account für automatische Zählerdaten und stundengenaue Tarifsynchronisation.")}
                        </p>
                    </div>
                </div>

                <span
                    className={`text-xs px-2.5 py-1 rounded-full font-medium ${isConnected
                            ? "bg-emerald-100 text-emerald-800"
                            : "bg-gray-100 text-gray-600"
                        }`}
                >
                    {isConnected ? `🟢 ${t("common.connected", "Verbunden")}` : `⚪ ${t("common.not_configured", "Nicht konfiguriert")}`}
                </span>
            </div>

            <form onSubmit={handleSave} className="space-y-4">
                {/* TOKEN */}
                <div>
                    <div className="flex items-center justify-between mb-1">
                        <label htmlFor="tibber_token" className="text-xs font-medium text-gray-700">
                            Personal Access Token:
                        </label>
                        <a
                            href="https://developer.tibber.com/settings/accessToken"
                            target="_blank"
                            rel="noreferrer"
                            className="text-xs text-emerald-600 hover:text-emerald-700 underline"
                        >
                            {t("tariffs.create_token_link", "Token erstellen auf developer.tibber.com ↗")}
                        </a>
                    </div>
                    <div className="flex gap-2">
                        <input
                            type="password"
                            id="tibber_token"
                            value={currentToken}
                            onChange={(e) => setToken(e.target.value)}
                            placeholder="z. B. 5KNB-abc123xyz..."
                            className="flex-1 px-3 py-2 text-sm rounded-lg border border-gray-300 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 font-mono"
                        />
                        <button
                            type="button"
                            onClick={handleFetchHomes}
                            disabled={fetchingHomes || !currentToken}
                            className="px-3 py-2 text-xs font-medium bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-lg border border-gray-300 disabled:opacity-50 transition-colors whitespace-nowrap"
                        >
                            {fetchingHomes ? `⏳ ${t("common.loading", "Prüfe…")}` : `🔍 ${t("tariffs.load_homes", "Homes laden")}`}
                        </button>
                    </div>
                </div>

                {/* TIBBER HOMES DROPDOWN */}
                {tibberHomes.length > 0 && (
                    <div className="p-3 bg-emerald-50/60 rounded-lg border border-emerald-200">
                        <label htmlFor="tibber_home_select" className="block text-xs font-medium text-gray-700 mb-1">
                            {t("tariffs.select_home", "Gefundenes Tibber-Zuhause auswählen:")}
                        </label>
                        <select
                            id="tibber_home_select"
                            value={currentHomeId}
                            onChange={(e) => setHomeId(e.target.value)}
                            className="w-full px-3 py-1.5 text-sm rounded-lg border border-emerald-300 bg-white focus:ring-2 focus:ring-emerald-500"
                        >
                            {tibberHomes.map((h) => (
                                <option key={h.id} value={h.id}>
                                    {h.name} {h.address ? `(${h.address})` : ""} — {h.id}
                                </option>
                            ))}
                        </select>
                    </div>
                )}

                {/* HOME ID INPUT */}
                <div>
                    <label htmlFor="tibber_home_id" className="block text-xs font-medium text-gray-700 mb-1">
                        Tibber Home ID:
                    </label>
                    <input
                        type="text"
                        id="tibber_home_id"
                        value={currentHomeId}
                        onChange={(e) => setHomeId(e.target.value)}
                        placeholder="z. B. 96a14971-525a-4420-a9ce-..."
                        className="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 font-mono text-xs"
                    />
                </div>

                {/* STATUS MESSAGE */}
                {statusMsg && (
                    <div
                        className={`p-3 rounded-lg text-xs font-medium ${statusMsg.type === "success"
                                ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                                : "bg-red-50 text-red-800 border border-red-200"
                            }`}
                    >
                        {statusMsg.text}
                    </div>
                )}

                {/* SUBMIT */}
                <div className="pt-2 flex justify-end">
                    <Button type="submit" variant="primary" onClick={handleSave}>
                        {saveMutation.isPending ? t("common.saving", "Speichern…") : t("tariffs.save_tibber", "Tibber-Daten speichern")}
                    </Button>
                </div>
            </form>
        </Card>
    );
}
