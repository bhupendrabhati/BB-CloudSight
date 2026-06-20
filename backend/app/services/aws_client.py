"""
AWS Infra Vision - AWS Client Factory & Discovery Engine
Production-ready AWS service integration
"""
import boto3
from botocore.config import Config
from typing import Dict, List, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class AWSClientFactory:
    """Factory for creating AWS service clients with proper configuration"""
    
    # AWS regions to scan
    ALL_REGIONS = [
        "us-east-1", "us-east-2", "us-west-1", "us-west-2",
        "eu-west-1", "eu-west-2", "eu-west-3", "eu-central-1",
        "ap-southeast-1", "ap-southeast-2", "ap-northeast-1", "ap-northeast-2",
        "sa-east-1", "ca-central-1", "ap-south-1"
    ]
    
    def __init__(self, credentials: Dict):
        """
        Initialize with credentials
        
        Args:
            credentials: Dict with credential information
                - type: 'access_key', 'profile', 'sso', 'role'
                - access_key_id, secret_access_key (for access_key type)
                - profile_name (for profile type)
                - role_arn, external_id (for role type)
        """
        self.credentials = credentials
        self.session = self._create_session()
        
    def _create_session(self) -> boto3.Session:
        """Create boto3 session based on credential type"""
        cred_type = self.credentials.get("type")
        
        if cred_type == "access_key":
            return boto3.Session(
                aws_access_key_id=self.credentials["access_key_id"],
                aws_secret_access_key=self.credentials["secret_access_key"],
                region_name=self.credentials.get("region", "us-east-1")
            )
        elif cred_type == "profile":
            return boto3.Session(
                profile_name=self.credentials["profile_name"]
            )
        elif cred_type == "role":
            # Assume role first
            sts_client = boto3.client("sts")
            assumed_role = sts_client.assume_role(
                RoleArn=self.credentials["role_arn"],
                RoleSessionName=self.credentials.get("session_name", "AWSInfraVision"),
                ExternalId=self.credentials.get("external_id")
            )
            creds = assumed_role["Credentials"]
            return boto3.Session(
                aws_access_key_id=creds["AccessKeyId"],
                aws_secret_access_key=creds["SecretAccessKey"],
                aws_session_token=creds["SessionToken"]
            )
        else:
            # Default session (uses environment variables or ~/.aws/config)
            return boto3.Session()
    
    def get_client(self, service: str, region: str = None):
        """Get AWS service client"""
        config = Config(
            retries={"max_attempts": 3, "mode": "standard"},
            connect_timeout=5,
            read_timeout=10
        )
        
        return self.session.client(
            service,
            region_name=region or self.credentials.get("region", "us-east-1"),
            config=config
        )
    
    def get_resource(self, service: str, region: str = None):
        """Get AWS resource object"""
        return self.session.resource(
            service,
            region_name=region or self.credentials.get("region", "us-east-1")
        )
    
    def validate_credentials(self) -> bool:
        """Validate AWS credentials"""
        try:
            sts = self.get_client("sts")
            response = sts.get_caller_identity()
            logger.info(f"Credentials validated for account: {response['Account']}")
            return True
        except Exception as e:
            logger.error(f"Credential validation failed: {str(e)}")
            return False
    
    def get_account_id(self) -> Optional[str]:
        """Get AWS account ID"""
        try:
            sts = self.get_client("sts")
            return sts.get_caller_identity()["Account"]
        except Exception as e:
            logger.error(f"Failed to get account ID: {str(e)}")
            return None


class ResourceDiscoveryEngine:
    """Discovers AWS resources across all services and regions"""
    
    def __init__(self, client_factory: AWSClientFactory):
        self.client_factory = client_factory
        self.discovered_resources = []
        self.scan_progress = {"total": 0, "completed": 0, "errors": []}
    
    def scan_all_regions(self, regions: List[str] = None) -> List[Dict]:
        """
        Scan all enabled regions for resources
        
        Args:
            regions: List of regions to scan (None = all regions)
            
        Returns:
            List of discovered resources
        """
        regions = regions or AWSClientFactory.ALL_REGIONS
        self.discovered_resources = []
        self.scan_progress = {"total": len(regions), "completed": 0, "errors": []}
        
        for region in regions:
            try:
                logger.info(f"Scanning region: {region}")
                region_resources = self._scan_region(region)
                self.discovered_resources.extend(region_resources)
                self.scan_progress["completed"] += 1
            except Exception as e:
                logger.error(f"Error scanning region {region}: {str(e)}")
                self.scan_progress["errors"].append({
                    "region": region,
                    "error": str(e)
                })
                self.scan_progress["completed"] += 1
        
        logger.info(f"Scan complete. Found {len(self.discovered_resources)} resources")
        return self.discovered_resources
    
    def _scan_region(self, region: str) -> List[Dict]:
        """Scan a single region for all supported services"""
        resources = []
        
        # EC2 Instances
        resources.extend(self._discover_ec2(region))
        
        # EBS Volumes
        resources.extend(self._discover_ebs(region))
        
        # S3 Buckets (global, but tag with region if applicable)
        if region == "us-east-1":
            resources.extend(self._discover_s3())
        
        # RDS Instances
        resources.extend(self._discover_rds(region))
        
        # Lambda Functions
        resources.extend(self._discover_lambda(region))
        
        # ECS Services
        resources.extend(self._discover_ecs(region))
        
        # DynamoDB Tables
        resources.extend(self._discover_dynamodb(region))
        
        # SQS Queues
        resources.extend(self._discover_sqs(region))
        
        # SNS Topics
        resources.extend(self._discover_sns(region))
        
        # Security Groups
        resources.extend(self._discover_security_groups(region))
        
        # Load Balancers
        resources.extend(self._discover_load_balancers(region))
        
        # CloudFront Distributions (global)
        if region == "us-east-1":
            resources.extend(self._discover_cloudfront())
        
        return resources
    
    def _discover_ec2(self, region: str) -> List[Dict]:
        """Discover EC2 instances"""
        resources = []
        try:
            ec2 = self.client_factory.get_client("ec2", region)
            response = ec2.describe_instances()
            
            for reservation in response.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    tags = self._extract_tags(instance.get("Tags", []))
                    resources.append({
                        "resource_id": instance["InstanceId"],
                        "arn": f"arn:aws:ec2:{region}:{self.client_factory.get_account_id()}:instance/{instance['InstanceId']}",
                        "service_name": "EC2",
                        "resource_type": "Instance",
                        "region": region,
                        "name": tags.get("Name", instance["InstanceId"]),
                        "status": instance["State"]["Name"],
                        "state": instance["State"]["Name"],
                        "environment": tags.get("Environment", ""),
                        "owner": tags.get("Owner", ""),
                        "created_at_resource": instance.get("LaunchTime"),
                        "tags": tags,
                        "metadata": {
                            "instance_type": instance.get("InstanceType"),
                            "platform": instance.get("Platform", "linux"),
                            "vpc_id": instance.get("VpcId"),
                            "subnet_id": instance.get("SubnetId")
                        }
                    })
        except Exception as e:
            logger.warning(f"EC2 discovery error in {region}: {str(e)}")
        
        return resources
    
    def _discover_ebs(self, region: str) -> List[Dict]:
        """Discover EBS volumes"""
        resources = []
        try:
            ec2 = self.client_factory.get_client("ec2", region)
            response = ec2.describe_volumes()
            
            for volume in response.get("Volumes", []):
                tags = self._extract_tags(volume.get("Tags", []))
                resources.append({
                    "resource_id": volume["VolumeId"],
                    "arn": f"arn:aws:ec2:{region}:{self.client_factory.get_account_id()}:volume/{volume['VolumeId']}",
                    "service_name": "EBS",
                    "resource_type": "Volume",
                    "region": region,
                    "name": tags.get("Name", volume["VolumeId"]),
                    "status": volume["State"],
                    "environment": tags.get("Environment", ""),
                    "owner": tags.get("Owner", ""),
                    "created_at_resource": volume.get("CreateTime"),
                    "tags": tags,
                    "metadata": {
                        "size": volume.get("Size"),
                        "volume_type": volume.get("VolumeType"),
                        "attached_to": [a.get("InstanceId") for a in volume.get("Attachments", [])]
                    }
                })
        except Exception as e:
            logger.warning(f"EBS discovery error in {region}: {str(e)}")
        
        return resources
    
    def _discover_s3(self) -> List[Dict]:
        """Discover S3 buckets"""
        resources = []
        try:
            s3 = self.client_factory.get_client("s3")
            response = s3.list_buckets()
            
            for bucket in response.get("Buckets", []):
                # Get bucket tags
                tags = {}
                try:
                    tag_response = s3.get_bucket_tagging(Bucket=bucket["Name"])
                    tags = self._extract_tags(tag_response.get("TagSet", []))
                except:
                    pass
                
                resources.append({
                    "resource_id": bucket["Name"],
                    "arn": f"arn:aws:s3:::{bucket['Name']}",
                    "service_name": "S3",
                    "resource_type": "Bucket",
                    "region": "global",
                    "name": bucket["Name"],
                    "status": "active",
                    "environment": tags.get("Environment", ""),
                    "owner": tags.get("Owner", ""),
                    "created_at_resource": bucket.get("CreationDate"),
                    "tags": tags,
                    "metadata": {}
                })
        except Exception as e:
            logger.warning(f"S3 discovery error: {str(e)}")
        
        return resources
    
    def _discover_rds(self, region: str) -> List[Dict]:
        """Discover RDS instances"""
        resources = []
        try:
            rds = self.client_factory.get_client("rds", region)
            response = rds.describe_db_instances()
            
            for db in response.get("DBInstances", []):
                tags = {}
                try:
                    arn = db["DBInstanceArn"]
                    tag_response = rds.list_tags_for_resource(ResourceName=arn)
                    tags = {t["Key"]: t["Value"] for t in tag_response.get("TagList", [])}
                except:
                    pass
                
                resources.append({
                    "resource_id": db["DBInstanceIdentifier"],
                    "arn": db["DBInstanceArn"],
                    "service_name": "RDS",
                    "resource_type": "DBInstance",
                    "region": region,
                    "name": db.get("DBName", db["DBInstanceIdentifier"]),
                    "status": db["DBInstanceStatus"],
                    "environment": tags.get("Environment", ""),
                    "owner": tags.get("Owner", ""),
                    "created_at_resource": db.get("InstanceCreateTime"),
                    "tags": tags,
                    "metadata": {
                        "engine": db.get("Engine"),
                        "instance_class": db.get("DBInstanceClass"),
                        "multi_az": db.get("MultiAZ", False)
                    }
                })
        except Exception as e:
            logger.warning(f"RDS discovery error in {region}: {str(e)}")
        
        return resources
    
    def _discover_lambda(self, region: str) -> List[Dict]:
        """Discover Lambda functions"""
        resources = []
        try:
            lambda_client = self.client_factory.get_client("lambda", region)
            response = lambda_client.list_functions()
            
            for func in response.get("Functions", []):
                tags = func.get("Tags", {})
                resources.append({
                    "resource_id": func["FunctionName"],
                    "arn": func["FunctionArn"],
                    "service_name": "Lambda",
                    "resource_type": "Function",
                    "region": region,
                    "name": func["FunctionName"],
                    "status": "active",
                    "environment": tags.get("Environment", ""),
                    "owner": tags.get("Owner", ""),
                    "created_at_resource": None,
                    "tags": tags,
                    "metadata": {
                        "runtime": func.get("Runtime"),
                        "memory_size": func.get("MemorySize"),
                        "timeout": func.get("Timeout")
                    }
                })
        except Exception as e:
            logger.warning(f"Lambda discovery error in {region}: {str(e)}")
        
        return resources
    
    def _discover_dynamodb(self, region: str) -> List[Dict]:
        """Discover DynamoDB tables"""
        resources = []
        try:
            dynamodb = self.client_factory.get_client("dynamodb", region)
            response = dynamodb.list_tables()
            
            for table_name in response.get("TableNames", []):
                table_desc = dynamodb.describe_table(TableName=table_name)
                table = table_desc["Table"]
                
                tags = {}
                try:
                    arn = table["TableArn"]
                    tag_response = dynamodb.list_tags_of_resource(ResourceArn=arn)
                    tags = {t["Key"]: t["Value"] for t in tag_response.get("Tags", [])}
                except:
                    pass
                
                resources.append({
                    "resource_id": table_name,
                    "arn": table["TableArn"],
                    "service_name": "DynamoDB",
                    "resource_type": "Table",
                    "region": region,
                    "name": table_name,
                    "status": table.get("TableStatus", "active"),
                    "environment": tags.get("Environment", ""),
                    "owner": tags.get("Owner", ""),
                    "created_at_resource": None,
                    "tags": tags,
                    "metadata": {
                        "item_count": table.get("ItemCount"),
                        "table_size_bytes": table.get("TableSizeBytes")
                    }
                })
        except Exception as e:
            logger.warning(f"DynamoDB discovery error in {region}: {str(e)}")
        
        return resources
    
    def _discover_sqs(self, region: str) -> List[Dict]:
        """Discover SQS queues"""
        resources = []
        try:
            sqs = self.client_factory.get_client("sqs", region)
            response = sqs.list_queues()
            
            for queue_url in response.get("QueueUrls", []):
                queue_name = queue_url.split("/")[-1]
                attrs = sqs.get_queue_attributes(
                    QueueUrl=queue_url,
                    AttributeNames=["All"]
                )
                
                resources.append({
                    "resource_id": queue_name,
                    "arn": attrs["Attributes"].get("QueueArn", ""),
                    "service_name": "SQS",
                    "resource_type": "Queue",
                    "region": region,
                    "name": queue_name,
                    "status": "active",
                    "environment": "",
                    "owner": "",
                    "created_at_resource": None,
                    "tags": {},
                    "metadata": {
                        "queue_url": queue_url,
                        "message_count": attrs["Attributes"].get("ApproximateNumberOfMessages", 0)
                    }
                })
        except Exception as e:
            logger.warning(f"SQS discovery error in {region}: {str(e)}")
        
        return resources
    
    def _discover_sns(self, region: str) -> List[Dict]:
        """Discover SNS topics"""
        resources = []
        try:
            sns = self.client_factory.get_client("sns", region)
            response = sns.list_topics()
            
            for topic in response.get("Topics", []):
                arn = topic["TopicArn"]
                topic_name = arn.split(":")[-1]
                
                resources.append({
                    "resource_id": topic_name,
                    "arn": arn,
                    "service_name": "SNS",
                    "resource_type": "Topic",
                    "region": region,
                    "name": topic_name,
                    "status": "active",
                    "environment": "",
                    "owner": "",
                    "created_at_resource": None,
                    "tags": {},
                    "metadata": {}
                })
        except Exception as e:
            logger.warning(f"SNS discovery error in {region}: {str(e)}")
        
        return resources
    
    def _discover_security_groups(self, region: str) -> List[Dict]:
        """Discover security groups"""
        resources = []
        try:
            ec2 = self.client_factory.get_client("ec2", region)
            response = ec2.describe_security_groups()
            
            for sg in response.get("SecurityGroups", []):
                tags = self._extract_tags(sg.get("Tags", []))
                resources.append({
                    "resource_id": sg["GroupId"],
                    "arn": f"arn:aws:ec2:{region}:{self.client_factory.get_account_id()}:security-group/{sg['GroupId']}",
                    "service_name": "EC2",
                    "resource_type": "SecurityGroup",
                    "region": region,
                    "name": sg.get("GroupName", sg["GroupId"]),
                    "status": "active",
                    "environment": tags.get("Environment", ""),
                    "owner": tags.get("Owner", ""),
                    "created_at_resource": None,
                    "tags": tags,
                    "metadata": {
                        "vpc_id": sg.get("VpcId"),
                        "ingress_rules": len(sg.get("IpPermissions", [])),
                        "egress_rules": len(sg.get("IpPermissionsEgress", []))
                    }
                })
        except Exception as e:
            logger.warning(f"Security group discovery error in {region}: {str(e)}")
        
        return resources
    
    def _discover_load_balancers(self, region: str) -> List[Dict]:
        """Discover load balancers (ALB/NLB)"""
        resources = []
        try:
            elbv2 = self.client_factory.get_client("elbv2", region)
            response = elbv2.describe_load_balancers()
            
            for lb in response.get("LoadBalancers", []):
                tags_response = elbv2.describe_tags(ResourceArns=[lb["LoadBalancerArn"]])
                tags = {}
                if tags_response.get("TagDescriptions"):
                    tags = {t["Key"]: t["Value"] for t in tags_response["TagDescriptions"][0].get("Tags", [])}
                
                resources.append({
                    "resource_id": lb["LoadBalancerName"],
                    "arn": lb["LoadBalancerArn"],
                    "service_name": "ELB",
                    "resource_type": f"{lb['Type']} LoadBalancer",
                    "region": region,
                    "name": lb.get("LoadBalancerName"),
                    "status": lb.get("State", {}).get("Code", "unknown"),
                    "environment": tags.get("Environment", ""),
                    "owner": tags.get("Owner", ""),
                    "created_at_resource": lb.get("CreatedTime"),
                    "tags": tags,
                    "metadata": {
                        "scheme": lb.get("Scheme"),
                        "vpc_id": lb.get("VpcId"),
                        "type": lb.get("Type")
                    }
                })
        except Exception as e:
            logger.warning(f"Load balancer discovery error in {region}: {str(e)}")
        
        return resources
    
    def _discover_cloudfront(self) -> List[Dict]:
        """Discover CloudFront distributions"""
        resources = []
        try:
            cf = self.client_factory.get_client("cloudfront")
            response = cf.list_distributions()
            
            for dist in response.get("DistributionList", {}).get("Items", []):
                resources.append({
                    "resource_id": dist["Id"],
                    "arn": f"arn:aws:cloudfront::{self.client_factory.get_account_id()}:distribution/{dist['Id']}",
                    "service_name": "CloudFront",
                    "resource_type": "Distribution",
                    "region": "global",
                    "name": dist.get("DomainName", dist["Id"]),
                    "status": dist.get("Status", "unknown"),
                    "environment": "",
                    "owner": "",
                    "created_at_resource": dist.get("LastModifiedTime"),
                    "tags": {},
                    "metadata": {
                        "enabled": dist.get("Enabled", False),
                        "price_class": dist.get("PriceClass")
                    }
                })
        except Exception as e:
            logger.warning(f"CloudFront discovery error: {str(e)}")
        
        return resources
    
    def _discover_ecs(self, region: str) -> List[Dict]:
        """Discover ECS services"""
        resources = []
        try:
            ecs = self.client_factory.get_client("ecs", region)
            clusters = ecs.list_clusters()
            
            for cluster_arn in clusters.get("clusterArns", []):
                cluster_name = cluster_arn.split("/")[-1]
                services = ecs.list_services(cluster=cluster_name)
                
                for service_arn in services.get("serviceArns", []):
                    service_name = service_arn.split("/")[-1]
                    resources.append({
                        "resource_id": service_arn,
                        "arn": service_arn,
                        "service_name": "ECS",
                        "resource_type": "Service",
                        "region": region,
                        "name": service_name,
                        "status": "active",
                        "environment": "",
                        "owner": "",
                        "created_at_resource": None,
                        "tags": {},
                        "metadata": {
                            "cluster": cluster_name
                        }
                    })
        except Exception as e:
            logger.warning(f"ECS discovery error in {region}: {str(e)}")
        
        return resources
    
    @staticmethod
    def _extract_tags(tag_list: List[Dict]) -> Dict[str, str]:
        """Extract tags from AWS tag list format"""
        if not tag_list:
            return {}
        
        tags = {}
        for tag in tag_list:
            if isinstance(tag, dict) and "Key" in tag:
                tags[tag["Key"]] = tag.get("Value", "")
        return tags
    
    def get_scan_progress(self) -> Dict:
        """Get current scan progress"""
        return self.scan_progress
