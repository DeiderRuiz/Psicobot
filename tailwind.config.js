/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/*.html", "./templates/auth/*.html"],
  theme: {
    extend: {
        fontFamily: {
            'bree-serif': ['Bree Serif', 'serif'],
        },
        colors: {
            'verde-uajs': '#21A454',
            'verde-paris': '#50C878',
            'verde-slavia': '#4BA89C',
            'verde-cali': '#00A651',
            'heaven': '#02A0E7',
            'heaven2': '#30D5C8',
        },
        width: {
        '1/7': '14.2857143%',
        },
        backgroundImage: theme => ({
            'uajs': "url('/static/assets/images/bgUAJS.png')",
            'ruta': "url('/static/assets/images/ruta.png')",
            'chatbot': "url('/static/assets/images/chatbot.png')",
            'user': "url('/static/assets/images/usuario.png')",
            'logo': "url('/static/assets/images/UAJS.png')",
        })
    },
  },
  plugins: [],
}