# src/orchestration/nodes/generate_candidates.py

import json
from typing import Any, Dict, List

from langchain_core.prompts import ChatPromptTemplate

from src.orchestration.state import DDxState
from src.orchestration.prompts import BASE_SYSTEM_PROMPT, GENERATE_CANDIDATES_USER
from src.llm import get_traced_llm


def _safe_parse_diagnoses(text: str) -> List[Dict[str, Any]]:
    """
    Expecting JSON like:
    {
      "diagnoses": [
        {
          "name": "...",
          "rationale": "...",
          "likelihood": "High"
        }
      ]
    }
    """
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "diagnoses" in data:
            value = data["diagnoses"]
            if isinstance(value, list):
                return value
    except json.JSONDecodeError:
        pass
    return []


def run(state: DDxState) -> DDxState:
    """
    Node: generate_candidates

    Uses the LLM to propose 3–5 differential diagnoses with:
    - name
    - rationale
    - likelihood (High/Moderate/Low)
    """
    llm = get_traced_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", BASE_SYSTEM_PROMPT),
            ("user", GENERATE_CANDIDATES_USER),
        ]
    )

    chain = prompt | llm

    case_summary = state["case_summary"]
    key_findings = state["key_findings"]

    result = chain.invoke(
        {
            "case_summary": case_summary,
            "key_findings": key_findings,
        }
    )

    diagnoses = _safe_parse_diagnoses(result.content)

    new_state: Dict[str, Any] = dict(state)
    new_state["candidate_diagnoses"] = diagnoses
    return new_state  # type: ignore[return-value]
