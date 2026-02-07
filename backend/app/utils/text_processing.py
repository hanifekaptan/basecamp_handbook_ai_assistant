"""
Utility functions for text processing and cleaning.
"""
import re
from pathlib import Path
from typing import List

from backend.app.core.logging import get_logger

logger = get_logger(__name__)


def clean_text(text: str) -> str:
    """
    Clean and normalize text content.
    
    Args:
        text: Raw text content
        
    Returns:
        str: Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep punctuation
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    return text.strip()


def extract_filename_from_path(file_path: str) -> str:
    """
    Extract clean filename from path.
    
    Args:
        file_path: Full file path
        
    Returns:
        str: Filename without extension
    """
    return Path(file_path).stem


def load_markdown_files(directory: str) -> List[tuple[str, str]]:
    """
    Load all markdown files from a directory.
    
    Args:
        directory: Path to directory containing markdown files
        
    Returns:
        List[tuple]: List of (filename, content) tuples
    """
    documents = []
    docs_path = Path(directory)
    
    if not docs_path.exists():
        logger.error(f"Directory not found: {directory}")
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    for md_file in docs_path.glob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                documents.append((str(md_file), content))
                logger.debug(f"Loaded file: {md_file.name}")
        except Exception as e:
            logger.warning(f"Error reading {md_file}: {e}")
            continue
    
    logger.info(f"Loaded {len(documents)} markdown files from {directory}")
    return documents


def format_source_metadata(source: str, header: str = None) -> str:
    """
    Format source metadata for user-friendly display.
    
    Args:
        source: Full source file path
        header: Optional section header from the document
        
    Returns:
        str: Formatted string like "filename.md" or "filename.md - Header"
    """
    filename = Path(source).name
    if header:
        return f"{filename} - {header}"
    return filename
