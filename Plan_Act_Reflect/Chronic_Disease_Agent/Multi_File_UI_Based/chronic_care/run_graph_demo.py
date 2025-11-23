# run_graph_demo.py
from __future__ import annotations

import os
import sys

# Ensure the Multi_File_Based `chronic_care` package is importable when running
# this script from the `Multi_File_UI_Based/chronic_care` folder. We add the
# sibling `Multi_File_Based` directory to `sys.path` if it exists.
here = os.path.dirname(__file__)
# parent of `here` is `Multi_File_UI_Based`; we want the Chronic_Disease_Agent folder
chronic_agent_root = os.path.dirname(os.path.dirname(here))
multi_based = os.path.join(chronic_agent_root, "Multi_File_Based")
if os.path.isdir(os.path.join(multi_based, "chronic_care")) and multi_based not in sys.path:
    sys.path.insert(0, multi_based)

from langgraph_app import graph, CoachState

try:
    # Prefer reused helper from the package implementation when available
    from chronic_care.demo import build_fake_yesterday
except Exception:
    # Fallback to a local demo.py if present (or raise the original import error)
    from demo import build_fake_yesterday  # type: ignore


def main() -> None:
    yesterday_state = build_fake_yesterday()

    # For the POC, let's simulate "live" readings as a couple of values
    live_readings = yesterday_state.glucose_readings[-2:]  # last 2 readings as example

    initial = CoachState(
        patient_state=yesterday_state,
        live_readings=live_readings,
    )

    result = graph.invoke(initial)

    print("\n=== LangGraph result state ===")
    print(f"Plan date: {result['plan'].date}")
    print(f"Actions count: {len(result['actions'])}")
    print("Reflection:")
    for line in result["reflection"].what_worked:
        print(f"  ✓ {line}")
    for line in result["reflection"].what_didnt:
        print(f"  ✗ {line}")

    updated_profile = result["patient_state"].profile
    print("\nUpdated profile:")
    print(f"  Post-meal walk minutes: {updated_profile.post_meal_walk_minutes}")
    print(
        f"  Expected walk effect: "
        f"{updated_profile.expected_walk_glucose_drop_pct * 100:.1f}%"
    )


if __name__ == "__main__":
    main()
