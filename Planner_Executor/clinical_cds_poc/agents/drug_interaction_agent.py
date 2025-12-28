from crewai import Agent

drug_agent = Agent(
    role="Drug Interaction Agent",
    goal="Identify medication contraindications and safety risks",
    backstory="Clinical pharmacology and patient safety specialist.",
    verbose=True
)
