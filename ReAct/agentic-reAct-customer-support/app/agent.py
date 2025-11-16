import os
import json
from typing import Tuple, List, Dict, Any, Optional
from .tools.order_service import check_order_status, find_order_id
from .models import ToolResult
from .utils import logger

# Optional OpenAI integration
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

if OPENAI_KEY:
    import openai
    openai.api_key = OPENAI_KEY


class ReActAgent:
    """
    Very small ReAct-style agent:
    - Receives user message
    - Constructs a prompt for the LLM (if available) asking: Reason what to do, choose action
    - Actions supported: check_order_status(order_id)
    - If no LLM key, uses a deterministic heuristic:
        - If message contains order id -> call check_order_status
        - Else ask clarifying question
    Returns tuple (reply, trace) where trace is list of ReAct steps
    """

    def __init__(self):
        self.trace: List[Dict[str, Any]] = []

    async def handle_message(self, user_id: str, message: str) -> Tuple[str, List[Dict[str, Any]]]:
        self.trace = []
        self._add_trace('user', message)

        # Try to find order id
        order_id = find_order_id(message)

        if OPENAI_KEY:
            # Use OpenAI function-calling style to get action from model
            reply, model_trace = await self._handle_with_openai(message, order_id)
            self.trace.extend(model_trace)
            return reply, self.trace
        else:
            reply = await self._deterministic_react(message, order_id)
            return reply, self.trace

    def _add_trace(self, ttype: str, content: str, meta: Optional[dict] = None):
        entry = {"type": ttype, "content": content}
        if meta:
            entry['meta'] = meta
        self.trace.append(entry)

    async def _deterministic_react(self, message: str, order_id: Optional[str]) -> str:
        # Simple reasoning
        self._add_trace('reason', f"Heuristic check: order_id={order_id}")
        if order_id:
            self._add_trace('action', f"check_order_status(order_id={order_id})")
            order = await check_order_status(order_id)
            if order:
                self._add_trace('observation', json.dumps(order.dict(), default=str))
                return self._format_order_reply(order)
            else:
                self._add_trace('observation', f"order {order_id} not found")
                return f"I couldn't find an order with ID {order_id}. Can you double-check the number?"

        # No order id -> ask clarifying question
        self._add_trace('action', 'ask_clarifying')
        return "Can you share your order ID (it is usually a 4–10 digit number) so I can look up the status?"

    async def _handle_with_openai(self, message: str, order_id: Optional[str]) -> Tuple[str, List[Dict[str, Any]]]:
        # Build messages + function schema
        messages = [
            {"role": "system", "content": "You are an assistant that follows the ReAct pattern. You should decide whether to call tools or ask clarifying questions. Use function calls where appropriate."},
            {"role": "user", "content": message}
        ]

        functions = [
            {
                "name": "check_order_status",
                "description": "Check the status of an order by ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "string", "description": "The numeric ID of the order."}
                    },
                    "required": ["order_id"]
                }
            }
        ]

        self._add_trace('reason', f"Calling OpenAI to decide next action. (order_id heuristic: {order_id})")

        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            functions=functions,
            function_call="auto",
            temperature=0.0,
        )

        choice = resp['choices'][0]
        msg = choice['message']
        model_trace = []

        # If model requested the function, call it
        if msg.get('function_call'):
            func_name = msg['function_call']['name']
            args_text = msg['function_call'].get('arguments') or '{}'
            try:
                args = json.loads(args_text)
            except Exception:
                args = {}

            self._add_trace('action', f"{func_name} with args={args}")

            if func_name == 'check_order_status':
                order_id_arg = args.get('order_id')
                order = await check_order_status(order_id_arg)
                if order:
                    observation = order.dict()
                    self._add_trace('observation', json.dumps(observation, default=str))
                    # Ask the model to produce final answer given the observation
                    followup = openai.ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are an assistant that responds to customers based on tool observations."},
                            {"role": "assistant", "content": json.dumps(observation, default=str)},
                            {"role": "user", "content": "Please produce a concise customer-facing reply about this order."}
                        ],
                        temperature=0.0
                    )
                    final = followup['choices'][0]['message']['content']
                    self._add_trace('final_answer', final)
                    return final, []
                else:
                    self._add_trace('observation', f"order {order_id_arg} not found")
                    return f"I couldn't find order {order_id_arg}. Could you confirm the number?", []

        # otherwise, model gave a direct reply
        if msg.get('content'):
            self._add_trace('final_answer', msg['content'])
            return msg['content'], []

        return "Sorry, I couldn't decide what to do.", []

    def _format_order_reply(self, order) -> str:
        if order.status.lower() == 'delivered':
            return f"Your order {order.order_id} was delivered on {order.last_update.split('T')[0]}. If you didn't receive it, please let us know and we'll investigate."
        elif order.status.lower() == 'shipped':
            return f"Order {order.order_id} is on the way. Estimated delivery: {order.eta.split('T')[0]}."
        elif order.status.lower() == 'processing':
            return f"Order {order.order_id} is still processing. We'll update you when it's shipped."
        else:
            return f"Order {order.order_id} status: {order.status}."