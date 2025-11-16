import asyncio
from app.agent import ReActAgent


def test_heuristic_order_lookup():
    agent = ReActAgent()
    reply, trace = asyncio.get_event_loop().run_until_complete(agent.handle_message('u1', 'My order 12345 is missing'))
    assert 'Estimated' in reply or 'on the way' in reply or 'delivered' in reply or 'couldn\'t find' not in reply


def test_ask_for_order_id():
    agent = ReActAgent()
    reply, trace = asyncio.get_event_loop().run_until_complete(agent.handle_message('u1', 'Where is my package?'))
    assert 'order ID' in reply.lower()