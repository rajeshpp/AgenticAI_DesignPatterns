# src/main.py
from infra.init_state import initial_state
from agents.orchestration import run_plan_act_cycle, run_reflect_cycle

if __name__ == "__main__":
    state = initial_state()
    print("=== Initial State ===")
    print(state["events"])

    state = run_plan_act_cycle(state)
    print("=== After Plan & Act ===")
    for t in state["tasks"]:
        print(t)

    state = run_reflect_cycle(state)
    print("=== After Reflect ===")
    for e in state["events"]:
        print(e)
