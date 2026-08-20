from __future__ import annotations

import sys
import types


def install_ragas_vertexai_compat() -> None:
    """
    Compatibility shim for RAGAS 0.3.9.

    RAGAS imports ChatVertexAI from the legacy
    langchain_community.chat_models.vertexai path.

    Modern LangChain exposes ChatVertexAI through
    langchain_google_vertexai instead.

    This shim maps the legacy module path to the
    modern implementation before importing RAGAS.
    """
    module_name = (
        "langchain_community.chat_models.vertexai"
    )

    if module_name in sys.modules:
        return

    from langchain_google_vertexai import ChatVertexAI

    shim = types.ModuleType(module_name)
    shim.ChatVertexAI = ChatVertexAI

    sys.modules[module_name] = shim
