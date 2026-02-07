"""
Prompt management for loading and formatting prompts from YAML configuration.
"""
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from functools import lru_cache

from backend.app.core.logging import get_logger

logger = get_logger(__name__)


class PromptManager:
    """Manages loading and formatting of prompts from YAML configuration."""
    
    def __init__(self, config_path: str):
        """
        Initialize prompt manager.
        
        Args:
            config_path: Path to prompts YAML configuration file
        """
        self.config_path = Path(config_path)
        self.prompts = self._load_prompts()
        logger.info(f"Prompt manager initialized from: {config_path}")
    
    def _load_prompts(self) -> Dict[str, Any]:
        """
        Load prompts from YAML configuration.
        
        Returns:
            Dict: Loaded prompts configuration
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                prompts = yaml.safe_load(f)
            logger.info("Prompts loaded successfully")
            return prompts
        except Exception as e:
            logger.error(f"Failed to load prompts: {e}")
            return self._get_default_prompts()
    
    def _get_default_prompts(self) -> Dict[str, Any]:
        """Get default prompts as fallback."""
        return {
            "system_prompt": {
                "role": "You are an expert on the 37signals employee handbook.",
                "instructions": [
                    "Use only the provided context.",
                    "If information is not available, say you don't know."
                ]
            },
            "rag_template": "{role}\n\n{instructions}\n\nCONTEXT:\n{context}\n\nQUESTION:\n{question}\n\nANSWER:"
        }
    
    def format_context(
        self, 
        documents: List[Dict[str, Any]]
    ) -> str:
        """
        Format retrieved documents into context string.
        
        Args:
            documents: List of retrieved documents with content and metadata
            
        Returns:
            str: Formatted context string
        """
        config = self.prompts.get("context_formatting", {})
        doc_template = config.get("document_template", "[Doc {index}]\n{content}")
        separator = config.get("separator", "\n---\n")
        
        formatted_docs = []
        for idx, doc in enumerate(documents, 1):
            content = doc.get("content", "")
            source = doc.get("metadata", {}).get("source", "unknown")
            section = doc.get("metadata", {}).get("Header 1", "")
            
            formatted = doc_template.format(
                index=idx,
                source=source,
                section=f"Section: {section}\n" if section else "",
                content=content
            )
            formatted_docs.append(formatted)
        
        return separator.join(formatted_docs)
    
    def build_prompt(
        self,
        question: str,
        context_documents: List[Dict[str, Any]]
    ) -> str:
        """
        Build complete LLM prompt from template, context, and question.
        
        The prompt includes:
        - System role and instructions
        - Formatted context from retrieved documents
        - User's question
        
        Args:
            question: User's natural language question
            context_documents: List of retrieved documents with content and metadata
            
        Returns:
            str: Complete formatted prompt ready for LLM inference
        """
        # Get system prompt (simplified - only one prompt type)
        system_prompt = self.prompts.get("system_prompt", {})
        
        role = system_prompt.get("role", "")
        instructions = system_prompt.get("instructions", [])
        instructions_text = "\n".join(f"{i+1}. {inst}" for i, inst in enumerate(instructions))
        
        # Format context
        context = self.format_context(context_documents)
        
        # Get template
        template = self.prompts.get("rag_template", "")
        
        # Build final prompt
        prompt = template.format(
            role=role,
            instructions=instructions_text,
            context=context,
            question=question
        )
        
        return prompt
    
    def get_no_context_message(self) -> str:
        """Get message for when no relevant context is found."""
        retrieval_config = self.prompts.get("retrieval", {})
        return retrieval_config.get(
            "no_context_message",
            "No information found in the handbook regarding this question."
        )
    
    def reload(self):
        """Reload prompts from configuration file."""
        logger.info("Reloading prompts configuration...")
        self.prompts = self._load_prompts()


@lru_cache()
def get_prompt_manager(config_path: Optional[str] = None) -> PromptManager:
    """
    Get cached prompt manager instance.
    
    Args:
        config_path: Path to prompts configuration
        
    Returns:
        PromptManager: Prompt manager instance
    """
    from backend.app.core.config import get_settings
    
    if config_path is None:
        settings = get_settings()
        config_path = settings.prompts_config_path
    
    return PromptManager(config_path)
