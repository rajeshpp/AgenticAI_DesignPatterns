from crewai import Agent

diagnosis_agent = Agent(
    role="Diagnosis Agent",
    goal="Generate ranked differential diagnoses based on symptoms and labs",
    backstory="Expert in internal medicine and diagnostic reasoning.",
    verbose=True
)
