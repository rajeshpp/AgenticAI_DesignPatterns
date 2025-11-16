"""Mock CPU metrics tool. In real life this would query Prometheus, CloudWatch, or an agent endpoint."""
import random
from typing import Dict


def get_cpu_metrics(interval: str = "last_5m") -> Dict[str, float]:
    # Simulate CPU average from 10% to 95%
    cpu_avg = random.choice([25, 30, 45, 78, 85, 92])
    return {"ok": True, "interval": interval, "cpu_avg": cpu_avg}

# exported name matches agent expectation
def get_cpu_metrics_tool(arg: str):
    return get_cpu_metrics(arg)