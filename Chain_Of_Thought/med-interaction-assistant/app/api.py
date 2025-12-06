from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from .graph import graph
from .state import MedInteractionState
from .observability import langfuse, span_ctx

app = FastAPI(
    title="Medication Interaction Reasoning Assistant (POC)",
    version="0.1.0",
)


class MedRequest(BaseModel):
    medications: List[str]
    comorbidities: List[str] = []


class MedResponse(BaseModel):
    medications: List[str]
    comorbidities: List[str]
    count_flagged_interactions: int
    interactions: list
    summary_list: list
    disclaimer: str


@app.post("/interactions", response_model=MedResponse)
def get_interactions(req: MedRequest):
    """
    Main endpoint: creates a Langfuse root span (trace),
    runs the LangGraph, and attaches the final result.
    """
    # Root span = root observation -> becomes the trace root
    with span_ctx(
        "med-interaction-request",
        input_data=req.model_dump(),
    ) as root_span:
        # Optional: attach trace-level metadata (shows on trace in Langfuse UI)
        root_span.update_trace(
            metadata={
                "medications": req.medications,
                "comorbidities": req.comorbidities,
                "source": "fastapi",
            }
        )

        initial_state: MedInteractionState = {
            "medications": req.medications,
            "comorbidities": req.comorbidities,
        }

        final_state = graph.invoke(initial_state)

        root_span.update(output=final_state.get("result"))

        return final_state["result"]
