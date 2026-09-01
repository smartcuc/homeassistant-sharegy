import { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import { useFunnel } from "../../hooks/useFunnel";

export function FunnelChart() {
    const { data, isLoading } = useFunnel();

    const validData = Array.isArray(data) ? data : [];

    const option = useMemo(() => {
        if (validData.length === 0) return null;

        return {
            tooltip: {
                trigger: "axis",
            },

            grid: {
                top: 20,
                left: 40,
                right: 20,
                bottom: 40,
            },

            xAxis: {
                type: "category",
                data: validData.map(item => item?.label || ""),
            },

            yAxis: {
                type: "value",
            },

            series: [
                {
                    type: "bar",
                    data: validData.map(item => item?.count || 0),
                    itemStyle: {
                        color: "#8884d8",
                    },
                },
            ],
        };
    }, [validData]);

    if (isLoading) {
        return <div className="p-4 text-xs text-gray-400">Lade Funnel-Daten...</div>;
    }

    if (validData.length === 0 || !option) {
        return <div className="p-4 text-xs text-gray-400">Keine Trichterdaten verfügbar</div>;
    }

    return (
        <ReactECharts
            option={option}
            style={{
                width: "500px",
                height: "300px",
            }}
            notMerge={true}
            lazyUpdate={true}
        />
    );
}


