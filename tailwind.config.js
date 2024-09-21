/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/*.html", "./templates/auth/*.html", "./templates/private/*.html"],
  theme: {
    extend: {
        fontFamily: {
            'bree-serif': ['Bree Serif', 'serif'],
        },
        colors: {
            'verde-uajs': '#21A454',
            'verde-uajs-dark': '#016738',
            'verde-paris': '#50C878',
            'splavia': '#4BA89C',
            'splavia-light': '#7BC1B4',
            'splavia-dark': '#007461',
            'gris-perla': '#cdcecf',
            'gris-antracita': '#293133',
            'gris-marengo': '#5b5d74',
            'plata': '#e3e4e5',
        },
        backgroundImage: theme => ({
            'uajs': "url('/static/assets/images/bgUAJS.png')",
            'ruta': "url('/static/assets/images/ruta.png')",
            'chatbot': "url('/static/assets/images/chatbot.png')",
            'user': "url('/static/assets/images/usuario.png')",
            'logo': "url('/static/assets/images/UAJS.png')",
            'patrones': "url(\"data:image/svg+xml,%3Csvg width='52' height='26' viewBox='0 0 52 26' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23cdcecf' fill-opacity='0.5'%3E%3Cpath d='M10 10c0-2.21-1.79-4-4-4-3.314 0-6-2.686-6-6h2c0 2.21 1.79 4 4 4 3.314 0 6 2.686 6 6 0 2.21 1.79 4 4 4 3.314 0 6 2.686 6 6 0 2.21 1.79 4 4 4v2c-3.314 0-6-2.686-6-6 0-2.21-1.79-4-4-4-3.314 0-6-2.686-6-6zm25.464-1.95l8.486 8.486-1.414 1.414-8.486-8.486 1.414-1.414z' /%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
            'patrones-dark': "url(\"data:image/svg+xml,%3Csvg width='52' height='26' viewBox='0 0 52 26' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%235b5d74' fill-opacity='0.5'%3E%3Cpath d='M10 10c0-2.21-1.79-4-4-4-3.314 0-6-2.686-6-6h2c0 2.21 1.79 4 4 4 3.314 0 6 2.686 6 6 0 2.21 1.79 4 4 4 3.314 0 6 2.686 6 6 0 2.21 1.79 4 4 4v2c-3.314 0-6-2.686-6-6 0-2.21-1.79-4-4-4-3.314 0-6-2.686-6-6zm25.464-1.95l8.486 8.486-1.414 1.414-8.486-8.486 1.414-1.414z' /%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
        })
    },
  },
  plugins: [],
}