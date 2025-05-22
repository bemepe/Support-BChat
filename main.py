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
from datetime import datetime
import pytz 


st.set_page_config(page_title="Support-B Chat", page_icon="💬", layout="centered", initial_sidebar_state="expanded" )

client = MongoClient("mongodb://localhost:27017/")
db = client["Chatbot_Database"]  
history_collection = db["Chat_History"]  
reports_collection = db["Reports"]  

# MODEL  

llm = ChatOllama(
    model = "llama3.2:3b",
    temperature = 0,
)

# we define the chains we are going to use 

welcome_chain = welcome_assistant | llm 
details_chain= details_assistant | llm


# FUNCTION TO DISPLAY CHAT HISTORY IN STREAMLIT

def display_chat_history():

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

# FUNCTION TO CONFIGURE AND CUSTOMISE THE INTERFACE

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


# FUNCTION TO STORE EACH INTERACTION IN THE DATABASE

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
    

# FUNCTION THAT EXECUTES THE MODEL AND STORES HISTORY.
def invoke_chain(chain, input_data= None, context = None):
    """
    Generic method to invoke chains and manage history.
    
    """
    # Execution process according to input type 

    if input_data is None:
        result_invoke = chain.invoke({})
    elif isinstance(input_data, str):
        result_invoke = chain.invoke({'input': input_data})
    else:
        result_invoke = chain.invoke(input_data)
    

    if hasattr(result_invoke, 'content'):  
        assistant_response = result_invoke.content.strip().strip('"')

        st.session_state.chat_history.append({
            "role": "assistant", 
            "message": assistant_response,
            "timestamp": datetime.now(pytz.timezone("Europe/Madrid")).strftime("%d/%m/%Y %H:%M:%S")})
        
        save_interaction(st.session_state.chat_id, "assistant", assistant_response)

    else:
        
        assistant_response = str(result_invoke).strip()
        save_interaction(st.session_state.chat_id, "assistant", assistant_response)

   
    print("Assistant: ", assistant_response)
    return result_invoke
    

# FUNCTION THAT CHECKS IF THE USER'S RESPONSE IS VALID BASED ON STATUS

def validate_user_response(user_input, current_state):
    """
    Validate the user's response based on the current state and expected format.
    """

    desc = f"Validation for state: {current_state}"

    validate_chain = validate_response(current_state, desc)

    validate_result = invoke_chain(
        chain=validate_chain,
        input_data=user_input,
        context=f"Validation for {current_state}"
    )

    return validate_result


# FUNCTION THAT MANAGES THE CHAT FLOW

def handle_conversation():
    """
    Handle conversation
    """

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.answers = {}
        st.session_state.step = 0  
        st.session_state.states = ["age", "name", "location", "situation"]
        st.session_state.current_state = "age"
        st.session_state.missing_info = True
        st.session_state.welcome_shown = False
        st.session_state.invalid_counter = 0 
        st.session_state.forced_unnecessary = False  
        st.session_state.chat_ended = False 

    
    # If we have already detected that it is unnecessary due to 3 invalid interactions, we terminate immediately.
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

    # User responds:

    if user_input:

        st.session_state.chat_history.append({
        "role": "user",
        "message": user_input,
        "timestamp": datetime.now(pytz.timezone("Europe/Madrid")).strftime("%d/%m/%Y %H:%M:%S")
        })

        with st.chat_message("user"):
            st.markdown(user_input)

        save_interaction(st.session_state.chat_id, "user", user_input)

        # If the user wants to leave the chat
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
           
            

        # STEP 0: FIRST QUESTION
        if st.session_state.step == 0:

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
            
        
        # STEP 1: DATA COLLECTION WITH VALIDATION IN EACH STATE
        
        elif (st.session_state.step >= 1) and (st.session_state.missing_info):
            
            validation_result = validate_user_response(user_input, st.session_state.current_state)

            if validation_result.valid == 1:
                st.session_state.invalid_counter = 0  # Reset counter if there is a valid answer
                st.session_state.answers[st.session_state.current_state] = user_input
                current_i = st.session_state.states.index(st.session_state.current_state)
                ic(current_i)

                
                if current_i == len(st.session_state.states) - 1:
                    st.session_state.missing_info = False # Collection ends
                    st.session_state.step += 1  

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
                

            # If valid = 0, ask again
            else:
                st.session_state.invalid_counter += 1 
                
                # If there are 3 valid = 0 in a row, we force the classification to unnecesary=1.
                if st.session_state.invalid_counter >= 3:
                    st.session_state.missing_info = False 
                    st.session_state.forced_unnecessary = True  
                    st.session_state.step = len(st.session_state.states) + 2   # We skip the following steps
                    
                    st.rerun()
                    return
                    
                
                else:
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

    # FINAL QUESTION OF DETAILS

    if (not st.session_state.missing_info) and (st.session_state.step == len(st.session_state.states) + 1):
        
        print("Lanzando pregunta de detalles...")

        # To personalize the message
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
        st.session_state.step += 1 

        return True
    

# FUNCTION CLASSIFYING THE CHAT

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
    
    # If forced_unnecesary is False, we continue with normal sorting
    classify_chain = classify_chat()
    interactions = []

    # Runs through history and saves interactions
    for interaction in st.session_state.chat_history:
        if interaction["role"] =="assistant": 
            interactions.append(f"Assistant: {interaction['message']}")

        elif interaction["role"]=="user":
            interactions.append(f"User: {interaction['message']}")
    
    formatted_chat = "\n".join(interactions)

    classification_result = invoke_chain(
        chain=classify_chain,  
        input_data={"input": formatted_chat},
        context=f"Classification for Chat {st.session_state.chat_id}"
    )

    if classification_result is None:
        ("classification_result is None (model returned nothing)")

    # Correct inconsistency: urgency and unnecessary use cannot coexist, assign to unnecessary
    if int(classification_result.urgency) == 1 and int(classification_result.unnecessary) == 1:
        classification_result = classification_result.copy(update={"urgency": 0})
    
    print(f"Chat{st.session_state.chat_id}\nClassification: {classification_result}\n")
    return classification_result

# FUNCTION THAT GENERATES THE FAREWELL MESSAGE ACCORDING TO THE RESULT OF THE CLASSIFICATION

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


# FUNCTION THAT CREATES A REPORT WITH THE CONVERSATION AND THE CLASSIFICATION AND SAVES IT IN THE DATABASE

def create_report(classification):
    """
    Generate a report at the end of the conversation with the chat_history and the classification.
    """

    interactions = []

    for interaction in st.session_state.chat_history:
        if interaction["role"] =="assistant": 
            interactions.append(f"Assistant: {interaction['message']}")

        elif interaction["role"]=="user":
            interactions.append(f"User: {interaction['message']}")

    try: 
        report ={
            "chat_id": str(st.session_state.chat_id),
            "content": interactions,
            "classification_urgency": int(classification.urgency),
            "classification_unnecessary": int(classification.unnecessary),
        }

        reports_collection.update_one(
            {"chat_id": str(st.session_state.chat_id)},
            {"$set": report},
            upsert=True
        )

        print(f"Report chat {st.session_state.chat_id} saved in MongoDB.")

    except Exception as e:
        print(f"Error saving chat report {st.session_state.chat_id}: {e}")


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

    done = handle_conversation()

    if done:
        classification = classify_conversation()
        if classification is None:
            st.error("Classification failed. The model returned no result.")
            return
        if classification is not None:
            generate_final_message(classification)
            create_report(classification)
        else:
            print("Error: No classification result available.")

if __name__ =="__main__":
    main()
    
