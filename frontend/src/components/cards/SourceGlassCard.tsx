"use client";
import Link from "next/link";
import { motion } from "framer-motion";

interface SourceGlassCardProps {
  sourceId: string;
  name?: string;
  delay?: number;
}

export function SourceGlassCard({ sourceId, name, delay = 0 }: SourceGlassCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: "easeOut" }}
    >
      <Link href={`/data-sources/${encodeURIComponent(sourceId)}`}>
        <div className="glass p-5 hover:bg-white/10 transition-all duration-300 cursor-pointer group hover:glow-blue">
          <div className="w-10 h-10 rounded-xl bg-accent-blue/20 flex items-center justify-center mb-3">
            <svg className="w-5 h-5 text-accent-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
            </svg>
          </div>
          <p className="text-white font-semibold">{name || sourceId}</p>
          <p className="text-xs text-[var(--text-secondary)] mt-1">{sourceId}</p>
        </div>
      </Link>
    </motion.div>
  );
}
