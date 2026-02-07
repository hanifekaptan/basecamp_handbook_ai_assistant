"""
Simple metrics tracker for monitoring RAG pipeline performance.
"""
from typing import Dict, List
from datetime import datetime
import time


class MetricsTracker:
    """Simple in-memory metrics tracker."""
    
    def __init__(self):
        self.queries: List[Dict] = []
        self.start_time = time.time()
    
    def track_query(
        self,
        question: str,
        response_time_ms: float,
        success: bool,
        llm_time_ms: float = 0,
        vector_search_time_ms: float = 0,
        tokens_generated: int = 0
    ):
        """Track a query execution."""
        self.queries.append({
            "timestamp": datetime.utcnow().isoformat(),
            "question": question,
            "response_time_ms": response_time_ms,
            "success": success,
            "llm_time_ms": llm_time_ms,
            "vector_search_time_ms": vector_search_time_ms,
            "tokens_generated": tokens_generated
        })
        
        # Keep only last 1000 queries to avoid memory issues
        if len(self.queries) > 1000:
            self.queries = self.queries[-1000:]
    
    def get_performance_metrics(self) -> Dict:
        """Get performance metrics."""
        if not self.queries:
            return {
                "avg_response_time_ms": 0,
                "min_response_time_ms": 0,
                "max_response_time_ms": 0,
                "llm_performance": {
                    "avg_generation_time_ms": 0,
                    "avg_tokens_per_second": 0
                },
                "vector_search_performance": {
                    "avg_search_time_ms": 0
                }
            }
        
        response_times = [q["response_time_ms"] for q in self.queries]
        llm_times = [q["llm_time_ms"] for q in self.queries if q["llm_time_ms"] > 0]
        vector_times = [q["vector_search_time_ms"] for q in self.queries if q["vector_search_time_ms"] > 0]
        
        # Calculate tokens per second for LLM
        tokens_per_second = 0
        if llm_times:
            total_tokens = sum(q["tokens_generated"] for q in self.queries if q["tokens_generated"] > 0)
            total_time_sec = sum(llm_times) / 1000
            tokens_per_second = total_tokens / total_time_sec if total_time_sec > 0 else 0
        
        return {
            "avg_response_time_ms": sum(response_times) / len(response_times) if response_times else 0,
            "min_response_time_ms": min(response_times) if response_times else 0,
            "max_response_time_ms": max(response_times) if response_times else 0,
            "llm_performance": {
                "avg_generation_time_ms": sum(llm_times) / len(llm_times) if llm_times else 0,
                "avg_tokens_per_second": tokens_per_second
            },
            "vector_search_performance": {
                "avg_search_time_ms": sum(vector_times) / len(vector_times) if vector_times else 0
            }
        }
    
    def get_usage_metrics(self) -> Dict:
        """Get usage metrics."""
        if not self.queries:
            return {
                "total_queries": 0,
                "success_rate": 0,
                "query_distribution": {
                    "success": 0,
                    "error": 0,
                    "empty_response": 0
                }
            }
        
        total = len(self.queries)
        success = sum(1 for q in self.queries if q["success"])
        
        return {
            "total_queries": total,
            "success_rate": (success / total * 100) if total > 0 else 0,
            "query_distribution": {
                "success": success,
                "error": total - success,
                "empty_response": 0  # Can be enhanced later
            }
        }
    
    def get_system_metrics(self) -> Dict:
        """Get system metrics with uptime."""
        import psutil
        
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "uptime_seconds": int(time.time() - self.start_time),
            "process": {
                "memory_mb": psutil.Process().memory_info().rss / (1024**2),
                "threads": psutil.Process().num_threads()
            }
        }


# Global instance
_metrics_tracker = MetricsTracker()


def get_metrics_tracker() -> MetricsTracker:
    """Get the global metrics tracker instance."""
    return _metrics_tracker
