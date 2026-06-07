"use client";

interface GlassInputProps {
  label?: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: string;
  className?: string;
}

export function GlassInput({ label, value, onChange, placeholder, type = "text", className }: GlassInputProps) {
  return (
    <div className={className}>
      {label && (
        <label className="block text-xs text-[var(--text-secondary)] mb-1 uppercase tracking-wider">{label}</label>
      )}
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full glass px-4 py-2.5 text-sm text-white bg-transparent border border-white/10 rounded-xl
                   placeholder-gray-500 focus:outline-none focus:border-accent-purple focus:glow-purple transition-all"
      />
    </div>
  );
}
