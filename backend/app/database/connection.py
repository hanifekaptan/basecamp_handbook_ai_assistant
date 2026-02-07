"""
ChromaDB database connection and management.
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from pathlib import Path
from typing import Optional

from backend.app.core.logging import get_logger
from backend.app.core.config import get_settings

logger = get_logger(__name__)


class ChromaDBConnection:
    """Manages ChromaDB client connection and lifecycle."""
    
    _instance: Optional['ChromaDBConnection'] = None
    _client: Optional[chromadb.ClientAPI] = None
    
    def __new__(cls):
        """Singleton pattern to ensure single database connection."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize database connection."""
        if self._client is None:
            self._connect()
    
    def _connect(self):
        """Establish connection to ChromaDB."""
        settings = get_settings()
        persist_dir = Path(settings.chroma_persist_directory)
        persist_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            self._client = chromadb.PersistentClient(
                path=str(persist_dir),
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info(f"ChromaDB connected: {persist_dir}")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            raise
    
    @property
    def client(self) -> chromadb.ClientAPI:
        """
        Get ChromaDB client.
        
        Returns:
            ClientAPI: ChromaDB client instance
        """
        if self._client is None:
            self._connect()
        return self._client
    
    def get_collection(
        self, 
        name: Optional[str] = None,
        create_if_not_exists: bool = True
    ) -> chromadb.Collection:
        """
        Get or create a collection.
        
        Args:
            name: Collection name (defaults to config value)
            create_if_not_exists: Create collection if it doesn't exist
            
        Returns:
            Collection: ChromaDB collection
        """
        if name is None:
            settings = get_settings()
            name = settings.chroma_collection_name
        
        try:
            if create_if_not_exists:
                collection = self.client.get_or_create_collection(
                    name=name,
                    metadata={"description": "Basecamp Employee Handbook documents"}
                )
            else:
                collection = self.client.get_collection(name=name)
            
            logger.debug(f"Collection retrieved: {name}")
            return collection
        except Exception as e:
            logger.error(f"Failed to get collection {name}: {e}")
            raise
    
    def reset_collection(self, name: Optional[str] = None):
        """
        Delete and recreate a collection (WARNING: Deletes all documents).
        
        Args:
            name: Collection name (defaults to config value)
        """
        if name is None:
            settings = get_settings()
            name = settings.chroma_collection_name
        
        try:
            self.client.delete_collection(name)
            logger.info(f"Collection deleted: {name}")
        except Exception:
            logger.debug(f"Collection {name} did not exist")
        
        self.get_collection(name, create_if_not_exists=True)
        logger.info(f"Collection recreated: {name}")
    
    def list_collections(self) -> list:
        """
        List all collections.
        
        Returns:
            list: List of collection names
        """
        collections = self.client.list_collections()
        return [col.name for col in collections]
    
    def close(self):
        """Close database connection."""
        if self._client is not None:
            self._client = None
            logger.info("ChromaDB connection closed")


def get_db() -> ChromaDBConnection:
    """
    Get database connection instance.
    
    Returns:
        ChromaDBConnection: Database connection
    """
    return ChromaDBConnection()
