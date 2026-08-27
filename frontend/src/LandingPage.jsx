/*
# src/pages/LandingPage.jsx
*/

import { useEffect, useState } from "react";
import { useUser } from "./hooks/useUser";
import { useNavigate } from "react-router-dom";

import Header from "./components/Header";
import EnergyFlow from "./components/EnergyFlow";
import Footer from "./components/Footer";

import { trackEvent } from "./lib/track";

export default function LandingPage() {

    const { user, loading } = useUser();
    const navigate = useNavigate();

    const [variant] = useState(() => (Math.random() > 0.5 ? "A" : "B"));

    useEffect(() => {
        document.title = "Sharegy – Dein Energy OS";
        trackEvent("landing_view", { variant });
    }, [variant]);


    const handleStart = () => {
        trackEvent("cta_click", {
            location: "hero_primary",
            variant
        });

        navigate("/login");
    };

    if (loading) {
        return <div className="p-6">Loading...</div>;
    }

    return (
        <div className="min-h-screen bg-gray-50">

            <Header user={user} />

            {/* 🔥 HERO */}
            <section className="relative bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white py-28 text-center px-6 overflow-hidden">

                <div className="absolute inset-0 bg-white/5 blur-3xl opacity-30" />

                <h1 className="text-5xl font-bold mb-6 leading-tight relative z-10">
                    {
                        variant === "A"
                            ? "Dein Strom kostet dich zu viel – obwohl genug da ist"
                            : "Du nutzt deine Energie nicht optimal – Sharegy ändert das"
                    }
                </h1>

                <p className="max-w-2xl mx-auto text-lg opacity-90 relative z-10">
                    Verstehe, wohin dein Strom geht, optimiere automatisch
                    und teile Energie lokal mit deiner Community – alles in einer Plattform.
                </p>

                <div className="mt-8 flex justify-center gap-4 flex-wrap relative z-10">

                    {/* LIVE VIEW */}
                    <button
                        onClick={() => {
                            trackEvent("cta_click", {
                                location: "hero_secondary",
                                variant
                            });

                            document
                                .getElementById("energy-flow")
                                ?.scrollIntoView({ behavior: "smooth" });
                        }}
                        className="bg-black/30 backdrop-blur px-6 py-3 rounded-lg hover:scale-105 transition"
                    >
                        Live ansehen
                    </button>

                    {/* MAIN CTA */}
                    <button
                        onClick={handleStart}
                        className="border border-white px-6 py-3 rounded-lg hover:scale-105 transition"
                    >
                        Jetzt kostenlos starten →
                    </button>

                </div>

                <div className="mt-6 text-sm opacity-80">
                    Kein Setup · Kein Risiko · Funktioniert sofort
                </div>

            </section>

            {/* TRUST */}
            <section className="mt-10 text-center px-6">

                <div className="text-sm text-gray-500">
                    Für Haushalte & Energie-Communities entwickelt
                </div>

                <div className="flex justify-center gap-8 mt-4 text-gray-400 text-sm">
                    <span>⚡ PV & Smart Meter</span>
                    <span>🏘️ Communities</span>
                    <span>🔌 Energy Sharing</span>
                </div>

            </section>

            {/* CORE */}
            <section className="mt-16 text-center px-6">

                <h2 className="text-2xl font-semibold mb-4 text-indigo-600">
                    Ein System für deine Energie
                </h2>

                <p className="text-gray-500 max-w-xl mx-auto">
                    Verstehen, steuern und teilen – alles an einem Ort.
                </p>

            </section>

            {/* SPLIT */}
            <section className="mt-12 max-w-6xl mx-auto grid md:grid-cols-2 gap-8 px-6">

                <div className="bg-white p-8 rounded-2xl shadow">
                    <h3 className="text-lg font-semibold mb-4 text-indigo-600">
                        ⚡ Für dein Zuhause
                    </h3>

                    <ul className="space-y-2 text-sm text-gray-600">
                        <li>✅ Live-Verbrauch</li>
                        <li>✅ Produktion sichtbar</li>
                        <li>✅ Kosten reduzieren</li>
                    </ul>
                </div>

                <div className="bg-white p-8 rounded-2xl shadow">
                    <h3 className="text-lg font-semibold mb-4 text-orange-500">
                        🤝 Für deine Community
                    </h3>

                    <ul className="space-y-2 text-sm text-gray-600">
                        <li>✅ Energie teilen</li>
                        <li>✅ Fair abrechnen</li>
                        <li>✅ Gemeinsam sparen</li>
                    </ul>
                </div>

            </section>

            {/* ENERGY FLOW */}
            <section id="energy-flow" className="mt-20 px-6 text-center">
                <EnergyFlow mode="demo" />
            </section>

            <Footer />

        </div>
    );
}