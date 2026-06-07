"use client";

interface GlassDatePickerProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
}

export function GlassDatePicker({ label, value, onChange }: GlassDatePickerProps) {
  return (
    <div>
      <label className="block text-xs text-[var(--text-secondary)] mb-1 uppercase tracking-wider">{label}</label>
      <input
        type="date"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full glass px-4 py-2.5 text-sm text-white bg-transparent border border-white/10 rounded-xl
                   focus:outline-none focus:border-accent-purple focus:glow-purple transition-all
                   [color-scheme:dark]"
      />
    </div>
  );
}
