"use client";
import { motion } from "framer-motion";
import clsx from "clsx";

interface GlassPanelProps {
  children: React.ReactNode;
  className?: string;
  glow?: "purple" | "pink" | "blue" | "green";
  animate?: boolean;
  delay?: number;
}

export function GlassPanel({ children, className, glow, animate = false, delay = 0 }: GlassPanelProps) {
  const glowClass = glow ? `glow-${glow}` : "";
  const content = (
    <div className={clsx("glass p-6", glowClass, className)}>
      {children}
    </div>
  );

  if (animate) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay, ease: "easeOut" }}
      >
        {content}
      </motion.div>
    );
  }

  return content;
}
