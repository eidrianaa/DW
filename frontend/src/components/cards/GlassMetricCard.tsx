"use client";
import { motion } from "framer-motion";
import clsx from "clsx";

interface GlassMetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  glow?: "purple" | "pink" | "blue" | "green";
  delay?: number;
}

export function GlassMetricCard({ title, value, change, glow = "purple", delay = 0 }: GlassMetricCardProps) {
  const glowClass = `glow-${glow}`;
  const colorMap = {
    purple: "from-accent-purple to-accent-pink",
    pink: "from-accent-pink to-accent-purple",
    blue: "from-accent-blue to-accent-purple",
    green: "from-accent-green to-accent-blue",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: "easeOut" }}
      className={clsx("glass p-6 animate-float", glowClass)}
      style={{ animationDelay: `${delay * 1000}ms` }}
    >
      <p className="text-xs uppercase tracking-wider text-[var(--text-secondary)] mb-2">{title}</p>
      <p className={clsx("text-3xl font-bold bg-gradient-to-r bg-clip-text text-transparent", colorMap[glow])}>
        {value}
      </p>
      {change && (
        <p className={clsx("text-xs mt-2", change.startsWith("+") ? "text-accent-green" : "text-accent-red")}>
          {change}
        </p>
      )}
    </motion.div>
  );
}
