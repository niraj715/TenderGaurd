/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#060B18',
          900: '#0B132B',
          800: '#1C2541',
          700: '#3A506B',
        },
        brand: {
          cyan: '#00F2FE',
          teal: '#06B6D4',
          blue: '#4FACFE',
          dark: '#0B132B'
        },
        risk: {
          critical: '#EF4444', // Red 90-100
          high: '#F97316',     // Orange 75-89
          medium: '#EAB308',   // Yellow 50-74
          low: '#10B981',      // Green 0-49
        }
      },
      backdropBlur: {
        xs: '2px',
      }
    },
  },
  plugins: [],
}
