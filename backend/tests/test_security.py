"""
Tests for security endpoints
"""
from fastapi.testclient import TestClient
import pytest


class TestSecurityEndpoints:
    """Test suite for security endpoints"""

    def test_get_findings_validation(self, client: TestClient):
        """Test findings endpoint requires account_id"""
        response = client.get("/api/v1/security/findings")
        assert response.status_code == 422  # Missing query param

    def test_get_findings_empty(self, client: TestClient):
        """Test findings returns empty list when no data"""
        response = client.get("/api/v1/security/findings?account_id=123456789012")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["findings"] == []

    def test_get_finding_detail_not_found(self, client: TestClient):
        """Test getting non-existent finding returns 404"""
        response = client.get("/api/v1/security/findings/999")
        assert response.status_code == 404

    def test_update_finding_status_not_found(self, client: TestClient):
        """Test updating non-existent finding returns 404"""
        response = client.put("/api/v1/security/findings/999/status?status=resolved")
        assert response.status_code == 404

    def test_security_score(self, client: TestClient):
        """Test security score endpoint"""
        response = client.get("/api/v1/security/score?account_id=123456789012")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "score" in data["data"]

    def test_scan_no_credentials(self, client: TestClient):
        """Test security scan with no credentials"""
        response = client.post(
            "/api/v1/security/scan",
            json={"account_id": "123456789012"}
        )
        assert response.status_code in [401, 500]
