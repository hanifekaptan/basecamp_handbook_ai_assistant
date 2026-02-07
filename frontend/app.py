"""
Streamlit frontend for Basecamp Handbook RAG API.
Modular architecture with separate components for better maintainability.
"""
import streamlit as st
from components import render_header, render_sidebar, render_answer
from config import PAGE_TITLE, PAGE_ICON


def main():
    """Main Streamlit application."""
    
    # Page config
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Render header with metrics button
    render_header()
    
    # Render sidebar (returns health status and streaming preference)
    health, use_streaming = render_sidebar()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Question input
        question = st.text_area(
            "❓ Type your question here:",
            value=st.session_state.get("question", ""),
            height=100,
            placeholder="Example: How does the vacation policy work at Basecamp?",
            key="question_input"
        )
        
        # Ask button
        ask_button = st.button("🚀 Ask Question", type="primary", use_container_width=True)
    
    with col2:
        st.info("""
        **💡 Tips:**
        
        - Ask clear and specific questions
        - You can ask about multiple topics
        - Performance metrics shown after answer
        """)
    
    # Process question
    if ask_button and question.strip():
        if not health:
            st.error("❌ API unavailable. Please start the backend.")
            return
        
        # Render answer with sources
        render_answer(question, use_streaming)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem;">
        <p>Basecamp Handbook RAG API v2.0 | Powered by Ollama & ChromaDB</p>
        <p>📚 <a href="http://localhost:8000/docs" target="_blank">API Documentation</a> | 
        🔧 <a href="http://localhost:8000/redoc" target="_blank">API ReDoc</a></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
