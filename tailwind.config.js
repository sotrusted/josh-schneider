/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './**/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: { gold: '#b8965a' },
      fontFamily: {
        serif: ['Georgia', 'Times New Roman', 'serif'],
      },
    }
  },
  plugins: [],
}
