"""
AWS Infra Vision - Security Endpoints
Security findings and scanning API
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from backend.app.services.security_scanner import SecurityScanner
from backend.app.repositories.security_repo import SecurityRepository
from backend.app.utils.credential_manager import CredentialManager
from backend.app.repositories.account_repo import AccountRepository
from backend.app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()
credential_manager = CredentialManager()


class SecurityScanRequest(BaseModel):
    account_id: str
    regions: Optional[List[str]] = None


@router.get("/findings")
async def get_security_findings(
    account_id: str = Query(...),
    severity: Optional[str] = Query(None, pattern="^(low|medium|high|critical)$"),
    status: Optional[str] = Query(None, pattern="^(open|acknowledged|resolved|false_positive)$"),
    finding_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get security findings with filtering"""
    try:
        repo = SecurityRepository(db)
        findings, total = repo.get_findings(
            account_id=account_id,
            severity=severity,
            status=status,
            finding_type=finding_type,
            page=page,
            limit=limit
        )
        
        return {
            "success": True,
            "data": {
                "findings": findings,
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
            detail=f"Failed to get findings: {str(e)}"
        )


@router.get("/findings/{finding_id}")
async def get_finding_details(
    finding_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a security finding"""
    try:
        repo = SecurityRepository(db)
        finding = repo.get_finding_by_id(finding_id)
        
        if not finding:
            raise HTTPException(status_code=404, detail="Finding not found")
        
        return {
            "success": True,
            "data": finding
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get finding: {str(e)}"
        )


@router.put("/findings/{finding_id}/status")
async def update_finding_status(
    finding_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """Update the status of a security finding"""
    try:
        repo = SecurityRepository(db)
        updated = repo.update_finding_status(finding_id, status)
        
        if not updated:
            raise HTTPException(status_code=404, detail="Finding not found")
        
        return {
            "success": True,
            "data": {"message": f"Finding status updated to {status}"}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update finding: {str(e)}"
        )


@router.post("/scan")
async def trigger_security_scan(
    request: SecurityScanRequest,
    db: Session = Depends(get_db)
):
    """Trigger a comprehensive security scan"""
    try:
        # Get credentials
        account_id = request.account_id
        credentials = credential_manager.retrieve_credentials(account_id)
        if not credentials:
            raise HTTPException(status_code=401, detail="Credentials not found")
        
        # Get account regions
        account_repo = AccountRepository(db)
        regions = request.regions
        if not regions:
            regions = account_repo.get_active_regions(account_id)
        
        # Run scanner
        scanner = SecurityScanner(credentials, account_id)
        findings = scanner.scan_all(regions)
        
        # Store findings in database
        repo = SecurityRepository(db)
        stored_count = repo.bulk_insert_findings(account_id, findings)
        
        return {
            "success": True,
            "data": {
                "scan_id": f"sec-scan-{datetime.utcnow().timestamp()}",
                "account_id": account_id,
                "findings_found": len(findings),
                "findings_stored": stored_count,
                "severity_breakdown": {
                    "critical": sum(1 for f in findings if f["severity"] == "critical"),
                    "high": sum(1 for f in findings if f["severity"] == "high"),
                    "medium": sum(1 for f in findings if f["severity"] == "medium"),
                    "low": sum(1 for f in findings if f["severity"] == "low")
                },
                "message": f"Security scan complete. Found {len(findings)} issues."
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Security scan failed: {str(e)}"
        )


@router.get("/score")
async def get_security_score(
    account_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get overall security score"""
    try:
        repo = SecurityRepository(db)
        score = repo.calculate_security_score(account_id)
        
        return {
            "success": True,
            "data": score
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate score: {str(e)}"
        )
