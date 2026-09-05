/*
# src/features/energy/components/EnergyKpis.jsx
*/

export default function EnergyKpis({ devices }) {

    let pv = 0;
    let consumption = 0;

    Object.values(devices).forEach(d => {
        if (!d.power) return;

        if (d.power > 0) pv += d.power;
        else consumption += Math.abs(d.power);
    });

    return (
        <div className="grid grid-cols-3 gap-4">
            <Card title="PV" value={pv} color="text-yellow-400" />
            <Card title="Verbrauch" value={consumption} color="text-red-400" />
        </div>
    );
}

function Card({ title, value, color }) {
    return (
        <div className="bg-slate-900 p-5 rounded-xl shadow">
            <div className={`text-sm ${color}`}>{title}</div>
            <div className="text-xl sm:text-2xl text-white font-bold truncate max-w-full">
                {value.toFixed(0)} W
            </div>
        </div>
    );
}
