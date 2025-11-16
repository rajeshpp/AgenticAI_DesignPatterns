from typing import Optional
from ..models import Order
from datetime import datetime, timedelta

# Mock "database" of orders
_ORDERS = {
    "12345": Order(order_id="12345", status="shipped", eta=(datetime.utcnow() + timedelta(days=2)).isoformat(), last_update=datetime.utcnow().isoformat()),
    "54321": Order(order_id="54321", status="delivered", eta=(datetime.utcnow() - timedelta(days=1)).isoformat(), last_update=(datetime.utcnow() - timedelta(days=1)).isoformat()),
    "99999": Order(order_id="99999", status="processing", eta=None, last_update=datetime.utcnow().isoformat()),
}

async def check_order_status(order_id: str) -> Optional[Order]:
    # In a real integration you'd call your DB or external API here.
    return _ORDERS.get(order_id)

# Helper for searching order id in text (very simple heuristic)
import re

def find_order_id(text: str) -> Optional[str]:
    m = re.search(r"\b(\d{4,10})\b", text)
    if m:
        return m.group(1)
    return None