# 1 IMPORTS
from langchain_core.prompts import PromptTemplate

# 2 DEFINE THE WELCOME MESSAGE
welcome_prompt = """
You are a chatbot created to interact with children and adolescents in difficult situations. 
Create a brief, warm, and empathetic welcome message that conveys security and support. 
You must not include any questions. 
Never mention that you are a chatbot or introduce yourself.

"""

welcome_assistant = PromptTemplate(
    input_variables=[],
    template=welcome_prompt)


current_state = "age"

# FUNCTION THAT GENERATES DYNAMIC QUESTIONS ACCORDING TO CURRENT STATUS
def get_info(state):
    """
    Generates a dynamic prompt based on the current state of the conversation.
    """

    # Stores the descriptions of each state and describes what kind of information the assistant should ask for.
    possibilities = {
    "age": "the age of the user",
    "name": "the name of the user",
    "location": "the city where the user lives",
    "situation": "the reason why the user needs help and contacts the chat",
    }
    # Check if state is in possibilities and create a message to request information about the corresponding variable.
    if state in possibilities:
        get_info_prompt= f"""
        
        You are interacting with children and adolescents in difficult situations, such as bullying, abuse, family conflicts, eating disorders, 
        or mental health issues.  
        Never mention that you are a chatbot or use a name.
        Do not ask more than one question at a time.
        Your goal is to collect essential data in a very short, simple, and supportive manner.
        Ask only about: {possibilities[state]}.
        """
        return get_info_prompt
    else:
        return "Invalid state. Please restart the conversation."


# DEFINES THE NECESSARY PROMPT TO LAUNCH A MORE DETAILED QUESTION.    
details_prompt = """

You are speaking to a young person who may be facing a difficult situation. 
Never mention that you are a chatbot or introduce yourself.
The user has mentioned the following problem: {situation}. 
Their name is: {name}
Address them by name in a gentle way at the beginning.
Ask one clear and supportive follow-up question to better understand what the user is going through and what made them reach out for help.
Keep your message short, gentle, and direct.

"""

details_assistant = PromptTemplate(
    input_variables=["name","situation"],
    template=details_prompt
)

def get_final_prompt(classification):
    """
    Generates a dynamic farewell prompt based on the classification result.
    """
    try: 
        urgency = int(classification.urgency)
        unnecessary = int(classification.unnecessary)
    except:
        return None

    if urgency == 1 and unnecessary == 0:
        clsf = "urgent"
    elif urgency == 0 and unnecessary == 0:
        clsf = "non_urgent"
    elif urgency == 0 and unnecessary == 1:
        clsf = "unnecessary"
    else:
        return None  # invalid classification

    # Dictionary of possibilities according to classification
    possibilities = {
        "urgent": "respond directly to the user with a short, warm, and encouraging farewell message. Thank the user for sharing their feelings and situation. Inform them clearly that their case has been classified as urgent and that a mental health professional will be notified immediately and get in touch as soon as possible",
        "non_urgent": "respond directly to the user with a short, warm, and encouraging farewell message. Thank the user and let them know a report has been created and will be reviewed by a professional. Encourage them to take care and reach out again if needed.",
        "unnecessary": "respond directly to the user to gently remind them that this chat is for serious situations only, and stresses the importance of using the platform responsibly to ensure that it remains available to those who really need it",
    }

    # We create the dynamic prompt
    if clsf in possibilities:
        final_prompt = f"""
            You are ending a conversation with a young user.
            The user has shared their situation with you, and it has been classified as: {clsf}
            Do not tell the user the classification result. 
            You should: {possibilities[clsf]}
            Your answer must be very concise, respectful, and appropriate to the conversation.
            Do not explain what you're doing or refer to yourself. 
            Only output the final message. No titles, explanations, or formatting.
            
            """
        return final_prompt
    else:
        return "Invalid classification. Cannot generate final prompt."
