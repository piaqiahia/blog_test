/** @type {import('tailwindcss').Config} */
export default {
  content: ["./app/main/themes/zsff/**/*.{html,js}"],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: '#FF7D00',
        secondary: '#FF9F45',
        dark: {
          100: '#1E293B',
          200: '#0F172A',
          300: '#020617'
        },
        light: {
          100: '#F8FAFC',
          200: '#F1F5F9',
          300: '#E2E8F0'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'card-hover': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'card-dark': '0 4px 6px -1px rgba(255, 255, 255, 0.1), 0 2px 4px -1px rgba(255, 255, 255, 0.06)',
        'card-hover-dark': '0 10px 15px -3px rgba(255, 255, 255, 0.1), 0 4px 6px -2px rgba(255, 255, 255, 0.05)',
      }
    }
  },
  plugins: [],
}