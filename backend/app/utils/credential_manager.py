"""
AWS Infra Vision - Secure Credential Manager
Uses OS-native keychain for secure credential storage
"""
import keyring
import json
import base64
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class CredentialManager:
    """
    Manages AWS credentials securely using OS keychain
    
    Supports:
    - macOS Keychain
    - Windows Credential Vault
    - Linux Secret Service (GNOME Keyring/KWallet)
    """
    
    SERVICE_NAME = "aws-infra-vision"
    
    def __init__(self):
        self.service_name = self.SERVICE_NAME
    
    def store_credentials(self, account_id: str, credentials: Dict) -> str:
        """
        Store credentials securely in OS keychain
        
        Args:
            account_id: AWS account ID
            credentials: Credential dictionary
            
        Returns:
            Key reference string
        """
        try:
            # Serialize credentials to JSON
            cred_json = json.dumps(credentials)
            
            # Encode to base64 for safe storage
            encoded_creds = base64.b64encode(cred_json.encode()).decode()
            
            # Store in keychain with account_id as username
            keyring.set_password(
                self.service_name,
                f"aws-account-{account_id}",
                encoded_creds
            )
            
            logger.info(f"Credentials stored securely for account {account_id}")
            return f"keychain://{account_id}"
            
        except Exception as e:
            logger.error(f"Failed to store credentials: {str(e)}")
            raise Exception(f"Credential storage failed: {str(e)}")
    
    def retrieve_credentials(self, account_id: str) -> Optional[Dict]:
        """
        Retrieve credentials from OS keychain
        
        Args:
            account_id: AWS account ID
            
        Returns:
            Credential dictionary or None
        """
        try:
            # Retrieve from keychain
            encoded_creds = keyring.get_password(
                self.service_name,
                f"aws-account-{account_id}"
            )
            
            if not encoded_creds:
                logger.warning(f"No credentials found for account {account_id}")
                return None
            
            # Decode from base64
            cred_json = base64.b64decode(encoded_creds.encode()).decode()
            credentials = json.loads(cred_json)
            
            logger.info(f"Credentials retrieved for account {account_id}")
            return credentials
            
        except Exception as e:
            logger.error(f"Failed to retrieve credentials: {str(e)}")
            return None
    
    def delete_credentials(self, account_id: str) -> bool:
        """
        Delete credentials from OS keychain
        
        Args:
            account_id: AWS account ID
            
        Returns:
            True if deleted successfully
        """
        try:
            keyring.delete_password(
                self.service_name,
                f"aws-account-{account_id}"
            )
            
            logger.info(f"Credentials deleted for account {account_id}")
            return True
            
        except keyring.errors.PasswordDeleteError:
            logger.warning(f"Credentials not found for deletion: {account_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete credentials: {str(e)}")
            return False
    
    def list_accounts(self) -> list:
        """
        List all accounts with stored credentials
        
        Returns:
            List of account IDs
        """
        try:
            # Note: keyring doesn't provide a direct way to list all entries
            # This would need to be tracked separately in the database
            return []
            
        except Exception as e:
            logger.error(f"Failed to list accounts: {str(e)}")
            return []
    
    def test_keychain_access(self) -> bool:
        """
        Test if keychain access is working
        
        Returns:
            True if keychain is accessible
        """
        try:
            test_service = f"{self.service_name}-test"
            test_username = "test"
            test_password = "test123"
            
            # Try to store and retrieve
            keyring.set_password(test_service, test_username, test_password)
            retrieved = keyring.get_password(test_service, test_username)
            keyring.delete_password(test_service, test_username)
            
            return retrieved == test_password
            
        except Exception as e:
            logger.error(f"Keychain test failed: {str(e)}")
            return False
