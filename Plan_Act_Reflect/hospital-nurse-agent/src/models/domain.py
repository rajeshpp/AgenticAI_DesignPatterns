# src/models/domain.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class TaskType(str, Enum):
    CHECK_VITALS = "check_vitals"
    MEDICATION = "medication"
    DOCUMENTATION = "documentation"
    ESCALATION = "escalation"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


@dataclass
class Patient:
    id: str
    name: str
    room: str
    risk_score: float  # 0–1


@dataclass
class VitalReading:
    patient_id: str
    timestamp: datetime
    heart_rate: int
    spo2: int
    systolic_bp: int
    diastolic_bp: int


@dataclass
class NursePreferences:
    nurse_id: str
    prefers_batch_documentation: bool = True
    max_concurrent_tasks: int = 3
    documentation_weight: float = 0.8  # <1 => documentation is painful


@dataclass
class Task:
    id: str
    patient_id: Optional[str]
    nurse_id: str
    task_type: TaskType
    description: str
    due_at: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)
    priority: float = 0.0
    status: TaskStatus = TaskStatus.PENDING
