from crewai import Crew, Task
from agents.planner_agent import planner_agent
from agents.diagnosis_agent import diagnosis_agent
from agents.drug_interaction_agent import drug_agent
from agents.guidelines_agent import guidelines_agent
from agents.verifier_agent import verifier_agent

def build_crew(patient_context):

    planning_task = Task(
        description=f"""
        Patient Context:
        {patient_context}

        Identify:
        - Key clinical problems
        - Diagnostic questions
        - Medication safety concerns
        - Guideline considerations
        """,
        expected_output="""
        A structured breakdown of the patient case including:
        - Core problems
        - Diagnostic focus areas
        - Medication risk areas
        - Relevant guideline domains
        """,
        agent=planner_agent
    )

    diagnosis_task = Task(
        description="""
        Based on the patient context and planning output,
        generate a ranked list of possible diagnoses with reasoning.
        """,
        expected_output="""
        A ranked differential diagnosis with reasoning
        and any urgent red flags clearly identified.
        """,
        agent=diagnosis_agent
    )

    drug_task = Task(
        description="""
        Review the patient's medications in the context of
        renal and cardiac conditions.
        """,
        expected_output="""
        A list of medication contraindications, safety concerns,
        and high-risk drugs with explanations.
        """,
        agent=drug_agent
    )

    guidelines_task = Task(
        description="""
        Map the patient's findings to relevant clinical guidelines
        across diabetes, cardiac, and renal domains.
        """,
        expected_output="""
        Guideline-aligned recommendations, conflicts between
        guidelines, and priority areas.
        """,
        agent=guidelines_agent
    )

    verifier_task = Task(
        description="""
        Review all agent outputs to ensure:
        - Patient safety
        - Guideline alignment
        - No unsupported or unsafe recommendations
        """,
        expected_output="""
        A final validation stating whether outputs are safe,
        along with any warnings or required clinician review notes.
        """,
        agent=verifier_agent
    )

    return Crew(
        agents=[
            planner_agent,
            diagnosis_agent,
            drug_agent,
            guidelines_agent,
            verifier_agent
        ],
        tasks=[
            planning_task,
            diagnosis_task,
            drug_task,
            guidelines_task,
            verifier_task
        ],
        verbose=True
    )
