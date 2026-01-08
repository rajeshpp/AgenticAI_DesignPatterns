from pydantic import BaseModel, Field
from typing import List


class ClinicalNote(BaseModel):
    note_type: str = Field(description="SOAP / Discharge / Progress")
    content: str


class CriticFinding(BaseModel):
    issue: str
    severity: str  # low | medium | high


class CriticReport(BaseModel):
    findings: List[CriticFinding]
    summary: str
    confidence_score: float


class FinalOutput(BaseModel):
    final_note: str
    critic_report: CriticReport
    audit_trail: List[str]
