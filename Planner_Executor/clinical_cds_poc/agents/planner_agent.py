from crewai import Agent

planner_agent = Agent(
    role="Clinical Planner",
    goal="Decompose complex multi-comorbidity cases into structured clinical reasoning tasks",
    backstory=(
        "A senior clinical reasoning assistant that understands how physicians "
        "analyze patients with multiple chronic conditions."
    ),
    verbose=True
)
