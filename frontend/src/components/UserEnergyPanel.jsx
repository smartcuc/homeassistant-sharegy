/*
# src/components/UserEnergyPanel.jsx
*/

import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

export default function UserEnergyPanel() {
    const { t } = useTranslation();
    const [power, setPower] = useState(0);

    useEffect(() => {
        // ✅ automatisch richtig für http/https
        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        const host = window.location.host;

        const socket = new WebSocket(`${protocol}://${host}/ws/energy`);

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setPower(data.power);
        };

        socket.onerror = (err) => {
            console.error("WS error:", err);
        };

        socket.onclose = () => {
            console.log("WS closed");
        };

        return () => socket.close();
    }, []);

    return (
        <div style={{ padding: "2rem" }}>
            <h3>{t("energy_kpis.current_consumption", "Dein aktueller Verbrauch")}</h3>
            <div style={{ fontSize: "2rem" }}>{power} W</div>
        </div>
    );
}