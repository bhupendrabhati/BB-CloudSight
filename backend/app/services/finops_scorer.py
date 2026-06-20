"""
AWS Infra Vision - FinOps Scorer
Calculates FinOps maturity score from 0-100
"""
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FinOpsScorer:
    """
    Calculates FinOps score based on multiple factors:
    - Resource Efficiency (20 points)
    - Unused Resources (20 points)
    - Tag Compliance (15 points)
    - Cost Trends (15 points)
    - Free Tier Utilization (10 points)
    - Rightsizing Opportunities (20 points)
    """
    
    def __init__(self, account_id: str, db_session):
        self.account_id = account_id
        self.db = db_session
    
    def calculate_score(self) -> Dict:
        """Calculate comprehensive FinOps score"""
        
        # Calculate individual factor scores
        resource_efficiency = self._calculate_resource_efficiency()
        unused_resources = self._calculate_unused_resources_score()
        tag_compliance = self._calculate_tag_compliance()
        cost_trends = self._calculate_cost_trend_score()
        free_tier = self._calculate_free_tier_score()
        rightsizing = self._calculate_rightsizing_score()
        
        # Weighted overall score
        overall = int(
            resource_efficiency["score"] * 0.20 +
            unused_resources["score"] * 0.20 +
            tag_compliance["score"] * 0.15 +
            cost_trends["score"] * 0.15 +
            free_tier["score"] * 0.10 +
            rightsizing["score"] * 0.20
        )
        
        # Ensure score is between 0-100
        overall = max(0, min(100, overall))
        
        return {
            "account_id": self.account_id,
            "score_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "overall_score": overall,
            "grade": self._score_to_grade(overall),
            "factors": {
                "resource_efficiency": resource_efficiency,
                "unused_resources": unused_resources,
                "tag_compliance": tag_compliance,
                "cost_trends": cost_trends,
                "free_tier_utilization": free_tier,
                "rightsizing_opportunities": rightsizing
            },
            "recommendations_count": self._count_recommendations(),
            "potential_monthly_savings": self._estimate_potential_savings(),
            "calculated_at": datetime.utcnow().isoformat()
        }
    
    def _calculate_resource_efficiency(self) -> Dict:
        """Calculate resource efficiency score (0-100)"""
        # This would analyze actual usage metrics
        # For now, return a placeholder calculation
        score = 75  # Placeholder
        
        return {
            "score": score,
            "max_points": 20,
            "weighted_points": score * 0.20,
            "metrics": {
                "cpu_utilization_avg": 45,
                "memory_utilization_avg": 60,
                "storage_utilization": 70
            }
        }
    
    def _calculate_unused_resources_score(self) -> Dict:
        """Calculate score based on unused resources (0-100)"""
        # Count unused resources
        unused_count = self._count_unused_resources()
        total_resources = self._count_total_resources()
        
        if total_resources == 0:
            score = 100
        else:
            unused_percentage = (unused_count / total_resources) * 100
            # Lower unused percentage = higher score
            score = max(0, 100 - (unused_percentage * 2))
        
        return {
            "score": int(score),
            "max_points": 20,
            "weighted_points": int(score * 0.20),
            "metrics": {
                "unused_resources": unused_count,
                "total_resources": total_resources,
                "unused_percentage": round(unused_percentage if total_resources > 0 else 0, 2)
            }
        }
    
    def _calculate_tag_compliance(self) -> Dict:
        """Calculate tag compliance score (0-100)"""
        # Check for required tags: Environment, Owner, Project
        required_tags = ["Environment", "Owner", "Project"]
        
        tagged_resources = self._count_tagged_resources(required_tags)
        total_resources = self._count_total_resources()
        
        if total_resources == 0:
            score = 100
        else:
            compliance_rate = (tagged_resources / total_resources) * 100
            score = compliance_rate
        
        return {
            "score": int(score),
            "max_points": 15,
            "weighted_points": int(score * 0.15),
            "metrics": {
                "tagged_resources": tagged_resources,
                "total_resources": total_resources,
                "compliance_rate": round(score, 2),
                "required_tags": required_tags
            }
        }
    
    def _calculate_cost_trend_score(self) -> Dict:
        """Calculate cost trend score (0-100)"""
        # Analyze cost trends over last 3 months
        # Stable or decreasing costs = higher score
        
        score = 80  # Placeholder
        
        return {
            "score": score,
            "max_points": 15,
            "weighted_points": score * 0.15,
            "metrics": {
                "trend": "stable",
                "month_over_month_change": 2.5,
                "forecast_accuracy": 85
            }
        }
    
    def _calculate_free_tier_score(self) -> Dict:
        """Calculate free tier utilization score (0-100)"""
        # Check if using free tier eligible services efficiently
        
        score = 70  # Placeholder
        
        return {
            "score": score,
            "max_points": 10,
            "weighted_points": score * 0.10,
            "metrics": {
                "free_tier_services_used": 5,
                "free_tier_eligible_total": 10,
                "utilization_rate": 50
            }
        }
    
    def _calculate_rightsizing_score(self) -> Dict:
        """Calculate rightsizing opportunities score (0-100)"""
        # Analyze EC2 and RDS instances for rightsizing
        
        rightsizing_opportunities = self._count_rightsizing_opportunities()
        total_instances = self._count_total_instances()
        
        if total_instances == 0:
            score = 100
        else:
            optimization_rate = (rightsizing_opportunities / total_instances) * 100
            score = max(0, 100 - optimization_rate)
        
        return {
            "score": int(score),
            "max_points": 20,
            "weighted_points": int(score * 0.20),
            "metrics": {
                "rightsizing_opportunities": rightsizing_opportunities,
                "total_instances": total_instances,
                "estimated_monthly_savings": self._estimate_rightsizing_savings()
            }
        }
    
    def _count_unused_resources(self) -> int:
        """Count unused resources"""
        # This would query the database for unused resources
        # Placeholder implementation
        return 5
    
    def _count_total_resources(self) -> int:
        """Count total resources"""
        # Placeholder
        return 100
    
    def _count_tagged_resources(self, required_tags: List[str]) -> int:
        """Count resources with all required tags"""
        # Placeholder
        return 75
    
    def _count_recommendations(self) -> int:
        """Count active recommendations"""
        # Placeholder
        return 12
    
    def _estimate_potential_savings(self) -> float:
        """Estimate total potential monthly savings"""
        # Placeholder
        return 450.00
    
    def _count_rightsizing_opportunities(self) -> int:
        """Count resources that could be rightsized"""
        # Placeholder
        return 8
    
    def _count_total_instances(self) -> int:
        """Count total EC2 and RDS instances"""
        # Placeholder
        return 25
    
    def _estimate_rightsizing_savings(self) -> float:
        """Estimate savings from rightsizing"""
        # Placeholder
        return 280.00
    
    @staticmethod
    def _score_to_grade(score: int) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
