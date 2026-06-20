"""
Tests for authentication endpoints
"""
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pytest


class TestAuthEndpoints:
    """Test suite for authentication endpoints"""

    def test_setup_wizard_validates_input(self, client: TestClient):
        """Test setup wizard requires proper input"""
        # Missing credential type
        response = client.post("/api/v1/auth/setup-wizard", json={})
        assert response.status_code == 422  # Validation error

    def test_setup_wizard_access_key_requires_keys(self, client: TestClient):
        """Test access_key type requires access_key_id and secret_access_key"""
        response = client.post("/api/v1/auth/setup-wizard", json={
            "credential_type": "access_key",
            # Missing access_key_id and secret_access_key
        })
        assert response.status_code == 400

    @patch("backend.app.api.v1.auth.AWSClientFactory")
    def test_setup_wizard_with_invalid_credentials(self, mock_factory, client: TestClient):
        """Test setup wizard fails with invalid credentials"""
        # Mock the factory to return invalid credentials
        mock_instance = MagicMock()
        mock_instance.validate_credentials.return_value = False
        mock_factory.return_value = mock_instance

        response = client.post("/api/v1/auth/setup-wizard", json={
            "credential_type": "access_key",
            "access_key_id": "AKIA-test",
            "secret_access_key": "test-secret",
            "region": "us-east-1"
        })
        assert response.status_code == 401

    def test_list_accounts_returns_empty(self, client: TestClient):
        """Test listing accounts returns empty list initially"""
        response = client.get("/api/v1/auth/accounts")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"] == []

    def test_validate_credentials_not_found(self, client: TestClient):
        """Test validate credentials returns 404 for unknown account"""
        response = client.post("/api/v1/auth/validate", json={
            "account_id": "123456789012"
        })
        assert response.status_code == 404

    def test_delete_account_not_found(self, client: TestClient):
        """Test delete returns 404 for unknown account"""
        response = client.delete("/api/v1/auth/accounts/123456789012")
        assert response.status_code == 404
