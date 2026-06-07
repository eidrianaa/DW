"use client";
import { motion } from "framer-motion";

interface AnimatedDataTableProps {
  columns: string[];
  rows: Record<string, string | number>[];
}

export function AnimatedDataTable({ columns, rows }: AnimatedDataTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/10">
            {columns.map((col) => (
              <th key={col} className="text-left py-3 px-4 text-[var(--text-secondary)] font-medium uppercase text-xs tracking-wider">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <motion.tr
              key={i}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: i * 0.05 }}
              className="border-b border-white/5 hover:bg-white/5 transition-colors"
            >
              {columns.map((col) => (
                <td key={col} className="py-3 px-4 text-white">
                  {row[col] ?? "-"}
                </td>
              ))}
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
