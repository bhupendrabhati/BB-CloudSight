"""
AWS Infra Vision - Security Repository
Data access layer for security findings
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json

from backend.app.database import SecurityFinding


class SecurityRepository:
    """Repository for security finding operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def bulk_insert_findings(self, account_id: str, findings: List[Dict]) -> int:
        """
        Bulk insert security findings
        
        Args:
            account_id: AWS account ID
            findings: List of finding dictionaries
            
        Returns:
            Number of findings stored
        """
        count = 0
        
        for finding in findings:
            try:
                # Check if similar finding exists
                existing = self.db.query(SecurityFinding).filter(
                    SecurityFinding.account_id == account_id,
                    SecurityFinding.finding_type == finding["finding_type"],
                    SecurityFinding.resource_id == finding.get("resource_id"),
                    SecurityFinding.status == "open"
                ).first()
                
                if not existing:
                    sf = SecurityFinding(
                        account_id=account_id,
                        finding_type=finding["finding_type"],
                        severity=finding["severity"],
                        resource_id=finding.get("resource_id"),
                        resource_arn=finding.get("resource_arn"),
                        service_name=finding.get("service_name"),
                        region=finding.get("region"),
                        title=finding["title"],
                        description=finding.get("description"),
                        remediation=finding.get("remediation"),
                        status="open",
                        metadata_json=json.dumps(finding.get("metadata", {}))
                    )
                    self.db.add(sf)
                    count += 1
            
            except Exception as e:
                print(f"Error storing finding: {str(e)}")
                continue
        
        self.db.commit()
        return count
    
    def get_findings(
        self,
        account_id: str,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        finding_type: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
        sort_by: str = "detected_at",
        order: str = "desc"
    ) -> Tuple[List[Dict], int]:
        """
        Get paginated security findings with filters
        
        Returns:
            Tuple of (findings list, total count)
        """
        query = self.db.query(SecurityFinding).filter(
            SecurityFinding.account_id == account_id
        )
        
        if severity:
            query = query.filter(SecurityFinding.severity == severity)
        
        if status:
            query = query.filter(SecurityFinding.status == status)
        
        if finding_type:
            query = query.filter(SecurityFinding.finding_type == finding_type)
        
        total = query.count()
        
        sort_column = getattr(SecurityFinding, sort_by, SecurityFinding.detected_at)
        if order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        offset = (page - 1) * limit
        findings = query.offset(offset).limit(limit).all()
        
        result = []
        for f in findings:
            result.append({
                "id": f.id,
                "account_id": f.account_id,
                "finding_type": f.finding_type,
                "severity": f.severity,
                "resource_id": f.resource_id,
                "resource_arn": f.resource_arn,
                "service_name": f.service_name,
                "region": f.region,
                "title": f.title,
                "description": f.description,
                "remediation": f.remediation,
                "status": f.status,
                "detected_at": f.detected_at.isoformat() if f.detected_at else None,
                "resolved_at": f.resolved_at.isoformat() if f.resolved_at else None
            })
        
        return result, total
    
    def get_finding_by_id(self, finding_id: int) -> Optional[Dict]:
        """Get detailed information about a specific finding"""
        finding = self.db.query(SecurityFinding).filter(
            SecurityFinding.id == finding_id
        ).first()
        
        if not finding:
            return None
        
        return {
            "id": finding.id,
            "account_id": finding.account_id,
            "finding_type": finding.finding_type,
            "severity": finding.severity,
            "resource_id": finding.resource_id,
            "resource_arn": finding.resource_arn,
            "service_name": finding.service_name,
            "region": finding.region,
            "title": finding.title,
            "description": finding.description,
            "remediation": finding.remediation,
            "compliance_standard": finding.compliance_standard,
            "status": finding.status,
            "detected_at": finding.detected_at.isoformat() if finding.detected_at else None,
            "resolved_at": finding.resolved_at.isoformat() if finding.resolved_at else None,
            "metadata": json.loads(finding.metadata_json) if finding.metadata_json else {}
        }
    
    def update_finding_status(self, finding_id: int, status: str) -> bool:
        """Update the status of a finding"""
        finding = self.db.query(SecurityFinding).filter(
            SecurityFinding.id == finding_id
        ).first()
        
        if not finding:
            return False
        
        finding.status = status
        if status in ["resolved", "false_positive"]:
            finding.resolved_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def calculate_security_score(self, account_id: str) -> Dict:
        """Calculate overall security score based on findings"""
        total = self.db.query(func.count(SecurityFinding.id)).filter(
            SecurityFinding.account_id == account_id
        ).scalar() or 0
        
        open_findings = self.db.query(func.count(SecurityFinding.id)).filter(
            SecurityFinding.account_id == account_id,
            SecurityFinding.status == "open"
        ).scalar() or 0
        
        by_severity = self.db.query(
            SecurityFinding.severity,
            func.count(SecurityFinding.id).label("count")
        ).filter(
            SecurityFinding.account_id == account_id,
            SecurityFinding.status == "open"
        ).group_by(SecurityFinding.severity).all()
        
        severity_map = {s[0]: s[1] for s in by_severity}
        
        # Calculate score (simple heuristic)
        critical_score = severity_map.get("critical", 0) * 25
        high_score = severity_map.get("high", 0) * 15
        medium_score = severity_map.get("medium", 0) * 5
        low_score = severity_map.get("low", 0) * 1
        
        penalty = min(critical_score + high_score + medium_score + low_score, 100)
        score = max(0, 100 - penalty)
        
        return {
            "score": score,
            "grade": "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D" if score >= 60 else "F",
            "total_findings": total,
            "open_findings": open_findings,
            "severity_breakdown": {
                "critical": severity_map.get("critical", 0),
                "high": severity_map.get("high", 0),
                "medium": severity_map.get("medium", 0),
                "low": severity_map.get("low", 0)
            },
            "resolved_findings": total - open_findings,
            "resolution_rate": round(((total - open_findings) / total * 100), 2) if total > 0 else 0
        }
