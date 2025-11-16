"""Core Agent implementing a minimal ReAct loop.

This intentionally keeps LLM calls out: the agent's `think()` is a placeholder that
mimics chain-of-thought reasoning. Swap `think()` with an LLM call to integrate.
"""
from typing import Any, Dict, List, Optional, Tuple
from utils.memory import Memory
from utils.pretty import print_action, print_thought, print_observation


class Agent:
    def __init__(self, tools: Dict[str, Any], memory: Optional[Memory] = None, max_steps: int = 6):
        self.tools = tools
        self.memory = memory or Memory()
        self.max_steps = max_steps

    def think(self, prompt: str) -> Dict[str, str]:
        """Pretend to reason and decide an action.

        Return structure:
        {
            'thought': '...chain of thought...',
            'action': 'tool_name' or 'finish',
            'action_input': 'argument for the tool' or 'final answer text'
        }
        
        NOTE: Replace this with a real LLM call for production.
        """
        # Very simple heuristic reasoning for the demo.
        thought = "I should check CPU usage first to see if high utilization explains slowness."
        if 'cpu' in prompt.lower() or 'slow' in prompt.lower():
            return {"thought": thought, "action": "get_cpu_metrics", "action_input": "last_5m"}
        # fallback finish
        return {"thought": "I couldn't identify an automated action.", "action": "finish", "action_input": "Manual investigation required."}

    def act(self, action: str, action_input: str) -> Any:
        tool = self.tools.get(action)
        if tool is None:
            return {"error": f"unknown tool: {action}"}
        print_action(action, action_input)
        result = tool(action_input)
        print_observation(result)
        return result

    def run(self, user_input: str) -> Dict[str, Any]:
        self.memory.append_user(user_input)
        step = 0
        final_answer = None

        while step < self.max_steps:
            step += 1
            prompt = self.memory.get_context() + "\nUser: " + user_input
            decision = self.think(prompt)
            thought = decision.get('thought', '')
            print_thought(thought)
            self.memory.append_thought(thought)

            action = decision.get('action')
            action_input = decision.get('action_input', '')

            if action == 'finish' or action == 'final_answer':
                final_answer = action_input
                break

            observation = self.act(action, action_input)
            self.memory.append_observation(observation)

            # Simple policy: if tool returns high CPU, finish with analysis.
            if isinstance(observation, dict) and observation.get('cpu_avg') is not None:
                cpu_avg = observation['cpu_avg']
                if cpu_avg >= 80:
                    final_answer = f"High CPU observed ({cpu_avg}%). Possible cause: CPU-bound process. Suggest: inspect top processes, consider scaling or cgroup limits."
                    break
                else:
                    # if CPU normal but still slow, fetch recent logs
                    if 'logs_api' in self.tools:
                        print('\nCPU is normal, fetching recent logs to look for I/O or errors...')
                        logs = self.act('get_recent_logs', 'last_10m')
                        self.memory.append_observation(logs)
                        # naive log analysis
                        if isinstance(logs, dict) and logs.get('errors'):
                            final_answer = f"Found errors in logs: {logs['errors'][:3]}. Likely application-level issue."
                        else:
                            final_answer = "No obvious CPU or error log cause found. Recommend deeper profiling and network checks."
                        break
            # otherwise continue loop
        return {"final": final_answer, "transcript": self.memory.dump()}