import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        glass: {
          bg: "rgba(255, 255, 255, 0.08)",
          border: "rgba(255, 255, 255, 0.15)",
        },
        accent: {
          purple: "#7c3aed",
          pink: "#ec4899",
          blue: "#3b82f6",
          green: "#10b981",
          red: "#ef4444",
        },
      },
      fontFamily: {
        sans: ["Plus Jakarta Sans", "sans-serif"],
      },
      backdropBlur: {
        glass: "16px",
        "glass-strong": "24px",
      },
      animation: {
        "float": "float 6s ease-in-out infinite",
        "glow-pulse": "glow-pulse 2s ease-in-out infinite alternate",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
        "glow-pulse": {
          "0%": { boxShadow: "0 0 20px rgba(124, 58, 237, 0.2)" },
          "100%": { boxShadow: "0 0 40px rgba(124, 58, 237, 0.4)" },
        },
      },
    },
  },
  plugins: [],
};
export default config;
