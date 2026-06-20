# BB-CloudSight — Complete Setup Guide

<div align="center">

**Step-by-step instructions to install and run BB-CloudSight locally on macOS, Linux, and Windows**

</div>

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Quick Start (5 minutes)](#2-quick-start-5-minutes)
3. [Detailed Installation by Platform](#3-detailed-installation-by-platform)
   - [macOS](#31-macos)
   - [Linux (Ubuntu/Debian)](#32-linux-ubuntudebian)
   - [Windows](#33-windows)
4. [Running the Application](#4-running-the-application)
   - [Start the Backend](#41-start-the-backend)
   - [Start the Frontend](#42-start-the-frontend)
   - [Start the Electron App](#43-start-the-electron-app)
   - [Development Mode (All at once)](#44-development-mode-all-at-once)
5. [Configuration](#5-configuration)
   - [Environment Variables](#51-environment-variables)
   - [AWS Credentials](#52-aws-credentials)
6. [Verifying the Setup](#6-verifying-the-setup)
7. [Project Structure Overview](#7-project-structure-overview)
8. [Available API Endpoints](#8-available-api-endpoints)
9. [Common Tasks](#9-common-tasks)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Prerequisites

Before you begin, ensure you have the following installed on your system:

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| **Python** | 3.11+ | `python3 --version` |
| **pip** | 23+ | `pip3 --version` |
| **Node.js** | 20+ | `node --version` |
| **npm** | 9+ | `npm --version` |
| **Git** | 2.x | `git --version` |
| **AWS Account** | Active | — |

### Installing Prerequisites

<details>
<summary><b>macOS</b> — Install via Homebrew</summary>

```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.12

# Install Node.js
brew install node@20

# Verify installations
python3 --version   # Should show Python 3.12.x
node --version      # Should show v20.x
npm --version       # Should show 10.x
```
</details>

<details>
<summary><b>Ubuntu/Debian</b> — Install via apt</summary>

```bash
# Update package list
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install -y python3 python3-pip python3-venv

# Install Node.js (using NodeSource)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installations
python3 --version
node --version
npm --version
```
</details>

<details>
<summary><b>Windows</b> — Install via Downloads</summary>

1. **Python**: Download from [python.org](https://www.python.org/downloads/) (Python 3.12+)
   - ✅ Check "Add Python to PATH" during installation
2. **Node.js**: Download from [nodejs.org](https://nodejs.org/) (LTS version 20.x)
   - ✅ This includes npm automatically
3. **Git**: Download from [git-scm.com](https://git-scm.com/download/win)
   - ✅ Use default options

Open **PowerShell as Administrator** and verify:
```powershell
python --version
node --version
npm --version
git --version
```
</details>

---

## 2. Quick Start (5 minutes)

If you already have the prerequisites installed:

```bash
# 1. Navigate to the project
cd aws-infra-vision

# 2. Set up Python backend
python3 -m venv .venv
source .venv/bin/activate     # macOS/Linux
# .venv\Scripts\activate      # Windows

pip install -r backend/requirements.txt

# 3. Set up frontend
cd frontend
npm install
cd ..

# 4. Install root dependencies (for Electron)
npm install

# 5. Start the backend
source .venv/bin/activate     # if not already activated
uvicorn backend.app.main:app --reload --port 8000
```

👉 Open your browser to **http://localhost:8000/docs** — you should see the Swagger API documentation.

---

## 3. Detailed Installation by Platform

### 3.1 macOS

#### Step 1: Clone or navigate to the project

```bash
cd /path/to/aws-infra-vision
```

#### Step 2: Set up Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Your terminal prompt should change to show `(.venv)`.

#### Step 3: Install Python dependencies

```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

#### Step 4: Install Node.js dependencies

```bash
# Frontend dependencies
cd frontend
npm install
cd ..

# Root dependencies (for Electron packaging)
npm install
```

#### Step 5: Create `.env` file (optional)

```bash
cat > .env << EOF
DEBUG=true
LOG_LEVEL=DEBUG
AWS_DEFAULT_REGION=us-east-1
EOF
```

---

### 3.2 Linux (Ubuntu/Debian)

#### Step 1: Navigate to the project

```bash
cd /path/to/aws-infra-vision
```

#### Step 2: Install system dependencies

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv python3-dev
```

> **For keychain support**, install Secret Service:
> ```bash
> sudo apt install -y gnome-keyring libsecret-1-dev
> ```

#### Step 3: Set up Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
```

#### Step 4: Install Node.js dependencies

```bash
cd frontend && npm install && cd ..
npm install
```

#### Step 5: Create `.env` file (optional)

```bash
cat > .env << EOF
DEBUG=true
LOG_LEVEL=DEBUG
EOF
```

---

### 3.3 Windows

#### Step 1: Open PowerShell or Command Prompt

```powershell
cd C:\path\to\aws-infra-vision
```

#### Step 2: Set up Python virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

> If you get a security error, run PowerShell as Administrator and execute:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

#### Step 3: Install Python dependencies

```powershell
pip install --upgrade pip
pip install -r backend\requirements.txt
```

> **Note about `keyring` on Windows**: On Windows, `keyring` uses the Windows Credential Vault. It works out of the box with no additional dependencies.

#### Step 4: Install Node.js dependencies

```powershell
cd frontend
npm install
cd ..

npm install
```

#### Step 5: Create `.env` file (optional)

```powershell
@"
DEBUG=true
LOG_LEVEL=DEBUG
"@ | Out-File -FilePath .env -Encoding UTF8
```

---

## 4. Running the Application

The application has three components that run together:

```
┌──────────────────────────────────────────┐
│           Your Web Browser                │
│        http://localhost:5173              │
│              React Frontend               │
└──────────────┬───────────────────────────┘
               │ HTTP (port 5173)
┌──────────────▼───────────────────────────┐
│    http://localhost:8000                  │
│         FastAPI Backend                   │
│         Python + boto3                    │
└──────────────┬───────────────────────────┘
               │ SQLite
┌──────────────▼───────────────────────────┐
│         aws_infra_vision.db              │
│         Local Database                    │
└──────────────────────────────────────────┘
```

### 4.1 Start the Backend

Open **Terminal 1** and activate the virtual environment:

```bash
cd aws-infra-vision
source .venv/bin/activate     # macOS/Linux
# .venv\Scripts\activate      # Windows

uvicorn backend.app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

✅ **Verify**: Open http://localhost:8000/health — should return `{"status":"healthy"}`

### 4.2 Start the Frontend

Open **Terminal 2** (keep the backend running):

```bash
cd aws-infra-vision/frontend
npm run dev
```

You should see:
```
VITE v5.x  ready in XXXms
➜  Local:   http://localhost:5173/
```

✅ **Verify**: Open http://localhost:5173 — you should see the BB-CloudSight interface.

### 4.3 Start the Electron App (Optional)

Open **Terminal 3** (keep backend + frontend running):

```bash
cd aws-infra-vision
npm run dev:electron
```

This launches the native desktop application window.

### 4.4 Development Mode (All at once)

```bash
cd aws-infra-vision

# Terminal 1
source .venv/bin/activate && uvicorn backend.app.main:app --reload --port 8000

# Terminal 2
cd frontend && npm run dev
```

---

## 5. Configuration

### 5.1 Environment Variables

Create a `.env` file in the project root (`aws-infra-vision/.env`):

```bash
# Application
DEBUG=true
LOG_LEVEL=DEBUG

# Server
HOST=127.0.0.1
PORT=8000

# AWS
AWS_DEFAULT_REGION=us-east-1

# Database (SQLite - default, no changes needed)
# DATABASE_URL=sqlite:///./aws_infra_vision.db
```

All variables have sensible defaults — the `.env` file is optional.

### 5.2 AWS Credentials

The app supports four ways to connect to AWS:

**Option A: AWS Access Keys (Recommended for first-time setup)**

1. Log into the [AWS Console](https://console.aws.amazon.com)
2. Go to **IAM → Users → Select your user → Security credentials**
3. Click **Create access key**
4. Copy the **Access Key ID** and **Secret Access Key**

**Option B: AWS Profile**

If you already configured AWS CLI:
```bash
# Your profile from ~/.aws/config
aws configure list
```

**Option C: IAM Role**

For cross-account access, you'll need the **Role ARN**.

**Option D: Environment Variables**

The app also reads standard AWS environment variables:
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

---

## 6. Verifying the Setup

Run these checks to make sure everything works:

```bash
# 1. Check Python virtual environment
cd aws-infra-vision
source .venv/bin/activate
python3 -c "import fastapi, uvicorn, boto3, sqlalchemy; print('All Python packages OK')"

# 2. Check Python syntax (all files compile)
python3 -c "
import py_compile, os
errors = []
for dirpath, _, filenames in os.walk('backend'):
    for f in filenames:
        if f.endswith('.py'):
            fpath = os.path.join(dirpath, f)
            try:
                py_compile.compile(fpath, doraise=True)
            except py_compile.PyCompileError as e:
                errors.append(str(e))
print(f'All {sum(1 for _ in os.walk(\"backend\"))} files compile OK' if not errors else f'{len(errors)} errors')
"

# 3. Check backend starts
uvicorn backend.app.main:app --port 9999 &
sleep 3
curl -s http://localhost:9999/health
kill %1 2>/dev/null

# 4. Run backend tests
pytest backend/tests/ -v 2>/dev/null || echo "Tests not yet written"
```

**Expected health check response:**
```json
{"status":"healthy","version":"1.0.0","timestamp":"...","database":"connected"}
```

---

## 7. Project Structure Overview

```
aws-infra-vision/
│
├── backend/                         # Python FastAPI backend
│   ├── app/
│   │   ├── main.py                  # Application entry point
│   │   ├── config.py                # Configuration settings
│   │   ├── database.py              # SQLAlchemy models & DB setup
│   │   ├── api/v1/                  # REST API routes (11 modules)
│   │   │   ├── auth.py             # AWS credential management
│   │   │   ├── resources.py        # Resource inventory
│   │   │   ├── costs.py            # Cost analytics
│   │   │   ├── security.py         # Security scanning
│   │   │   ├── terraform.py        # Terraform integration
│   │   │   ├── cloudformation.py   # CloudFormation support
│   │   │   ├── recommendations.py  # Optimization recommendations
│   │   │   ├── timeline.py         # Infrastructure timeline
│   │   │   ├── actions.py          # Resource actions
│   │   │   ├── finops.py           # FinOps scoring
│   │   │   └── ai.py               # AI assistant
│   │   ├── services/               # Business logic (10 modules)
│   │   │   ├── aws_client.py       # AWS SDK factory
│   │   │   ├── cost_analyzer.py    # Cost Explorer integration
│   │   │   ├── security_scanner.py # Security checks
│   │   │   ├── finops_scorer.py    # FinOps scoring engine
│   │   │   ├── anomaly_detector.py # Cost anomaly detection
│   │   │   ├── cfn_analyzer.py     # CloudFormation analysis
│   │   │   ├── terraform_parser.py # Terraform state parsing
│   │   │   ├── rightsizing.py      # Rightsizing engine
│   │   │   ├── unused_detector.py  # Unused resource detection
│   │   │   ├── free_tier.py        # Free tier tracking
│   │   │   ├── timeline_builder.py # CloudTrail timeline
│   │   │   └── ai_assistant.py     # AI query processing
│   │   ├── repositories/           # Data access layer
│   │   ├── utils/                  # Utilities
│   │   └── core/                   # Core framework
│   ├── data/                       # SQLite database files
│   ├── tests/                      # Test suite
│   ├── requirements.txt
│   └── requirements-dev.txt
│
├── frontend/                       # React + TypeScript UI
│   ├── src/
│   │   ├── App.tsx                 # Root component
│   │   ├── pages/                  # Page components
│   │   ├── components/             # Reusable components
│   │   ├── services/               # API client layer
│   │   └── store/                  # State management
│   └── package.json
│
├── electron/                       # Desktop shell
│   ├── main.ts                     # Electron main process
│   └── preload.ts                  # IPC bridge
│
├── docs/                           # Documentation
├── .github/workflows/              # CI/CD pipelines
├── GUIDE.md                        # ← You are here
├── README.md
├── CHANGELOG.md
├── package.json
├── .gitignore
└── LICENSE
```

---

## 8. Available API Endpoints

Once the backend is running, explore the full API at:

| URL | Description |
|-----|-------------|
| **http://localhost:8000/docs** | Swagger UI (interactive docs) |
| **http://localhost:8000/redoc** | ReDoc (alternative docs) |
| **http://localhost:8000/health** | Health check |
| **http://localhost:8000/** | Root API info |

**Key endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/setup-wizard` | Configure AWS credentials |
| `POST` | `/api/v1/auth/validate` | Validate stored credentials |
| `GET` | `/api/v1/resources` | List inventory (paginated) |
| `POST` | `/api/v1/resources/scan` | Trigger resource discovery |
| `GET` | `/api/v1/resources/stats/summary` | Resource statistics |
| `GET` | `/api/v1/costs/summary` | Cost analytics |
| `GET` | `/api/v1/costs/forecast` | Cost forecasting |
| `GET` | `/api/v1/costs/anomalies` | Cost anomalies |
| `GET` | `/api/v1/security/findings` | Security findings |
| `POST` | `/api/v1/security/scan` | Trigger security scan |
| `GET` | `/api/v1/security/score` | Security score |
| `GET` | `/api/v1/finops/score` | FinOps score |
| `POST` | `/api/v1/ai/query` | Ask AI assistant |
| `POST` | `/api/v1/actions/ec2/stop` | Stop EC2 instance |

---

## 9. Common Tasks

### Run backend tests
```bash
cd aws-infra-vision
source .venv/bin/activate
pytest backend/tests/ -v
```

### Run frontend tests
```bash
cd aws-infra-vision/frontend
npm test
```

### Type-check all Python code
```bash
cd aws-infra-vision
source .venv/bin/activate
mypy backend/app/
```

### Type-check frontend code
```bash
cd aws-infra-vision/frontend
npx tsc --noEmit
```

### Lint Python code
```bash
cd aws-infra-vision
source .venv/bin/activate
flake8 backend/app/
```

### Lint frontend code
```bash
cd aws-infra-vision/frontend
npm run lint
```

### Build for production
```bash
cd aws-infra-vision
npm run build:frontend    # Build React app
npm run build:electron    # Compile Electron
npm run package:mac       # Package for macOS
npm run package:win       # Package for Windows
npm run package:linux     # Package for Linux
```

### Reset the database
```bash
cd aws-infra-vision
rm -f backend/data/aws_infra_vision.db
# Restart the backend — it will recreate the database automatically
```

---

## 10. Troubleshooting

### Python issues

| Problem | Solution |
|---------|----------|
| `python3: command not found` | Install Python: `brew install python@3.12` (macOS) or `sudo apt install python3` (Linux) |
| `pip: command not found` | Install pip: `python3 -m ensurepip --upgrade` (macOS/Linux) |
| `ModuleNotFoundError: No module named '...'` | Run `pip install -r backend/requirements.txt` in the venv |
| `Failed to build cryptography` | Install OpenSSL: `brew install openssl` (macOS) or `sudo apt install libssl-dev` (Linux) |
| `keyring.errors.NoKeyringError` | Install keychain backend: `pip install keyrings.alt` or use environment variables instead |

### Node.js issues

| Problem | Solution |
|---------|----------|
| `node: command not found` | Install Node.js from [nodejs.org](https://nodejs.org/) or use `brew install node` |
| `npm ERR!` during install | Delete `node_modules` and `package-lock.json`, then run `npm install` again |
| `Vite not found` | Run `cd frontend && npm install` |

### Backend won't start

```bash
# Check if port is already in use
lsof -i:8000                    # macOS/Linux
netstat -ano | findstr :8000    # Windows

# Kill the process using the port
kill -9 <PID>                   # macOS/Linux
taskkill /PID <PID> /F          # Windows

# Try a different port
uvicorn backend.app.main:app --reload --port 8001
```

### SQLite database issues

```bash
# Delete and recreate the database
rm -f backend/data/aws_infra_vision.db
# Restart the backend — it will recreate on startup
```

### AWS credential issues

```bash
# Test credentials manually
cd aws-infra-vision
source .venv/bin/activate
python3 -c "
import boto3
sts = boto3.client('sts')
print(sts.get_caller_identity()['Account'])
"
```

If this fails, check your AWS credentials are valid and have the required permissions.

### Electron issues

| Problem | Solution |
|---------|----------|
| `electron: command not found` | Run `npm install` in the project root |
| Blank white window | Ensure backend is running on port 8000 and frontend is running on port 5173 |
| `Error: Cannot find module 'electron'` | Run `npm install electron --save-dev` |

### Getting help

If you encounter any issues not covered here:

- Check the [docs/](./docs/) folder for architecture and design details
- Open an issue on the project repository
- Review the [CHANGELOG.md](./CHANGELOG.md) for version-specific notes

---

<div align="center">

**🎉 You're all set! Start exploring your AWS infrastructure with BB-CloudSight.**

</div>
