import logging

logger = logging.getLogger("agentic_react")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def pretty_trace_step(step: dict) -> str:
    return f"[{step.get('type')}] {step.get('content')[:200]}"