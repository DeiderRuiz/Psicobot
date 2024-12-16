from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import os
import markdown

# Cargar las variables del archivo .env
load_dotenv()

# Configuración del chatbot
def configurar_chatbot():
    try:
        llm = ChatOpenAI(
            temperature=0.7,
            model='ft:gpt-3.5-turbo-0125:personal::9mpoKFq7',
            top_p=0.9,
            frequency_penalty=1,
            presence_penalty=0.6,
            # max_tokens=150,  # Limitar longitud de respuesta
            # stop=["Human:", "AI:"],  # Parar en estos prompts
            # n=1,  # Una respuesta, ajustable según necesidad
            # logprobs=None,  # Dejarlo como None si no esnecesario un análisis en profundidad
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
    except Exception as e:
        # Manejo de errores en la configuración del modelo
        print(f"Error al configurar el modelo: {e}")
        llm = None

    template = """
    Eres Psicobot, un asistente psicológico virtual y empático que trata de ayudar a los estudiantes de Corposucre con la gestión de sus emociones lo mejor posible.

    Conversación previa:
    {chat_history}

    Nueva pregunta del humano: {question}
    AI:
    """

    prompt_template = PromptTemplate.from_template(template)
    memory = ConversationBufferMemory(memory_key="chat_history")

    conversation = LLMChain(
        llm=llm,
        prompt=prompt_template,
        memory=memory,
        verbose=True
    )
    return conversation


conversation = configurar_chatbot()


def generar_respuesta(chat):
    if conversation is None:
        return "El modelo no está configurado correctamente. Intenta de nuevo más tarde."
    response = conversation(chat)
    return response.get('text', 'Error en la generación de la respuesta.')

# Función para limpiar el historial
def limpiar_historial():
    conversation.memory.clear()

def process_markdown(text):
    return markdown.markdown(text)
