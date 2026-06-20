# AWS INFRA VISION - API DESIGN
# Version: 1.0.0
# Framework: FastAPI
# Base URL: http://localhost:8000/api/v1

## API ARCHITECTURE

RESTful API with the following structure:
- /api/v1/auth - Authentication endpoints
- /api/v1/accounts - Account management
- /api/v1/resources - Resource inventory
- /api/v1/costs - Cost analytics
- /api/v1/security - Security findings
- /api/v1/terraform - Terraform intelligence
- /api/v1/cloudformation - CloudFormation stacks
- /api/v1/recommendations - Optimization recommendations
- /api/v1/timeline - Infrastructure timeline
- /api/v1/actions - Resource actions
- /api/v1/finops - FinOps scoring
- /api/v1/ai - AI assistant queries

All responses follow standard format:
```json
{
    "success": boolean,
    "data": any,
    "error": string | null,
    "metadata": {
        "timestamp": string,
        "request_id": string,
        "account_id": string
    }
}
```

---

## ENDPOINT SUMMARY

### Authentication
- POST /auth/setup-wizard - Configure AWS credentials
- POST /auth/validate - Validate credentials
- GET /auth/accounts - List configured accounts
- DELETE /auth/accounts/{account_id} - Remove account

### Accounts
- GET /accounts - List accounts
- GET /accounts/{account_id} - Account details
- PUT /accounts/{account_id} - Update settings
- GET /accounts/{account_id}/status - Connection status

### Resources
- GET /resources - List resources (paginated, filterable)
- GET /resources/{resource_id} - Resource details
- GET /resources/stats/summary - Resource statistics
- POST /resources/scan - Trigger discovery
- GET /resources/export - Export to CSV/JSON

### Costs
- GET /costs/summary - Cost summary
- GET /costs/by-service - Costs by service
- GET /costs/by-region - Costs by region
- GET /costs/by-tag - Costs by tag
- GET /costs/forecast - Cost forecast
- GET /costs/anomalies - Cost anomalies
- POST /costs/analyze - Trigger analysis

### Security
- GET /security/findings - List findings
- GET /security/findings/{id} - Finding details
- PUT /security/findings/{id}/status - Update status
- POST /security/scan - Trigger scan
- GET /security/score - Security score

### Terraform
- GET /terraform/resources - TF resources
- GET /terraform/drift - Drift detection
- POST /terraform/sync - Sync state
- GET /terraform/workspaces - List workspaces

### CloudFormation
- GET /cloudformation/stacks - List stacks
- GET /cloudformation/stacks/{id} - Stack details
- GET /cloudformation/drift - Stack drift
- POST /cloudformation/refresh - Refresh info

### Recommendations
- GET /recommendations - Optimization recommendations
- GET /recommendations/{id} - Recommendation details
- PUT /recommendations/{id}/status - Update status
- GET /recommendations/savings-summary - Savings summary

### Timeline
- GET /timeline/events - Infrastructure events
- GET /timeline/resource/{id} - Resource timeline
- POST /timeline/refresh - Refresh events

### FinOps
- GET /finops/score - Current score
- GET /finops/score/history - Score history
- POST /finops/calculate - Recalculate score

### AI Assistant
- POST /ai/query - Ask about infrastructure
- POST /ai/analyze-cost-increase - Analyze cost increase
- POST /ai/suggest-optimizations - AI suggestions

### System
- GET /health - Health check
- GET /system/info - System information

---

## ERROR RESPONSES

```json
// 400 Bad Request
{"success": false, "error": "Validation error message", "details": [...]}

// 401 Unauthorized
{"success": false, "error": "Invalid or expired credentials"}

// 404 Not Found
{"success": false, "error": "Resource not found"}

// 500 Internal Server Error
{"success": false, "error": "Internal server error", "request_id": string}
```

---

## RATE LIMITING

- 100 requests per minute per endpoint
- 10 concurrent scans per account
- Exponential backoff for AWS API calls
- Configurable via settings

---

## WEBSOCKET EVENTS

For real-time updates:
- ws://localhost:8000/ws/scan/{scan_id} - Scan progress
- ws://localhost:8000/ws/actions/{action_id} - Action status

Events format:
```json
{"type": "progress" | "complete" | "error", "data": object, "timestamp": string}
```
