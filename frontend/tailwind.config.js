/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        nyaya: {
          50: "#f4f1ff",
          100: "#ebe4ff",
          200: "#d9cbff",
          300: "#bda6ff",
          400: "#9c77ff",
          500: "#7d4bff",
          600: "#6a2df0",
          700: "#5920c9",
          800: "#491ca3",
          900: "#3e1b85",
          950: "#1c094f",
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "-apple-system", "sans-serif"],
      },
      boxShadow: {
        glow: "0 0 24px -6px rgba(125,75,255,0.45)",
      },
    },
  },
  plugins: [],
};
