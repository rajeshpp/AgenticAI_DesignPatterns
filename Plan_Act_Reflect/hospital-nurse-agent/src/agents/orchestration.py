# src/agents/orchestration.py
from models.state import AgentState
from models.services import ConsoleNotificationService, DummyEHRClient
from .planner import PlannerAgent
from .act import ActAgent
from .reflect import ReflectAgent


planner = PlannerAgent()
act_agent = ActAgent(ConsoleNotificationService(), DummyEHRClient())
reflector = ReflectAgent()


def run_plan_act_cycle(state: AgentState) -> AgentState:
    """Plan then Act – typical real-time cycle."""
    state = planner.plan(state)
    state = act_agent.act(state)
    return state


def run_reflect_cycle(state: AgentState) -> AgentState:
    """Reflect – run at end-of-shift or on-demand."""
    state = reflector.reflect(state)
    return state
