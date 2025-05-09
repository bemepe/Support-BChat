
from main import invoke_chain
from chats import chat_1, chat_2, chat_3, chat_4, chat_14,  chat_5, chat_6, chat_7, chat_8, chat_9, chat_10, chat_11, chat_12, chat_13, chat_15, chat_16, chat_17, chat_18
from langchain_openai import ChatOpenAI



# 1 IMPORTACIONES
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from pydantic import BaseModel, Field

chat_a = [
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

chat_b = [
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

chat_c = [
    {'role': 'assistant', 'message': 'Hi! How old are you?'},
    {'role': 'user', 'message': 'I am fifteen years old'},
    {'role': 'assistant', 'message': 'What is your name?'},
    {'role': 'user', 'message': 'I am Daniel'},
    {'role': 'assistant', 'message': 'Where are you from, Daniel?'},
    {'role': 'user', 'message': 'I live in Texas'},
    {'role': 'assistant', 'message': 'Thank you for telling me. How are you feeling today?'},
    {'role': 'user', 'message': 'I feel a bit lonely because I moved to a new school and I don\'t know anyone.'},
    {'role': 'assistant', 'message': 'I see, it can be hard to adjust to a new place. Have you tried joining any clubs or activities?'},
    {'role': 'user', 'message': 'Not yet, I don\'t know where to start.'},
    {'role': 'assistant', 'message': 'Maybe you can start by talking to one or two people in your classes. Making small connections can help.'},
]

chat_d = [
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

chat_e = [
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

chat_f = [
    {'role': 'assistant', 'message': 'Hi, I am Kate. How old are you?'},
    {'role': 'user', 'message': 'I am 200 years old.'},
    {'role': 'assistant', 'message': 'That does not seem to be a real age. Can you tell me your actual age?'},
    {'role': 'user', 'message': 'Nah, I just want to have fun messing with the chatassistant.'},
    {'role': 'assistant', 'message': 'This chat is designed for people who need emotional support.'},
    {'role': 'user', 'message': 'I don\'t care, this is boring.'},
    {'role': 'assistant', 'message': 'If you are not here for support, please exit the chat.'},
]

chats = [chat_a, chat_b, chat_c, chat_d, chat_e, chat_f]
def build_examples(chat):
    interactions = []

    for interaction in chat:
        if interaction["role"] == "assistant":
            interactions.append(f"Assistant: {interaction['message']}")
        elif interaction["role"] == "user":
            interactions.append(f"User: {interaction['message']}")
    interactions = "\n".join(interactions)
    return interactions

available_models = {
    "1": "meta-llama/llama-3.2-3b-instruct",
    "2": "openai/gpt-4o-2024-11-20",
    "3": "mistralai/mistral-7b-instruct",
    "4": "huggingfaceh4/zephyr-7b-beta",
    "5": "gryphe/mythomax-l2-13b"
}



# 2 FUNCION PARA CLASIFICAR UNA CONVERSACION 
def classify_chat(model_name):
    """
    Classify the given chat history as urgent or unnecessary.
    """
    class ClassificationChat(BaseModel):
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
    llm = ChatOpenAI(
        model= model_name,
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        base_url="https://openrouter.ai/api/v1",
        api_key="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",  # if you prefer to pass api key in directly instaed of using env vars
        # organization="...",
        # other params...
    ).with_structured_output(ClassificationChat)
    

    classify_chain = classify_prompt | llm  

    # Devuelve el classify_chain que es lo que nos interesa 
    return classify_chain


def main():
    """
    Main function to classify and generate reports for all chats.
    """
    chats = {
        1: chat_1, 2: chat_2, 3: chat_3, 4: chat_4,
        5: chat_5, 6: chat_6, 7: chat_7, 8: chat_8,
        9: chat_9, 10: chat_10, 11: chat_11, 12: chat_12,
        13: chat_13, 14: chat_14, 15: chat_15,  16: chat_16, 17: chat_17, 18: chat_18
    }

    print("Modelos OpenRouter disponibles:")
    for key, name in available_models.items():
        print(f"{key}. {name}")

    model_choice = input("Selecciona el número del modelo: ").strip()
    model_name = available_models.get(model_choice)

    if not model_name:
        print("Modelo no válido.")
        return

    chat_id = int(input("Enter the chat ID: "))

    if chat_id in chats:
        chat = chats[chat_id]
        chain = classify_chat(model_name)
        result = chain.invoke({"input": build_examples(chat)})

        print(f"Chat{chat_id}\nClassification: {result} Model:{model_name} ")

    else:
        print("Invalid chat number.")


if __name__ == "__main__":
    main()