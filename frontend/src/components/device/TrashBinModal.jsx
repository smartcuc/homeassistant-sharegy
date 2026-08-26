/*
# src/components/device/TrashBinModal.jsx
*/

import { useState, useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../../api/client";
import { useTranslation } from "react-i18next";

export default function TrashBinModal({
    open,
    onClose,
}) {
    const { t } = useTranslation();
    const queryClient = useQueryClient();

    const [selectedIds, setSelectedIds] = useState([]);

    const [page, setPage] = useState(1);

    useEffect(() => {

        if (!open) {
            return;
        }

        function handleKeyDown(event) {

            if (event.key === "Escape") {
                setPage(1);
                setSelectedIds([]);
                onClose();
            }
        }

        window.addEventListener("keydown", handleKeyDown);

        return () => {
            window.removeEventListener("keydown", handleKeyDown);
        };

    }, [open, onClose]);

    const trashQuery = useQuery({
        queryKey: ["device-trash"],
        queryFn: () => apiFetch("/api/devices/trash/"),
        enabled: open,
    });

    const devices = [...(trashQuery.data ?? [])].sort(
        (a, b) =>
            a.display_name.localeCompare(
                b.display_name,
                "de",
                { sensitivity: "base" }
            )
    );

    const PAGE_SIZE = 3;

    const pageCount = Math.max(
        1,
        Math.ceil(devices.length / PAGE_SIZE)
    );

    const safePage = Math.min(page, pageCount)

    const pagedDevices = devices.slice(
        (safePage - 1) * PAGE_SIZE,
        safePage * PAGE_SIZE
    );

    if (!open) {
        return null;
    }

    const allSelected =
        devices.length > 0 &&
        devices.every(d => selectedIds.includes(d.id));

    function toggleDevice(id) {

        setSelectedIds(prev =>
            prev.includes(id)
                ? prev.filter(x => x !== id)
                : [...prev, id]
        );
    }

    function toggleAll() {

        if (allSelected) {
            setSelectedIds([]);
            return;
        }

        setSelectedIds(
            devices.map(d => d.id)
        );
    }

    function closeModal() {

        setPage(1);
        setSelectedIds([]);
        onClose();
    }

    async function restoreSelected() {

        if (!selectedIds.length) {
            return;
        }

        try {

            await apiFetch("/api/devices/restore/", {
                method: "POST",
                body: JSON.stringify({
                    device_ids: selectedIds,
                }),
            });

            await Promise.all([
                queryClient.invalidateQueries({
                    queryKey: ["devices"],
                }),
                queryClient.invalidateQueries({
                    queryKey: ["device-trash"],
                }),
                queryClient.invalidateQueries({
                    queryKey: ["device-trash-count"],
                }),
                queryClient.invalidateQueries({
                    queryKey: ["unconfigured-devices"],
                }),
            ]);

            setSelectedIds([]);

            closeModal();

        } catch (err) {

            console.error(err);
            alert("Wiederherstellen fehlgeschlagen.");
        }
    }

    async function purgeSelected() {

        if (!selectedIds.length) {
            return;
        }

        const confirmed = window.confirm(
            t("device_trash.confirm_purge", "Ausgewählte Geräte endgültig löschen?")
        );

        if (!confirmed) {
            return;
        }

        try {

            await apiFetch("/api/devices/purge/", {
                method: "POST",
                body: JSON.stringify({
                    device_ids: selectedIds,
                }),
            });

            await Promise.all([
                queryClient.invalidateQueries({
                    queryKey: ["devices"],
                }),
                queryClient.invalidateQueries({
                    queryKey: ["device-trash"],
                }),
                queryClient.invalidateQueries({
                    queryKey: ["device-trash-count"],
                }),
            ]);

            setSelectedIds([]);

        } catch (err) {

            console.error(err);
            alert("Löschen fehlgeschlagen.");
        }
    }

    return (
        <div
            className="fixed inset-0 z-50 bg-black/30 flex items-center justify-center"
            onClick={closeModal}
        >
            <div
                className="
                    bg-white
                    rounded-2xl
                    shadow-xl
                    w-full
                    max-w-2xl
                    h-[80vh]
                    flex
                    flex-col
                    overflow-hidden
                "

                onClick={(e) => e.stopPropagation()}
            >

                {/* Header */}
                <div className="p-4 border-b bg-gradient-to-r from-amber-50 to-orange-50">
                    <div className="flex justify-between items-center">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center text-xl shadow-sm">
                                ♻️
                            </div>
                            <div>
                                <h2 className="font-semibold text-lg text-gray-900">
                                    {t("device_trash.title", "Papierkorb")}
                                </h2>
                                <div className="text-xs text-gray-500">
                                    {t("device_trash.subtitle", "Gelöschte Geräte wiederherstellen oder endgültig entfernen")}
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center gap-3">
                            <div
                                title={t("device_trash.info_tooltip", "Geräte bleiben 7 Tage im Papierkorb. Wenn Home Assistant, ioBroker oder MQTT weiterhin Daten senden, kann ein Gerät nach der endgültigen Löschung automatisch erneut erkannt werden.")}
                                className="w-8 h-8 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center cursor-help text-sm font-medium"
                            >
                                ℹ
                            </div>

                            <button
                                onClick={closeModal}
                                className="text-gray-400 hover:text-gray-600 text-lg"
                            >
                                ✕
                            </button>
                        </div>
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-4">
                    {trashQuery.isLoading ? (
                        <div>{t("common.loading", "Lade Papierkorb...")}</div>
                    ) : (
                        <>
                            <label className="flex items-center gap-2 mb-4 text-sm font-medium text-gray-700 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={allSelected}
                                    onChange={toggleAll}
                                />
                                {t("common.select_all", "Alle auswählen")}
                            </label>

                            <div className="space-y-2">
                                {devices.length === 0 && (
                                    <div className="p-6 text-center text-gray-500 border rounded-xl">
                                        {t("device_trash.empty", "Der Papierkorb ist leer")}
                                    </div>
                                )}

                                {pagedDevices.map(device => (
                                    <div
                                        key={device.id}
                                        className="border rounded-xl p-3 bg-white shadow-xs hover:shadow-md transition-all"
                                    >
                                        <div className="flex items-start gap-3">
                                            <input
                                                type="checkbox"
                                                checked={selectedIds.includes(device.id)}
                                                onChange={() => toggleDevice(device.id)}
                                                className="mt-1"
                                            />

                                            <div className="flex-1">
                                                <div className="flex items-start justify-between">
                                                    <div>
                                                        <div className="font-medium text-gray-900">
                                                            {device.display_name}
                                                        </div>
                                                        <div className="text-xs text-gray-500 font-mono">
                                                            {device.identifier}
                                                        </div>
                                                    </div>

                                                    <div className="px-2 py-0.5 text-xs rounded-full bg-amber-100 text-amber-800 font-medium">
                                                        ♻️ {t("nav.trash_bin", "Papierkorb")}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}

                                {pageCount > 1 && (
                                    <div className="flex justify-center items-center gap-3 pt-2">
                                        <button
                                            onClick={() => setPage(Math.max(1, safePage - 1))}
                                            disabled={safePage === 1}
                                            className="px-3 py-1 border rounded-lg bg-white disabled:opacity-40"
                                        >
                                            ←
                                        </button>

                                        <span className="text-xs text-gray-600">
                                            {t("common.page_of", { current: safePage, total: pageCount, defaultValue: `Seite ${safePage} von ${pageCount}` })}
                                        </span>

                                        <button
                                            onClick={() => setPage(Math.min(pageCount, safePage + 1))}
                                            disabled={safePage === pageCount}
                                            className="px-3 py-1 border rounded-lg bg-white disabled:opacity-40"
                                        >
                                            →
                                        </button>
                                    </div>
                                )}
                            </div>
                        </>
                    )}
                </div>

                {/* Footer */}
                <div className="border-t p-4 flex justify-between items-center bg-gray-50">
                    <div className="text-xs text-gray-500">
                        {t("common.items_selected", { count: selectedIds.length, defaultValue: `${selectedIds.length} ausgewählt` })}
                    </div>

                    <div className="flex gap-2">
                        <button
                            onClick={restoreSelected}
                            disabled={!selectedIds.length}
                            className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold shadow-xs disabled:bg-gray-300 transition"
                        >
                            {t("common.restore", "Wiederherstellen")}
                        </button>

                        <button
                            onClick={purgeSelected}
                            disabled={!selectedIds.length}
                            className="px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white text-sm font-semibold shadow-xs disabled:bg-gray-300 transition"
                        >
                            {t("common.delete_permanently", "Endgültig löschen")}
                        </button>
                    </div>
                </div>

            </div>

        </div>
    );
}
