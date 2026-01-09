"""
Monitoring and Metrics Module

Comprehensive monitoring for the RAG API:

1. Structured Logging
   - All API requests logged with timestamp, query, strategy, response time, status
   - Errors logged with full stack traces
   - JSON format for easy parsing

2. Metrics Tracking
   - Query count
   - Average response time
   - Error rate
   - Cost per query
   - Storage: logs/metrics.json

3. Performance Monitoring
   - Retrieval time
   - Generation time
   - Total time
   - Slow query alerts (>30 seconds)
   - Error monitoring

Usage:
    from .monitoring import MetricsTracker
    metrics = MetricsTracker()
    
    metrics.log_query(query="test", strategy="hybrid", response_time=1.5)
    metrics.log_error("query_failed", error="Error message")
    metrics.get_metrics()
    metrics.save_metrics()
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
import threading


class MetricsTracker:
    """Track and store API metrics"""
    
    def __init__(self, metrics_file: str = "logs/metrics.json"):
        """
        Initialize metrics tracker
        
        Parameters:
            metrics_file: Path to metrics JSON file
        """
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # In-memory metrics
        self.queries = []
        self.errors = []
        self.performance = defaultdict(list)
        
        # Load existing metrics
        self._load_metrics()
        
        # Thread lock for thread-safe operations
        self.lock = threading.RLock()
    
    def _load_metrics(self) -> None:
        """Load metrics from file"""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                    self.queries = data.get('queries', [])
                    self.errors = data.get('errors', [])
                    self.performance = defaultdict(
                        list, 
                        data.get('performance', {})
                    )
                    self.logger.info(f"Loaded metrics: {len(self.queries)} queries")
        except Exception as e:
            self.logger.warning(f"Could not load metrics: {str(e)}")
            self.queries = []
            self.errors = []
            self.performance = defaultdict(list)
    
    def log_query(
        self,
        query: str,
        strategy: str,
        response_time: float,
        num_results: int = 5,
        cost: float = 0.0,
        conversation_id: Optional[str] = None,
        status: str = "success",
    ) -> None:
        """
        Log a query request
        
        Parameters:
            query: The search query
            strategy: Retrieval strategy used
            response_time: Time to process query (seconds)
            num_results: Number of results returned
            cost: API cost for this query
            conversation_id: Optional conversation ID
            status: Query status (success, error, etc.)
        """
        with self.lock:
            query_log = {
                "timestamp": datetime.utcnow().isoformat(),
                "query": query[:100],  # Store first 100 chars
                "query_length": len(query),
                "strategy": strategy,
                "response_time": response_time,
                "num_results": num_results,
                "cost": cost,
                "conversation_id": conversation_id,
                "status": status,
            }
            
            self.queries.append(query_log)
            
            # Alert on slow queries
            if response_time > 30:
                self.logger.warning(
                    f"Slow query detected: {response_time:.2f}s",
                    extra={"query": query[:50], "response_time": response_time}
                )
            
            self.logger.info(
                f"Query logged: {strategy} ({response_time:.2f}s)",
                extra={
                    "strategy": strategy,
                    "response_time": response_time,
                    "status": status,
                }
            )
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        query: Optional[str] = None,
        strategy: Optional[str] = None,
        stack_trace: Optional[str] = None,
    ) -> None:
        """
        Log an error
        
        Parameters:
            error_type: Type of error (validation_error, api_error, etc.)
            error_message: Error description
            query: Related query (if applicable)
            strategy: Related strategy (if applicable)
            stack_trace: Full stack trace
        """
        with self.lock:
            error_log = {
                "timestamp": datetime.utcnow().isoformat(),
                "error_type": error_type,
                "error_message": error_message,
                "query": query[:100] if query else None,
                "strategy": strategy,
                "stack_trace": stack_trace,
            }
            
            self.errors.append(error_log)
            
            self.logger.error(
                f"Error logged: {error_type} - {error_message}",
                extra={"error_type": error_type, "query": query}
            )
    
    def log_performance(
        self,
        operation: str,
        duration: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log performance metrics
        
        Parameters:
            operation: Operation name (retrieval, generation, reranking, etc.)
            duration: Duration in seconds
            metadata: Additional metadata
        """
        with self.lock:
            perf_log = {
                "timestamp": datetime.utcnow().isoformat(),
                "duration": duration,
                "metadata": metadata or {},
            }
            
            self.performance[operation].append(perf_log)
            
            if operation not in self.performance:
                self.performance[operation] = []
            
            self.logger.debug(
                f"Performance: {operation} ({duration:.3f}s)",
                extra={"operation": operation, "duration": duration}
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics summary"""
        with self.lock:
            # Calculate statistics
            query_count = len(self.queries)
            error_count = len(self.errors)
            
            if query_count == 0:
                avg_response_time = 0
                error_rate = 0
            else:
                response_times = [q["response_time"] for q in self.queries]
                avg_response_time = sum(response_times) / len(response_times)
                error_rate = (error_count / (query_count + error_count)) * 100
            
            # Strategy breakdown
            strategy_stats = defaultdict(lambda: {"count": 0, "avg_time": 0})
            for query in self.queries:
                strategy = query["strategy"]
                strategy_stats[strategy]["count"] += 1
                strategy_stats[strategy]["total_time"] = strategy_stats[strategy].get("total_time", 0) + query["response_time"]
            
            for strategy in strategy_stats:
                count = strategy_stats[strategy]["count"]
                total_time = strategy_stats[strategy].get("total_time", 0)
                strategy_stats[strategy]["avg_time"] = total_time / count if count > 0 else 0
                del strategy_stats[strategy]["total_time"]
            
            # Performance stats
            perf_stats = {}
            for operation, logs in self.performance.items():
                if logs:
                    durations = [log["duration"] for log in logs]
                    perf_stats[operation] = {
                        "count": len(logs),
                        "avg_duration": sum(durations) / len(durations),
                        "min_duration": min(durations),
                        "max_duration": max(durations),
                    }
            
            return {
                "summary": {
                    "total_queries": query_count,
                    "total_errors": error_count,
                    "avg_response_time": round(avg_response_time, 3),
                    "error_rate_percent": round(error_rate, 2),
                    "timestamp": datetime.utcnow().isoformat(),
                },
                "by_strategy": dict(strategy_stats),
                "performance": perf_stats,
                "recent_errors": self.errors[-10:],  # Last 10 errors
            }
    
    def get_metrics_by_date(self, days: int = 7) -> Dict[str, Any]:
        """Get metrics for the last N days"""
        with self.lock:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            recent_queries = [
                q for q in self.queries
                if datetime.fromisoformat(q["timestamp"]) > cutoff_date
            ]
            recent_errors = [
                e for e in self.errors
                if datetime.fromisoformat(e["timestamp"]) > cutoff_date
            ]
            
            if not recent_queries:
                avg_time = 0
                error_rate = 0
            else:
                response_times = [q["response_time"] for q in recent_queries]
                avg_time = sum(response_times) / len(response_times)
                total = len(recent_queries) + len(recent_errors)
                error_rate = (len(recent_errors) / total) * 100 if total > 0 else 0
            
            return {
                "period_days": days,
                "query_count": len(recent_queries),
                "error_count": len(recent_errors),
                "avg_response_time": round(avg_time, 3),
                "error_rate_percent": round(error_rate, 2),
            }
    
    def save_metrics(self) -> None:
        """Save metrics to JSON file"""
        with self.lock:
            try:
                metrics_data = {
                    "generated_at": datetime.utcnow().isoformat(),
                    "summary": self.get_metrics(),
                    "queries": self.queries[-1000:],  # Keep last 1000
                    "errors": self.errors[-100:],  # Keep last 100
                    "performance": {k: v[-100:] for k, v in self.performance.items()},
                }
                
                with open(self.metrics_file, 'w') as f:
                    json.dump(metrics_data, f, indent=2)
                
                self.logger.info(f"Metrics saved to {self.metrics_file}")
            except Exception as e:
                self.logger.error(f"Error saving metrics: {str(e)}")
    
    def reset_metrics(self) -> None:
        """Reset all metrics"""
        with self.lock:
            self.queries = []
            self.errors = []
            self.performance = defaultdict(list)
            self.logger.info("Metrics reset")


# Global metrics instance
metrics = MetricsTracker()


def periodic_save_metrics(interval: int = 60) -> None:
    """
    Periodically save metrics to file
    
    Parameters:
        interval: Save interval in seconds
    """
    import time
    import threading
    
    def save_loop():
        while True:
            time.sleep(interval)
            metrics.save_metrics()
    
    thread = threading.Thread(target=save_loop, daemon=True)
    thread.start()
