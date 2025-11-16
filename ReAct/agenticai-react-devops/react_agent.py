"""Demo runner for the ReAct Agent (DevOps diagnostic example)."""
from agent_core import Agent
from utils.memory import Memory
import tools.cpu_api as cpu_api
import tools.logs_api as logs_api
import tools.notifier as notifier


def tool_adapter():
    # map agent action names to tool callables
    return {
        'get_cpu_metrics': cpu_api.get_cpu_metrics_tool,
        'get_recent_logs': logs_api.get_recent_logs_tool,
        'notify': notifier.notify_tool,
    }


def main():
    tools = tool_adapter()
    memory = Memory()
    agent = Agent(tools=tools, memory=memory)

    # Demo user input
    user_input = "Server slow"
    result = agent.run(user_input)

    print('\n=== FINAL ANALYSIS ===')
    print(result['final'])
    print('\n=== TRANSCRIPT ===')
    for line in result['transcript']:
        print(line)


if __name__ == '__main__':
    main()