/*
# src/components/ui/KPISparklineECharts.jsx
*/

import { memo, useMemo } from "react";

function KPISparklineECharts({
    values = [],
    color = "#2563eb",
    unit = "N/A",
}) {
    const rawValues = Array.isArray(values) ? values : [];
    const validNumbers = useMemo(() => {
        return rawValues
            .map((v) => (typeof v === "number" ? v : parseFloat(v)))
            .filter((v) => !isNaN(v));
    }, [rawValues]);

    const chartValues = useMemo(() => {
        if (validNumbers.length === 0) return [];
        if (validNumbers.length === 1) return [validNumbers[0], validNumbers[0]];
        return validNumbers;
    }, [validNumbers]);

    if (chartValues.length === 0) {
        return (
            <div className="h-10 mt-1 flex items-center justify-center text-xs text-slate-300">
                —
            </div>
        );
    }

    const min = Math.min(...chartValues);
    const max = Math.max(...chartValues);
    const range = max - min || 1;

    const width = 240;
    const height = 44;
    const padding = 3;

    const points = chartValues.map((val, idx) => {
        const x = padding + (idx / (chartValues.length - 1)) * (width - 2 * padding);
        const y = height - padding - ((val - min) / range) * (height - 2 * padding);
        return [x, y];
    });

    // Erzeuge glatte Bezier-Kurve
    const pathD = points.reduce((acc, [x, y], idx, arr) => {
        if (idx === 0) return `M ${x} ${y}`;
        const [prevX, prevY] = arr[idx - 1];
        const midX = (prevX + x) / 2;
        return `${acc} C ${midX} ${prevY}, ${midX} ${y}, ${x} ${y}`;
    }, "");

    const lastX = points[points.length - 1][0];
    const firstX = points[0][0];
    const areaD = `${pathD} L ${lastX} ${height} L ${firstX} ${height} Z`;

    const gradientId = `spark-grad-${color.replace("#", "")}`;

    return (
        <div className="h-11 mt-1 w-full overflow-hidden">
            <svg
                viewBox={`0 0 ${width} ${height}`}
                className="w-full h-full"
                preserveAspectRatio="none"
            >
                <defs>
                    <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor={color} stopOpacity="0.28" />
                        <stop offset="90%" stopColor={color} stopOpacity="0.02" />
                        <stop offset="100%" stopColor={color} stopOpacity="0.0" />
                    </linearGradient>
                </defs>
                <path d={areaD} fill={`url(#${gradientId})`} />
                <path
                    d={pathD}
                    fill="none"
                    stroke={color}
                    strokeWidth="2.2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                />
            </svg>
        </div>
    );
}

export default memo(KPISparklineECharts);

