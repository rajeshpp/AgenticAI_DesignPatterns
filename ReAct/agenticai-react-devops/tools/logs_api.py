"""Mock logs fetcher that returns structured logs and some detected errors."""
from typing import Dict


def get_recent_logs(interval: str = "last_10m") -> Dict[str, any]:
    # For demo, sometimes return errors
    errors = []
    if interval == 'last_10m':
        errors = ["TimeoutError connecting to db", "ValueError: invalid payload"]
    return {"ok": True, "interval": interval, "logs_count": 120, "errors": errors}


def get_recent_logs_tool(arg: str):
    return get_recent_logs(arg)