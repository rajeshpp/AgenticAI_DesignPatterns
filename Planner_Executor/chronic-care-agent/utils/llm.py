import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DEFAULT_MODEL = "gpt-4.1-mini"

def call_llm(prompt: str, system_prompt: str = None) -> str:
    if len(prompt) > 6000:
        raise ValueError("Prompt too long – cost/safety guard")

    messages = []

    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })

    messages.append({
        "role": "user",
        "content": prompt
    })

    response = client.responses.create(
        model=DEFAULT_MODEL,
        input=messages,
        temperature=0.3,
        max_output_tokens=400
    )

    return response.output_text
