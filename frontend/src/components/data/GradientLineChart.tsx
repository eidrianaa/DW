"use client";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface GradientLineChartProps {
  data: { date: string; value: number }[];
  height?: number;
  color?: string;
}

export function GradientLineChart({ data, height = 300, color = "#7c3aed" }: GradientLineChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data}>
        <defs>
          <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#7c3aed" />
            <stop offset="100%" stopColor="#ec4899" />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
        <XAxis dataKey="date" stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 11 }} />
        <YAxis stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 11 }} />
        <Tooltip
          contentStyle={{
            background: "rgba(15, 12, 41, 0.9)",
            border: "1px solid rgba(255,255,255,0.15)",
            borderRadius: "12px",
            backdropFilter: "blur(16px)",
            color: "#f0f0f0",
          }}
        />
        <Line
          type="monotone"
          dataKey="value"
          stroke="url(#lineGradient)"
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 4, fill: "#7c3aed" }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
