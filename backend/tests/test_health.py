"""
Tests for health check and root endpoints
"""
from fastapi.testclient import TestClient
import pytest


class TestHealthEndpoints:
    """Test suite for health check endpoints"""

    def test_health_check(self, client: TestClient):
        """Test the /health endpoint returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data
        assert "database" in data

    def test_root_endpoint(self, client: TestClient):
        """Test the / endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["version"] == "1.0.0"
        assert "docs" in data
