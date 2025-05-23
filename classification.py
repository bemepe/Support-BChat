
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

# EXAMPLES FOR THE FEW-SHOT PROMPT

#urgent = 1

chat_1 = [
    {'role': 'assistant', 'message': 'Hello, I am Kate. How old are you?'},
    {'role': 'user', 'message': 'I am thirteen years old'},
    {'role': 'assistant', 'message': 'Thank you for sharing. What is your name?'},
    {'role': 'user', 'message': 'My name is Lucas'},
    {'role': 'assistant', 'message': 'Where are you from, Lucas?'},
    {'role': 'user', 'message': 'I am from New York'},
    {'role': 'assistant', 'message': 'Thank you for telling me. How are you feeling?'},
    {'role': 'user', 'message': 'I am very scared. My father gets angry and hurts me when he drinks.'},
    {'role': 'assistant', 'message': 'I am really sorry to hear that. Are you in a safe place right now?'},
    {'role': 'user', 'message': 'No, I am at home and he is here.'},
    {'role': 'assistant', 'message': 'I need you to find a way to stay safe. Can you call someone you trust?'},
    {'role': 'user', 'message': 'I don\'t know, I feel trapped. Please help me.'},
]

chat_2 = [
    {'role': 'assistant', 'message': 'Hi, how old are you?'},
    {'role': 'user', 'message': 'I am 14.'},
    {'role': 'assistant', 'message': 'What is your name?'},
    {'role': 'user', 'message': 'My name is Valeria.'},
    {'role': 'assistant', 'message': 'Valeria how are you feeling today?'},
    {'role': 'user', 'message': 'I want to die. I can not take it anymore.'},
    {'role': 'assistant', 'message': 'I am here for you. Can you tell me what is happening?'},
    {'role': 'user', 'message': 'I have pills in my hand. I do nott want to live.'},
    {'role': 'assistant', 'message': 'Please, put the pills down. Can you call emergency services or a trusted adult right now?'},
    {'role': 'user', 'message': 'I do not know, I just need help now!'},
]

#urgent = 0

chat_3 = [
    {'role': 'assistant', 'message': 'Hi! How old are you?'},
    {'role': 'user', 'message': 'I am fifteen years old'},
    {'role': 'assistant', 'message': 'What is your name?'},
    {'role': 'user', 'message': 'I am Daniel'},
    {'role': 'assistant', 'message': 'Where are you from, Daniel?'},
    {'role': 'user', 'message': 'I live in Caceres'},
    {'role': 'assistant', 'message': 'Thank you for telling me. How are you feeling today?'},
    {'role': 'user', 'message': 'I feel a bit lonely because I moved to a new school and I don\'t know anyone.'},
    {'role': 'assistant', 'message': 'I see, it can be hard to adjust to a new place. Have you tried joining any clubs or activities?'},
    {'role': 'user', 'message': 'Not yet, I don\'t know where to start.'},
    {'role': 'assistant', 'message': 'Maybe you can start by talking to one or two people in your classes. Making small connections can help.'},
]

chat_4 = [
    {'role': 'assistant', 'message': 'Hello! My name is Kate. How old are you?'},
    {'role': 'user', 'message': 'I\'m 12.'},
    {'role': 'assistant', 'message': 'What\'s your name?'},
    {'role': 'user', 'message': 'I\'m Nora.'},
    {'role': 'assistant', 'message': 'Nice to meet you, Nora. Where are you from?'},
    {'role': 'user', 'message': 'I live in Seville, Spain.'},
    {'role': 'assistant', 'message': 'How are you feeling today?'},
    {'role': 'user', 'message': 'Confused... I think I might like girls but I don\'t know how to tell anyone.'},
    {'role': 'assistant', 'message': 'It\'s okay to feel this way. Have you talked to anyone about it?'},
    {'role': 'user', 'message': 'No, my family is very religious. I heard my dad say bad things about gay people.'},
    {'role': 'assistant', 'message': 'That must be hard. Would you feel safe talking to a friend first?'},
    {'role': 'user', 'message': 'Maybe my cousin... she\'s open-minded. But what if others find out?'},
    {'role': 'assistant', 'message': 'You don\'t have to rush. When you\'re ready, LGBTQ+ organizations can offer support.'},
    {'role': 'user', 'message': 'Thanks... I just needed to say it out loud to someone.'},
]

#unnecessary = 1

chat_5 = [
    {'role': 'assistant', 'message': 'Hello, I am here to listen and support you. How are you feeling today?'},
    {'role': 'user', 'message': 'I\'m feeling like I want to hear a joke.'},
    {'role': 'assistant', 'message': 'This chat is meant to provide emotional support. Is there something on your mind?'},
    {'role': 'user', 'message': 'Yes, I\'m thinking about how to turn my math teacher into a frog.'},
    {'role': 'assistant', 'message': 'I see. If you are feeling frustrated, I can help you talk about it.'},
    {'role': 'user', 'message': 'No, I just want to know if you have magic powers.'},
    {'role': 'assistant', 'message': 'I don\'t have magic powers, but I can help you work through your feelings.'},
    {'role': 'user', 'message': 'Okay, okay... but can you tell me how to rob a bank?'},
    {'role': 'assistant', 'message': 'This chat is for support and well-being. If you need help, I am here to listen.'},
    {'role': 'user', 'message': 'Nah, I\'m just messing with you. You\'re no fun!'},
]

chat_6 = [
    {'role': 'assistant', 'message': 'Hi, I am Kate. How old are you?'},
    {'role': 'user', 'message': 'I am 200 years old.'},
    {'role': 'assistant', 'message': 'That does not seem to be a real age. Can you tell me your actual age?'},
    {'role': 'user', 'message': 'Nah, I just want to have fun messing with the chatassistant.'},
    {'role': 'assistant', 'message': 'This chat is designed for people who need emotional support.'},
    {'role': 'user', 'message': 'I don\'t care, this is boring.'},
    {'role': 'assistant', 'message': 'If you are not here for support, please exit the chat.'},
]

chats = [chat_1, chat_2, chat_3, chat_4, chat_5, chat_6]
def build_examples(chat):
    interactions = []

    for interaction in chat:
        if interaction["role"] == "assistant":
            interactions.append(f"Assistant: {interaction['message']}")
        elif interaction["role"] == "user":
            interactions.append(f"User: {interaction['message']}")
    interactions = "\n".join(interactions)
    return interactions


# FUNCTION TO CLASSIFY A CONVERSATION
def classify_chat():
    """
    Classify the given chat history as urgent or unnecessary.
    """
    class ClassificationChat(BaseModel):
        # Describes the rules of classification for each category
        urgency:  str = Field(
            description=
            "Indicates whether the conversation describes an urgent situation requiring immediate attention."
            "Assign 1 if the conversation includes:"
            "- Mentions of self-harm, suicidal thoughts, or harm to others."
            "- Descriptions of physical or emotional abuse requiring intervention."
            "- Extreme distress, crisis situations, or immediate danger."
            "Assign 0 if none of the above conditions are met.",
            
            enum=["0","1"]
        )
        unnecessary: str = Field(
            description= 
            "Indicates whether the conversation contains irrelevant, non-serious, or inappropriate content."
            "Assign 1 if the conversation includes:"
            "- Jokes, sarcasm, or playful banter unrelated to seeking support."
            "- Spam, random statements, or unrelated topics."
            "- Repeated off-topic responses or trolling behavior."
            "Assign 0 if the content is relevant, appropriate, and aligned with seeking support.",

            enum= ["0", "1"])
        
    
    # Structure of the few-shot prompt (sandwich)
    classification_examples = [
    {"input": build_examples(chats[0]), "output": {"urgency": 1, "unnecessary": 0}},
    {"input": build_examples(chats[1]), "output": {"urgency": 1, "unnecessary": 0}},
    {"input": build_examples(chats[2]), "output": {"urgency": 0, "unnecessary": 0}},
    {"input": build_examples(chats[3]), "output": {"urgency": 0, "unnecessary": 0}},
    {"input": build_examples(chats[4]), "output": {"urgency": 0, "unnecessary": 1}},
    {"input": build_examples(chats[5]), "output": {"urgency": 0, "unnecessary": 1}},
    ]

    example_prompt = ChatPromptTemplate.from_messages(
    [
        ("user", "{input}"),
        ("assistant", "{output}"),
    ]
)
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples= classification_examples
    )

    # Description of the system
    description = """
        You are an AI that classifies conversations based on urgency and appropriateness. 
        Extract only the properties defined in 'ClassificationChat' when analyzing the provided conversation.

        Respond strictly with the classification values.

        Conversation:
        {input}
        """

    classify_prompt = ChatPromptTemplate.from_messages([
        ("system", description),
        few_shot_prompt,
        ("user", "{input}")
    ])


    # LLM
    classify_llm = ChatOllama(
        model = "llama3.2:3b",
        temperature = 0, 
        num_predict = 128,
    ).with_structured_output(ClassificationChat)

    classify_chain = classify_prompt | classify_llm 

    return classify_chain



# 3 FUNCTION TO VALIDATE USER RESPONSES IN THE CONVERSATION
def validate_response(state,desc):
    """
    Create a validation chain to validate user responses for a specific state.
    """
    # Defines what each response should contain according to the status
    possibilities = {
        "age": "The response should clearly indicate an age, either as a number or in written form. It may be embedded in a sentence such as 'I just turned ten', or 'almost fifteen'.",
        "name": "The response should mention a real name, like 'My name is Lucia' or 'They call me Dani'. Do not accept jokes or unrelated words.",
        "location": "The response should clearly mention the name of a city, even if the sentence includes additional context like 'I have moved from.., I now live in...', 'with my family', etc.",
        "situation": "The response should describe a personal problem, emotional struggle, family conflict, feelings of loneliness, fear, sadness, bullying, violence, or any situation that might affect the child's or adolescent's well-being."
    }
    # Describes what is expected in the user's response, based on the current state of the user.
    desc= f"""
        You must verify if a user's response matches the expected format or content for a specific state. 
        Expected format: {possibilities[state]}
        Verify if the user's response meets this expectation and respond with '1' if it matches or '0' if it does not.
        """
    class ValidationResponse(BaseModel):
        valid:  int = Field(
            description=desc,
            enum=["0","1"]
        )
    validate_prompt = ChatPromptTemplate.from_template(
        """
        Only extract the properties mentioned in 'ValidationResponse'.

        Response:
        {input}
        """
    )
    
    validate_llm = ChatOllama(
        model = "llama3.2:3b",
        temperature = 0, 
        num_predict = 128,
    ).with_structured_output(ValidationResponse)

    validate_chain = validate_prompt | validate_llm 
    
    return validate_chain

