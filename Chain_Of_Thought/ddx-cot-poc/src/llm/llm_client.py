# src/llm/llm_client.py

import logging
from typing import List, Optional

from langchain_openai import ChatOpenAI

from src.config.settings import OPENAI_API_KEY

logger = logging.getLogger(__name__)


# Try to set up Langfuse integration (optional) — be explicit about failures so
# users can see why tracing is disabled.
langfuse_client = None
langfuse_handler = None
CALLBACKS: List = []
try:
    from langfuse import get_client
    # The langfuse.langchain integration requires the "langchain" package to be
    # installed. If it's missing, the import below will raise and we will report
    # the reason rather than silently swallowing the error.
    from langfuse.langchain import CallbackHandler

    # Initialize Langfuse client (not strictly required for CallbackHandler in
    # some setups, but useful if you want to use the client elsewhere)
    try:
        langfuse_client = get_client()
    except Exception as e:
        logger.warning("langfuse.get_client() failed, tracing may not be active: %s", e)
        langfuse_client = None

    # This handler is what LangChain / LangGraph will use for tracing
    try:
        # Prefer attaching the client if available — some versions of
        # langfuse.langchain.CallbackHandler may not accept a `client` arg,
        # so try both ways and fall back gracefully.
        if langfuse_client:
            try:
                langfuse_handler: Optional[CallbackHandler] = CallbackHandler(client=langfuse_client)
            except TypeError:
                # older/newer versions may not accept `client`; use no-arg constructor
                logger.debug("CallbackHandler(client=...) not supported, falling back to no-arg constructor")
                langfuse_handler = CallbackHandler()
        else:
            langfuse_handler = CallbackHandler()
        CALLBACKS = [langfuse_handler]
        logger.info("Langfuse tracing enabled via CallbackHandler=%s", type(langfuse_handler))
    except Exception as e:
        logger.exception("Failed to create Langfuse CallbackHandler, will run without tracing: %s", e)
        langfuse_handler = None
        CALLBACKS = []
except ModuleNotFoundError as err:
    # Known failure: missing 'langchain' package required by langfuse.langchain
    logger.warning(
        "Langfuse langchain integration not available: %s — please install 'langchain' to enable tracing",
        err,
    )
except Exception as err:  # pragma: no cover - defensive logging
    logger.warning("Unexpected error while initializing Langfuse integration: %s", err)


def get_traced_llm() -> ChatOpenAI:
    """
    Return a ChatOpenAI model.

    - If Langfuse is available, the model will use Langfuse's CallbackHandler
      for tracing (via CALLBACKS).
    - If not, it will just run without callbacks.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set in environment/.env")

    llm = ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0.2,
        api_key=OPENAI_API_KEY,
        callbacks=CALLBACKS,
    )
    return llm
