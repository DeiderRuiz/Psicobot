const { createApp, ref, onMounted, watch, nextTick } = Vue

createApp({
  delimiters: ['[[', ']]'], // Cambia los delimitadores de interpolación de {{ }} a [[ ]]
  setup() {
    const chatMessage = ref('');
    const conversacion = ref(JSON.parse(localStorage.getItem('conversacion') || '[]'));
    let ventana = ref(false);
    let lastChildId = ref('');
    let citas_opciones = ref(false);
    console.log(citas_opciones.value)
    const currentRoute = ref(window.location.pathname);
    let url = currentRoute.value;

    onMounted(() => {
      var chatDiv = document.getElementById('chatDiv');
      if (chatDiv) chatDiv.scrollTop = chatDiv.scrollHeight;
      const acciones = document.getElementById('acciones');
      if (acciones){
        const lastChildElement = acciones.lastElementChild;
        lastChildId.value = lastChildElement ? lastChildElement.id : '';
        console.log('ID del último hijo:', lastChildId);
      } else {
        console.error('No se encontró el div con el id "acciones".');
      }
    });

    watch(conversacion, (newConversacion) => {
      localStorage.setItem('conversacion', JSON.stringify(newConversacion));
      nextTick(() => {
        var chatDiv = document.getElementById('chatDiv');
        if (chatDiv) chatDiv.scrollTop = chatDiv.scrollHeight;
      });
    }, { deep: true });

    const mandarChat = async () => {
      if (chatMessage.value.trim() === '') return;
      const mensajeUsuario = { rol: 'usuario', mensaje: chatMessage.value };
      conversacion.value.push(mensajeUsuario);
      chatMessage.value = '';
      const textarea = document.getElementById('chat');
      if (textarea) {
        textarea.style.height = 'auto';
      }
      const mensajeTemporal = { rol: 'modelo', mensaje: 'Escribiendo...' };
      conversacion.value.push(mensajeTemporal);
      nextTick(() => {
        var chatDiv = document.getElementById('chatDiv');
        if (chatDiv) chatDiv.scrollTop = chatDiv.scrollHeight;
      });

      try {
        const response = await axios.post(url, { chat: mensajeUsuario.mensaje }, {
          headers: { 'Content-Type': 'application/json' }
        });
        if (response.data && response.data.length > 0) {
          const mensajeIA = response.data[response.data.length - 1];
          if (mensajeIA && mensajeIA.mensaje) {
            conversacion.value[conversacion.value.length - 1].mensaje = mensajeIA.mensaje;
            nextTick(() => {
              var chatDiv = document.getElementById('chatDiv');
              if (chatDiv) chatDiv.scrollTop = chatDiv.scrollHeight;
            });
          } else {
            throw new Error('La respuesta no contiene el mensaje esperado');
          }
        } else {
          throw new Error('Respuesta del servidor vacía o inesperada');
        }
      } catch (error) {
        console.error('Error al enviar el chat:', error);
        conversacion.value.pop();
      }
    };

    const cerrarSesion = (event) => {
      localStorage.removeItem('conversacion');
      setTimeout(() => {
        window.location.href = event.target.href;
      }, 100);
    };

    const saltoDeLinea = (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        mandarChat();
      }
    };

    const ajustarAltura = (event) => {
      event.target.style.height = '';
      event.target.style.height = event.target.scrollHeight + 'px';
    };

    const navigateToDetail = (id) => {
      window.location.href = `/detalle_cita/${id}`;
    };

    const showModal = (item) => {
      if (ventana.value === item) {
        closeModal();
      } else {
        ventana.value = item;
      }
    };

    const closeModal = () => {
      ventana.value = null;
    };

    return {
      chatMessage,
      conversacion,
      ventana,
      citas_opciones,
      url,
      currentRoute,
      showModal,
      closeModal,
      navigateToDetail,
      saltoDeLinea,
      ajustarAltura,
      mandarChat,
      cerrarSesion,
      lastChildId,
    }
  }
}).mount('#app')
