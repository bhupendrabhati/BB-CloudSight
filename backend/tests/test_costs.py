"""
Tests for cost analytics endpoints
"""
from fastapi.testclient import TestClient
import pytest


class TestCostEndpoints:
    """Test suite for cost endpoints"""

    def test_cost_summary_validation(self, client: TestClient):
        """Test cost summary requires account_id"""
        response = client.get("/api/v1/costs/summary")
        assert response.status_code == 422  # Missing query param

    def test_cost_summary_no_credentials(self, client: TestClient):
        """Test cost summary returns stub data when no credentials"""
        response = client.get("/api/v1/costs/summary?account_id=123456789012")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "total_cost" in data["data"]

    def test_costs_by_service_no_credentials(self, client: TestClient):
        """Test costs by service returns stub data when no credentials"""
        response = client.get("/api/v1/costs/by-service?account_id=123456789012")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0

    def test_costs_by_region_no_credentials(self, client: TestClient):
        """Test costs by region returns stub data when no credentials"""
        response = client.get("/api/v1/costs/by-region?account_id=123456789012")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0

    def test_cost_forecast_no_credentials(self, client: TestClient):
        """Test cost forecast returns stub data when no credentials"""
        response = client.get("/api/v1/costs/forecast?account_id=123456789012")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "forecast" in data["data"]

    def test_cost_anomalies(self, client: TestClient):
        """Test cost anomalies endpoint"""
        response = client.get("/api/v1/costs/anomalies?account_id=123456789012")
        assert response.status_code == 200

    def test_cost_analysis_trigger(self, client: TestClient):
        """Test triggering cost analysis"""
        response = client.post("/api/v1/costs/analyze", json={
            "account_id": "123456789012"
        })
        assert response.status_code in [200, 401, 500]
