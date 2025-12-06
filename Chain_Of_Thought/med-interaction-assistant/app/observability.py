from typing import Any, Dict, Optional
from contextlib import contextmanager

from langfuse import get_client

# Singleton Langfuse client (configured via env vars)
langfuse = get_client()


@contextmanager
def span_ctx(
    name: str,
    *,
    as_type: str = "span",
    input_data: Optional[Dict[str, Any]] = None,
):
    """
    Convenience context manager for creating a Langfuse span/generation.

    Usage:
        with span_ctx("normalize_input", input_data={...}) as span:
            # do work
            span.update(output={...})
    """
    with langfuse.start_as_current_observation(
        name=name,
        as_type=as_type,  # "span", "generation", "tool", "chain", etc. 
    ) as span:
        if input_data is not None:
            span.update(input=input_data)
        yield span
