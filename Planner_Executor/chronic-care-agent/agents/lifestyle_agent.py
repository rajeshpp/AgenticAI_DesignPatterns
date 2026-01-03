from utils.llm import call_llm

SYSTEM_PROMPT = """
You are a health coaching assistant.
Rules:
- Give safe, realistic lifestyle advice
- No extreme diets or exercise
"""

def lifestyle_recommendation(bp_trend):
    prompt = f"""
    Patient BP trend: {bp_trend}

    Suggest ONE lifestyle recommendation today
    related to diet, exercise, or stress.
    """

    return call_llm(prompt, SYSTEM_PROMPT)
