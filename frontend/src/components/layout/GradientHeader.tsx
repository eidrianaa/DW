"use client";

interface GradientHeaderProps {
  title: string;
  subtitle?: string;
}

export function GradientHeader({ title, subtitle }: GradientHeaderProps) {
  return (
    <header className="mb-8">
      <h1 className="text-3xl font-bold gradient-text">{title}</h1>
      {subtitle && (
        <p className="mt-2 text-[var(--text-secondary)] text-sm">{subtitle}</p>
      )}
      <div className="mt-3 h-[2px] w-24 bg-gradient-to-r from-accent-purple to-accent-pink rounded-full" />
    </header>
  );
}
