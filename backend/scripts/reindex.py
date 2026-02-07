#!/usr/bin/env python3
"""
CLI script to reindex documents.
Used to replace the removed /admin/reindex endpoint.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.services.rag_pipeline import RAGPipeline
from backend.app.core import get_settings, setup_logging, get_logger

# Setup logging
settings = get_settings()
setup_logging(log_level=settings.log_level, log_dir=settings.log_dir)
logger = get_logger(__name__)


def main():
    """Main reindexing function."""
    try:
        logger.info("=" * 60)
        logger.info("Starting document reindexing...")
        logger.info("=" * 60)
        
        pipeline = RAGPipeline()
        stats = pipeline.initialize(force_reindex=True)
        
        logger.info("=" * 60)
        logger.info("Reindexing completed successfully!")
        logger.info(f"Statistics: {stats}")
        logger.info("=" * 60)
        
        print("\n✓ Reindexing completed successfully!")
        print(f"  - Documents processed: {stats.get('documents_processed', 'N/A')}")
        print(f"  - Chunks created: {stats.get('chunks_created', 'N/A')}")
        print(f"  - Status: {stats.get('status', 'N/A')}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Reindexing failed: {e}", exc_info=True)
        print(f"\n✗ Reindexing failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
