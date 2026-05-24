import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { useT } from "../i18n";
import { colorFor, formatNumber, type ChartData } from "../lib/transform";

interface TrendChartProps {
  chart: ChartData;
}

export function TrendChart({ chart }: TrendChartProps) {
  const t = useT();
  return (
    <div className="chart-frame">
      <ResponsiveContainer width="100%" height={420}>
        <LineChart data={chart.data} margin={{ top: 16, right: 24, bottom: 8, left: 12 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f2f4f7" />
          <XAxis dataKey="year" stroke="#667085" fontSize={12} />
          <YAxis
            stroke="#667085"
            fontSize={12}
            width={72}
            tickFormatter={(value: number) => formatNumber(value)}
          />
          <Tooltip
            formatter={(value) => formatNumber(Number(value ?? 0))}
            labelFormatter={(label) => `${t("chart.year")} ${String(label)}`}
          />
          <Legend />
          {chart.categories.map((category) => (
            <Line
              key={category}
              type="monotone"
              dataKey={category}
              stroke={colorFor(category)}
              strokeWidth={2.5}
              dot={false}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
