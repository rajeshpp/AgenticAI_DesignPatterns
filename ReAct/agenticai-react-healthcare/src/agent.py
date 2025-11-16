from typing import Dict, Any, Optional
from .utils.logger import logger
from .utils.types import PatientData

class ReActAgent:
    """A small ReAct-style agent for healthcare triage.

    Pattern: observe -> reason -> act -> observe -> finish
    Reasoning is logged (but not 'private chain-of-thought').
    Tools are only used from the environment passed in.
    """

    def __init__(self, environment):
        self.env = environment

    def _reason(self, observations: Dict[str, Any]) -> str:
        """Formulate reasoning based on observations. Keep it explainable."""
        temp = observations.get("temperature")
        hr = observations.get("heart_rate")
        reasons = []
        if temp is not None:
            reasons.append(f"Temp={temp}C")
        if hr is not None:
            reasons.append(f"HR={hr}bpm")
        reason_str = "; ".join(reasons)
        logger.debug(f"[Reason] Based on observations: {reason_str}")
        # simple symbolic reasoning decision
        if temp >= 40 or hr >= 130:
            return "RED"
        if temp >= 38 and hr >= 100:
            return "YELLOW"
        if temp < 38:
            return "GREEN"
        return "UNKNOWN"

    def act(self, patient: PatientData) -> Dict[str, Any]:
        logger.info(f"Starting ReAct loop for patient {patient.patient_id}")

        # Observe (initial): symptoms provided
        logger.debug(f"Observations (symptoms): {patient.symptoms}")

        # Action: fetch vitals
        vitals = self.env.get_vitals(patient.patient_id)
        logger.info(f"Fetched vitals: {vitals}")

        # Reason
        decision_level = self._reason(vitals)

        # Consult external guidelines tool for supporting text
        guideline_text = self.env.consult_guidelines(vitals)
        logger.info(f"Guideline says: {guideline_text}")

        result = {"patient_id": patient.patient_id, "vitals": vitals, "level": decision_level, "guideline": guideline_text}

        # Act (if necessary): schedule followup for YELLOW cases
        if decision_level == "YELLOW":
            followup = self.env.book_followup(patient.patient_id, when="24 hours")
            logger.info(f"Follow-up booked: {followup}")
            result["followup"] = followup

        if decision_level == "RED":
            result["action"] = "Refer to emergency department immediately"

        if decision_level == "GREEN":
            result["action"] = "Home care: paracetamol, rest, fluids, monitor"

        logger.info(f"Final result: {result}")
        return result