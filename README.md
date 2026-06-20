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
Working on it and after that you can ask questions such as:

```text
How much am I spending on EC2?

What security issues exist in my account?

Which resources can be optimized?

Show me underutilized infrastructure.
```

---

## Quick Links

- 📋 [Prerequisites](Guide-Prerequisite.md)
- ⚙️ [Installation Guide](Guide-Installation&Test.md)

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
