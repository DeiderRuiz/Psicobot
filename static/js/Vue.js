const { createApp, ref, onMounted } = Vue
createApp({
  delimiters: ['[[', ']]'], // Cambia los delimitadores de interpolación de {{ }} a [[ ]]
  setup() {
    let perfil = ref(false);
    let ventana = ref(false);
    const currentRoute = ref(window.location.pathname);
    console.log(currentRoute.value);
    let url = currentRoute.value;
    console.log(url);
    onMounted(() => {
      document.getElementById('chat').addEventListener('keydown', function(e) {
        if (e.key == 'Enter' && !e.shiftKey) {
          e.preventDefault();
          document.forms[0].submit();
        }
      });
      var chatDiv = document.getElementById('chatDiv');
      chatDiv.scrollTop = chatDiv.scrollHeight;
    });
    const showModal = (day) => {
      ventana.value = day; // Establece el día del modal que se está abriendo
    };

    const closeModal = () => {
      ventana.value = null; // Cierra el modal estableciendo ventana a null
    };
    return {
      perfil,
      ventana,
      currentRoute,
      url,
      showModal,
      closeModal,
    }
  }
}).mount('#app')

/* const { createApp, ref, onMounted } = Vue
createApp({
  delimiters: ['[[', ']]'], // Cambia los delimitadores de interpolación a [[ ]]
  setup() {
    const message = ref('Hello vue!')
    const date = ref(new Date());
    const currentMonth = ref(date.value.getMonth());
    const currentYear = ref(date.value.getFullYear());
    const displayedMonth = ref('');
    let diasContainer, nextDay, prevDay, mes;

    onMounted(() => {
      diasContainer = document.querySelector("#dias");
      nextDay = document.querySelector("#next");
      prevDay = document.querySelector("#prev");
      mes = document.querySelector("#mes");
      renderCalendar();
    });

    const meses = [
      "Enero",
      "Febrero",
      "Marzo",
      "Abril",
      "Mayo",
      "Junio",
      "Julio",
      "Agosto",
      "Septiembre",
      "Octubre",
      "Noviembre",
      "Diciembre",
    ];
    const dias = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"];
    //Obtaner mes pasado actual y siguiente
    function renderCalendar() {
      date.value.setDate(1);
      const firstDay = new Date(currentYear.value, currentMonth.value, 1);
      const lastDay = new Date(currentYear.value, currentMonth.value + 1, 0);
      const lastDayIndex = lastDay.getDay();
      const lastDayDate = lastDay.getDate();
      const prevLastDay = new Date(currentYear.value, currentMonth.value, 0);
      const prevLastDayDate = prevLastDay.getDate();
      const nextDays = 7 - lastDayIndex -1;

      //Actualizar mes en header
      displayedMonth.value = `${meses[currentMonth.value]} ${currentYear.value}`

      //Actualizar dias html
      let dias = "";

      // Dias pervios html
      for (let x = firstDay.getDay(); x > 0; x--) {
        dias += `<div class="flex items-center justify-center w-full"><p class="bg-gray-100 hover:bg-verde-paris text-gray-500 rounded-md w-10">${prevLastDayDate - x + 1}</p></div>`;
      }

      // dias del mes actual
      for (let i = 1; i <= lastDayDate; i++) {
        if (
          i === new Date().getDate() &&
          currentMonth.value === new Date().getMonth() &&
          currentYear.value === new Date().getFullYear()
        ) {
          // Si la fecha coincide con la de hoy
          dias += `<div class="flex items-center justify-center w-full"><p class="bg-verde-uajs text-white hover:bg-verde-paris rounded-md w-10">${i}</p></div>`;
        } else {
          //sino
          dias += `<div class="flex items-center justify-center w-full"><p class="bg-gray-200 hover:bg-verde-paris rounded-md w-10">${i}</p></div>`;
        }
      }
       // next MOnth days
      for (let j = 1; j <= nextDays; j++) {
        dias += `<div class="flex items-center justify-center w-full"><p class="bg-gray-100 hover:bg-verde-paris text-gray-500 rounded-md w-10">${j}</p></div>`;
      }

      diasContainer.innerHTML = dias;
    }

    console.log(message.value)
    console.log(meses)
    console.log(dias)
    console.log(date.value, currentMonth.value, currentYear.value);
    return {
      message,
      meses,
      dias,
      date,
      currentMonth,
      currentYear,
      displayedMonth,
      renderCalendar,
    }
  }
}).mount('#app')
 */