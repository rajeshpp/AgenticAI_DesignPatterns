# src/orchestration/nodes/evidence_for_against.py

import json
from typing import Any, Dict, List

from langchain_core.prompts import ChatPromptTemplate

from src.orchestration.state import DDxState
from src.orchestration.prompts import BASE_SYSTEM_PROMPT, EVIDENCE_FOR_AGAINST_USER
from src.llm import get_traced_llm


def _safe_parse_evidence(text: str) -> List[Dict[str, Any]]:
    """
    Expecting JSON like:
    {
      "evidence": [
        {
          "name": "...",
          "features_supporting": [...],
          "features_against_or_missing": [...],
          "potential_red_flags": [...]
        }
      ]
    }
    """
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "evidence" in data:
            value = data["evidence"]
            if isinstance(value, list):
                return value
    except json.JSONDecodeError:
        pass
    return []


def run(state: DDxState) -> DDxState:
    """
    Node: evidence_for_against

    For each candidate diagnosis, asks the LLM to list:
    - supporting features
    - features against / missing
    - potential red flags
    """
    llm = get_traced_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", BASE_SYSTEM_PROMPT),
            ("user", EVIDENCE_FOR_AGAINST_USER),
        ]
    )

    chain = prompt | llm

    case_summary = state["case_summary"]
    cands = state["candidate_diagnoses"]

    result = chain.invoke(
        {
            "case_summary": case_summary,
            # Pass candidates as JSON string so the prompt can embed it nicely
            "candidate_diagnoses": json.dumps(cands),
        }
    )

    evidence = _safe_parse_evidence(result.content)

    new_state: Dict[str, Any] = dict(state)
    new_state["evidence_matrix"] = evidence
    return new_state  # type: ignore[return-value]
