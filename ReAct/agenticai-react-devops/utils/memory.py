"""Simple in-memory transcript memory for the demo."""
from typing import List, Any


class Memory:
    def __init__(self):
        self.transcript: List[str] = []

    def append_user(self, text: str):
        self.transcript.append(f"User: {text}")

    def append_thought(self, text: str):
        self.transcript.append(f"Thought: {text}")

    def append_observation(self, obs: Any):
        self.transcript.append(f"Observation: {repr(obs)}")

    def get_context(self) -> str:
        return "\n".join(self.transcript[-10:])

    def dump(self) -> List[str]:
        return list(self.transcript)