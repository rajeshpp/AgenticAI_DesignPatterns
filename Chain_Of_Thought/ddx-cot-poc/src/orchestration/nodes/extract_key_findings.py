# src/orchestration/nodes/extract_key_findings.py

from langchain_core.prompts import ChatPromptTemplate

from src.orchestration.state import DDxState
from src.orchestration.prompts import BASE_SYSTEM_PROMPT, EXTRACT_KEY_FINDINGS_USER
from src.llm import get_traced_llm


def run(state: DDxState) -> DDxState:
    """
    Node: extract_key_findings

    Uses the LLM to:
    - Extract key positive/negative findings
    - Briefly comment on acuity/severity
    """
    llm = get_traced_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", BASE_SYSTEM_PROMPT),
            ("user", EXTRACT_KEY_FINDINGS_USER),
        ]
    )

    chain = prompt | llm

    case_summary = state["case_summary"]
    result = chain.invoke({"case_summary": case_summary})

    new_state = dict(state)
    new_state["key_findings"] = result.content
    return new_state  # type: ignore[return-value]
