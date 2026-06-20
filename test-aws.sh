#!/bin/bash
# BB-CloudSight - Complete Manual Test Script
# Usage: bash test-aws.sh YOUR_ACCOUNT_ID

ACCOUNT_ID="${1:-123456789012}"  # Default to a placeholder if not provided
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