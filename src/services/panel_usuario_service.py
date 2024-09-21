from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import markdown

# Configuración del chatbot
try:
    llm = ChatOpenAI(
        temperature=0.5,
        model='ft:gpt-3.5-turbo-0125:personal::9mpoKFq7',
        top_p=1,
        frequency_penalty=0.5,
        presence_penalty=0,
        openai_api_key='API KEY DE OPENAI'
    )
except Exception as e:
    # Manejo de errores en la configuración del modelo
    print(f"Error al configurar el modelo: {e}")
    llm = None  # Asegúrate de manejar el caso donde `llm` es `None` en el resto del código

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


def generar_respuesta(chat):
    if llm is None:
        return "El modelo no está configurado correctamente. Intenta de nuevo más tarde."

    try:
        response = conversation(chat)
        return response.get('text', 'Error en la generación de la respuesta.')
    except Exception as e:
        # Manejo de errores en la generación de la respuesta
        print(f"Error al generar la respuesta: {e}")
        return "Error en la generación de la respuesta."


def process_markdown(text):
    try:
        return markdown.markdown(text)
    except Exception as e:
        # Manejo de errores en el procesamiento de Markdown
        print(f"Error al procesar Markdown: {e}")
        return "Error en el procesamiento de Markdown."
