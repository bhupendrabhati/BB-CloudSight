# BB-CloudSight ☁️

> AWS Infrastructure Discovery, Security Analysis & FinOps Intelligence Platform

BB-CloudSight is a cloud visibility and optimization platform that helps engineers discover AWS resources, identify security risks, analyze cloud usage, and gain infrastructure insights through a unified dashboard and API-driven architecture.

---

## 🚀 Overview

Managing AWS environments becomes increasingly difficult as cloud infrastructure grows. Organizations often struggle with:

* Tracking resources across multiple AWS regions
* Identifying security risks and misconfigurations
* Understanding cloud spending patterns
* Maintaining visibility across EC2, S3, EBS, IAM, and other services
* Generating actionable infrastructure insights

BB-CloudSight solves these challenges by providing:

✅ AWS Resource Discovery

✅ Security Posture Analysis

✅ FinOps & Cost Visibility

✅ AI-Powered Infrastructure Insights

✅ Multi-Region AWS Inventory

✅ Infrastructure Intelligence Dashboard

---

## 🏗 Architecture

```text
┌─────────────────────────────┐
│        React Frontend       │
└──────────────┬──────────────┘
               │ REST API
               ▼
┌─────────────────────────────┐
│       FastAPI Backend       │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│        AWS Services         │
│ EC2 | S3 | EBS | IAM | CE   │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       SQLite Database       │
└─────────────────────────────┘
```

---

## 🛠 Tech Stack

### Backend

* Python 3.11+
* FastAPI
* SQLAlchemy
* SQLite
* Boto3

### Frontend

* React
* TypeScript
* Vite

### Desktop

* Electron

### AWS Services

* EC2
* S3
* EBS
* IAM
* Cost Explorer
* CloudTrail

---

## ✨ Features

### 🔍 Resource Discovery

* Multi-region AWS scanning
* EC2 inventory
* EBS inventory
* Security Group inventory
* S3 bucket discovery
* Resource metadata collection

### 🔒 Security Analysis

* Open Security Group detection
* Unencrypted EBS detection
* Security findings dashboard
* Severity-based classification
* Remediation recommendations

### 💰 FinOps & Cost Intelligence

* FinOps scoring engine
* Resource utilization analysis
* Cost visibility
* Savings recommendations
* Cost anomaly detection (roadmap)

### 🤖 AI Assistant

Ask questions such as:

```text
How much am I spending on EC2?

What security issues exist in my account?

Which resources can be optimized?

Show me underutilized infrastructure.
```

---

## 📋 Prerequisites

```bash
Python 3.11+
Node.js 20+
npm 9+
Git
AWS Account
```

Verify installation:

```bash
python3 --version
node --version
npm --version
git --version
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/bb-cloudsight.git

cd bb-cloudsight
```

### Create Virtual Environment

```bash
python3 -m venv .venv

source .venv/bin/activate
```

### Install Backend Dependencies

```bash
pip install -r backend/requirements.txt
```

### Install Frontend Dependencies

```bash
cd frontend

npm install

cd ..
```

### Install Electron Dependencies

```bash
npm install
```

---

## 🚀 Running the Application

### Start Backend

```bash
uvicorn backend.app.main:app --reload --port 8000
```

Health Check:

```bash
curl http://localhost:8000/health
```

Expected Output:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected"
}
```

### Start Frontend

```bash
cd frontend

npm run dev
```

### Start Electron

```bash
npm run dev:electron
```

---

## 🔑 Connect AWS Account

Supported Authentication Methods:

* AWS Access Keys
* AWS Profiles
* IAM Roles

Example:

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/setup-wizard \
-H "Content-Type: application/json" \
-d '{
  "credential_type": "profile",
  "profile_name": "default",
  "region": "us-east-1"
}'
```

Response:

```json
{
  "success": true,
  "data": {
    "account_id": "123456789101",
    "message": "AWS account configured successfully"
  }
}
```

---

## 🔍 Resource Discovery Example

Run a scan:

```bash
curl -s -X POST http://localhost:8000/api/v1/resources/scan \
-H "Content-Type: application/json" \
-d '{
  "account_id": "123456789101",
  "scan_type": "full",
  "regions": ["us-east-1","ap-south-1"]
}'
```

Output:

```json
{
  "success": true,
  "data": {
    "regions_scanned": 2,
    "resources_found": 16,
    "resources_stored": 16
  }
}
```

---

## 📊 Sample Discovery Results

### Resources Found

| Service | Count |
| ------- | ----- |
| EC2     | 10    |
| EBS     | 4     |
| S3      | 2     |
| Total   | 16    |

### Regional Distribution

| Region     | Resources |
| ---------- | --------- |
| ap-south-1 | 7         |
| us-east-1  | 7         |
| global     | 2         |

---

## 🔒 Security Findings Example

Security Scan:

```bash
curl -s -X POST \
http://localhost:8000/api/v1/security/scan
```

Results:

```json
{
  "findings_found": 8,
  "severity_breakdown": {
    "critical": 2,
    "high": 2,
    "medium": 4
  }
}
```

### Example Critical Finding

```text
Security Group: mumbai-sg

Port: 22

CIDR: 0.0.0.0/0
```

Risk:

```text
Anyone on the internet can attempt SSH access.
```

Recommendation:

```text
Restrict SSH access to specific IP ranges.
```

---

## 💰 FinOps Engine

Current Capabilities:

* FinOps Score Calculation
* Infrastructure Efficiency Analysis
* Savings Opportunity Detection
* Resource Optimization Recommendations

Planned Enhancements:

* Reserved Instance Analysis
* Savings Plans Recommendations
* Cost Forecasting
* Cost Anomaly Detection
* Rightsizing Recommendations

---

## 📡 API Endpoints

### Authentication

```text
POST /api/v1/auth/setup-wizard
POST /api/v1/auth/validate
GET  /api/v1/auth/accounts
```

### Resources

```text
POST /api/v1/resources/scan
GET  /api/v1/resources
GET  /api/v1/resources/stats/summary
```

### Security

```text
POST /api/v1/security/scan
GET  /api/v1/security/findings
GET  /api/v1/security/score
```

### FinOps

```text
GET  /api/v1/finops/score
POST /api/v1/finops/calculate
GET  /api/v1/finops/metrics
```

### AI

```text
POST /api/v1/ai/query
POST /api/v1/ai/suggest-optimizations
```

---

## 🛣 Roadmap

### Version 2.0

* [ ] AWS Organizations Support
* [ ] Multi-Account Visibility
* [ ] Cost Forecasting
* [ ] Cost Anomaly Detection
* [ ] Terraform State Analysis
* [ ] CloudFormation Drift Detection
* [ ] AI Remediation Suggestions
* [ ] Kubernetes Discovery
* [ ] Grafana Integration

---

## 🤝 Contributing

Contributions, feature requests, and suggestions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a Pull Request

---

## 📜 License

MIT License

---

## 👨‍💻 Author

**Bhupendra Bhati**

Cloud & DevOps Engineer

🏅 AWS Community Builder 2026

🏅 AWS New Voices 2026

---

⭐ If you find this project useful, consider giving it a star on GitHub.
