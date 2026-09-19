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
        background: '#070B18',
        surface: {
          DEFAULT: '#10182B',
          light: '#18233C',
          border: 'rgba(255, 255, 255, 0.08)',
          card: 'rgba(16, 24, 43, 0.75)',
        },
        brand: {
          violet: '#8B5CF6',
          cyan: '#22D3EE',
          blue: '#3B82F6',
        },
        sentiment: {
          positive: '#34D399',
          negative: '#FB7185',
          warning: '#FBBF24',
          neutral: '#94A3B8',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 12s linear infinite',
      },
      backdropBlur: {
        xs: '2px',
      }
    },
  },
  plugins: [],
}
