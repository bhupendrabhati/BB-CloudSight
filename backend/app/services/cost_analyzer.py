"""
AWS Infra Vision - Cost Analyzer Service
Integrates with AWS Cost Explorer API
"""
import boto3
from botocore.config import Config
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CostAnalyzer:
    """Analyzes AWS costs using Cost Explorer API"""
    
    def __init__(self, credentials: Dict, account_id: str):
        self.credentials = credentials
        self.account_id = account_id
        self.client = self._create_client()
    
    def _create_client(self):
        """Create Cost Explorer client"""
        session = boto3.Session(
            aws_access_key_id=self.credentials.get("access_key_id"),
            aws_secret_access_key=self.credentials.get("secret_access_key"),
            region_name="us-east-1"  # Cost Explorer is only available in us-east-1
        )
        
        config = Config(
            retries={"max_attempts": 3, "mode": "standard"}
        )
        
        return session.client("ce", config=config)
    
    def get_cost_summary(
        self,
        start_date: str,
        end_date: str,
        granularity: str = "MONTHLY"
    ) -> Dict:
        """
        Get cost summary
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            granularity: DAILY, MONTHLY
            
        Returns:
            Cost summary with breakdowns
        """
        try:
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    "Start": start_date,
                    "End": end_date
                },
                Granularity=granularity,
                Metrics=["UnblendedCost", "AmortizedCost"],
                GroupBy=[
                    {"Type": "DIMENSION", "Key": "SERVICE"},
                    {"Type": "DIMENSION", "Key": "REGION"}
                ]
            )
            
            results = response.get("ResultsByTime", [])
            
            # Calculate totals
            total_cost = 0
            service_costs = {}
            region_costs = {}
            
            for result in results:
                total = float(result.get("Total", {}).get("UnblendedCost", {}).get("Amount", 0))
                total_cost += total
                
                # Group by service
                for group in result.get("Groups", []):
                    keys = group.get("Keys", [])
                    amount = float(group.get("Metrics", {}).get("UnblendedCost", {}).get("Amount", 0))
                    
                    if len(keys) >= 1:
                        service = keys[0]
                        service_costs[service] = service_costs.get(service, 0) + amount
                    
                    if len(keys) >= 2:
                        region = keys[1]
                        region_costs[region] = region_costs.get(region, 0) + amount
            
            return {
                "period": {
                    "start": start_date,
                    "end": end_date,
                    "granularity": granularity
                },
                "total_cost": round(total_cost, 2),
                "currency": "USD",
                "by_service": [
                    {"service": k, "cost": round(v, 2)}
                    for k, v in sorted(service_costs.items(), key=lambda x: x[1], reverse=True)
                ],
                "by_region": [
                    {"region": k, "cost": round(v, 2)}
                    for k, v in sorted(region_costs.items(), key=lambda x: x[1], reverse=True)
                ],
                "daily_average": round(total_cost / max(1, len(results)), 2)
            }
            
        except Exception as e:
            logger.error(f"Cost summary error: {str(e)}")
            raise
    
    def get_costs_by_service(self, start_date: str, end_date: str) -> List[Dict]:
        """Get costs grouped by service"""
        try:
            response = self.client.get_cost_and_usage(
                TimePeriod={"Start": start_date, "End": end_date},
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"],
                GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}]
            )
            
            service_costs = {}
            
            for result in response.get("ResultsByTime", []):
                for group in result.get("Groups", []):
                    service = group["Keys"][0]
                    amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
                    service_costs[service] = service_costs.get(service, 0) + amount
            
            return [
                {"service": k, "cost": round(v, 2)}
                for k, v in sorted(service_costs.items(), key=lambda x: x[1], reverse=True)
            ]
            
        except Exception as e:
            logger.error(f"Service cost error: {str(e)}")
            return []
    
    def get_costs_by_region(self, start_date: str, end_date: str) -> List[Dict]:
        """Get costs grouped by region"""
        try:
            response = self.client.get_cost_and_usage(
                TimePeriod={"Start": start_date, "End": end_date},
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"],
                GroupBy=[{"Type": "DIMENSION", "Key": "REGION"}]
            )
            
            region_costs = {}
            
            for result in response.get("ResultsByTime", []):
                for group in result.get("Groups", []):
                    region = group["Keys"][0]
                    amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
                    region_costs[region] = region_costs.get(region, 0) + amount
            
            return [
                {"region": k, "cost": round(v, 2)}
                for k, v in sorted(region_costs.items(), key=lambda x: x[1], reverse=True)
            ]
            
        except Exception as e:
            logger.error(f"Region cost error: {str(e)}")
            return []
    
    def get_cost_forecast(self, months: int = 3) -> Dict:
        """
        Generate cost forecast
        
        Args:
            months: Number of months to forecast
            
        Returns:
            Forecast data with confidence intervals
        """
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
            
            # Get historical data
            response = self.client.get_cost_forecast(
                TimePeriod={
                    "Start": start_date,
                    "End": end_date
                },
                Metric="UNBLENDED_COST",
                Granularity="MONTHLY"
            )
            
            forecast_total = float(response.get("Total", {}).get("Amount", 0))
            forecast_by_service = []
            
            for forecast in response.get("ForecastResultsByTime", []):
                for group in forecast.get("Groups", []):
                    service = group["Keys"][0]
                    amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
                    forecast_by_service.append({
                        "service": service,
                        "forecasted_cost": round(amount, 2)
                    })
            
            return {
                "forecast_period_months": months,
                "total_forecasted_cost": round(forecast_total, 2),
                "currency": "USD",
                "by_service": sorted(forecast_by_service, key=lambda x: x["forecasted_cost"], reverse=True),
                "confidence_level": 0.8,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Forecast error: {str(e)}")
            return {
                "error": str(e),
                "message": "Forecast generation failed"
            }
    
    def run_full_analysis(self) -> Dict:
        """Run comprehensive cost analysis"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        
        summary = self.get_cost_summary(start_date, end_date)
        forecast = self.get_cost_forecast()
        
        return {
            "summary": summary,
            "forecast": forecast,
            "analysis_date": datetime.utcnow().isoformat()
        }
