"""
Tests for resource inventory endpoints
"""
from fastapi.testclient import TestClient
import pytest


class TestResourceEndpoints:
    """Test suite for resource endpoints"""

    def test_list_resources_validation(self, client: TestClient):
        """Test listing resources requires account_id"""
        response = client.get("/api/v1/resources/")
        assert response.status_code == 422  # Missing required query param

    def test_list_resources_no_account(self, client: TestClient):
        """Test resources route exists"""
        response = client.get("/api/v1/resources/?account_id=123456789012")
        # Should return empty results since no data exists
        assert response.status_code == 200
        data = response.json()
        assert "success" in data

    def test_resource_stats_validation(self, client: TestClient):
        """Test resource stats returns structure"""
        response = client.get("/api/v1/resources/stats/summary?account_id=123456789012")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_resource_details_not_found(self, client: TestClient):
        """Test getting non-existent resource returns 404"""
        response = client.get("/api/v1/resources/non-existent-id?account_id=123456789012")
        assert response.status_code == 404

    def test_scan_without_account(self, client: TestClient):
        """Test scan requires account_id"""
        response = client.post("/api/v1/resources/scan", json={})
        assert response.status_code == 422  # FastAPI validation for missing field

    def test_scan_no_credentials(self, client: TestClient):
        """Test scan with unknown account"""
        # Account doesn't exist in database
        response = client.post(
            "/api/v1/resources/scan",
            json={"account_id": "123456789012", "scan_type": "full"}
        )
        # Account not found in database
        assert response.status_code == 404

    def test_export_endpoint(self, client: TestClient):
        """Test export endpoint exists"""
        response = client.get("/api/v1/resources/export?account_id=123456789012&format=csv")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
