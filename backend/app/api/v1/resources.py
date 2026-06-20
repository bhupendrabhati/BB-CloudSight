"""
AWS Infra Vision - Resource Endpoints
Resource inventory management API
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

from backend.app.services.aws_client import ResourceDiscoveryEngine
from backend.app.services.aws_client import AWSClientFactory
from backend.app.repositories.resource_repo import ResourceRepository
from backend.app.repositories.account_repo import AccountRepository
from backend.app.utils.credential_manager import CredentialManager
from backend.app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()
credential_manager = CredentialManager()


class ScanRequest(BaseModel):
    account_id: str
    scan_type: str = "full"
    regions: Optional[List[str]] = None


@router.post("/scan")
async def trigger_scan(
    request: ScanRequest,
    db: Session = Depends(get_db)
):
    """
    Trigger resource discovery scan
    
    Args:
        account_id: AWS account ID
        scan_type: 'full' or 'incremental'
        regions: Specific regions to scan (optional)
    """
    try:
        account_id = request.account_id
        # Get account
        account_repo = AccountRepository(db)
        account = account_repo.get_account(account_id)
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Retrieve credentials
        credentials = credential_manager.retrieve_credentials(account_id)
        
        if not credentials:
            raise HTTPException(status_code=401, detail="Credentials not found")
        
        # Create discovery engine
        aws_factory = AWSClientFactory(credentials)
        discovery_engine = ResourceDiscoveryEngine(aws_factory)
        
        # Determine regions to scan
        if not request.regions:
            regions = account_repo.get_active_regions(account_id)
        else:
            regions = request.regions
        
        # Start scan
        resources = discovery_engine.scan_all_regions(regions)
        
        # Store resources in database
        resource_repo = ResourceRepository(db)
        stored_count = resource_repo.bulk_upsert_resources(account_id, resources)
        
        # Update account last scan time
        account_repo.update_last_scan(account_id)
        
        return {
            "success": True,
            "data": {
                "scan_id": f"scan-{datetime.utcnow().timestamp()}",
                "account_id": account_id,
                "scan_type": request.scan_type,
                "regions_scanned": len(regions),
                "resources_found": len(resources),
                "resources_stored": stored_count,
                "scan_progress": discovery_engine.get_scan_progress(),
                "message": f"Scan completed. Found {len(resources)} resources."
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scan failed: {str(e)}"
        )


@router.get("/")
async def list_resources(
    account_id: str = Query(..., description="AWS account ID"),
    service: Optional[str] = Query(None, description="Filter by service"),
    region: Optional[str] = Query(None, description="Filter by region"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    environment: Optional[str] = Query(None, description="Filter by environment"),
    search: Optional[str] = Query(None, description="Search term"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("name", description="Sort field"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db)
):
    """
    Get resource inventory with filtering and pagination
    """
    try:
        resource_repo = ResourceRepository(db)
        
        resources, total = resource_repo.get_resources(
            account_id=account_id,
            service=service,
            region=region,
            resource_type=resource_type,
            environment=environment,
            search=search,
            page=page,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        return {
            "success": True,
            "data": {
                "resources": resources,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve resources: {str(e)}"
        )


@router.get("/export")
async def export_resources(
    account_id: str = Query(..., description="AWS account ID"),
    format: str = Query("csv", pattern="^(csv|json)$", description="Export format")
):
    """Export resources to CSV or JSON"""
    try:
        return {
            "success": True,
            "data": {
                "message": f"Export in {format.upper()} format initiated",
                "download_url": f"/api/v1/resources/download/{account_id}.{format}"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Export failed: {str(e)}"
        )


@router.get("/stats/summary")
async def get_resource_stats(
    account_id: str = Query(..., description="AWS account ID"),
    db: Session = Depends(get_db)
):
    """Get resource statistics grouped by service, region, and type"""
    try:
        resource_repo = ResourceRepository(db)
        stats = resource_repo.get_resource_stats(account_id)
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve stats: {str(e)}"
        )


@router.get("/{resource_id}")
async def get_resource_details(
    resource_id: str,
    account_id: str = Query(..., description="AWS account ID"),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific resource"""
    try:
        resource_repo = ResourceRepository(db)
        resource = resource_repo.get_resource_by_id(resource_id, account_id)
        
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        return {
            "success": True,
            "data": resource
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve resource: {str(e)}"
        )
