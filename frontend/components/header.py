"""
Header component with metrics display.
"""
import streamlit as st
from client.api_client import get_performance_metrics, get_usage_metrics, get_system_metrics
from config import CUSTOM_CSS, PAGE_TITLE


def render_metrics_modal():
    """
    Render system metrics in an expandable section.
    
    Displays three tabs:
    - Performance: Response times, LLM speed, vector search
    - Usage: Query statistics and success rate
    - System: CPU, memory, disk usage
    """
    with st.expander("📊 **System Performance Metrics**", expanded=False):
        tab1, tab2, tab3 = st.tabs(["⚡ Performance", "📈 Usage", "💻 System"])
        
        with tab1:
            perf_metrics = get_performance_metrics()
            if perf_metrics:
                st.markdown("### ⚡ Performance Metrics")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    avg_time = perf_metrics.get("avg_response_time_ms", 0)
                    st.metric("Avg Response Time", f"{avg_time:.0f} ms")
                with col2:
                    min_time = perf_metrics.get("min_response_time_ms", 0)
                    st.metric("Fastest", f"{min_time:.0f} ms")
                with col3:
                    max_time = perf_metrics.get("max_response_time_ms", 0)
                    st.metric("Slowest", f"{max_time:.0f} ms")
                
                # LLM Performance
                llm_perf = perf_metrics.get("llm_performance", {})
                if llm_perf:
                    st.markdown("#### 🤖 LLM Performance")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Avg Duration", f"{llm_perf.get('avg_generation_time_ms', 0):.0f} ms")
                    with col2:
                        tokens_per_sec = llm_perf.get("avg_tokens_per_second", 0)
                        st.metric("Tokens/Second", f"{tokens_per_sec:.2f}")
                
                # Vector Search Performance
                vector_perf = perf_metrics.get("vector_search_performance", {})
                if vector_perf:
                    st.markdown("#### 🔍 Vector Search Performance")
                    st.metric("Avg Search Time", f"{vector_perf.get('avg_search_time_ms', 0):.0f} ms")
            else:
                st.warning("⚠️ Performance metrics unavailable")
        
        with tab2:
            usage_metrics = get_usage_metrics()
            if usage_metrics:
                st.markdown("### 📈 Usage Metrics")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Queries", usage_metrics.get("total_queries", 0))
                with col2:
                    success_rate = usage_metrics.get("success_rate", 0)
                    st.metric("Success Rate", f"{success_rate:.1f}%")
                
                # Query Distribution
                dist = usage_metrics.get("query_distribution", {})
                if dist:
                    st.markdown("#### 📊 Query Distribution")
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
                st.markdown("### 💻 System Information")
                
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
                    st.markdown("#### 🔧 Process Info")
                    col1, col2 = st.columns(2)
                    with col1:
                        mem_mb = process.get("memory_mb", 0)
                        st.metric("Memory", f"{mem_mb:.0f} MB")
                    with col2:
                        threads = process.get("threads", 0)
                        st.metric("Threads", f"{threads}")
            else:
                st.warning("⚠️ System metrics unavailable")


def render_header():
    """Render the main header."""
    # Apply custom CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Header
    st.markdown(f'<div class="main-header">📚 {PAGE_TITLE}</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Ask questions about your employee handbook</div>', unsafe_allow_html=True)
