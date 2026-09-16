import { NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useUserNavigation } from "../../hooks/useUserNavigation";
import { NAV_MODES } from "../../config/navigationConfig";
import { Home, Zap, Sliders, Car, Building2, FileText, Wrench, Shield, Menu } from "lucide-react";
import { useMemo } from "react";

export default function MobileBottomNav({ onOpenMenu }) {
    const { t } = useTranslation();
    const { activeMode } = useUserNavigation();

    const triggerHaptic = () => {
        if (window.navigator?.vibrate) {
            window.navigator.vibrate(10);
        }
    };

    const navItems = useMemo(() => {
        // 🏢 User 2: Nur Energy-Sharing / Mieter
        if (activeMode === NAV_MODES.SHARING_ONLY) {
            return [
                {
                    name: t("nav.community", "Community"),
                    path: "/app/tenant",
                    icon: Building2,
                },
                {
                    name: t("energy.energy_balance", "Energie"),
                    path: "/app/energy",
                    icon: Zap,
                },
                {
                    name: t("nav.billing", "Belege"),
                    path: "/app/billing",
                    icon: FileText,
                },
            ];
        }

        // 🔧 Partner / Installateur
        if (activeMode === NAV_MODES.PARTNER) {
            return [
                {
                    name: t("nav.partner_fleet", "Flotte"),
                    path: "/app/partner",
                    icon: Wrench,
                },
                {
                    name: t("nav.devices", "Geräte"),
                    path: "/app/devices",
                    icon: Sliders,
                },
                {
                    name: t("nav.system_status", "Status"),
                    path: "/app/status",
                    icon: Zap,
                },
            ];
        }

        // 🛡️ Admin
        if (activeMode === NAV_MODES.ADMIN) {
            return [
                {
                    name: t("nav.admin_dashboard", "Admin"),
                    path: "/app/admin/dashboard",
                    icon: Shield,
                },
                {
                    name: t("nav.tenant_management", "Mandanten"),
                    path: "/app/tenant",
                    icon: Building2,
                },
                {
                    name: t("nav.partner_fleet", "Flotte"),
                    path: "/app/partner",
                    icon: Wrench,
                },
            ];
        }

        // 🏠 User 1 (EMS) & User 3 (Hybrid)
        return [
            {
                name: t("nav.dashboard", "Home"),
                path: "/app/dashboard",
                icon: Home,
            },
            {
                name: t("energy.energy_balance", "Energie"),
                path: "/app/energy",
                icon: Zap,
            },
            {
                name: t("nav.energy_control", "Steuerung"),
                path: "/app/control",
                icon: Sliders,
            },
            {
                name: t("nav.mobility", "Mobilität"),
                path: "/app/mobility",
                icon: Car,
            },
        ];
    }, [activeMode, t]);

    return (
        <nav className="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border-t border-slate-200 dark:border-slate-800 px-2 py-1 flex items-center justify-around shadow-lg transition-colors">
            {navItems.map((item) => {
                const Icon = item.icon;
                return (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        onClick={triggerHaptic}
                        className={({ isActive }) =>
                            `flex flex-col items-center justify-center py-1.5 px-3 rounded-2xl transition-all cursor-pointer min-w-[60px] ${
                                isActive
                                    ? "text-indigo-600 dark:text-indigo-400 font-bold scale-105"
                                    : "text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                            }`
                        }
                    >
                        <Icon className="w-5 h-5 mb-0.5" />
                        <span className="text-[10px] tracking-tight">{item.name}</span>
                    </NavLink>
                );
            })}

            {/* Menu Button to trigger Drawer */}
            <button
                type="button"
                onClick={() => {
                    triggerHaptic();
                    if (onOpenMenu) onOpenMenu();
                }}
                className="flex flex-col items-center justify-center py-1.5 px-3 rounded-2xl text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all cursor-pointer min-w-[60px]"
            >
                <Menu className="w-5 h-5 mb-0.5" />
                <span className="text-[10px] tracking-tight">{t("common.menu", "Menü")}</span>
            </button>
        </nav>
    );
}
