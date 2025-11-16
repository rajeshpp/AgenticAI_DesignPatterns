from typing import Dict

class GuidelinesTool:
    """Simple guideline lookup. Replaceable with a clinical knowledge base."""
    def lookup(self, findings: Dict[str, float]) -> str:
        temp = findings.get("temperature", 0)
        hr = findings.get("heart_rate", 0)
        if temp >= 40 or hr >= 130:
            return "RED: Immediate ED referral."
        if temp >= 38 and hr >= 100:
            return "YELLOW: Consider urgent telehealth / clinician review within 24 hours."
        if temp < 38:
            return "GREEN: Home care & symptomatic treatment."
        return "UNKNOWN: Monitor and re-evaluate."