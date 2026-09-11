from typing import Dict, List, Any
from dataclasses import dataclass, field
import statistics


@dataclass
class PerformanceMetrics:
    """Tracks performance metrics across research queries."""

    queries_processed: int = 0
    quality_scores: List[float] = field(default_factory=list)
    response_times: List[float] = field(default_factory=list)
    sources_found: List[int] = field(default_factory=list)
    iterations_used: List[int] = field(default_factory=list)
    fact_checks_performed: List[int] = field(default_factory=list)
    citations_generated: List[int] = field(default_factory=list)

    def record_query(self, quality: float, time: float, sources: int,
                    iterations: int, fact_checks: int, citations: int):
        """Record metrics for a completed query."""
        self.queries_processed += 1
        self.quality_scores.append(quality)
        self.response_times.append(time)
        self.sources_found.append(sources)
        self.iterations_used.append(iterations)
        self.fact_checks_performed.append(fact_checks)
        self.citations_generated.append(citations)

    def get_average_quality(self) -> float:
        """Calculate average quality score."""
        return statistics.mean(self.quality_scores) if self.quality_scores else 0.0

    def get_average_time(self) -> float:
        """Calculate average response time."""
        return statistics.mean(self.response_times) if self.response_times else 0.0

    def get_total_sources(self) -> int:
        """Get total sources gathered."""
        return sum(self.sources_found)

    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        return {
            "queries_processed": self.queries_processed,
            "average_quality": self.get_average_quality(),
            "average_response_time": self.get_average_time(),
            "total_sources": self.get_total_sources(),
            "total_citations": sum(self.citations_generated),
            "total_fact_checks": sum(self.fact_checks_performed),
            "average_iterations": statistics.mean(self.iterations_used) if self.iterations_used else 0.0
        }


class PerformanceEvaluator:
    """
    Evaluates system performance and identifies optimization opportunities.
    """

    def __init__(self):
        """Initialize the performance evaluator."""
        self.metrics = PerformanceMetrics()

    def evaluate_query_result(self, result: Dict[str, Any], processing_time: float):
        """
        Evaluate a single query result and update metrics.

        Args:
            result: Query result dictionary
            processing_time: Time taken to process query
        """
        self.metrics.record_query(
            quality=result.get("quality_score", 0.0),
            time=processing_time,
            sources=result.get("sources_found", 0),
            iterations=result.get("iterations", 0),
            fact_checks=result.get("fact_checks", 0),
            citations=result.get("citations_count", 0)
        )

    def analyze_performance(self) -> Dict[str, Any]:
        """
        Analyze overall system performance.

        Returns:
            Performance analysis with optimization recommendations
        """
        summary = self.metrics.get_summary()

        # Performance assessment
        avg_quality = summary["average_quality"]
        if avg_quality >= 0.85:
            health_status = "excellent"
        elif avg_quality >= 0.75:
            health_status = "good"
        elif avg_quality >= 0.60:
            health_status = "fair"
        else:
            health_status = "needs_improvement"

        # Identify bottlenecks
        bottlenecks = []
        if avg_quality < 0.75:
            bottlenecks.append("Low quality scores - consider adjusting prompts or increasing iterations")
        if summary["average_response_time"] > 60:
            bottlenecks.append("Slow response times - optimize source gathering")
        if summary["total_sources"] / max(summary["queries_processed"], 1) < 10:
            bottlenecks.append("Insufficient sources - expand search strategies")

        return {
            "metrics": summary,
            "health_status": health_status,
            "bottlenecks": bottlenecks,
            "performance_score": avg_quality,
            "recommendations": self._generate_recommendations(summary)
        }

    def _generate_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations based on metrics."""
        recommendations = []

        if summary["average_quality"] < 0.80:
            recommendations.append("Increase max_iterations or adjust quality thresholds")

        if summary["total_sources"] / max(summary["queries_processed"], 1) < 15:
            recommendations.append("Enable additional source types or increase source gathering")

        if summary["average_iterations"] < 1.5:
            recommendations.append("Queries completing too quickly - may need stricter quality criteria")

        return recommendations or ["System performing well - no changes recommended"]
