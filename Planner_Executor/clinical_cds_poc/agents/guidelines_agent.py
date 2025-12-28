from crewai import Agent

guidelines_agent = Agent(
    role="Guidelines Agent",
    goal="Map patient findings to diabetes, cardiac, and renal clinical guidelines",
    backstory="Evidence-based medicine expert.",
    verbose=True
)
