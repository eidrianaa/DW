"use client";
import Link from "next/link";
import { motion } from "framer-motion";

interface AssetGlassCardProps {
  assetId: string;
  name: string;
  type?: string;
  delay?: number;
}

export function AssetGlassCard({ assetId, name, type, delay = 0 }: AssetGlassCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: "easeOut" }}
    >
      <Link href={`/assets/${encodeURIComponent(assetId)}`}>
        <div className="glass p-5 hover:bg-white/10 transition-all duration-300 cursor-pointer group hover:glow-purple">
          <p className="text-sm gradient-text font-semibold truncate">{assetId}</p>
          <p className="text-white text-lg font-medium mt-1">{name || assetId.split("/").pop()}</p>
          {type && (
            <span className="inline-block mt-2 text-xs px-3 py-1 rounded-full bg-accent-purple/20 text-accent-purple border border-accent-purple/30">
              {type}
            </span>
          )}
          <div className="mt-3 h-8 w-full rounded bg-white/5 overflow-hidden">
            <div className="h-full bg-gradient-to-r from-accent-purple/30 to-accent-pink/30 rounded animate-pulse" style={{ width: `${Math.random() * 60 + 40}%` }} />
          </div>
        </div>
      </Link>
    </motion.div>
  );
}
