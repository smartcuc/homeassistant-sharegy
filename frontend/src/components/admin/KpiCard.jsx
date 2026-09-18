/*
# src/components/admin/KpiCard.jsx
*/

export function KpiCard({ title, value, icon, subtitle }) {
    return (
        <div className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 p-5 rounded-3xl shadow-xs transition-all hover:border-indigo-300 dark:hover:border-indigo-700">
            <div className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider flex items-center justify-between">
                <span>{title}</span>
                {icon && <span className="text-base">{icon}</span>}
            </div>
            <div className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white mt-2">
                {value ?? 0}
            </div>
            {subtitle && (
                <div className="text-[11px] text-slate-400 dark:text-slate-500 mt-1 font-medium">
                    {subtitle}
                </div>
            )}
        </div>
    );
}

export default KpiCard;
