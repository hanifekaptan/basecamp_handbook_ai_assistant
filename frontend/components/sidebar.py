"""
Sidebar component.
"""
import streamlit as st
from client.api_client import check_api_health
from config import EXAMPLE_QUESTIONS


def render_sidebar():
    """
    Render the sidebar with API health status, user settings, and example questions.
    
    Returns:
        tuple: (health_status: Dict, use_streaming: bool)
            - health_status: API health check result or None
            - use_streaming: User's streaming preference
    """
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # API Health Check
        st.subheader("🏥 API Status")
        health = check_api_health()
        
        if health:
            st.success("✅ API Running")
            st.metric("Version", health.get("version", "N/A"))
            st.metric("Indexed Documents", health.get("documents_indexed", 0))
            ollama_status = "✅ Active" if health.get("ollama_available") else "❌ Inactive"
            st.metric("Ollama LLM", ollama_status)
        else:
            st.error("❌ Cannot connect to API")
            st.warning("Make sure backend is running:\n```bash\ncd backend && python main.py\n```")
        
        st.divider()
        
        # Streaming option
        use_streaming = st.checkbox(
            "🌊 Streaming Response",
            value=True,
            help="Display answer word by word"
        )
        
        st.divider()
        
        # Example questions
        st.subheader("💡 Example Questions")
        for eq in EXAMPLE_QUESTIONS:
            if st.button(eq, key=f"example_{eq}", use_container_width=True):
                st.session_state.question = eq
        
        return health, use_streaming
