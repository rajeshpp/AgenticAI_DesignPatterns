from typing import Dict, Any
from pydantic import BaseModel

class PatientData(BaseModel):
    patient_id: str
    age: int
    symptoms: Dict[str, Any]
    vitals: Dict[str, float] = {}