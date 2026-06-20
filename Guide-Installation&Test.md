# Test AWS Integration — Manual Testing Guide

<div align="center">

**Step-by-step instructions for testing BB-CloudSight with real AWS credentials**

</div>

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Step 1: Start the Backend](#2-step-1-start-the-backend)
3. [Step 2: Test the Health Endpoint](#3-step-2-test-the-health-endpoint)
4. [Step 3: Configure AWS Credentials](#4-step-3-configure-aws-credentials)
5. [Step 4: Validate Credentials](#5-step-4-validate-credentials)
6. [Step 5: Run Resource Discovery](#6-step-5-run-resource-discovery)
7. [Step 6: Query Resources](#7-step-6-query-resources)
8. [Step 7: Cost Analytics](#8-step-7-cost-analytics)
9. [Step 8: Security Scanning](#9-step-8-security-scanning)
10. [Step 9: FinOps Score](#10-step-9-finops-score)
11. [Step 10: AI Assistant](#11-step-10-ai-assistant)
12. [Complete Test Script](#12-complete-test-script)
13. [Troubleshooting](#13-troubleshooting)
14. [Cleaning Up](#14-cleaning-up)

---

## 1. Prerequisites

Before you begin, ensure you have:

- ✅ **AWS account** with appropriate permissions
- ✅ **AWS Access Key ID** and **Secret Access Key** (or AWS Profile)
- ✅ **IAM permissions** (minimum read-only for testing):
  ```
  EC2:DescribeInstances, DescribeVolumes, DescribeSecurityGroups
  S3:ListAllMyBuckets, GetBucketLocation
  RDS:DescribeDBInstances
  Lambda:ListFunctions
  DynamoDB:ListTables, DescribeTable
  CostExplorer:GetCostAndUsage, GetCostForecast
  CloudTrail:LookupEvents
  IAM:ListUsers, ListAccessKeys, GetAccessKeyLastUsed
  STS:GetCallerIdentity
  ```
- ✅ **IAM policy permission** for Cost Explorer (requires `ce:GetCostAndUsage`, `ce:GetCostForecast`)
- ✅ **Backend running** (see [GUIDE.md](./GUIDE.md) for setup)

---

## 2. Step 1: Start the Backend

```bash
cd aws-infra-vision
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate       # Windows

uvicorn backend.app.main:app --reload --port 8000
```

✅ **Verify** — Open a new terminal and run:
```bash
curl http://localhost:8000/health
```
Expected response:
```json
{"status":"healthy","version":"1.0.0","timestamp":"...","database":"connected"}
```

---

## 3. Step 2: Test the Health Endpoint

```bash
# Quick health check
curl -s http://localhost:8000/health | python3 -m json.tool

# API root
curl -s http://localhost:8000/ | python3 -m json.tool

# Swagger docs (open in browser)
open http://localhost:8000/docs      # macOS
# xdg-open http://localhost:8000/docs  # Linux
# start http://localhost:8000/docs     # Windows
```

---

## 4. Step 3: Configure AWS Credentials

Choose one of the following methods:

### Option A: Access Keys (Recommended)

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/setup-wizard \
  -H "Content-Type: application/json" \
  -d '{
    "credential_type": "access_key",
    "access_key_id": "YOUR_AWS_ACCESS_KEY_ID",
    "secret_access_key": "YOUR_AWS_SECRET_ACCESS_KEY",
    "region": "us-east-1"
  }' | python3 -m json.tool
```

✅ **Expected success response (201):**
```json
{
  "success": true,
  "data": {
    "account_id": "123456789012",
    "message": "AWS account configured successfully",
    "next_steps": [
      "Run a resource scan to discover your infrastructure",
      "Configure cost analytics",
      "Set up security scanning"
    ]
  }
}
```

❌ **Expected error responses:**
- `400` — Missing required fields
- `401` — Invalid AWS credentials (`Invalid AWS credentials. Please check your credentials and try again.`)

> **Note:** Your credentials are stored securely in your OS keychain (macOS Keychain, Windows Credential Vault, or Linux Secret Service). They are never stored in plaintext.

### Option B: AWS Profile

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/setup-wizard \
  -H "Content-Type: application/json" \
  -d '{
    "credential_type": "profile",
    "profile_name": "default",
    "region": "us-east-1"
  }' | python3 -m json.tool
```

### Option C: IAM Role

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/setup-wizard \
  -H "Content-Type: application/json" \
  -d '{
    "credential_type": "role",
    "role_arn": "arn:aws:iam::123456789012:role/YourRoleName",
    "session_name": "AWSInfraVision",
    "region": "us-east-1"
  }' | python3 -m json.tool
```

---

## 5. Step 4: Validate Credentials

Verify stored credentials are still valid:

```bash
# Replace ACCOUNT_ID with the account ID from the setup response
curl -s -X POST http://localhost:8000/api/v1/auth/validate \
  -H "Content-Type: application/json" \
  -d '{"account_id": "YOUR_ACCOUNT_ID"}' | python3 -m json.tool
```

Expected response:
```json
{
  "success": true,
  "data": {
    "valid": true,
    "account_id": "YOUR_ACCOUNT_ID",
    "message": "Credentials are valid"
  }
}
```

Check configured accounts:
```bash
curl -s http://localhost:8000/api/v1/auth/accounts | python3 -m json.tool
```

---

## 6. Step 5: Run Resource Discovery

Trigger a resource scan to discover your AWS infrastructure:

```bash
# Trigger full scan
curl -s -X POST http://localhost:8000/api/v1/resources/scan \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "scan_type": "full"
  }' | python3 -m json.tool
```

✅ **Expected response:**
```json
{
  "success": true,
  "data": {
    "scan_id": "scan-...",
    "account_id": "YOUR_ACCOUNT_ID",
    "scan_type": "full",
    "regions_scanned": 15,
    "resources_found": 42,
    "resources_stored": 42,
    ...
    "message": "Scan completed. Found 42 resources."
  }
}
```

> **Performance note:** Scanning all 15 regions typically takes 30-60 seconds. For a faster test, specify only 1-2 regions.

**Scan specific regions (faster):**
```bash
curl -s -X POST http://localhost:8000/api/v1/resources/scan \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "scan_type": "full",
    "regions": ["us-east-1", "us-west-2"]
  }' | python3 -m json.tool
```

---

## 7. Step 6: Query Resources

### List all resources:
```bash
curl -s 'http://localhost:8000/api/v1/resources/?account_id=YOUR_ACCOUNT_ID' | python3 -m json.tool
```

### Filter by service:
```bash
curl -s 'http://localhost:8000/api/v1/resources/?account_id=YOUR_ACCOUNT_ID&service=EC2' | python3 -m json.tool
```

### Filter by region:
```bash
curl -s 'http://localhost:8000/api/v1/resources/?account_id=YOUR_ACCOUNT_ID&region=us-east-1' | python3 -m json.tool
```

### Get resource statistics:
```bash
curl -s 'http://localhost:8000/api/v1/resources/stats/summary?account_id=YOUR_ACCOUNT_ID' | python3 -m json.tool
```

### Search resources:
```bash
curl -s 'http://localhost:8000/api/v1/resources/?account_id=YOUR_ACCOUNT_ID&search=web' | python3 -m json.tool
```

### Export to CSV format:
```bash
curl -s 'http://localhost:8000/api/v1/resources/export?account_id=YOUR_ACCOUNT_ID&format=csv' | python3 -m json.tool
```

---

## 8. Step 7: Cost Analytics

> **Note:** Cost Explorer data is only available in `us-east-1`. You need the `ce:GetCostAndUsage` permission.

### Cost summary:
```bash
curl -s 'http://localhost:8000/api/v1/costs/summary?account_id=YOUR_ACCOUNT_ID&period=monthly' | python3 -m json.tool
```

### Cost by service:
```bash
curl -s 'http://localhost:8000/api/v1/costs/by-service?account_id=YOUR_ACCOUNT_ID' | python3 -m json.tool
```

### Cost by region:
```bash
curl -s 'http://localhost:8000/api/v1/costs/by-region?account_id=YOUR_ACCOUNT_ID' | python3 -m json.tool
```

### Cost forecast (requires `ce:GetCostForecast`):
```bash
curl -s 'http://localhost:8000/api/v1/costs/forecast?account_id=YOUR_ACCOUNT_ID&months=3' | python3 -m json.tool
```

### Cost anomalies:
```bash
curl -s 'http://localhost:8000/api/v1/costs/anomalies?account_id=YOUR_ACCOUNT_ID' | python3 -m json.tool
```

### Trigger comprehensive cost analysis:
```bash
curl -s -X POST http://localhost:8000/api/v1/costs/analyze \
  -H "Content-Type: application/json" \
  -d '{"account_id": "YOUR_ACCOUNT_ID"}' | python3 -m json.tool
```

---

## 9. Step 8: Security Scanning

> **Note:** The security scanner checks for common AWS misconfigurations. It requires read-only access to multiple services.

### Run security scan:
```bash
curl -s -X POST http://localhost:8000/api/v1/security/scan \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "regions": ["us-east-1", "us-west-2"]
  }' | python3 -m json.tool
```

✅ **Expected response:**
```json
{
  "success": true,
  "data": {
    "scan_id": "sec-scan-...",
    "findings_found": 3,
    "severity_breakdown": {
      "critical": 1,
      "high": 1,
      "medium": 1,
      "low": 0
    },
    "message": "Security scan complete. Found 3 issues."
  }
}
```

### List security findings:
```bash
curl -s 'http://localhost:8000/api/v1/security/findings?account_id=YOUR_ACCOUNT_ID' | python3 -m json.tool
```

### Filter by severity:
```bash
curl -s 'http://localhost:8000/api/v1/security/findings?account_id=YOUR_ACCOUNT_ID&severity=critical' | python3 -m json.tool
```

### Get finding details:
```bash
# Replace FINDING_ID with an actual finding ID
curl -s http://localhost:8000/api/v1/security/findings/FINDING_ID | python3 -m json.tool
```

### Update finding status:
```bash
curl -s -X PUT "http://localhost:8000/api/v1/security/findings/FINDING_ID/status?status=acknowledged" | python3 -m json.tool
```

### Get security score:
```bash
curl -s 'http://localhost:8000/api/v1/security/score?account_id=YOUR_ACCOUNT_ID' | python3 -m json.tool
```

---

## 10. Step 9: FinOps Score

```bash
# Get current FinOps score
curl -s 'http://localhost:8000/api/v1/finops/score?account_id=YOUR_ACCOUNT_ID' | python3 -m json.tool
```

✅ **Expected response (excerpt):**
```json
{
  "success": true,
  "data": {
    "account_id": "YOUR_ACCOUNT_ID",
    "overall_score": 76,
    "grade": "C",
    "factors": { ... },
    "potential_monthly_savings": 450.0
  }
}
```

### Get FinOps metrics:
```bash
curl -s 'http://localhost:8000/api/v1/finops/metrics?account_id=YOUR_ACCOUNT_ID' | python3 -m json.tool
```

### Recalculate score:
```bash
curl -s -X POST http://localhost:8000/api/v1/finops/calculate \
  -H "Content-Type: application/json" \
  -d '{"account_id": "YOUR_ACCOUNT_ID"}' | python3 -m json.tool
```

---

## 11. Step 10: AI Assistant

```bash
# Ask a question about your infrastructure
curl -s -X POST http://localhost:8000/api/v1/ai/query \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "query": "How much am I spending on EC2?"
  }' | python3 -m json.tool
```

### Analyze cost increase:
```bash
curl -s -X POST http://localhost:8000/api/v1/ai/analyze-cost-increase \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "period_days": 30
  }' | python3 -m json.tool
```

### Get optimization suggestions:
```bash
curl -s -X POST http://localhost:8000/api/v1/ai/suggest-optimizations \
  -H "Content-Type: application/json" \
  -d '{"account_id": "YOUR_ACCOUNT_ID"}' | python3 -m json.tool
```

---

## 12. Complete Test Script

Save this script as `test-aws.sh` and run it to test everything at once:

```bash
#!/bin/bash
# BB-CloudSight - Complete Manual Test Script
# Usage: bash test-aws.sh YOUR_ACCOUNT_ID

ACCOUNT_ID="${1:-123456789012}"
BASE_URL="http://localhost:8000/api/v1"
PASS=0
FAIL=0

check() {
  local desc="$1"
  local method="$2"
  local url="$3"
  local data="$4"
  local expected="$5"
  
  if [ "$method" = "GET" ]; then
    status=$(curl -s -o /dev/null -w '%{http_code}' "$url")
  else
    status=$(curl -s -o /dev/null -w '%{http_code}' -X "$method" -H "Content-Type: application/json" -d "$data" "$url")
  fi
  
  if [ "$status" = "$expected" ]; then
    echo "✅ $desc (HTTP $status)"
    ((PASS++))
  else
    echo "❌ $desc (expected $expected, got $status)"
    ((FAIL++))
  fi
}

echo ""
echo "=== BB-CloudSight - Manual Test Suite ==="
echo "Account: $ACCOUNT_ID"
echo ""

# Health
check "Health Check" "GET" "http://localhost:8000/health" "" "200"
check "Root API" "GET" "http://localhost:8000/" "" "200"

# Auth
check "List Accounts (empty)" "GET" "$BASE_URL/auth/accounts" "" "200"
check "Delete unknown account" "DELETE" "$BASE_URL/auth/accounts/999999999999" "" "404"

# Resources (without credentials)
check "List Resources (no data)" "GET" "$BASE_URL/resources/?account_id=$ACCOUNT_ID" "" "200"
check "Resource Stats" "GET" "$BASE_URL/resources/stats/summary?account_id=$ACCOUNT_ID" "" "200"
check "Resource Detail (not found)" "GET" "$BASE_URL/resources/i-123?account_id=$ACCOUNT_ID" "" "404"
check "Export CSV" "GET" "$BASE_URL/resources/export?account_id=$ACCOUNT_ID&format=csv" "" "200"

# Security (without scan)
check "Security Findings (empty)" "GET" "$BASE_URL/security/findings?account_id=$ACCOUNT_ID" "" "200"
check "Security Score" "GET" "$BASE_URL/security/score?account_id=$ACCOUNT_ID" "" "200"
check "Finding Detail (not found)" "GET" "$BASE_URL/security/findings/999" "" "404"

# Stub endpoints (no AWS needed)
check "Terraform Resources" "GET" "$BASE_URL/terraform/resources?account_id=$ACCOUNT_ID" "" "200"
check "Terraform Drift" "GET" "$BASE_URL/terraform/drift?account_id=$ACCOUNT_ID" "" "200"
check "Terraform Sync" "POST" "$BASE_URL/terraform/sync" '{"account_id":"'$ACCOUNT_ID'"}' "200"
check "Terraform Workspaces" "GET" "$BASE_URL/terraform/workspaces?account_id=$ACCOUNT_ID" "" "200"
check "CFN Stacks" "GET" "$BASE_URL/cloudformation/stacks?account_id=$ACCOUNT_ID" "" "200"
check "CFN Drift" "GET" "$BASE_URL/cloudformation/drift?account_id=$ACCOUNT_ID" "" "200"
check "CFN Refresh" "POST" "$BASE_URL/cloudformation/refresh" '{"account_id":"'$ACCOUNT_ID'"}' "200"
check "Recommendations" "GET" "$BASE_URL/recommendations/?account_id=$ACCOUNT_ID" "" "200"
check "Savings Summary" "GET" "$BASE_URL/recommendations/savings-summary?account_id=$ACCOUNT_ID" "" "200"
check "Timeline Events" "GET" "$BASE_URL/timeline/events?account_id=$ACCOUNT_ID" "" "200"
check "Timeline Resource" "GET" "$BASE_URL/timeline/resource/i-123?account_id=$ACCOUNT_ID" "" "200"
check "Timeline Refresh" "POST" "$BASE_URL/timeline/refresh" '{"account_id":"'$ACCOUNT_ID'"}' "200"
check "FinOps Score" "GET" "$BASE_URL/finops/score?account_id=$ACCOUNT_ID" "" "200"
check "FinOps Calculate" "POST" "$BASE_URL/finops/calculate" '{"account_id":"'$ACCOUNT_ID'"}' "200"
check "FinOps Metrics" "GET" "$BASE_URL/finops/metrics?account_id=$ACCOUNT_ID" "" "200"
check "AI Query" "POST" "$BASE_URL/ai/query" '{"account_id":"'$ACCOUNT_ID'","query":"test"}' "200"
check "AI Suggest" "POST" "$BASE_URL/ai/suggest-optimizations" '{"account_id":"'$ACCOUNT_ID'"}' "200"

# Actions (confirmation required)
check "EC2 Stop (no confirm)" "POST" "$BASE_URL/actions/ec2/stop" '{"account_id":"'$ACCOUNT_ID'","instance_id":"i-123","confirmation":false}' "400"
check "EC2 Start (no confirm)" "POST" "$BASE_URL/actions/ec2/start" '{"account_id":"'$ACCOUNT_ID'","instance_id":"i-123","confirmation":false}' "400"
check "EBS Delete (no confirm)" "POST" "$BASE_URL/actions/ebs/delete" '{"account_id":"'$ACCOUNT_ID'","volume_id":"vol-123","confirmation":false}' "400"
check "Action History" "GET" "$BASE_URL/actions/history?account_id=$ACCOUNT_ID" "" "200"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
if [ $FAIL -eq 0 ]; then
  echo "🎉 All API endpoints are working correctly!"
else
  echo "⚠️  $FAIL test(s) failed. Check the output above for details."
fi
```

**Usage:**
```bash
chmod +x test-aws.sh

# Test without real credentials (stub tests only)
./test-aws.sh 123456789012

# Test with your real AWS account
./test-aws.sh YOUR_ACTUAL_ACCOUNT_ID
```

---

## 13. Troubleshooting

### AWS API Errors

| Error | Likely Cause | Solution |
|-------|-------------|----------|
| `401 Invalid credentials` | Wrong access key/secret | Check AWS credentials in IAM console |
| `403 Access Denied` | Missing IAM permissions | Add required permissions to IAM policy |
| `500 Cost Explorer error` | Cost Explorer not enabled | Enable Cost Explorer in AWS Billing console |
| `500 Region not enabled` | Region not opted-in | Enable region in AWS Account settings |
| `404 Account not found` | Account not configured | Run setup-wizard first |
| `Operation timed out` | Network/firewall issue | Check internet connection and AWS API access |

### Cost Explorer Not Available

If `/api/v1/costs/summary` returns an error:
1. Log into the [AWS Billing Console](https://console.aws.amazon.com/billing)
2. Go to **Cost Explorer** → **Enable Cost Explorer**
3. Wait 24 hours for data to populate

### IAM Permissions Check

If you're getting access denied errors, test your credentials directly:
```bash
# Test basic STS access
aws sts get-caller-identity

# Test EC2 access
aws ec2 describe-instances --region us-east-1 --max-items 1

# Test Cost Explorer
aws ce get-cost-and-usage \
  --time-period Start=2026-05-01,End=2026-06-01 \
  --granularity MONTHLY \
  --metrics UnblendedCost
```

### Still Having Issues?

1. Check the backend logs: `cat aws-infra-vision/aws-infra-vision.log`
2. Run with debug mode: set `DEBUG=true` in `.env` and restart
3. Review the [GUIDE.md](./GUIDE.md) for setup instructions
4. Check the [docs/](./docs/) folder for architecture details

---

## 14. Cleaning Up

### Remove a configured account:

```bash
curl -s -X DELETE "http://localhost:8000/api/v1/auth/accounts/YOUR_ACCOUNT_ID" -w '%{http_code}'
# Should return 204 No Content
```

### Reset the database completely:

```bash
cd aws-infra-vision
source .venv/bin/activate
rm -f backend/data/aws_infra_vision.db
# Restart the backend — it will recreate an empty database
```

### Stop the backend:

```bash
# Find and kill the uvicorn process
lsof -ti:8000 | xargs kill -9
```

---

<div align="center">

**🎉 You've completed the BB-CloudSight testing guide!**

The app is ready for real-world use. Explore the dashboard, run scans, and optimize your AWS infrastructure.

</div>
