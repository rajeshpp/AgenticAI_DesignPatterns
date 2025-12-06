from typing import List, Dict, Any
import json

from openai import OpenAI
from langgraph.graph import StateGraph, END

from .state import MedInteractionState
from .rules import (
    MED_NORMALIZATION,
    COMORBIDITY_NORMALIZATION,
    INTERACTION_RULES,
)
from .config import settings
from .observability import span_ctx, langfuse

client = OpenAI(api_key=settings.openai_api_key)


# ---------- Node: normalize_input ----------

def normalize_input(state: MedInteractionState) -> MedInteractionState:
    with span_ctx(
        "normalize_input",
        input_data={
            "medications": state.get("medications", []),
            "comorbidities": state.get("comorbidities", []),
        },
    ) as span:
        meds = state.get("medications", []) or []
        comorbs = state.get("comorbidities", []) or []

        normalized_meds: List[str] = []
        for m in meds:
            key = m.strip().lower()
            norm = MED_NORMALIZATION.get(key, key)
            normalized_meds.append(norm)

        normalized_comorbs: List[str] = []
        for c in comorbs:
            key = c.strip().lower()
            norm = COMORBIDITY_NORMALIZATION.get(key, key)
            normalized_comorbs.append(norm)

        state["normalized_meds"] = normalized_meds
        state["normalized_comorbidities"] = normalized_comorbs

        span.update(
            output={
                "normalized_meds": normalized_meds,
                "normalized_comorbidities": normalized_comorbs,
            }
        )

    return state


# ---------- Node: find_interactions ----------

def find_interactions(state: MedInteractionState) -> MedInteractionState:
    with span_ctx(
        "find_interactions",
        input_data={
            "normalized_meds": state.get("normalized_meds", []),
            "normalized_comorbidities": state.get("normalized_comorbidities", []),
        },
    ) as span:
        meds = set(state.get("normalized_meds", []) or [])
        comorbs = set(state.get("normalized_comorbidities", []) or [])

        candidates: List[Dict[str, Any]] = []

        for rule in INTERACTION_RULES:
            a = rule["drug_a"]
            b = rule["drug_b"]

            if (
                (a in meds and b in meds)
                or (a in meds and b in comorbs)
                or (a in comorbs and b in meds)
            ):
                candidates.append(
                    {
                        "rule_id": rule["id"],
                        "pair": (a, b),
                        "base_severity": rule["base_severity"],
                        "rule_notes": rule["notes"],
                    }
                )

        state["interaction_candidates"] = candidates

        span.update(output={"interaction_candidates": candidates})

    return state


# ---------- Helper: LLM call with generation observation ----------

def _call_llm_for_explanations(
    candidates: List[Dict[str, Any]],
    original_meds: List[str],
    comorbidities: List[str],
) -> List[Dict[str, Any]]:
    system_prompt = (
        "You are a clinical pharmacist assistant that explains potential medication "
        "interactions for clinicians. You are cautious, concise, and always emphasize "
        "that your output is not a substitute for clinical judgment."
    )

    user_prompt = f"""
You are given:
- A patient's medication list: {original_meds}
- Comorbidities: {comorbidities}
- Interaction candidates (from a simple rules engine): {candidates}

Think step-by-step in your own mind, then ONLY output valid JSON with this schema:

{{
  "interactions": [
    {{
      "pair": {{
        "drug_a": "string",
        "drug_b": "string"
      }},
      "mechanism": "string",
      "clinical_consequences": "string",
      "severity": "minor | moderate | major | contraindicated | unknown",
      "monitoring_and_mitigation": "string",
      "safer_alternatives": "string",
      "notes_for_clinician": "string"
    }}
  ]
}}

Rules:
1. Start from the provided candidates, but you may add or drop a pair if clearly wrong.
2. In mechanism, describe enzyme systems or pharmacodynamic effects if known.
3. In clinical_consequences, focus on real-world outcomes.
4. In monitoring_and_mitigation, give specific steps.
5. In safer_alternatives, mention high-level options.
6. Severity should align with common clinical references, but it is approximate.
7. notes_for_clinician must start with:
   "Use this as a decision-support aid only, not a final recommendation.".
"""

    # Generation-type observation (specialized for LLM calls) 
    with langfuse.start_as_current_observation(
        name="interaction_reasoning_llm",
        as_type="generation",
    ) as gen:
        gen.update(
            input={
                "system": system_prompt,
                "user": user_prompt,
            },
            model=settings.openai_model,
            metadata={"component": "reason_about_interactions"},
        )

        resp = client.chat.completions.create(
            model=settings.openai_model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )

        content = resp.choices[0].message.content or "{}"

        # If usage is available, you can attach it:
        usage_details = None
        if getattr(resp, "usage", None):
            usage_details = {
                "input_tokens": resp.usage.prompt_tokens,
                "output_tokens": resp.usage.completion_tokens,
            }

        gen.update(
            output=content,
            usage_details=usage_details,
        )

    parsed = json.loads(content)
    return parsed.get("interactions", [])


# ---------- Node: reason_about_interactions ----------

def reason_about_interactions(state: MedInteractionState) -> MedInteractionState:
    with span_ctx(
        "reason_about_interactions",
        input_data={
            "interaction_candidates": state.get("interaction_candidates", []),
        },
    ) as span:
        candidates = state.get("interaction_candidates", []) or []
        if not candidates:
            state["interaction_explanations"] = []
            span.update(output={"interaction_explanations": []})
            return state

        original_meds = state.get("medications", []) or []
        comorbidities = state.get("comorbidities", []) or []

        explanations = _call_llm_for_explanations(
            candidates=candidates,
            original_meds=original_meds,
            comorbidities=comorbidities,
        )
        state["interaction_explanations"] = explanations

        span.update(output={"interaction_explanations": explanations})

    return state


# ---------- Node: format_result ----------

def format_result(state: MedInteractionState) -> MedInteractionState:
    with span_ctx(
        "format_result",
        input_data={
            "interaction_explanations": state.get("interaction_explanations", []),
        },
    ) as span:
        interactions = state.get("interaction_explanations", []) or []
        simple_list = []

        for inter in interactions:
            pair = inter.get("pair", {}) or {}
            drug_a = pair.get("drug_a", "?")
            drug_b = pair.get("drug_b", "?")

            label = f"{drug_a} + {drug_b}"
            simple_list.append(
                {
                    "label": label,
                    "severity": inter.get("severity"),
                    "mechanism": inter.get("mechanism"),
                    "clinical_consequences": inter.get("clinical_consequences"),
                    "monitoring_and_mitigation": inter.get(
                        "monitoring_and_mitigation"
                    ),
                }
            )

        state["result"] = {
            "medications": state.get("medications", []),
            "comorbidities": state.get("comorbidities", []),
            "count_flagged_interactions": len(interactions),
            "interactions": interactions,
            "summary_list": simple_list,
            "disclaimer": (
                "Prototype decision-support tool. Not complete, not validated, "
                "and not a substitute for a clinical pharmacist or clinician judgment."
            ),
        }

        span.update(output={"result": state["result"]})

    return state


# ---------- Build & export the compiled graph ----------

def build_graph():
    workflow = StateGraph(MedInteractionState)

    workflow.add_node("normalize_input", normalize_input)
    workflow.add_node("find_interactions", find_interactions)
    workflow.add_node("reason_about_interactions", reason_about_interactions)
    workflow.add_node("format_result", format_result)

    workflow.set_entry_point("normalize_input")
    workflow.add_edge("normalize_input", "find_interactions")

    def should_reason(state: MedInteractionState) -> str:
        if state.get("interaction_candidates"):
            return "reason"
        return "skip"

    workflow.add_conditional_edges(
        "find_interactions",
        should_reason,
        {
            "reason": "reason_about_interactions",
            "skip": "format_result",
        },
    )

    workflow.add_edge("reason_about_interactions", "format_result")
    workflow.add_edge("format_result", END)

    return workflow.compile()


graph = build_graph()
