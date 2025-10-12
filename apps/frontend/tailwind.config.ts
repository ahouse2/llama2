import type { Config } from "tailwindcss";
import { violet, indigoDark, mauveDark } from "@radix-ui/colors";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          primary: "#6366f1",
          secondary: "#a855f7",
          accent: "#22d3ee"
        },
        "mauve-dark": mauveDark,
        "indigo-dark": indigoDark,
        "violet-scale": violet
      },
      fontFamily: {
        display: ["Inter", "system-ui", "sans-serif"],
        sans: ["Inter", "system-ui", "sans-serif"]
      },
      boxShadow: {
        neon: "0 28px 80px -35px rgba(99,102,241,0.6)",
        "card-neon": "0 22px 48px -30px rgba(76,29,149,0.75)"
      }
    }
  },
  plugins: []
};

export default config;
