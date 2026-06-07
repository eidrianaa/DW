"use client";
import { LineChart, Line, ResponsiveContainer } from "recharts";

interface SparklineWidgetProps {
  data: number[];
  color?: string;
  height?: number;
}

export function SparklineWidget({ data, color = "#7c3aed", height = 40 }: SparklineWidgetProps) {
  const chartData = data.map((value, index) => ({ index, value }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={chartData}>
        <Line
          type="monotone"
          dataKey="value"
          stroke={color}
          strokeWidth={1.5}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
