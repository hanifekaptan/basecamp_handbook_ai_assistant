"""
LLM client for interacting with Ollama and generating responses.
"""
import ollama
from typing import AsyncGenerator, List, Dict, Any
import asyncio

from backend.app.core.config import get_settings
from backend.app.core.logging import get_logger
from backend.app.llm.prompt_manager import get_prompt_manager

logger = get_logger(__name__)


class LLMClient:
    """Client for interacting with local LLM via Ollama."""
    
    def __init__(self):
        """Initialize Ollama client and prompt manager."""
        self.settings = get_settings()
        self.client = ollama.AsyncClient(host=self.settings.ollama_base_url)
        self.prompt_manager = get_prompt_manager()
        logger.info(f"Ollama client initialized: {self.settings.ollama_base_url}")
    
    async def check_availability(self) -> bool:
        """
        Check if Ollama service is running and the configured model is available.
        
        Returns:
            bool: True if service is reachable and model is loaded, False otherwise
            
        Note:
            Logs warning if model is not found with list of available models.
        """
        try:
            # Try to list models
            models = await self.client.list()
            model_names = [model['name'] for model in models.get('models', [])]
            
            # Check if our model is available
            is_available = any(
                self.settings.ollama_model in name 
                for name in model_names
            )
            
            if not is_available:
                logger.warning(
                    f"Model {self.settings.ollama_model} not found. "
                    f"Available models: {model_names}"
                )
            else:
                logger.debug(f"Model {self.settings.ollama_model} is available")
            
            return is_available
        except Exception as e:
            logger.error(f"Ollama availability check failed: {e}")
            return False
    
    async def generate_answer(
        self, 
        question: str, 
        context_documents: List[Dict[str, Any]]
    ) -> str:
        """
        Generate answer using LLM with RAG context (non-streaming).
        
        Args:
            question: User's question in natural language
            context_documents: Retrieved documents with content and metadata
            
        Returns:
            str: Generated answer text
            
        Raises:
            Exception: If LLM generation fails
        """
        # Build prompt using prompt manager
        prompt = self.prompt_manager.build_prompt(
            question=question,
            context_documents=context_documents
        )
        
        try:
            logger.info(f"Generating answer for question: {question[:100]}...")
            
            response = await self.client.generate(
                model=self.settings.ollama_model,
                prompt=prompt,
                options={
                    'temperature': self.settings.temperature,
                    'num_predict': 512,
                }
            )
            
            answer = response.get('response', '').strip()
            logger.info("Answer generated successfully")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}", exc_info=True)
            raise Exception(f"LLM generation failed: {str(e)}")
    
    async def generate_answer_stream(
        self, 
        question: str, 
        context_documents: List[Dict[str, Any]]
    ) -> AsyncGenerator[str, None]:
        """
        Generate answer using LLM with streaming response (token-by-token).
        
        Args:
            question: User's question in natural language
            context_documents: Retrieved documents with content and metadata
            
        Yields:
            str: Generated answer chunks (individual tokens or small text pieces)
            
        Raises:
            Exception: If streaming fails (yields error message instead)
        """
        # Build prompt using prompt manager
        prompt = self.prompt_manager.build_prompt(
            question=question,
            context_documents=context_documents
        )
        
        try:
            logger.info(f"Generating streaming answer for: {question[:100]}...")
            
            stream = await self.client.generate(
                model=self.settings.ollama_model,
                prompt=prompt,
                stream=True,
                options={
                    'temperature': self.settings.temperature,
                    'num_predict': 512,
                }
            )
            
            async for chunk in stream:
                if 'response' in chunk:
                    yield chunk['response']
            
            logger.info("Streaming answer completed")
            
        except Exception as e:
            logger.error(f"Error in streaming generation: {e}", exc_info=True)
            yield f"\n\n[Error: {str(e)}]"
