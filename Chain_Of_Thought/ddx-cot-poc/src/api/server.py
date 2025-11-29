from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Any, Dict

from src.orchestration import build_ddx_graph

app = FastAPI(title="DDx CoT Explainer (POC)")
graph = build_ddx_graph()


class PatientCase(BaseModel):
    age: int | None = Field(None, example=65)
    sex: str | None = Field(None, example="male")
    chief_complaint: str | None = Field(
        None, example="fever and pleuritic chest pain"
    )
    symptoms: str | None = Field(
        None, example="fever, productive cough, pleuritic chest pain"
    )
    vitals: str | None = Field(
        None, example="RR 28, SpO2 90%, HR 102, BP 130/80"
    )
    labs: str | None = None
    history: str | None = Field(
        None, example="No known chronic lung disease documented."
    )
    notes: str | None = Field(
        None, example="Crackles in right lower lung field on auscultation."
    )


class DDXResponse(BaseModel):
    output: Dict[str, Any]


@app.post("/ddx", response_model=DDXResponse)
def ddx_endpoint(case: PatientCase):
    """
    Simple synchronous endpoint for the DDx graph.
    """
    state = {"patient_case": case.dict(exclude_none=True)}
    result_state = graph.invoke(state)
    return DDXResponse(output=result_state["final_output"])
