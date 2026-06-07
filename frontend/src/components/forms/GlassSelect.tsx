"use client";

interface GlassSelectProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: { value: string; label: string }[];
  placeholder?: string;
}

export function GlassSelect({ label, value, onChange, options, placeholder }: GlassSelectProps) {
  return (
    <div>
      <label className="block text-xs text-[var(--text-secondary)] mb-1 uppercase tracking-wider">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full glass px-4 py-2.5 text-sm text-white bg-transparent border border-white/10 rounded-xl
                   focus:outline-none focus:border-accent-purple focus:glow-purple transition-all
                   appearance-none cursor-pointer [color-scheme:dark]"
        style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23a0a0b8'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'/%3E%3C/svg%3E")`, backgroundPosition: 'right 12px center', backgroundSize: '16px', backgroundRepeat: 'no-repeat' }}
      >
        {placeholder && <option value="">{placeholder}</option>}
        {options.map((opt) => (
          <option key={opt.value} value={opt.value} className="bg-[#1a1a2e]">{opt.label}</option>
        ))}
      </select>
    </div>
  );
}
