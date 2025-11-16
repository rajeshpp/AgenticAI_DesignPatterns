"""Small auxiliary calculator tool for the agent to do math or thresholds."""

def is_vol_high(vol: float, threshold: float = 0.3) -> bool:
    return vol >= threshold


def recommend_action_by_vol(vol: float) -> str:
    if vol >= 0.5:
        return "consider significant de-risking or hedging"
    if vol >= 0.3:
        return "consider trimming positions or add hedges"
    if vol >= 0.15:
        return "volatility moderate — monitor"
    return "low volatility — no immediate action"