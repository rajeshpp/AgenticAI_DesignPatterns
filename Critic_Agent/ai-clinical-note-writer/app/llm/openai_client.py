from langchain_openai import ChatOpenAI
import os


def get_llm():
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.2,
        api_key=os.getenv("OPENAI_API_KEY")
    )
