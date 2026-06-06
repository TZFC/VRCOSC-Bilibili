/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        unity: {
          dark: '#282828',
          panel: '#383838',
          light: '#3e3e42',
          accent: '#007acc',
          text: '#d4d4d4'
        }
      }
    },
  },
  plugins: [],
}