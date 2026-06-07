"use client";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

interface AnimatedBarChartProps {
  data: { name: string; value: number }[];
  height?: number;
}

const COLORS = ["#7c3aed", "#ec4899", "#3b82f6", "#10b981", "#f59e0b"];

export function AnimatedBarChart({ data, height = 300 }: AnimatedBarChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
        <XAxis dataKey="name" stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 11 }} />
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
        <Bar dataKey="value" radius={[8, 8, 0, 0]} animationDuration={1000}>
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} fillOpacity={0.8} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
