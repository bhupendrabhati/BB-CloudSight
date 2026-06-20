"""
AWS Infra Vision - Resource Repository
Data access layer for AWS resources
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json

from backend.app.database import Resource, ResourceTag


class ResourceRepository:
    """Repository for resource operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def bulk_upsert_resources(self, account_id: str, resources: List[Dict]) -> int:
        """
        Bulk insert or update resources
        
        Args:
            account_id: AWS account ID
            resources: List of resource dictionaries
            
        Returns:
            Number of resources stored
        """
        count = 0
        
        for res in resources:
            try:
                # Check if resource exists
                existing = self.db.query(Resource).filter(
                    Resource.resource_id == res["resource_id"],
                    Resource.account_id == account_id
                ).first()
                
                if existing:
                    # Update existing resource
                    for key, value in res.items():
                        if hasattr(existing, key) and key not in ["tags"]:
                            setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                else:
                    # Create new resource
                    resource = Resource(
                        resource_id=res["resource_id"],
                        arn=res["arn"],
                        account_id=account_id,
                        service_name=res["service_name"],
                        resource_type=res["resource_type"],
                        region=res["region"],
                        name=res.get("name"),
                        status=res.get("status"),
                        state=res.get("state"),
                        environment=res.get("environment", ""),
                        owner=res.get("owner", ""),
                        created_at_resource=res.get("created_at_resource"),
                        configuration=json.dumps(res.get("metadata", {})),
                        metadata_json=json.dumps(res.get("metadata", {}))
                    )
                    self.db.add(resource)
                
                # Handle tags separately
                tags = res.get("tags", {})
                if tags:
                    self._upsert_tags(res["resource_id"], account_id, tags)
                
                count += 1
                
            except Exception as e:
                # Log error but continue with other resources
                print(f"Error storing resource {res.get('resource_id')}: {str(e)}")
                continue
        
        self.db.commit()
        return count
    
    def _upsert_tags(self, resource_id: str, account_id: str, tags: Dict):
        """Insert or update resource tags"""
        for key, value in tags.items():
            existing_tag = self.db.query(ResourceTag).filter(
                ResourceTag.resource_id == resource_id,
                ResourceTag.account_id == account_id,
                ResourceTag.tag_key == key
            ).first()
            
            if existing_tag:
                existing_tag.tag_value = value
            else:
                tag = ResourceTag(
                    resource_id=resource_id,
                    account_id=account_id,
                    tag_key=key,
                    tag_value=value
                )
                self.db.add(tag)
    
    def get_resources(
        self,
        account_id: str,
        service: Optional[str] = None,
        region: Optional[str] = None,
        resource_type: Optional[str] = None,
        environment: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
        sort_by: str = "name",
        order: str = "asc"
    ) -> Tuple[List[Dict], int]:
        """
        Get paginated resources with filters
        
        Returns:
            Tuple of (resources list, total count)
        """
        query = self.db.query(Resource).filter(
            Resource.account_id == account_id
        )
        
        # Apply filters
        if service:
            query = query.filter(Resource.service_name == service)
        
        if region:
            query = query.filter(Resource.region == region)
        
        if resource_type:
            query = query.filter(Resource.resource_type == resource_type)
        
        if environment:
            query = query.filter(Resource.environment == environment)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Resource.name.ilike(search_term)) |
                (Resource.resource_id.ilike(search_term)) |
                (Resource.arn.ilike(search_term))
            )
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        sort_column = getattr(Resource, sort_by, Resource.name)
        if order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Apply pagination
        offset = (page - 1) * limit
        resources = query.offset(offset).limit(limit).all()
        
        # Convert to dictionaries
        result = []
        for res in resources:
            res_dict = {
                "id": res.id,
                "resource_id": res.resource_id,
                "arn": res.arn,
                "service_name": res.service_name,
                "resource_type": res.resource_type,
                "region": res.region,
                "name": res.name,
                "status": res.status,
                "environment": res.environment,
                "owner": res.owner,
                "is_terraform_managed": res.is_terraform_managed,
                "discovered_at": res.discovered_at.isoformat() if res.discovered_at else None
            }
            result.append(res_dict)
        
        return result, total
    
    def get_resource_by_id(self, resource_id: str, account_id: str) -> Optional[Dict]:
        """Get full resource details including tags"""
        resource = self.db.query(Resource).filter(
            Resource.resource_id == resource_id,
            Resource.account_id == account_id
        ).first()
        
        if not resource:
            return None
        
        # Get tags
        tags = self.db.query(ResourceTag).filter(
            ResourceTag.resource_id == resource_id,
            ResourceTag.account_id == account_id
        ).all()
        
        tag_dict = {tag.tag_key: tag.tag_value for tag in tags}
        
        return {
            "id": resource.id,
            "resource_id": resource.resource_id,
            "arn": resource.arn,
            "account_id": resource.account_id,
            "service_name": resource.service_name,
            "resource_type": resource.resource_type,
            "region": resource.region,
            "name": resource.name,
            "status": resource.status,
            "state": resource.state,
            "environment": resource.environment,
            "owner": resource.owner,
            "created_at_resource": resource.created_at_resource.isoformat() if resource.created_at_resource else None,
            "discovered_at": resource.discovered_at.isoformat() if resource.discovered_at else None,
            "updated_at": resource.updated_at.isoformat() if resource.updated_at else None,
            "is_terraform_managed": resource.is_terraform_managed,
            "terraform_resource_id": resource.terraform_resource_id,
            "is_cloudformation_managed": resource.is_cloudformation_managed,
            "configuration": json.loads(resource.configuration) if resource.configuration else {},
            "tags": tag_dict
        }
    
    def get_resource_stats(self, account_id: str) -> Dict:
        """Get resource statistics"""
        # By service
        by_service = self.db.query(
            Resource.service_name,
            func.count(Resource.id).label("count")
        ).filter(
            Resource.account_id == account_id
        ).group_by(
            Resource.service_name
        ).all()
        
        # By region
        by_region = self.db.query(
            Resource.region,
            func.count(Resource.id).label("count")
        ).filter(
            Resource.account_id == account_id
        ).group_by(
            Resource.region
        ).all()
        
        # By type
        by_type = self.db.query(
            Resource.resource_type,
            func.count(Resource.id).label("count")
        ).filter(
            Resource.account_id == account_id
        ).group_by(
            Resource.resource_type
        ).all()
        
        # By environment
        by_env = self.db.query(
            Resource.environment,
            func.count(Resource.id).label("count")
        ).filter(
            Resource.account_id == account_id
        ).group_by(
            Resource.environment
        ).all()
        
        # Total
        total = self.db.query(func.count(Resource.id)).filter(
            Resource.account_id == account_id
        ).scalar()
        
        return {
            "total_resources": total,
            "by_service": [{"service": s[0], "count": s[1]} for s in by_service],
            "by_region": [{"region": r[0], "count": r[1]} for r in by_region],
            "by_type": [{"type": t[0], "count": t[1]} for t in by_type],
            "by_environment": [{"environment": e[0] or "untagged", "count": e[1]} for e in by_env]
        }
    
    def delete_resources_for_account(self, account_id: str) -> int:
        """Delete all resources for an account"""
        # Delete tags first
        self.db.query(ResourceTag).filter(
            ResourceTag.account_id == account_id
        ).delete()
        
        # Delete resources
        count = self.db.query(Resource).filter(
            Resource.account_id == account_id
        ).delete()
        
        self.db.commit()
        return count
