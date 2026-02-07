"""
LLM module for Ollama client and prompt management.
"""
from backend.app.llm.client import LLMClient
from backend.app.llm.prompt_manager import PromptManager, get_prompt_manager

__all__ = [
    "LLMClient",
    "PromptManager",
    "get_prompt_manager",
]
