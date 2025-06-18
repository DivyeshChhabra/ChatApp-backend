# Importing LangChain Libraries.
from langchain_openai import ChatOpenAI

from tools.key import open_ai_api_key


# Defining OpenAI chat model.
def get_chat_model(model, temperature):
    gpt_chat_model = ChatOpenAI(model=model,
                            api_key=open_ai_api_key,
                            temperature=temperature)

    return gpt_chat_model