"""
AWS Infra Vision - Security Scanner Service
Detects common AWS security misconfigurations
"""
import boto3
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SecurityScanner:
    """Scans AWS account for security issues"""
    
    def __init__(self, credentials: Dict, account_id: str):
        self.credentials = credentials
        self.account_id = account_id
        self.findings = []
    
    def _get_client(self, service: str, region: str = "us-east-1"):
        """Create AWS client"""
        session = boto3.Session(
            aws_access_key_id=self.credentials.get("access_key_id"),
            aws_secret_access_key=self.credentials.get("secret_access_key")
        )
        return session.client(service, region_name=region)
    
    def scan_all(self, regions: List[str] = None) -> List[Dict]:
        """Run all security checks"""
        self.findings = []
        
        regions = regions or ["us-east-1", "us-west-2", "eu-west-1"]
        
        # Run all checks
        self._check_public_s3_buckets()
        self._check_open_security_groups(regions)
        self._check_unused_iam_users()
        self._check_unused_access_keys()
        self._check_root_account_usage()
        self._check_unencrypted_ebs_volumes(regions)
        self._check_public_rds_instances(regions)
        
        logger.info(f"Security scan complete. Found {len(self.findings)} findings.")
        return self.findings
    
    def _add_finding(
        self,
        finding_type: str,
        severity: str,
        title: str,
        description: str,
        resource_id: str = None,
        resource_arn: str = None,
        service_name: str = None,
        region: str = None,
        remediation: str = None,
        metadata: Dict = None
    ):
        """Add a security finding"""
        self.findings.append({
            "account_id": self.account_id,
            "finding_type": finding_type,
            "severity": severity,
            "title": title,
            "description": description,
            "resource_id": resource_id,
            "resource_arn": resource_arn,
            "service_name": service_name,
            "region": region,
            "remediation": remediation,
            "status": "open",
            "detected_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        })
    
    def _check_public_s3_buckets(self):
        """Check for publicly accessible S3 buckets"""
        try:
            s3 = self._get_client("s3")
            response = s3.list_buckets()
            
            for bucket in response.get("Buckets", []):
                bucket_name = bucket["Name"]
                
                try:
                    # Check bucket policy
                    try:
                        policy = s3.get_bucket_policy(Bucket=bucket_name)
                        # Simple check for public access in policy
                        if "Principal" in policy.get("Policy", "") and "*" in policy["Policy"]:
                            self._add_finding(
                                finding_type="public_s3_bucket",
                                severity="critical",
                                title=f"Public S3 Bucket: {bucket_name}",
                                description=f"S3 bucket {bucket_name} has a policy that may allow public access",
                                resource_id=bucket_name,
                                resource_arn=f"arn:aws:s3:::{bucket_name}",
                                service_name="S3",
                                remediation="Review and restrict bucket policy. Remove wildcard (*) principals unless absolutely necessary."
                            )
                    except:
                        pass  # No policy is fine
                    
                    # Check ACL
                    acl = s3.get_bucket_acl(Bucket=bucket_name)
                    for grant in acl.get("Grants", []):
                        grantee = grant.get("Grantee", {})
                        if grantee.get("URI") and "AllUsers" in grantee["URI"]:
                            self._add_finding(
                                finding_type="public_s3_acl",
                                severity="high",
                                title=f"Public ACL on S3 Bucket: {bucket_name}",
                                description=f"S3 bucket {bucket_name} has public read ACL",
                                resource_id=bucket_name,
                                resource_arn=f"arn:aws:s3:::{bucket_name}",
                                service_name="S3",
                                remediation="Remove public ACL grants. Use bucket policies instead."
                            )
                
                except Exception as e:
                    logger.debug(f"Error checking bucket {bucket_name}: {str(e)}")
        
        except Exception as e:
            logger.error(f"S3 security check error: {str(e)}")
    
    def _check_open_security_groups(self, regions: List[str]):
        """Check for overly permissive security groups"""
        for region in regions:
            try:
                ec2 = self._get_client("ec2", region)
                response = ec2.describe_security_groups()
                
                for sg in response.get("SecurityGroups", []):
                    sg_id = sg["GroupId"]
                    sg_name = sg.get("GroupName", sg_id)
                    
                    # Check ingress rules
                    for rule in sg.get("IpPermissions", []):
                        for ip_range in rule.get("IpRanges", []):
                            cidr = ip_range.get("CidrIp", "")
                            
                            # Check for 0.0.0.0/0 (open to world)
                            if cidr == "0.0.0.0/0":
                                port_range = self._get_port_range(rule)
                                
                                # Critical if SSH (22) or RDP (3389) is open
                                if 22 in self._get_ports(rule) or 3389 in self._get_ports(rule):
                                    severity = "critical"
                                elif self._is_all_traffic(rule):
                                    severity = "critical"
                                else:
                                    severity = "high"
                                
                                self._add_finding(
                                    finding_type="open_security_group",
                                    severity=severity,
                                    title=f"Open Security Group: {sg_name}",
                                    description=f"Security group {sg_name} ({sg_id}) allows inbound traffic from 0.0.0.0/0 on {port_range}",
                                    resource_id=sg_id,
                                    resource_arn=f"arn:aws:ec2:{region}:{self.account_id}:security-group/{sg_id}",
                                    service_name="EC2",
                                    region=region,
                                    remediation="Restrict CIDR range to specific IP addresses or ranges. Avoid using 0.0.0.0/0.",
                                    metadata={
                                        "cidr": cidr,
                                        "port_range": port_range,
                                        "protocol": rule.get("IpProtocol", "tcp")
                                    }
                                )
            
            except Exception as e:
                logger.error(f"Security group check error in {region}: {str(e)}")
    
    def _check_unused_iam_users(self):
        """Check for unused IAM users"""
        try:
            iam = self._get_client("iam")
            response = iam.list_users()
            
            for user in response.get("Users", []):
                username = user["UserName"]
                
                # Get last used date
                try:
                    access_keys = iam.list_access_keys(UserName=username)
                    
                    for key in access_keys.get("AccessKeyMetadata", []):
                        key_id = key["AccessKeyId"]
                        
                        # Get access key last used
                        try:
                            last_used = iam.get_access_key_last_used(
                                UserName=username,
                                AccessKeyId=key_id
                            )
                            
                            last_used_date = last_used.get("AccessKeyLastUsed", {}).get("LastUsedDate")
                            
                            if last_used_date:
                                days_since_use = (datetime.utcnow().replace(tzinfo=None) - last_used_date.replace(tzinfo=None)).days
                                
                                if days_since_use > 90:
                                    self._add_finding(
                                        finding_type="unused_iam_user",
                                        severity="medium",
                                        title=f"Unused IAM User: {username}",
                                        description=f"IAM user {username} has not been used in {days_since_use} days",
                                        resource_id=username,
                                        service_name="IAM",
                                        remediation="Review if this user is still needed. Consider disabling or deleting the user.",
                                        metadata={
                                            "days_inactive": days_since_use,
                                            "last_used": last_used_date.isoformat()
                                        }
                                    )
                        except:
                            pass
                
                except Exception as e:
                    logger.debug(f"Error checking user {username}: {str(e)}")
        
        except Exception as e:
            logger.error(f"IAM user check error: {str(e)}")
    
    def _check_unused_access_keys(self):
        """Check for unused access keys"""
        try:
            iam = self._get_client("iam")
            response = iam.list_users()
            
            for user in response.get("Users", []):
                username = user["UserName"]
                
                try:
                    keys = iam.list_access_keys(UserName=username)
                    
                    for key in keys.get("AccessKeyMetadata", []):
                        key_id = key["AccessKeyId"]
                        status = key["Status"]
                        created = key["CreateDate"]
                        
                        # Check if key is active but old
                        days_old = (datetime.utcnow().replace(tzinfo=None) - created.replace(tzinfo=None)).days
                        
                        if status == "Active" and days_old > 180:
                            self._add_finding(
                                finding_type="old_access_key",
                                severity="medium",
                                title=f"Old Access Key for {username}",
                                description=f"Access key {key_id} for user {username} is {days_old} days old",
                                resource_id=username,
                                service_name="IAM",
                                remediation="Rotate access keys regularly. Recommended rotation period is 90 days.",
                                metadata={
                                    "key_id": key_id,
                                    "age_days": days_old,
                                    "created": created.isoformat()
                                }
                            )
                
                except Exception as e:
                    logger.debug(f"Error checking keys for {username}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Access key check error: {str(e)}")
    
    def _check_root_account_usage(self):
        """Check for root account usage"""
        try:
            cloudtrail = self._get_client("cloudtrail")
            
            # Look for root account activity in last 24 hours
            end_time = datetime.utcnow()
            start_time = end_time.replace(hour=0, minute=0, second=0, microsecond=0)
            
            try:
                events = cloudtrail.lookup_events(
                    LookupAttributes=[
                        {"AttributeKey": "Username", "AttributeValue": "root"}
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    MaxResults=5
                )
                
                if events.get("Events"):
                    self._add_finding(
                        finding_type="root_account_usage",
                        severity="critical",
                        title="Root Account Activity Detected",
                        description=f"Root account was used {len(events['Events'])} times in the last 24 hours",
                        service_name="IAM",
                        remediation="Avoid using root account for daily operations. Create IAM users with appropriate permissions.",
                        metadata={
                            "event_count": len(events["Events"]),
                            "period": "last 24 hours"
                        }
                    )
            except:
                pass  # CloudTrail might not be enabled
        
        except Exception as e:
            logger.error(f"Root account check error: {str(e)}")
    
    def _check_unencrypted_ebs_volumes(self, regions: List[str]):
        """Check for unencrypted EBS volumes"""
        for region in regions:
            try:
                ec2 = self._get_client("ec2", region)
                response = ec2.describe_volumes()
                
                for volume in response.get("Volumes", []):
                    if not volume.get("Encrypted", False):
                        self._add_finding(
                            finding_type="unencrypted_ebs",
                            severity="medium",
                            title=f"Unencrypted EBS Volume: {volume['VolumeId']}",
                            description=f"EBS volume {volume['VolumeId']} in {region} is not encrypted",
                            resource_id=volume["VolumeId"],
                            resource_arn=f"arn:aws:ec2:{region}:{self.account_id}:volume/{volume['VolumeId']}",
                            service_name="EBS",
                            region=region,
                            remediation="Enable encryption for EBS volumes. Create encrypted snapshots and restore.",
                            metadata={
                                "size": volume.get("Size"),
                                "state": volume.get("State")
                            }
                        )
            
            except Exception as e:
                logger.error(f"EBS encryption check error in {region}: {str(e)}")
    
    def _check_public_rds_instances(self, regions: List[str]):
        """Check for publicly accessible RDS instances"""
        for region in regions:
            try:
                rds = self._get_client("rds", region)
                response = rds.describe_db_instances()
                
                for db in response.get("DBInstances", []):
                    if db.get("PubliclyAccessible", False):
                        self._add_finding(
                            finding_type="public_rds",
                            severity="high",
                            title=f"Publicly Accessible RDS: {db['DBInstanceIdentifier']}",
                            description=f"RDS instance {db['DBInstanceIdentifier']} is publicly accessible",
                            resource_id=db["DBInstanceIdentifier"],
                            resource_arn=db.get("DBInstanceArn", ""),
                            service_name="RDS",
                            region=region,
                            remediation="Disable public accessibility unless absolutely required. Use VPC and security groups for access control.",
                            metadata={
                                "engine": db.get("Engine"),
                                "instance_class": db.get("DBInstanceClass")
                            }
                        )
            
            except Exception as e:
                logger.error(f"RDS check error in {region}: {str(e)}")
    
    @staticmethod
    def _get_port_range(rule: Dict) -> str:
        """Get port range string from security group rule"""
        from_port = rule.get("FromPort")
        to_port = rule.get("ToPort")
        
        if from_port and to_port:
            if from_port == to_port:
                return f"port {from_port}"
            return f"ports {from_port}-{to_port}"
        return "all ports"
    
    @staticmethod
    def _get_ports(rule: Dict) -> List[int]:
        """Get list of ports from rule"""
        from_port = rule.get("FromPort")
        to_port = rule.get("ToPort")
        
        if from_port and to_port:
            return list(range(from_port, to_port + 1))
        return []
    
    @staticmethod
    def _is_all_traffic(rule: Dict) -> bool:
        """Check if rule allows all traffic"""
        return (
            rule.get("IpProtocol") == "-1" and
            not rule.get("FromPort") and
            not rule.get("ToPort")
        )
