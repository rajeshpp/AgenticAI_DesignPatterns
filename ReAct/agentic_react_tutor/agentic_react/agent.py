"""
ReAct-style Agent implementation (structured transcript).

This version builds a structured list of steps with fields:
- 'think' (string): the LLM's THINK output
- 'action' (dict or None): {'tool': tool_name, 'payload': payload} when an action was taken
- 'observation' (any): tool return value (or error) once executed

At the end the agent returns:
{
  "final": bool,
  "final_answer": str,
  "transcript": [step1, step2, ...]
}

This produces a concise ReAct-style output suitable for display to users (no raw history).
"""
from typing import Any, Dict, Callable, List
import json
import re
from .prompt_templates import REACT_INSTRUCTIONS, USER_PROMPT_TEMPLATE

class ReActAgent:
    def __init__(self, llm_adapter, tools: Dict[str, Callable]):
        self.llm = llm_adapter
        self.tools = tools

    def _build_prompt(self, student_profile: Dict[str, str], question: str, history: str) -> str:
        user_prompt = USER_PROMPT_TEMPLATE.format(
            student_name=student_profile.get("name", "Student"),
            level=student_profile.get("level", "beginner"),
            weakness=student_profile.get("weakness", ""),
            question=question,
        )
        prompt = REACT_INSTRUCTIONS + "\n\n" + user_prompt + "\n\nHistory:\n" + history
        return prompt

    def _parse_think_action_final(self, text: str) -> Dict[str, Any]:
        """
        Parse the LLM output into:
        - think: text after THINK: up to ACTION or FINAL_ANSWER
        - action: parsed tool name + payload if present
        - final: final answer if present
        """
        # Extract THINK (optional)
        think_match = re.search(r"THINK:\s*(.*?)(?=(ACTION:|FINAL_ANSWER:|$))", text, re.IGNORECASE | re.DOTALL)
        think = think_match.group(1).strip() if think_match else ""

        # Check FINAL_ANSWER
        final_match = re.search(r"FINAL_ANSWER:\s*(.*)", text, re.IGNORECASE | re.DOTALL)
        if final_match:
            final_answer = final_match.group(1).strip()
            return {"think": think, "type": "final", "final_answer": final_answer}

        # Check ACTION
        action_match = re.search(r"ACTION:\s*([a-zA-Z0-9_]+)\s*\|\s*(.*)", text, re.IGNORECASE | re.DOTALL)
        if action_match:
            tool = action_match.group(1).strip()
            payload_raw = action_match.group(2).strip()
            # Attempt JSON parse, then Python literal eval, else raw string
            payload = None
            if payload_raw:
                try:
                    payload = json.loads(payload_raw)
                except Exception:
                    try:
                        payload = eval(payload_raw, {})
                    except Exception:
                        payload = payload_raw
            return {"think": think, "type": "action", "tool": tool, "payload": payload}
        # Fallback: treat entire text as final answer
        return {"think": think or text.strip(), "type": "final", "final_answer": text.strip()}

    def run(self, student_profile: Dict[str,str], question: str, max_steps: int = 8) -> Dict[str, Any]:
        """
        Run the ReAct loop and return a structured transcript and final answer.
        """
        history = ""
        transcript: List[Dict[str, Any]] = []

        for step in range(max_steps):
            prompt = self._build_prompt(student_profile, question, history)
            llm_out = self.llm.complete(prompt)
            parsed = self._parse_think_action_final(llm_out)

            # Prepare step record
            step_record: Dict[str, Any] = {"think": parsed.get("think", "") , "action": None, "observation": None}

            if parsed["type"] == "final":
                # End the loop with final answer
                final_answer = parsed.get("final_answer", "")
                # append final "think" as last transcript item (no action/observation)
                transcript.append(step_record)
                return {"final": True, "final_answer": final_answer, "transcript": transcript}
            elif parsed["type"] == "action":
                tool_name = parsed.get("tool")
                payload = parsed.get("payload", {})
                step_record["action"] = {"tool": tool_name, "payload": payload}
                # Execute tool
                if tool_name not in self.tools:
                    observation = {"error": f"Unknown tool: {tool_name}"}
                else:
                    try:
                        # Allow both dict payload or raw payload
                        if isinstance(payload, dict):
                            observation = self.tools[tool_name](**payload)
                        else:
                            observation = self.tools[tool_name](payload)
                    except Exception as e:
                        observation = {"error": str(e)}
                step_record["observation"] = observation
                # Append to transcript and history (history still a plain string for prompt)
                transcript.append(step_record)
                history += f"LLM: {llm_out}\n"
                history += f"OBSERVATION from {tool_name}: {observation}\n"
                continue
            else:
                # Unexpected case: treat as final with content
                final_answer = llm_out.strip()
                transcript.append(step_record)
                return {"final": True, "final_answer": final_answer, "transcript": transcript}

        # If we exhaust steps without final answer
        return {"final": False, "final_answer": "Could not reach final answer in allotted steps.", "transcript": transcript}
