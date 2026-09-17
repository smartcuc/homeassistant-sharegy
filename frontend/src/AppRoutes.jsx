/*
# src/AppRoutes.jsx
*/

import { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";

const TenantPageWrapper = lazy(() => import("./TenantPageWrapper"));
const LandingPage = lazy(() => import("./LandingPage"));
const Login = lazy(() => import("./pages/Login"));
const MagicLogin = lazy(() => import("./pages/MagicLogin"));
const ConfirmEmailChangePage = lazy(() => import("./pages/ConfirmEmailChangePage"));
const Join = lazy(() => import("./pages/Join"));
const CooperativeJoinPage = lazy(() => import("./features/community/pages/CooperativeJoinPage"));
const EnergyPage = lazy(() => import("./pages/EnergyPage"));
const Impressum = lazy(() => import("./pages/Impressum"));
const Datenschutz = lazy(() => import("./pages/Datenschutz"));
const Agb = lazy(() => import("./pages/Agb"));
const Widerruf = lazy(() => import("./pages/Widerruf"));

function RouteLoader() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-400">
            <div className="flex items-center gap-2">
                <div className="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
                <span>Sharegy lädt…</span>
            </div>
        </div>
    );
}

export default function AppRoutes() {
    return (
        <Suspense fallback={<RouteLoader />}>
            <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/demo" element={<LandingPage />} />
                <Route path="/preview-landing" element={<LandingPage />} />

                <Route path="/login" element={<Login />} />
                <Route path="/join" element={<Join />} />
                <Route path="/join/:slug" element={<CooperativeJoinPage />} />
                <Route path="/t/:token" element={<MagicLogin />} />
                <Route path="/magic-login" element={<MagicLogin />} />
                <Route path="/auth/magic/:token" element={<MagicLogin />} />
                <Route path="/confirm-email-change" element={<ConfirmEmailChangePage />} />

                <Route path="/impressum" element={<Impressum />} />
                <Route path="/datenschutz" element={<Datenschutz />} />
                <Route path="/agb" element={<Agb />} />
                <Route path="/widerruf" element={<Widerruf />} />

                <Route
                    path="/tenant/:tenantSlug/:pageSlug"
                    element={<TenantPageWrapper />}
                />

                <Route
                    path="/tenant/:tenantSlug"
                    element={<TenantPageWrapper defaultPage="home" />}
                />

                <Route
                    path="/tenant/:tenantSlug/energy"
                    element={<EnergyPage />}
                />
            </Routes>
        </Suspense>
    );
}
