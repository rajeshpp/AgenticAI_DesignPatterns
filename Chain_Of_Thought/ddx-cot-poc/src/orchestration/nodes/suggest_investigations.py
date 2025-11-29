# src/orchestration/nodes/suggest_investigations.py

import json
from typing import Any, Dict, List

from langchain_core.prompts import ChatPromptTemplate

from src.orchestration.state import DDxState
from src.orchestration.prompts import BASE_SYSTEM_PROMPT, SUGGEST_INVESTIGATIONS_USER
from src.llm import get_traced_llm


def _safe_parse_investigations(text: str) -> List[Dict[str, Any]]:
    """
    Expecting JSON like:
    {
      "investigations": [
        {
          "name": "...",
          "why_it_helps": "..."
        }
      ]
    }
    """
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "investigations" in data:
            value = data["investigations"]
            if isinstance(value, list):
                return value
    except json.JSONDecodeError:
        pass
    return []


def run(state: DDxState) -> DDxState:
    """
    Node: suggest_investigations

    Uses the LLM to suggest 3–5 next-best investigations that help
    discriminate between the top candidate diagnoses.
    """
    llm = get_traced_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", BASE_SYSTEM_PROMPT),
            ("user", SUGGEST_INVESTIGATIONS_USER),
        ]
    )

    chain = prompt | llm

    case_summary = state["case_summary"]
    cands = state["candidate_diagnoses"]

    result = chain.invoke(
        {
            "case_summary": case_summary,
            "candidate_diagnoses": json.dumps(cands),
        }
    )

    investigations = _safe_parse_investigations(result.content)

    new_state: Dict[str, Any] = dict(state)
    new_state["suggested_investigations"] = investigations
    return new_state  # type: ignore[return-value]
