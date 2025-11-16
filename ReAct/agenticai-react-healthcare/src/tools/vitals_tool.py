from typing import Dict

class VitalsTool:
    """Mock vitals check. In real life this would query an EHR or IoT vitals service."""
    def fetch_vitals(self, patient_id: str) -> Dict[str, float]:
        # Mocked data; in production replace with a DB/EHR call
        # Return keys: temperature (C), heart_rate, respiratory_rate, systolic_bp, diastolic_bp
        mocked = {
            "temperature": 38.5,
            "heart_rate": 110,
            "respiratory_rate": 20,
            "systolic_bp": 120,
            "diastolic_bp": 78,
        }
        return mocked