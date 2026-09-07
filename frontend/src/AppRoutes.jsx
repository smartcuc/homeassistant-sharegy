/*
# src/AppRoutes.jsx
*/

import { Routes, Route } from "react-router-dom";

import TenantPageWrapper from "./TenantPageWrapper";
import LandingPage from "./LandingPage";
import Login from "./pages/Login";
import MagicLogin from "./pages/MagicLogin";
import ConfirmEmailChangePage from "./pages/ConfirmEmailChangePage";
import Join from "./pages/Join";
import EnergyPage from "./pages/EnergyPage";
import Impressum from "./pages/Impressum";
import Datenschutz from "./pages/Datenschutz";
import Agb from "./pages/Agb";
import Widerruf from "./pages/Widerruf";

export default function AppRoutes() {
    return (
        <Routes>
            <Route path="/" element={<LandingPage />} />

            <Route path="/login" element={<Login />} />
            <Route path="/join" element={<Join />} />
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
    );
}
