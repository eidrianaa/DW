"use client";
import { motion } from "framer-motion";

export function GlassLoader() {
  return (
    <div className="flex items-center justify-center py-12">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        className="w-10 h-10 rounded-full border-2 border-transparent border-t-accent-purple border-r-accent-pink"
      />
    </div>
  );
}
