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

# STREAMLIT

# Configuración inicial de la página
st.set_page_config(page_title="Chatbot de Apoyo ANAR ", page_icon="🎈", layout="centered", initial_sidebar_state="collapsed" )

# Creamos base de datos con dos colecciones 
client = MongoClient("mongodb://localhost:27017/")

db = client["chatbot_prueba"]  # base de datos
collection_history = db["chat_history"]  # Nueva colección para almacenar el historial del chat
collection_reports = db["chat_reports"]  # Nueva colección para almacenar los informes

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



def apply_custom_styles():
    st.markdown("""
    <style>
    /* 🎨 Fondo general */
    body, .stApp {
        background-color: #e6f2ff !important; /* Azul muy claro */
        color: #003366 !important; /* 🔥 Texto general azul oscuro */
    }

    /* 🎨 Títulos */
    h1, h2, h3 {
        color: #003366 !important; /* 🔥 Azul oscuro real */
        text-align: center;
        font-weight: bold;
    }

    /* 🎨 Mensajes del usuario (alineados a la derecha) */
    [data-testid="stChatMessage-user"] {
        background-color: #cce0ff;
        color: #003366 !important; /* 🔥 Texto azul oscuro en mensajes de usuario */
        border-radius: 12px 12px 0px 12px;
        padding: 10px;
        margin-bottom: 10px;
        margin-left: auto; /* 🔥 Empuja a la derecha */
        max-width: 75%;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }

    /* 🎨 Mensajes del asistente (alineados a la izquierda) */
    [data-testid="stChatMessage-assistant"] {
        background-color: #b3d1ff;
        color: #00264d !important; /* 🔥 Texto azul oscuro en mensajes de bot */
        border-radius: 12px 12px 12px 0px;
        padding: 10px;
        margin-bottom: 10px;
        margin-right: auto; /* 🔥 Se queda a la izquierda */
        max-width: 75%;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }

    /* 🎨 Input del usuario (contenedor) */
    [data-testid="stChatInput"] {
        background: transparent !important;
        padding: 0 !important;
        margin: 0 auto !important;
        width: 100% !important;
    }

    /* 🎨 Textarea real (barra de escribir) */
    [data-testid="stChatInput"] textarea {
        width: 100% !important;
        height: 50px;
        background-color: #e6f2ff !important;
        color: #003366 !important;
        border: 2px solid #99c2ff !important;
        border-radius: 20px !important;
        padding: 12px 20px !important;
        font-size: 16px !important;
        box-shadow: none !important;
        outline: none !important;
        resize: none !important;
    }

    /* 🎨 Placeholder del textarea */
    [data-testid="stChatInput"] textarea::placeholder {
        color: #337ab7 !important;
    }

    /* 🎨 Botón de enviar */
    button[kind="icon"] {
        background-color: #99c2ff !important;
        border-radius: 50% !important;
        color: #003366 !important;
        border: none !important;
        box-shadow: none !important;
    }

    button[kind="icon"]:hover {
        background-color: #80b3ff !important;
        color: #001f4d !important;
    }
    </style>
    """, unsafe_allow_html=True)





def save_interaction(chat_id, role, message):
    """
    Saves an interaction (user or assistant) in the MongoDB chat history collection.
    """

    collection_history.update_one(
        {"chat_id": chat_id},
        {"$push": {"interactions": {"role": role, "message": message, "timestamp": datetime.now(UTC).strftime("%d/%m/%Y %H:%M:%S")}}},
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
            "timestamp": datetime.now(UTC).strftime("%d/%m/%Y %H:%M:%S")})
        
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

    if "chat_id" not in st.session_state:
        st.session_state.chat_id = f"{datetime.now().strftime('%d%m%Y-%H%M')}_{str(ObjectId())}"
        st.session_state.chat_history = []
        st.session_state.answers = {}
        st.session_state.step = 0  # 0 = bienvenida, 1 = info, 2+ = cada pregunta
        st.session_state.states = ["age", "name", "location", "situation"]
        st.session_state.current_state = "age"
        st.session_state.missing_info = True
        st.session_state.welcome_shown = False
        st.session_state.invalid_counter = 0 # Cuenta las respuestas invalidas (valid =0)
        st.session_state.forced_unnecessary = False  # Broma detectada 

    
    # Si ya hemos detectado que es innecesario, terminamos inmediatamente

    if st.session_state.get("forced_unnecessary", False):
        return True

    st.title("Chatbot de Apoyo para Niños y Adolescentes")
    
    st.markdown("""
        ### Welcome to the Support Chat 
        Feel free to share your feelings. We're here to help you.
    """
    )
    
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
        


    # Usuario responde:
    user_input = st.chat_input("Write to us, we are here to help you")


    if user_input:

        st.session_state.chat_history.append({
        "role": "user",
        "message": user_input,
        "timestamp": datetime.now(UTC).strftime("%d/%m/%Y %H:%M:%S")
        })

        with st.chat_message("user"):
            st.markdown(user_input)

        save_interaction(st.session_state.chat_id, "user", user_input)

        if user_input.lower() == "exit":
            with st.chat_message("assistant"):
                st.markdown("Thank you for reaching out. The conversation has ended.")
           
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
                    st.session_state.missing_info = False  # Termina recogida

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
                    st.session_state.missing_info = False # Ya no recogemos ams informacion del usuario
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
            "timestamp": datetime.now(UTC).isoformat()
        })
        
        save_interaction(st.session_state.chat_id, "assistant", assistant_details)
        
        with st.chat_message("assistant"):
            st.markdown(assistant_details)

        st.session_state.step +=1
        st.rerun()
        return

    if (st.session_state.step == len(st.session_state.states) + 2) and user_input:
           
        with st.chat_message("user"):
            st.markdown(user_input)


        st.session_state.chat_history.append({
            "role": "user",
            "message": user_input,
            "timestamp": datetime.now(UTC).isoformat()
        })

        save_interaction(st.session_state.chat_id, "user", user_input)                
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

    # Corregir incoherencia: urgencia y uso innecesario no pueden coexistir

    if classification_result.urgency == 1 and classification_result.unnecessary == 1:
        classification_result.unnecessary = 0
    
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
            "Content": interactions,
            "Classification_urgency": int(classification.urgency),
            "Classification_unnecessary": int(classification.unnecessary),
        }

        # Guardamos el report en un archivo local en formato JSON
        with open (f"chat_report_{st.session_state.chat_id}.json", "w", encoding= "utf-8") as fich:
            json.dump(report, fich, indent=4, ensure_ascii=False)

        collection_reports.update_one(
            {"Chat_id": str(st.session_state.chat_id)},
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

    apply_custom_styles()

    # Manejar la conversación y obtener el historial de chat
    done = handle_conversation()

    if done:
           
        # Clasificar la conversación basada en el historial
        classification = classify_conversation()

        generate_final_message(classification)

        if classification is not None:
            create_report(classification)
        # Crear y mostrar el reporte final
        else:
            print("Error: No classification result available.")

if __name__ =="__main__":
    main()
    
