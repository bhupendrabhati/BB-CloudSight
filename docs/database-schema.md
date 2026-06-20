# AWS INFRA VISION - DATABASE SCHEMA
# Version: 1.0.0
# Database: SQLite 3

## SCHEMA OVERVIEW

**Tables:**
1. accounts - AWS account configurations
2. credentials - Secure credential storage references
3. resources - Discovered AWS resources
4. resource_tags - Resource tags (normalized)
5. costs - Cost data from Cost Explorer
6. cost_anomalies - Detected anomalies
7. security_findings - Security issues
8. terraform_state - Terraform managed resources
9. cloudformation_stacks - CFN stack information
10. scan_history - Scan execution logs
11. finops_scores - FinOps scoring history
12. recommendations - Optimization recommendations
13. timeline_events - CloudTrail events
14. user_actions - Audit log

---

## TABLE DEFINITIONS

### accounts
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-incrementing ID |
| account_id | VARCHAR(12) UNIQUE | AWS account ID |
| account_name | VARCHAR(255) | Account name |
| alias | VARCHAR(255) | Friendly alias |
| is_active | BOOLEAN | Whether account is active |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |
| last_scan_at | TIMESTAMP | Last scan timestamp |
| regions_enabled | TEXT | JSON array of enabled regions |
| metadata | TEXT | JSON additional info |

### credentials
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-incrementing ID |
| account_id | VARCHAR(12) FK | Reference to accounts |
| credential_type | VARCHAR(50) | access_key, profile, sso, role |
| key_reference | VARCHAR(255) | OS keychain reference |
| role_arn | VARCHAR(255) | IAM role ARN |
| external_id | VARCHAR(255) | External ID for role |
| session_name | VARCHAR(255) | Session name |
| is_active | BOOLEAN | Whether credential is active |
| expires_at | TIMESTAMP | Expiration timestamp |

### resources
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-incrementing ID |
| resource_id | VARCHAR(255) | AWS resource ID (unique per account) |
| arn | VARCHAR(1024) UNIQUE | AWS Resource ARN |
| account_id | VARCHAR(12) FK | AWS account ID |
| service_name | VARCHAR(100) | AWS service name |
| resource_type | VARCHAR(100) | Resource type |
| region | VARCHAR(50) | AWS region |
| name | VARCHAR(500) | Resource name |
| status | VARCHAR(50) | Resource status |
| state | VARCHAR(50) | Resource state |
| environment | VARCHAR(50) | Extracted from tags |
| owner | VARCHAR(255) | Extracted from tags |
| is_terraform_managed | BOOLEAN | TF managed flag |
| is_cloudformation_managed | BOOLEAN | CFN managed flag |
| configuration | TEXT | JSON snapshot |
| metadata | TEXT | JSON additional attributes |

### resource_tags
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-incrementing ID |
| resource_id | VARCHAR(255) | Resource ID |
| tag_key | VARCHAR(255) | Tag key |
| tag_value | TEXT | Tag value |

### costs
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-incrementing ID |
| account_id | VARCHAR(12) FK | Account ID |
| date | DATE | Cost date |
| service_name | VARCHAR(100) | AWS service |
| unblended_cost | DECIMAL(12,4) | Cost amount |
| amortized_cost | DECIMAL(12,4) | Amortized cost |
| currency | VARCHAR(10) | Currency (default USD) |

### security_findings
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-incrementing ID |
| account_id | VARCHAR(12) FK | Account ID |
| finding_type | VARCHAR(100) | Type of finding |
| severity | VARCHAR(20) | low/medium/high/critical |
| title | VARCHAR(500) | Finding title |
| description | TEXT | Detailed description |
| remediation | TEXT | Fix instructions |
| status | VARCHAR(20) | open/acknowledged/resolved |
| detected_at | TIMESTAMP | Detection timestamp |

---

## RELATIONSHIPS

```
accounts (1) ────< (M) resources
accounts (1) ────< (M) costs
accounts (1) ────< (M) security_findings
accounts (1) ────< (M) scan_history
accounts (1) ────< (M) finops_scores
accounts (1) ────< (M) recommendations
accounts (1) ────< (M) timeline_events

resources (1) ────< (M) resource_tags
resources (1) ────< (M) security_findings
resources (1) ────< (M) recommendations
```

---

## MIGRATION STRATEGY

Use Alembic for database migrations:
- Initial migration creates all tables
- Subsequent migrations handle schema changes
- Downgrade support for rollbacks
- Data integrity checks
