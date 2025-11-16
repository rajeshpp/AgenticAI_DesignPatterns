import re
from langchain_community.tools import Tool
from langchain.agents import create_agent

# ========== TOOL DEFINITION ==========
def get_weather(city: str) -> str:
    return f"{city} is 29°C and cloudy."

tools = [
    Tool(
        name="WeatherTool",
        func=get_weather,
        description="Get the weather for a city. ALWAYS use the city in the user's question."
    )
]

model = "openai:gpt-3.5-turbo"

# ========== HELPER: EXTRACT CITY ==========
def extract_city(user_text):
    # Extracts the city from common weather questions
    match = re.search(r"weather in ([A-Za-z ]+)", user_text)
    return match.group(1).strip() if match else None

user_question = "What's the weather in Hyderabad?"
requested_city = extract_city(user_question)

# ========== EXPLICIT SYSTEM PROMPT ==========
prompt = f"""
You are an assistant that always uses tools for weather questions.

- When given a question about the weather in a city, ALWAYS call WeatherTool with the user's city.
- DO NOT guess, substitute, or default to a different city.
- Show your thought, action, action input, observation, and final answer step by step.

Example:
Question: What's the weather in Paris?
Thought: I need the weather for Paris, so I'll call WeatherTool.
Action: WeatherTool
Action Input: Paris
Observation: Paris is 29°C and cloudy.
Final Answer: Paris is 29°C and cloudy.

Question: {user_question}
Thought:"""

agent = create_agent(
    model,
    tools,
    system_prompt=prompt,
    debug=True,
)

result = agent.invoke({"input": user_question})

# ========== OUTPUT: Show Full ReAct Reasoning ==========
def print_react_steps(result, requested_city=None):
    steps = []
    if isinstance(result, dict) and "messages" in result and result["messages"]:
        for msg in result["messages"]:
            if hasattr(msg, "content") and msg.content:
                c = msg.content.strip()
                if "Thought:" in c:
                    steps.append(f"Thought: {c.split('Thought:',1)[1].strip()}")
                elif "Action:" in c:
                    steps.append(f"Action: {c.split('Action:',1)[1].strip()}")
                elif "Action Input:" in c:
                    steps.append(f"Action Input: {c.split('Action Input:',1)[1].strip()}")
                elif "Observation:" in c or "cloudy" in c or "clear" in c:
                    steps.append(f"Observation: {c}")
                elif "Final Answer:" in c:
                    steps.append(f"Final Answer: {c.split('Final Answer:',1)[1].strip()}")
                elif requested_city and requested_city in c:
                    steps.append(f"Final Answer: {c}")
        # Print all steps, or fallback to last message
        if steps:
            print("\n-- ReAct Reasoning Steps --")
            for step in steps:
                print(step)
        else:
            final_message = result["messages"][-1]
            print("Final Answer:", getattr(final_message, "content", str(final_message)))
    else:
        print("Final Answer:", str(result))

print_react_steps(result, requested_city)
