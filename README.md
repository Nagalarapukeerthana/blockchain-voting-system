# CyberSecure Blockchain Voting System with AI Fraud Detection

A secure, full-stack electronic voting system leveraging local rule-based cybersecurity filters, custom SHA-256 block-chained ledgers, and live Llama 3 AI audits via the Groq API.

## Features

- **Decentralized Ledger**: An immutable blockchain built from scratch in Python to record votes. Includes block linkage with previous block hash and automatic chain validation.
- **Cybersecurity Core**:
  - Input sanitization (XSS filtering).
  - Voter ID syntax constraint audits.
  - SQL Injection signature detection.
  - IP-based voting storm rate-limiting.
  - One-vote-per-voter strict enforcement.
- **AI Fraud Auditor**: Powered by Llama 3 via Groq API. Real-time auditing of voting patterns, client headers, and transaction frequency. Includes a robust local heuristics engine that falls back gracefully if the API key is not present.
- **Officer Dashboard Console**: Secure password authentication using `bcrypt`. Real-time metrics polling, interactive stats visualizations, block ledger explorer, and threat activity console.

---

## Local Setup & Run Instructions

### Prerequisites
- Python 3.8 or higher.
- A terminal shell.

### 1. Install Dependencies
Run the following command in your terminal to install packages:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
To enable the **AI Fraud Detection** module, get your API Key from the Groq console and set it as an environment variable:

**For Windows (CMD):**
```cmd
set GROQ_API_KEY=gsk_your_groq_api_key_here
```

**For Windows (PowerShell):**
```powershell
$env:GROQ_API_KEY="gsk_your_groq_api_key_here"
```

**For Linux / macOS:**
```bash
export GROQ_API_KEY="gsk_your_groq_api_key_here"
```

*Note: If no API key is set, the system will seamlessly fall back to local rule-based heuristics to evaluate fraud scores.*

### 3. Launch Flask Server
Run the application:
```bash
python app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.

---

## Deployment to Render

To deploy this application to Render:

1. **GitHub Repository**: Push this directory to your GitHub account.
2. **Create Web Service**:
   - Go to [dashboard.render.com](https://dashboard.render.com) and click **New > Web Service**.
   - Connect your GitHub repository.
3. **Configure Service Details**:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py` (Flask handles binding the `$PORT` automatically via the environment variable in `app.py`).
4. **Environment Variables**:
   - In Render, click the **Environment** tab of your service.
   - Add `GROQ_API_KEY` with your Groq API token.
   - Add `FLASK_SECRET_KEY` with a strong random string (e.g. `openssl rand -hex 24`).
5. **Deploy**: Deploy the service. Render will build and launch your application.
## 🚀 Live Demo
https://blockchain-voting-system-xc7q.onrender.com