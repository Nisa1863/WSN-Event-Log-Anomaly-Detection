/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        wsn: {
          primary: '#3b82f6',
          secondary: '#64748b',
          light: '#f1f5f9',
          dark: '#1e293b',
        },
      },
    },
  },
  plugins: [],
}
