from pydantic import BaseModel
from typing import Optional

class Order(BaseModel):
    order_id: str
    status: str
    eta: Optional[str] = None
    last_update: Optional[str] = None

class ToolResult(BaseModel):
    tool: str
    success: bool
    payload: dict