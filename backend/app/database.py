"""
AWS Infra Vision - Database Models
SQLAlchemy ORM models for SQLite database
"""
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, 
    DateTime, Float, Text, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from backend.app.config import DATABASE_PATH

# Database setup
engine = create_engine(
    f"sqlite:///{DATABASE_PATH}",
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Account(Base):
    """AWS Account configuration"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(12), unique=True, nullable=False, index=True)
    account_name = Column(String(255))
    alias = Column(String(255))
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scan_at = Column(DateTime)
    regions_enabled = Column(Text)  # JSON array
    metadata_json = Column(Text)  # JSON
    
    # Relationships
    resources = relationship("Resource", back_populates="account")
    costs = relationship("Cost", back_populates="account")
    security_findings = relationship("SecurityFinding", back_populates="account")
    
    def __repr__(self):
        return f"<Account {self.account_id} ({self.alias or self.account_name})>"


class Credential(Base):
    """AWS credential storage reference"""
    __tablename__ = "credentials"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(12), ForeignKey("accounts.account_id"), nullable=False, index=True)
    credential_type = Column(String(50), nullable=False)  # access_key, profile, sso, role
    key_reference = Column(String(255), nullable=False)  # OS keychain reference
    role_arn = Column(String(255))
    external_id = Column(String(255))
    session_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)


class Resource(Base):
    """Discovered AWS resource"""
    __tablename__ = "resources"
    __table_args__ = (
        UniqueConstraint("resource_id", "account_id", name="uq_resource_account"),
        Index("idx_resources_service", "service_name"),
        Index("idx_resources_region", "region"),
        Index("idx_resources_type", "resource_type"),
        Index("idx_resources_env", "environment"),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(String(255), nullable=False)
    arn = Column(String(1024), unique=True, nullable=False)
    account_id = Column(String(12), ForeignKey("accounts.account_id"), nullable=False, index=True)
    service_name = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    region = Column(String(50), nullable=False)
    name = Column(String(500))
    status = Column(String(50))
    state = Column(String(50))
    environment = Column(String(50))  # from tags
    owner = Column(String(255))  # from tags
    created_at_resource = Column(DateTime)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_terraform_managed = Column(Boolean, default=False)
    terraform_resource_id = Column(String(500))
    terraform_workspace = Column(String(255))
    is_cloudformation_managed = Column(Boolean, default=False)
    cloudformation_stack_id = Column(String(500))
    configuration = Column(Text)  # JSON
    metadata_json = Column(Text)  # JSON
    
    # Relationships
    account = relationship("Account", back_populates="resources")
    tags = relationship("ResourceTag", back_populates="resource",
        primaryjoin="and_(ResourceTag.resource_id==Resource.resource_id, ResourceTag.account_id==Resource.account_id)",
        foreign_keys="[ResourceTag.resource_id, ResourceTag.account_id]")
    
    def __repr__(self):
        return f"<Resource {self.resource_type}:{self.name or self.resource_id}>"


class ResourceTag(Base):
    """Resource tags (normalized)"""
    __tablename__ = "resource_tags"
    __table_args__ = (
        Index("idx_tags_resource", "resource_id", "account_id"),
        Index("idx_tags_key", "tag_key"),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(String(255), nullable=False)
    account_id = Column(String(12), nullable=False)
    tag_key = Column(String(255), nullable=False)
    tag_value = Column(Text)
    
    # Relationship
    resource = relationship("Resource", back_populates="tags",
        primaryjoin="and_(ResourceTag.resource_id==Resource.resource_id, ResourceTag.account_id==Resource.account_id)",
        foreign_keys="[ResourceTag.resource_id, ResourceTag.account_id]",
        overlaps="tags")


class Cost(Base):
    """Cost data from AWS Cost Explorer"""
    __tablename__ = "costs"
    __table_args__ = (
        Index("idx_costs_account_date", "account_id", "date"),
        Index("idx_costs_service", "service_name"),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(12), ForeignKey("accounts.account_id"), nullable=False)
    date = Column(DateTime, nullable=False)
    service_name = Column(String(100), nullable=False)
    region = Column(String(50))
    resource_id = Column(String(255))
    usage_type = Column(String(255))
    operation = Column(String(255))
    unblended_cost = Column(Float, nullable=False)
    amortized_cost = Column(Float)
    currency = Column(String(10), default="USD")
    tags = Column(Text)  # JSON
    
    # Relationship
    account = relationship("Account", back_populates="costs")


class SecurityFinding(Base):
    """Security finding"""
    __tablename__ = "security_findings"
    __table_args__ = (
        Index("idx_findings_severity", "severity"),
        Index("idx_findings_status", "status"),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(12), ForeignKey("accounts.account_id"), nullable=False, index=True)
    finding_type = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    resource_id = Column(String(255))
    resource_arn = Column(String(1024))
    service_name = Column(String(100))
    region = Column(String(50))
    title = Column(String(500), nullable=False)
    description = Column(Text)
    remediation = Column(Text)
    compliance_standard = Column(String(100))
    status = Column(String(20), default="open")
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    metadata_json = Column(Text)  # JSON
    
    # Relationship
    account = relationship("Account", back_populates="security_findings")


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
