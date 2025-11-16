"""A tiny notifier mock to demonstrate side-effects (e.g., send alert)."""

def notify_team(message: str) -> dict:
    # In production, integrate with Slack, PagerDuty or e-mail.
    print(f"[notifier] alert -> {message}")
    return {"ok": True, "message": message}


def notify_tool(arg: str):
    return notify_team(arg)