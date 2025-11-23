# src/models/services.py
from abc import ABC, abstractmethod
from .domain import VitalReading


class NotificationService(ABC):
    @abstractmethod
    def send(self, *, to_nurse: str | None = None,
             to_role: str | None = None,
             message: str) -> None:
        ...


class EHRClient(ABC):
    @abstractmethod
    def write_vital(self, vital: VitalReading) -> None:
        ...


class ConsoleNotificationService(NotificationService):
    def send(self, *, to_nurse: str | None = None,
             to_role: str | None = None,
             message: str) -> None:
        target = to_nurse or to_role or "unknown"
        print(f"[NOTIFY -> {target}] {message}")


class DummyEHRClient(EHRClient):
    def write_vital(self, vital: VitalReading) -> None:
        print(f"[EHR] Recorded vital for patient {vital.patient_id} at {vital.timestamp}")
