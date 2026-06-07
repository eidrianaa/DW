// ─── Canonical frontend types ───
// All API response types live in api.ts. These are UI-level domain types.

export interface Asset {
  id: string;
  name: string;
  description: string;
  attributes: Record<string, string>;
}

export interface DataSource {
  id: string;
  name: string;
  description: string;
  attributes: string[];
}

export interface MetricCard {
  title: string;
  value: string | number;
  change?: string;
  glow: "purple" | "pink" | "blue" | "green";
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "error";
  content: string;
  timestamp: Date;
}

export interface NavItem {
  label: string;
  href: string;
  icon: string;
}

export interface SelectOption {
  value: string;
  label: string;
}
