"use client";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface GradientAreaChartProps {
  data: { date: string; value: number }[];
  height?: number;
}

export function GradientAreaChart({ data, height = 300 }: GradientAreaChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#7c3aed" stopOpacity={0.3} />
            <stop offset="100%" stopColor="#7c3aed" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="areaStroke" x1="0" y1="0" x2="1" y2="0">
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
        <Area
          type="monotone"
          dataKey="value"
          stroke="url(#areaStroke)"
          fill="url(#areaFill)"
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
