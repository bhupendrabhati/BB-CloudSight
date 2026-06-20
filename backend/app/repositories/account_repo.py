"""
AWS Infra Vision - Account Repository
Data access layer for AWS accounts
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json

from backend.app.database import Account, Credential


class AccountRepository:
    """Repository for AWS account operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_or_update_account(
        self,
        account_id: str,
        credential_type: str,
        key_reference: str,
        region: str = "us-east-1",
        alias: str = None,
        role_arn: str = None,
        external_id: str = None
    ) -> Account:
        """Create or update an AWS account"""
        
        # Check if account exists
        account = self.db.query(Account).filter(
            Account.account_id == account_id
        ).first()
        
        if not account:
            # Create new account
            account = Account(
                account_id=account_id,
                alias=alias,
                is_active=True,
                regions_enabled=json.dumps([region]),
                metadata_json=json.dumps({"default_region": region})
            )
            self.db.add(account)
        
        # Update credential reference
        credential = Credential(
            account_id=account_id,
            credential_type=credential_type,
            key_reference=key_reference,
            role_arn=role_arn,
            external_id=external_id,
            is_active=True
        )
        self.db.add(credential)
        
        self.db.commit()
        self.db.refresh(account)
        
        return account
    
    def get_account(self, account_id: str) -> Optional[Account]:
        """Get account by ID"""
        return self.db.query(Account).filter(
            Account.account_id == account_id
        ).first()
    
    def list_accounts(self, active_only: bool = True) -> List[Account]:
        """List all accounts"""
        query = self.db.query(Account)
        
        if active_only:
            query = query.filter(Account.is_active == True)
        
        return query.all()
    
    def update_account(self, account_id: str, **kwargs) -> Optional[Account]:
        """Update account fields"""
        account = self.get_account(account_id)
        
        if not account:
            return None
        
        for key, value in kwargs.items():
            if hasattr(account, key):
                setattr(account, key, value)
        
        account.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(account)
        
        return account
    
    def update_last_scan(self, account_id: str) -> Optional[Account]:
        """Update last scan timestamp"""
        return self.update_account(
            account_id,
            last_scan_at=datetime.utcnow()
        )
    
    def delete_account(self, account_id: str) -> bool:
        """Delete account and associated credentials"""
        account = self.get_account(account_id)
        
        if not account:
            return False
        
        # Delete associated credentials
        self.db.query(Credential).filter(
            Credential.account_id == account_id
        ).delete()
        
        # Delete account
        self.db.delete(account)
        self.db.commit()
        
        return True
    
    def get_active_regions(self, account_id: str) -> List[str]:
        """Get enabled regions for an account"""
        account = self.get_account(account_id)
        
        if not account or not account.regions_enabled:
            return ["us-east-1"]
        
        return json.loads(account.regions_enabled)
