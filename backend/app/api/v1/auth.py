"""
AWS Infra Vision - Authentication Endpoints
AWS credential management and account setup
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import json

from backend.app.services.aws_client import AWSClientFactory
from backend.app.utils.credential_manager import CredentialManager
from backend.app.repositories.account_repo import AccountRepository
from backend.app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()
credential_manager = CredentialManager()


class SetupWizardRequest(BaseModel):
    """Setup wizard request model"""
    credential_type: str = Field(..., description="Type of credentials")
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    profile_name: Optional[str] = None
    sso_start_url: Optional[str] = None
    sso_region: Optional[str] = None
    role_arn: Optional[str] = None
    external_id: Optional[str] = None
    session_name: Optional[str] = "AWSInfraVision"
    region: Optional[str] = "us-east-1"


class ValidateCredentialsRequest(BaseModel):
    """Validate credentials request"""
    account_id: str


class AccountResponse(BaseModel):
    """Account response model"""
    id: int
    account_id: str
    account_name: Optional[str]
    alias: Optional[str]
    is_active: bool
    created_at: datetime
    last_scan_at: Optional[datetime]
    regions_enabled: List[str]


@router.post("/setup-wizard", status_code=201)
async def setup_wizard(request: SetupWizardRequest, db: Session = Depends(get_db)):
    """
    Initial AWS credential setup wizard
    
    Supports:
    - Access Keys
    - AWS Profiles
    - AWS SSO
    - IAM Roles
    """
    try:
        # Prepare credentials dict
        credentials = {"type": request.credential_type}
        
        if request.credential_type == "access_key":
            if not request.access_key_id or not request.secret_access_key:
                raise HTTPException(
                    status_code=400,
                    detail="access_key_id and secret_access_key are required for access_key type"
                )
            credentials["access_key_id"] = request.access_key_id
            credentials["secret_access_key"] = request.secret_access_key
            credentials["region"] = request.region
            
        elif request.credential_type == "profile":
            if not request.profile_name:
                raise HTTPException(
                    status_code=400,
                    detail="profile_name is required for profile type"
                )
            credentials["profile_name"] = request.profile_name
            
        elif request.credential_type == "role":
            if not request.role_arn:
                raise HTTPException(
                    status_code=400,
                    detail="role_arn is required for role type"
                )
            credentials["role_arn"] = request.role_arn
            credentials["external_id"] = request.external_id
            credentials["session_name"] = request.session_name
        
        # Create AWS client and validate
        aws_factory = AWSClientFactory(credentials)
        if not aws_factory.validate_credentials():
            raise HTTPException(
                status_code=401,
                detail="Invalid AWS credentials. Please check your credentials and try again."
            )
        
        # Get account information
        account_id = aws_factory.get_account_id()
        if not account_id:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve account ID"
            )
        
        # Store credentials securely
        key_ref = credential_manager.store_credentials(account_id, credentials)
        
        # Create or update account in database
        account_repo = AccountRepository(db)
        account = account_repo.create_or_update_account(
            account_id=account_id,
            credential_type=request.credential_type,
            key_reference=key_ref,
            region=request.region
        )
        
        return {
            "success": True,
            "data": {
                "account_id": account_id,
                "message": "AWS account configured successfully",
                "next_steps": [
                    "Run a resource scan to discover your infrastructure",
                    "Configure cost analytics",
                    "Set up security scanning"
                ]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Setup failed: {str(e)}"
        )


@router.post("/validate")
async def validate_credentials(request: ValidateCredentialsRequest, db: Session = Depends(get_db)):
    """Validate stored AWS credentials"""
    try:
        account_repo = AccountRepository(db)
        account = account_repo.get_account(request.account_id)
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Retrieve credentials from secure storage
        credentials = credential_manager.retrieve_credentials(request.account_id)
        
        if not credentials:
            raise HTTPException(status_code=401, detail="Credentials not found")
        
        # Validate
        aws_factory = AWSClientFactory(credentials)
        is_valid = aws_factory.validate_credentials()
        
        return {
            "success": True,
            "data": {
                "valid": is_valid,
                "account_id": request.account_id,
                "message": "Credentials are valid" if is_valid else "Credentials are invalid"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )


@router.get("/accounts")
async def list_accounts(db: Session = Depends(get_db)):
    """List all configured AWS accounts"""
    try:
        account_repo = AccountRepository(db)
        accounts = account_repo.list_accounts()
        
        data = [
            AccountResponse(
                id=acc.id,
                account_id=acc.account_id,
                account_name=acc.account_name,
                alias=acc.alias,
                is_active=acc.is_active,
                created_at=acc.created_at,
                last_scan_at=acc.last_scan_at,
                regions_enabled=json.loads(acc.regions_enabled) if acc.regions_enabled else []
            )
            for acc in accounts
        ]
        
        return {
            "success": True,
            "data": data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list accounts: {str(e)}"
        )


@router.delete("/accounts/{account_id}", status_code=204)
async def delete_account(account_id: str, db: Session = Depends(get_db)):
    """Remove an AWS account configuration"""
    try:
        account_repo = AccountRepository(db)
        account = account_repo.get_account(account_id)
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Delete credentials from secure storage
        credential_manager.delete_credentials(account_id)
        
        # Delete from database
        account_repo.delete_account(account_id)
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete account: {str(e)}"
        )
