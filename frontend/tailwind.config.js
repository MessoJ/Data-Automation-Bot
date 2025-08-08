/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#16a085',
          dark: '#0e806a',
          foreground: '#e6fffa',
          muted: '#195e55'
        },
      },
    },
  },
  plugins: [],
}

