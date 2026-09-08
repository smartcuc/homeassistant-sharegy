import { NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Home, Zap, Sliders, Car, Menu } from "lucide-react";

export default function MobileBottomNav({ onOpenMenu }) {
    const { t } = useTranslation();

    const triggerHaptic = () => {
        if (window.navigator?.vibrate) {
            window.navigator.vibrate(10);
        }
    };

    const navItems = [
        {
            name: t("nav.dashboard", "Home"),
            path: "/app/dashboard",
            icon: Home,
            color: "text-indigo-600 dark:text-indigo-400",
        },
        {
            name: t("energy.energy_balance", "Energie"),
            path: "/app/energy",
            icon: Zap,
            color: "text-amber-500 dark:text-amber-400",
        },
        {
            name: t("nav.energy_control", "Steuerung"),
            path: "/app/control",
            icon: Sliders,
            color: "text-indigo-600 dark:text-indigo-400",
        },
        {
            name: t("nav.mobility", "Mobilität"),
            path: "/app/mobility",
            icon: Car,
            color: "text-cyan-600 dark:text-cyan-400",
        },
    ];

    return (
        <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border-t border-slate-200 dark:border-slate-800 px-2 py-1 flex items-center justify-around shadow-lg transition-colors">
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
