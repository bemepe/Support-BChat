# IMPORTACIONES nuevas 

from langchain_ollama import ChatOllama
from classification import classify_chat, validate_response
import json
from prompts import welcome_assistant, get_info, details_assistant, get_final_prompt
from icecream import ic
from langchain_core.prompts import PromptTemplate
import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, UTC
import pytz #hora España

# STREAMLIT

# Configuración inicial de la página
st.set_page_config(page_title="Support-B Chat", page_icon="💬", layout="centered", initial_sidebar_state="expanded" )

# Creamos base de datos con dos colecciones 
client = MongoClient("mongodb://localhost:27017/")

db = client["Chatbot_Database"]  # base de datos
history_collection = db["Chat_History"]  # Nueva colección para almacenar el historial del chat
reports_collection = db["Reports"]  # Nueva colección para almacenar los informes

# Modelo 

llm = ChatOllama(
    model = "llama3.2:3b",
    temperature = 0,
)

# Chains a empelar: para el mensaje de bienvenida y la pregunta detallada de la situation.

welcome_chain = welcome_assistant | llm 
details_chain= details_assistant | llm

#Función para mostrar el historial del chat en Streamlit

def display_chat_history():

    """Muestra el historial del chat en la interfaz de Streamlit"""

    for message in st.session_state.chat_history:
        
        content = message.get("message", "")
        timestamp_str = message.get("timestamp", None)

        if content: 
            if timestamp_str:

                timestamp = datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M:%S")  
                timestamp_display = timestamp.strftime("%H:%M:%S")

                with st.chat_message(message["role"]):
                    st.markdown(content)
                    st.markdown(
                            f"<div style='font-size: 12px; color: gray; text-align: right; margin-top: -8px;'>🕒 {timestamp_display}</div>",
                            unsafe_allow_html=True
                        )



def apply_styles():
    st.markdown("""
    <style>
    /* Fondo general */
    body, .stApp {
        background-color: #f6fcff !important; 
        color: #003366 !important;
        margin: 0 !important;
        padding-top: 0 !important;
        font-size: 20px !important;
    }
    /* Fondo blanco y contenido centrado en la barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        text-align: center;
        padding: 20px;
        width: 350px !important;
        min-width: 350px !important;
                
    }
     .block-container {
        padding-left: 5rem !important;
        padding-right: 5rem !important;
        max-width: 1200px !important;
    }

    /* Títulos */
    h1, h2, h3 {
        color: #084f75 !important; 
        text-align: center;
        font-weight: bold;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #000000 !important;
        text-align: center;
    }

    /* Mensajes del usuario*/
    [data-testid="stChatMessage-user"] {
        background-color: #f3fbfe !important;
        color: #000000 ; 
        border-radius: 12px 12px 0px 12px;
        padding: 10px;
        margin-bottom: 10px;
        margin-left: auto;
        max-width: 850px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        font-size: 20px !important;
    }
                
    /* Fondo blanco en el contenedor del input (chat input box completa) */
    section[data-testid="stChatInput"] {
        background-color: #f3fbfe !important;
        border: 1px solid #dddddd;
        border-radius: 24px;
        padding: 8px;
    }

    /* Mensajes del asistente */
    [data-testid="stChatMessage-assistant"] {
        background-color: #003366;
        color: #000000 !important; 
        border-radius: 12px 12px 12px 0px;
        padding: 10px;
        margin-bottom: 10px;
        margin-right: auto;
        max-width: 850px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        font-size: 20px !important;
    }


    </style>
    """, unsafe_allow_html=True)



def save_interaction(chat_id, role, message):
    """
    Saves an interaction (user or assistant) in the MongoDB chat history collection.
    """
    if not chat_id:
        print("chat_is is missing")
        return

    history_collection.update_one(
        {"chat_id": chat_id},
        {"$push": {"interactions": {"role": role, "message": message, "timestamp": datetime.now(pytz.timezone("Europe/Madrid")).strftime("%d/%m/%Y %H:%M:%S")}}},
        upsert=True    
    )
    

# EJECUTA EL MODELO Y ALMACENA EL HISTORIAL
def invoke_chain(chain, input_data= None, context = None):
    """
    Generic method to invoke chains and manage history.
    
    """
    # 1 PROCESO DE EJECUCION SEGUN EL TIPO DE ENTRADA 
    
    # Si no hay input_data y la cadena no lo requiere, hacerlo directamente
    if input_data is None:
        result_invoke = chain.invoke({})
    elif isinstance(input_data, str):
        result_invoke = chain.invoke({'input': input_data})
    else:
        result_invoke = chain.invoke(input_data)
    
    # Extraer la respuesta correctamente según su tipo, evitar AttributeError
    if hasattr(result_invoke, 'content'):  # Si es AIMessage
        assistant_response = result_invoke.content.strip().strip('"')

        st.session_state.chat_history.append({
            "role": "assistant", 
            "message": assistant_response,
            "timestamp": datetime.now(pytz.timezone("Europe/Madrid")).strftime("%d/%m/%Y %H:%M:%S")})
        
        save_interaction(st.session_state.chat_id, "assistant", assistant_response)

    else:
        # Si no tiene .content, asumimos que es una respuesta estructurada (validación, clasificación...)
        # Guardamos en MongoDB, pero no en el historial
        assistant_response = str(result_invoke).strip()
        save_interaction(st.session_state.chat_id, "assistant", assistant_response)


                
    # 3 DEVUELVE EL RESULTADO
   
    print("Assistant: ", assistant_response)
    
    return result_invoke
    

# VERIFICA SI LA RESPUESTA DEL USUARIO ES VALIDA EN FUNCION DEL ESTADO
def validate_user_response(user_input, current_state):
    """
    Validate the user's response based on the current state and expected format.
    """

    desc = f"Validation for state: {current_state}"

    # 1 OBTIENE LA CADENA DE VALIDACION con el metodo create_validate_chain
    validate_chain = validate_response(current_state, desc)

    # 2 EJECUTA LA VALIDACION con invoke_chain
    validate_result = invoke_chain(
        chain=validate_chain,
        input_data=user_input,
        context=f"Validation for {current_state}"
    )

    #3 DEVUELVE EL RESULTADO valid=0/1
    return validate_result



# GESTIONA EL FLUJO DEL CHAT 
def handle_conversation():
    """
    Handle conversation
    """

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.answers = {}
        st.session_state.step = 0  # 0 = bienvenida, 1 = info, 2+ = cada pregunta
        st.session_state.states = ["age", "name", "location", "situation"]
        st.session_state.current_state = "age"
        st.session_state.missing_info = True
        st.session_state.welcome_shown = False
        st.session_state.invalid_counter = 0 # Cuenta las respuestas invalidas (valid =0)
        st.session_state.forced_unnecessary = False  # Broma detectada 
        st.session_state.chat_ended = False # Si el usuario escribe exit, cambiamo a True

    
    # Si ya hemos detectado que es innecesario, terminamos inmediatamente

    if st.session_state.get("forced_unnecessary", False):
        return True

    
    display_chat_history()

    if not st.session_state.welcome_shown:
        welcome_message= invoke_chain(
                chain=welcome_chain,
                input_data=None,
                context="Welcome Prompt"
            )
        

        with st.chat_message("assistant"):
            st.markdown(welcome_message.content.strip().strip('"'))
        
        st.session_state.welcome_shown = True
        

    if not st.session_state.get("chat_ended", False):
        user_input = st.chat_input("Write to us, we are here to help you")
    else:
        user_input = None

    # Usuario responde:

    if user_input:

        st.session_state.chat_history.append({
        "role": "user",
        "message": user_input,
        "timestamp": datetime.now(pytz.timezone("Europe/Madrid")).strftime("%d/%m/%Y %H:%M:%S")
        })

        with st.chat_message("user"):
            st.markdown(user_input)

        save_interaction(st.session_state.chat_id, "user", user_input)

        if user_input.lower() == "exit":
            bye_message = "Thank you for reaching out. The conversation has ended."
            
            with st.chat_message("assistant"):
                st.markdown(bye_message)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "message": bye_message,
                    "timestamp": datetime.now(pytz.timezone("Europe/Madrid")).strftime("%d/%m/%Y %H:%M:%S")
                })

            save_interaction(st.session_state.chat_id, "assistant", bye_message)

            st.session_state.chat_ended = True
            return True
           
            
        

        # PASO 0: PREGUNTA AGE 
        if st.session_state.step == 0:

            prompt = get_info(st.session_state.current_state)
            prompt_question = PromptTemplate.from_template(prompt)
            question_chain =  prompt_question | llm
            
            # 6 envio de la pregunta al chatassistant
            assistant_response = invoke_chain(
                chain=question_chain,  
                input_data=None,
                context=f"Question for state: {st.session_state.current_state}"
            )

            with st.chat_message("assistant"):
                st.markdown(assistant_response.content.strip().strip('"'))
        

            # Actualizamos el paso 
            st.session_state.step += 1
            st.rerun()
            
        
        # PASO 1: RECOGIDA DE DATOS CON VALIDACION 
        
        elif (st.session_state.step >= 1) and (st.session_state.missing_info):
            
            validation_result = validate_user_response(user_input, st.session_state.current_state)

            if validation_result.valid == 1:
                st.session_state.invalid_counter = 0  # Reiniciar contador si hay una respuesta válida
                st.session_state.answers[st.session_state.current_state] = user_input
                current_i = st.session_state.states.index(st.session_state.current_state)
                ic(current_i)

                
                # Si es el ultimo estado == situation 
                if current_i == len(st.session_state.states) - 1:
                    st.session_state.missing_info = False # Termina recogida
                    st.session_state.step += 1  

                # Si no es el ultimo estado - Pasamos a la siguiente pregunta
                else:
                    st.session_state.current_state= st.session_state.states[current_i + 1]
                    
                    prompt = get_info(st.session_state.current_state)
                    prompt_question = PromptTemplate.from_template(prompt)
                    question_chain =  prompt_question | llm
                    
                    assistant_response = invoke_chain(
                        chain=question_chain,  
                        input_data=None,
                        context=f"Question for state: {st.session_state.current_state}"
                    )

                    with st.chat_message("assistant"):
                        st.markdown(assistant_response.content.strip().strip('"'))
    
                    st.session_state.step += 1

                    st.rerun()
                    return 
                

            # Si valid = 0, volver a preguntar 
            else:
                st.session_state.invalid_counter += 1 # Marcar si valid = 0, una repeticion
                
                #Si hay 3 valid = 0 seguidos, forzamos la clasificacion a unnecesary=1
                if st.session_state.invalid_counter >= 3:
                    st.session_state.missing_info = False # Ya no recogemos mas informacion del usuario
                    st.session_state.forced_unnecessary = True  
                    st.session_state.step = len(st.session_state.states) + 2 # Nos saltamos los pasos siguientes
                    
                    st.rerun()
                    return
                    
                
                else:
                # Repetir la misma pregunta
                    repeat_prompt = get_info(st.session_state.current_state)
                    repeat_chain = PromptTemplate.from_template(repeat_prompt) | llm

                    assistant_response = invoke_chain(
                        chain=repeat_chain,
                        input_data=None,
                        context=f"Repeat question for state: {st.session_state.current_state}"
                    )

                    with st.chat_message("assistant"):
                        st.markdown(assistant_response.content.strip().strip('"'))

                    st.rerun()
                    return

                
            print("STEP CHECK:", st.session_state.step)
            print("STATE CHECK:", st.session_state.current_state)
            print("MISSING INFO:", st.session_state.missing_info)

    # PASO 2 PREGUNTA FINAL DE LOS DETALLES, FUERA DEL USER INPUT

    #step ==4

    if (not st.session_state.missing_info) and (st.session_state.step == len(st.session_state.states) + 1):
        
        print("Lanzando pregunta de detalles...")

        # Sacamos el nombre y la situaciones de las answers del usuario
        situation = st.session_state.answers.get("situation", "unknown")
        name = st.session_state.answers.get("name", "unknown") 

        details_question = details_chain.invoke({
            "situation": situation,
            "name": name
        })

        assistant_details = details_question.content.strip().strip('"')

        st.session_state.chat_history.append({
            "role": "assistant",
            "message": assistant_details,
            "timestamp": datetime.now(pytz.timezone("Europe/Madrid")).strftime("%d/%m/%Y %H:%M:%S")
        })
        
        save_interaction(st.session_state.chat_id, "assistant", assistant_details)
        
        with st.chat_message("assistant"):
            st.markdown(assistant_details)

        st.session_state.step +=1
        st.rerun()
        return

    if (st.session_state.step == len(st.session_state.states) + 2) and user_input:
                       
        st.session_state.step += 1 # step ==6 

        return True
    

# CLASIFICA EL CHAT 
def classify_conversation():
    """
    Classify the conversation based on the text provided.
    """

    if st.session_state.get("forced_unnecessary", False):
        class Result:
            urgency = 0
            unnecessary = 1
        print("Forced classification as inappropriate use for 3 invalid answers. ")
        return Result()
    
    # Si forced_unnecesary es False, seguimos con la clasificacion normal
    # Obtenemos la cadena 
    classify_chain = classify_chat()
    interactions = []

    # 2 RECORRE EL HISTORIAL Y GUARDA LAS INTERACCIONES 
    for interaction in st.session_state.chat_history:
        if interaction["role"] =="assistant": # Mensaje del Assistant
            interactions.append(f"Assistant: {interaction['message']}")

        elif interaction["role"]=="user":
            interactions.append(f"User: {interaction['message']}")
    
    formatted_chat = "\n".join(interactions)

    # Ejecuta la clasificacion y develve el resultado
    classification_result = invoke_chain(
        chain=classify_chain,  
        input_data={"input": formatted_chat},
        context=f"Classification for Chat {st.session_state.chat_id}"
    )

    if classification_result is None:
        ("classification_result is None (model returned nothing)")

    # Corregir incoherencia: urgencia y uso innecesario no pueden coexistir, se asigna a innecesario
    if int(classification_result.urgency) == 1 and int(classification_result.unnecessary) == 1:
        classification_result = classification_result.copy(update={"urgency": 0})
    
    print(f"Chat{st.session_state.chat_id}\nClassification: {classification_result}\n")
    return classification_result

# GENERA EL MENSAJE DE DESPEDIDA EN FUNCION DEL RESULTADO DE LA CLASIFICACIÓN

def generate_final_message(classification):
    """
    Generate a final message from the chatassistant based on the classification result.
    """

    prompt = get_final_prompt(classification)
    final_prompt = PromptTemplate.from_template(prompt)
    final_chain =  final_prompt | llm
        
    final_message = invoke_chain(
        chain=final_chain,  
        input_data=None,
        context=f"Final message for:{classification}",
        )
    
    with st.chat_message("assistant"):
        st.markdown(final_message.content.strip().strip('"'))
    
    st.session_state.chat_ended = True


# CREA UN INFORME JSON CON LA CONVERSACION Y LA CLASIFICACION
def create_report(classification):
    """
    Generate a report at the end of the conversation with the chat_history and the classification.
    """
    # 1 LISTA VACIA DE INTERACCIONES 
    interactions = []

    # 2 RECORRE EL HISTORIAL Y GUARDA LAS INTERACCIONES 
    for interaction in st.session_state.chat_history:
        if interaction["role"] =="assistant": # Mensaje del Chatassistant
            interactions.append(f"Assistant: {interaction['message']}")

        elif interaction["role"]=="user":
            interactions.append(f"User: {interaction['message']}")

    
    # 3 CREACION DEL INFORME EN FORMATO JSON
    try: 
        report ={
            "chat_id": str(st.session_state.chat_id),
            "content": interactions,
            "classification_urgency": int(classification.urgency),
            "classification_unnecessary": int(classification.unnecessary),
        }

        # Guardamos el report en un archivo local en formato JSON
        # with open (f"chat_report_{st.session_state.chat_id}.json", "w", encoding= "utf-8") as fich:
        #     json.dump(report, fich, indent=4, ensure_ascii=False)

        reports_collection.update_one(
            {"chat_id": str(st.session_state.chat_id)},
            {"$set": report},
            upsert=True
        )

        print(f"Informe del chat {st.session_state.chat_id} guardado en MongoDB.")

    except Exception as e:
        print(f"Error al guardar el informe del chat {st.session_state.chat_id}: {e}")


def main():
    """
    Main function to handle the entire flow: conversation, classification, and report generation.
    """

    if "chat_id" not in st.session_state:
        st.session_state.chat_id = f"{datetime.now(pytz.timezone("Europe/Madrid")).strftime("%d%m%Y-%H%M")}_{str(ObjectId())}"


    st.title("¡Bienvenido a Support-B Chat!")
    
    st.markdown("""
    <div style='text-align: center; color: #084f75;'>
    <h3 style = 'font-size: 28px;'>Chatbot de Apoyo para Niños y Adolescentes</h3>
    <p style = 'font-size: 20px;'>
        Este es un espacio seguro donde puedes expresar cómo te sientes.<br>
        No estas solo/a, cada palabra cuenta y lo que sientes es importante.<br>
        Estoy aquí para escucharte, acompañarte y ayudarte de la mejor manera posible.
    </p>
    </div>
    """, unsafe_allow_html=True)

    
    apply_styles()
    with st.sidebar:

        st.image("logo_chat.png", width=150)
        
        st.markdown(f"""
        <div style='text-align: left; color: #084f75; font-size: 18px;'>
        <p><strong>Chat ID:</strong><br> {st.session_state.chat_id} </p>

        <p>📞 <strong>Teléfono de Contacto</strong><br>
        639 58 55 68</p>

        <p>📩 <strong>Correo</strong><br>
        <a href='mailto:beatriz.mendez.peraza@alumnos.upm.es' style='color: #04698d; text-decoration: none;'>
        beatriz.mendez.peraza@alumnos.upm.es</a></p>
        </div>
        """, unsafe_allow_html=True)

    # Manejar la conversación y obtener el historial de chat
    done = handle_conversation()

    if done:
           
        # Clasificar la conversación basada en el historial
        classification = classify_conversation()

        if classification is None:
            st.error("Classification failed. The model returned no result.")
            return
        
        if classification is not None:
            generate_final_message(classification)
            create_report(classification)
        # Crear y mostrar el reporte final
        else:
            print("Error: No classification result available.")

if __name__ =="__main__":
    main()
    
