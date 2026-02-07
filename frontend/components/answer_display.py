"""
Answer display component.
"""
import streamlit as st
from typing import Dict, Any
import time
from client.api_client import (
    ask_question, 
    ask_question_stream,
    get_performance_metrics,
    get_usage_metrics,
    get_system_metrics
)


def render_answer(question: str, use_streaming: bool = True):
    """
    Render the answer section.
    
    Args:
        question: User's question
        use_streaming: Whether to use streaming response
    """
    st.divider()
    st.markdown(f"### ❓ Question: {question}")
    
    with st.spinner("🤔 Thinking..."):
        if use_streaming:
            # Streaming response
            st.markdown("### 💬 Answer:")
            answer_placeholder = st.empty()
            full_answer = ""
            
            for chunk in ask_question_stream(question):
                full_answer += chunk
                answer_placeholder.markdown(
                    f'<div class="answer-box">{full_answer}</div>', 
                    unsafe_allow_html=True
                )
                time.sleep(0.01)  # Small delay for better visual effect
            
            # Get metadata (need non-streaming call)
            result = ask_question(question)

            # Metadata
            if result and result.get("metadata"):
                _render_metadata(result["metadata"])
            
            # Auto-fetch and display metrics after answer
            _render_performance_metrics()
        else:
            # Non-streaming response
            result = ask_question(question)
            
            if result:
                # Display answer
                st.markdown("### 💬 Answer:")
                st.markdown(
                    f'<div class="answer-box">{result["answer"]}</div>', 
                    unsafe_allow_html=True
                )
                
                # Metadata
                if result.get("metadata"):
                    _render_metadata(result["metadata"])
                
                # Auto-fetch and display metrics after answer
                _render_performance_metrics()


def _render_metadata(metadata: Dict[str, Any]):
    """
    Render answer metadata in an expandable section.
    
    Args:
        metadata: Dictionary containing documents_retrieved and confidence
    """
    with st.expander("ℹ️ Metadata"):
        col1, col2 = st.columns(2)
        with col1:
            docs = metadata.get("documents_retrieved", 0)
            st.metric("Retrieved Documents", docs)
        with col2:
            confidence = metadata.get("confidence", "N/A")
            st.metric("Confidence Level", confidence)


def _render_performance_metrics():
    """
    Render performance metrics in an expandable section.
    
    Automatically fetches and displays:
    - Response time statistics
    - LLM performance (tokens/sec)
    - Vector search performance
    - Usage statistics
    - System health metrics
    """
    with st.expander("📊 Show Performance Metrics", expanded=False):
        tab1, tab2, tab3 = st.tabs(["⚡ Performance", "📈 Usage", "💻 System"])
        
        with tab1:
            perf_metrics = get_performance_metrics()
            if perf_metrics:
                st.markdown("#### ⚡ Response Time Metrics")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    avg_time = perf_metrics.get("avg_response_time_ms", 0)
                    st.metric("Average", f"{avg_time:.0f} ms")
                with col2:
                    min_time = perf_metrics.get("min_response_time_ms", 0)
                    st.metric("Fastest", f"{min_time:.0f} ms")
                with col3:
                    max_time = perf_metrics.get("max_response_time_ms", 0)
                    st.metric("Slowest", f"{max_time:.0f} ms")
            else:
                st.warning("⚠️ Performance metrics unavailable")
        
        with tab2:
            usage_metrics = get_usage_metrics()
            if usage_metrics:
                st.markdown("#### 📈 Usage Metrics")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Queries", usage_metrics.get("total_queries", 0))
                with col2:
                    success_rate = usage_metrics.get("success_rate", 0)
                    st.metric("Success Rate", f"{success_rate:.1f}%")
                
                # Query Distribution
                dist = usage_metrics.get("query_distribution", {})
                if dist:
                    st.markdown("##### 📊 Query Distribution")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Success", dist.get("success", 0))
                    with col2:
                        st.metric("Error", dist.get("error", 0))
                    with col3:
                        st.metric("Empty Response", dist.get("empty_response", 0))
            else:
                st.warning("⚠️ Usage metrics unavailable")
        
        with tab3:
            sys_metrics = get_system_metrics()
            if sys_metrics:
                st.markdown("#### 💻 System Information")
                
                # System Info
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("CPU Usage", f"{sys_metrics.get('cpu_percent', 0):.1f}%")
                    st.metric("RAM Usage", f"{sys_metrics.get('memory_percent', 0):.1f}%")
                with col2:
                    disk = sys_metrics.get("disk_percent", 0)
                    st.metric("Disk Usage", f"{disk:.1f}%")
                    uptime = sys_metrics.get("uptime_seconds", 0)
                    hours = uptime // 3600
                    minutes = (uptime % 3600) // 60
                    st.metric("Uptime", f"{hours:.0f}h {minutes:.0f}m")
                
                # Process Info
                process = sys_metrics.get("process", {})
                if process:
                    st.markdown("##### 🔧 Process Info")
                    col1, col2 = st.columns(2)
                    with col1:
                        mem_mb = process.get("memory_mb", 0)
                        st.metric("Memory", f"{mem_mb:.0f} MB")
                    with col2:
                        threads = process.get("threads", 0)
                        st.metric("Threads", f"{threads}")
            else:
                st.warning("⚠️ System metrics unavailable")
