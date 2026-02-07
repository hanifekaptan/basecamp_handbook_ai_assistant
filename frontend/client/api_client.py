"""
API client for backend communication.
"""
import requests
from typing import Optional, Dict, Any, Generator
import streamlit as st
from config import API_BASE_URL, API_TIMEOUT, STREAM_TIMEOUT


def check_api_health() -> Optional[Dict[str, Any]]:
    """
    Check if API is available and healthy.
    
    Returns:
        Dict: Health status or None if unavailable
    """
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def ask_question(question: str) -> Optional[Dict[str, Any]]:
    """
    Send question to API and get response.
    
    Args:
        question: Question to ask
        
    Returns:
        Dict: API response or None if failed
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/ask",
            json={"question": question},
            timeout=API_TIMEOUT
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None


def ask_question_stream(question: str) -> Generator[str, None, None]:
    """
    Stream answer from API.
    
    Args:
        question: Question to ask
        
    Yields:
        str: Answer chunks
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/ask/stream",
            json={"question": question},
            stream=True,
            timeout=STREAM_TIMEOUT
        )
        
        if response.status_code == 200:
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                if chunk:
                    yield chunk
        else:
            yield f"Error: {response.status_code}"
    except Exception as e:
        yield f"Error: {str(e)}"


def get_performance_metrics() -> Optional[Dict[str, Any]]:
    """
    Get performance metrics from API.
    
    Returns:
        Dict: Performance metrics or None if failed
    """
    try:
        response = requests.get(f"{API_BASE_URL}/metrics/performance", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def get_usage_metrics() -> Optional[Dict[str, Any]]:
    """
    Get usage metrics from API.
    
    Returns:
        Dict: Usage metrics or None if failed
    """
    try:
        response = requests.get(f"{API_BASE_URL}/metrics/usage", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def get_system_metrics() -> Optional[Dict[str, Any]]:
    """
    Get system metrics from API.
    
    Returns:
        Dict: System metrics or None if failed
    """
    try:
        response = requests.get(f"{API_BASE_URL}/metrics/system", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None
