def escalate(alerts):
    if alerts:
        return {
            "level": "HIGH",
            "action": "Notify clinician and patient immediately"
        }

    return {
        "level": "LOW",
        "action": "Continue routine monitoring"
    }
