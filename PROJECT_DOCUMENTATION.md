# PROJECT DOCUMENTATION: CyberSecure Blockchain Voting System with AI Fraud Detection

---

## 1. Project Title
**CyberSecure Blockchain Voting System with AI Fraud Detection**

---

## 2. Project Overview

### Purpose of the Application
The **CyberSecure Blockchain Voting System** is a decentralized, secure, and smart electronic voting framework. It provides a reliable interface for citizens to cast votes online, while safeguarding the democratic integrity of the election using a custom cryptographic blockchain ledger and live AI threat auditing.

### Problem It Solves
Electronic voting is traditionally plagued by security vulnerabilities, including:
- **Centralized Ledger Tampering**: Database administrators or hackers altering voting records.
- **Sybil Attacks**: Automation bots casting fake votes using generated or stolen identities.
- **Double Voting**: Single voters casting multiple votes under different network profiles.
- **Cyber Penetration**: SQL Injection (SQLi) and Cross-Site Scripting (XSS) targeting web voting APIs.

This application mitigates these risks by combining a cryptographic blockchain ledger (where tampering is instantly detected) with real-time AI security screening that acts as an automated election auditor.

### Key Objectives
1. **Immutability**: Guarantee that once a vote is cast, it cannot be edited, deleted, or re-ordered.
2. **Identity Verification**: Enforce strict one-vote-per-voter constraints.
3. **Automated Auditing**: Inspect the security profile of every transaction using a Llama 3 AI model to spot bots, automation frameworks, and identity spam.
4. **Transparency**: Expose a visual dashboard for election officers to inspect the chronological block-chain linkages and read live security audit logs.

---

## 3. Tech Stack

### Frontend Technologies
- **HTML5**: Core semantic layout structure.
- **CSS3 (Vanilla)**: Cyberpunk-inspired aesthetic, featuring HSL neon colors, grid overlays, custom scrolls, responsive layouts, glassmorphism (`backdrop-filter`), and micro-animations.
- **JavaScript (ES6+)**: Handles async fetch APIs, DOM updates, form state disabling, and dynamic block card layout creation.
- **Chart.js (via CDN)**: Interactive circular charts displaying real-time candidate standings.
- **FontAwesome (via CDN)**: Vector security and technical icons.

### Backend Technologies
- **Python 3.8+**: Application development environment.
- **Flask (v3.0.0+)**: Lightweight RESTful micro-framework to manage HTTP request/response loops, session states, and template routing.

### Database
- **SQLite3**: Lightweight relational database. Serves as the persistence layer for admin accounts, duplicate checking, the blockchain block log, and threat audit records.

### Libraries and Frameworks (Python)
- **`bcrypt`**: Industry-standard Blowfish-based password hashing algorithm to secure administrative registration credentials.
- **`requests`**: Handles REST requests to the external Groq Chat Completion API endpoints.
- **`hashlib` & `json`**: core cryptographic hashing engine (SHA-256) and data serialization.

### Development Tools Used
- **PowerShell**: Environment command execution.
- **Python Verification Script**: Custom-built testing suite (`verify_system.py`) to validate local cryptographic and cybersecurity logic.

---

## 4. Project Architecture

### High-Level Architecture
The application follows a client-server architecture split into five logical layers:
1. **Presentation Layer (Voter Portal & Admin Dashboard)**: Web interface running in the browser.
2. **Security Gateway Layer (Sanitization & Rate Limiting)**: Immediate input scrubbing, SQLi protection, and rate monitoring.
3. **Intelligence Layer (Groq Llama 3 API & Local Rules)**: Assesses transactional parameters and returns a fraud risk score.
4. **Ledger Layer (Decentralized Hashing)**: Chronological blockchain builder wrapping transaction blocks.
5. **Persistence Layer (SQLite Database)**: Stores state indices, users, and audit records.

```
       +---------------------------------------------+
       |           Client Web Browser                |
       |  (Voter Portal  /  Admin Dash / Script.js)  |
       +----------------------+----------------------+
                              |  (HTTP POST / GET)
                              v
       +---------------------------------------------+
       |             Flask Web Server                |
       |                 (app.py)                    |
       +----------------------+----------------------+
                              |
     +------------------------+------------------------+
     v                                                 v
+----+-------------------+                        +----+-------------------+
|  Security Controller   |                        |  Blockchain Ledger     |
| (security_groq.py)     |                        |   (blockchain.py)      |
+----+-------------------+                        +----+-------------------+
     |                                                 |
     |--> Local Heuristics Check                       |--> SHA-256 Hashing
     |--> Groq Llama 3 API Audit                       |--> Prev Block Linking
     v                                                 v
+----+-------------------------------------------------+-------------------+
|                           SQLite Database                                |
|           (Users  |  Votes  |  Blockchain  |  Audit Logs)               |
+--------------------------------------------------------------------------+
```

### Component Interaction Flow
1. A voter enters their Voter ID, selects a candidate, and clicks "Cast Vote".
2. **`script.js`** intercepts the submit, disables input fields, and posts a payload to `/vote`.
3. **`app.py`** processes the route, sanitizes inputs, and runs a format validation using **`security_groq.py`**.
4. If valid, **`security_groq.py`** checks if the voter has already voted, performs a speed limit rate check, and analyzes headers:
   - It formats request metadata and invokes the Groq Llama 3 API.
   - If the API is offline or the token is missing, the local heuristics engine evaluates the threat score.
5. If the transaction is approved:
   - **`database.py`** inserts the voter's token into the `votes` table to prevent duplicates.
   - **`blockchain.py`** mints a new block (linking it to the hash of the previous block) and saves it to the `blockchain` table.
6. The transaction details are written to the `audit_logs` table.
7. Flask returns a JSON response containing success metrics and the AI fraud report, which **`script.js`** displays on screen.
8. The Admin Dashboard polls `/admin/stats` to update the real-time metrics, Chart.js standings, blocks, and logs.

---

## 5. Folder Structure

```
blockchain-voting-system/
│
├── app.py                      # Core server backend controller (routes, auth sessions, REST API)
├── blockchain.py               # Cryptographic block structures, ledger builder, chain validators
├── database.py                 # SQLite setup helper, DB initializers, SQL transactions
├── security_groq.py            # Sanitizers, rate limiters, local heuristics, and Groq API connector
│
├── requirements.txt            # Python dependencies lists
├── README.md                   # Installation guidelines, environment configuration, run commands
├── PROJECT_DOCUMENTATION.md    # Comprehensive system engineering manual
│
├── templates/                  # Flask HTML UI Views
│   ├── vote.html               # Voter portal (Vote Casting, real-time AI security feedback)
│   └── admin.html              # Officer panel (Officer login/register, metrics, block explorer, log console)
│
└── static/                     # Web Frontend static resources
    ├── style.css               # Futuristic cyberpunk Dark HSL stylesheet
    └── script.js               # AJAX actions, polling intervals, Chart.js rendering, and visual builders
```

### Module Responsibilities
- **`app.py`**: Manages HTTP session lifecycles, parses incoming form values, handles route permissions, and coordinates communication between modules.
- **`blockchain.py`**: Manages cryptographic calculations. Ensures that the blockchain is in sync with database tables and exposes methods to check whether tampering occurred.
- **`database.py`**: Encapsulates all SQL statements. Prevents SQL injections using tuple parameter bindings.
- **`security_groq.py`**: The cybersecurity filter of the system. Implements custom heuristics to spot bots, handles connection state handling for AI requests, and parses JSON output from Llama 3.

---

## 6. Features

### 1. Cryptographic Blockchain Ledger
- Custom-built Python blockchain implementing SHA-256 block hashing.
- Auto-generates a system genesis block upon initial database seeding.
- Inter-block links using a `previous_hash` key.
- Automatic verification checks: if a single block's attributes are altered in the SQLite file, the system flags the ledger integrity as compromised.

### 2. AI-Powered Fraud Auditing
- Live Llama 3 API integration via Groq.
- Inspects voter keyboard spam (repetition checking), suspicious user agents (bot frameworks), duplicate attempt history, and transaction rates.
- Returns a structured threat analysis, fraud score, and audit status.

### 3. Local Cybersecurity Fallback Engine
- Seamlessly falls back to an offline rule-based heuristics analyzer if the Groq API key is not configured or fails to respond, ensuring zero voting downtime.

### 4. Duplicate Cast Prevention (Double Voting)
- Database-enforced primary key constraints on `voter_id` combined with blockchain validations.

### 5. Secure Officer Access (Admin Authentication)
- Registration and login systems utilizing `bcrypt` password hashing (Blowfish encryption) to secure the Admin Dashboard.

### 6. Interactive Visual Dashboard
- Doughnut chart rendering candidate vote ratios (using Chart.js).
- Horizontal block viewer displaying the minted blocks, index, timestamp, and hashes in real-time.
- Interactive log console color-coding events by security threat levels (APPROVED = Green, SUSPICIOUS = Orange, BLOCKED = Red).

---

## 7. Installation Guide

### Prerequisites
- **Python**: Version 3.8 or higher.
- **Package Manager**: `pip` (included by default in standard Python installations).

### Step-by-Step Installation
1. Open a terminal or shell window.
2. Navigate to your project directory:
   ```bash
   cd C:\Users\Lenovo\.gemini\antigravity\scratch\blockchain-voting-system
   ```
3. Install the application dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 8. Configuration

### Environment Variables
The application looks for two environment variables to secure sessions and enable live AI auditing:
- `GROQ_API_KEY`: Your private Groq Cloud API access key (e.g., `gsk_...`).
- `FLASK_SECRET_KEY`: A cryptographically secure random string used to sign Flask session cookies.

#### Setting Variables on Windows (CMD)
```cmd
set GROQ_API_KEY=gsk_your_actual_key_here
set FLASK_SECRET_KEY=9a1b8c2d7e3f4g5h6i7j8k9l0m
```

#### Setting Variables on Windows (PowerShell)
```powershell
$env:GROQ_API_KEY="gsk_your_actual_key_here"
$env:FLASK_SECRET_KEY="9a1b8c2d7e3f4g5h6i7j8k9l0m"
```

#### Setting Variables on macOS / Linux
```bash
export GROQ_API_KEY="gsk_your_actual_key_here"
export FLASK_SECRET_KEY="9a1b8c2d7e3f4g5h6i7j8k9l0m"
```

### Database Seeding
The SQLite database file `voting_system.db` is initialized automatically on server boot. There is no need for manual schema provisioning.

---

## 9. How to Run the Application

### Development Mode
To launch the application in development mode:
```bash
python app.py
```
Open your web browser and navigate to:
**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

### Production Mode
For production deployments (such as Render or Heroku):
1. **PORT Handling**: The server binds to the environment variable `PORT` automatically, which is required by cloud runtimes:
   ```python
   port = int(os.environ.get("PORT", 5000))
   app.run(host='0.0.0.0', port=port, debug=False)
   ```
2. **Web Server Gateway**: In high-traffic environments, it is recommended to run the Flask application behind a WSGI server like `gunicorn`:
   ```bash
   pip install gunicorn
   gunicorn app:app
   ```

### Deployment Steps (Render)
1. Push the project code to a GitHub repository.
2. Log in to [Render Console](https://dashboard.render.com/) and create a new **Web Service**.
3. Link your GitHub repository.
4. Set the **Build Command** to: `pip install -r requirements.txt`.
5. Set the **Start Command** to: `python app.py` or `gunicorn app:app`.
6. Add your `GROQ_API_KEY` and `FLASK_SECRET_KEY` variables under the **Environment** tab.

---

## 10. Application Workflow

### End-to-End User Flow

#### A. Cast a Vote
```
[Voter Web Portal] --(1. Enter Voter ID & Pick Candidate)--> [Submit Transaction]
                                                                     |
                                                                     v
                                                          [Cybersecurity Gateway]
                                                          - Sanitize String input
                                                          - Check DB Duplicate
                                                          - Run SQLi heuristics
                                                                     |
                                                                     v
                                                            [AI Fraud Auditor]
                                                            - Eval Client IP/Agent
                                                            - Query Llama 3 model
                                                                     |
                                           +-------------------------+-------------------------+
                                           | Status: BLOCKED                                   | Status: APPROVED
                                           v                                                   v
                                 [Reject Transaction]                                [Insert Vote to SQLite]
                                 - Add Blocked Audit Log                             - Mint Cryptographic Block
                                 - Return Blocked alert response                     - Save Block to Ledger
                                                                                     - Return Success response
```

#### B. Administrative Audit
```
[Officer Access Portal] --(1. Registration / Login Verification)--> [Admin Dashboard]
                                                                            |
                                                                            v
                                                                   [Auto Stats Polling]
                                                                   - Get Vote Breakdown
                                                                   - Check Ledger Integrity
                                                                   - Render Block Linkages
                                                                   - Load live Audit Log table
```

### Screen-by-Screen Explanation
1. **Vote Portal (`/`)**: Displays a secure card interface. It prompts the voter for their Voter ID and candidate. Upon submission, it renders a details panel showing the AI analysis report (status, risk score, and justification).
2. **Admin Panel (`/admin`)**:
   - **Logged Out State**: Displays forms to either log in or register a new administrative officer.
   - **Logged In State**: Displays metric cards (total votes, ledger validity, and security alert counts), a real-time standing chart, a scrollable blockchain block explorer, and an audit table showing live logs.

---

## 11. API Documentation

### Endpoints List

#### 1. `GET /`
- **Description**: Serves the voter portal client interface.
- **Response**: `text/html`

#### 2. `GET /admin`
- **Description**: Serves the admin dashboard UI (renders authentication forms if session is unauthorized).
- **Response**: `text/html`

#### 3. `POST /vote`
- **Description**: Casts a secure vote.
- **Request Headers**: `Content-Type: application/x-www-form-urlencoded`
- **Request Body Parameters**:
  - `voter_id` (string, required)
  - `candidate` (string, required)
- **Response Examples**:
  - **Success (200 OK)**:
    ```json
    {
      "success": true,
      "message": "Vote securely cast and verified by blockchain consensus.",
      "analysis": {
        "status": "APPROVED",
        "fraud_score": 0.05,
        "security_explanation": "Low risk profile transaction. (AI Audited)"
      }
    }
    ```
  - **ValidationError (400 Bad Request)**:
    ```json
    {
      "success": false,
      "message": "Voter ID contains invalid characters. Only alphanumeric, hyphens, and underscores are allowed."
    }
    ```
  - **Blocked Transaction (403 Forbidden)**:
    ```json
    {
      "success": false,
      "message": "Vote transaction blocked by security rules.",
      "reason": "HIGH RISK: SQL Injection signature detected in the Voter ID input."
    }
    ```

#### 4. `GET /chain`
- **Description**: Exposes the entire raw blockchain ledger.
- **Response (200 OK)**:
    ```json
    {
      "length": 2,
      "chain": [
        {
          "index": 0,
          "voter_id": "GENESIS_SYSTEM",
          "candidate": "GENESIS_SYSTEM",
          "timestamp": "1782012011",
          "previous_hash": "0",
          "hash": "a6174e250eef7605ae42a63e2194d28344da98180cd519619606aae0ad55c928"
        },
        {
          "index": 1,
          "voter_id": "VOTER-100",
          "candidate": "Candidate A",
          "timestamp": "1782012025",
          "previous_hash": "a6174e250eef7605ae42a63e2194d28344da98180cd519619606aae0ad55c928",
          "hash": "c7112028da3d7605ae42a63e2194d28344da98180cd519619606aae0ad55c110"
        }
      ],
      "valid": true
    }
    ```

#### 5. `GET /admin/stats`
- **Description**: Returns statistical metrics for dashboard UI updates. Requires administrative session login.
- **Response (200 OK)**:
    ```json
    {
      "total_votes": 1,
      "breakdown": {
        "Candidate A": 1,
        "Candidate B": 0,
        "Candidate C": 0
      },
      "chain_valid": true,
      "blocks": [...],
      "logs": [...]
    }
    ```

---

## 12. Database Design

The database uses SQLite (`voting_system.db`) and consists of four main tables:

### 1. Table: `users`
Stores officer credentials for admin dashboard access.
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique row identifier |
| `username` | TEXT | UNIQUE, NOT NULL | Administrative officer username |
| `password_hash`| TEXT | NOT NULL | Blowfish bcrypt hash of user password |
| `role` | TEXT | DEFAULT 'admin' | User permission scope |

### 2. Table: `votes`
Maintains voter status to enforce one-vote-per-voter constraints.
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `voter_id` | TEXT | PRIMARY KEY | The unique identifier of the voter |
| `candidate` | TEXT | NOT NULL | The candidate selected |
| `timestamp` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Date and time the vote was cast |

### 3. Table: `blockchain`
The persistent ledger of minted cryptographic blocks.
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `block_index` | INTEGER | PRIMARY KEY | Incrementing sequence of blocks |
| `voter_id` | TEXT | NOT NULL | The voter identifier |
| `candidate` | TEXT | NOT NULL | The candidate voted for |
| `timestamp` | TEXT | NOT NULL | Transaction Unix epoch timestamp |
| `previous_hash`| TEXT | NOT NULL | Cryptographic SHA-256 hash of the parent block |
| `hash` | TEXT | NOT NULL | Cryptographic SHA-256 hash of current block variables |

### 4. Table: `audit_logs`
A log table storing cybersecurity threat metrics and audit results.
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Log identifier |
| `timestamp` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Audit date and time |
| `voter_id` | TEXT | - | Voter ID associated with the request |
| `ip_address` | TEXT | - | Client IP network address |
| `user_agent` | TEXT | - | Client HTTP browser string |
| `status` | TEXT | NOT NULL | Threat determination: `APPROVED`, `SUSPICIOUS`, `BLOCKED` |
| `fraud_score` | REAL | NOT NULL | Calculated fraud score (0.0 to 1.0) |
| `security_explanation` | TEXT | - | Explanatory statement of threat analysis factors |
| `recommendations` | TEXT | - | Actions recommended for cybersecurity engineers |

---

## 13. Security Measures

1. **Password Hashing**: Administrative passwords are salted and hashed using `bcrypt`. Plaintext passwords are never saved.
2. **Session Hijacking Prevention**: Session cookies are configured with the `HttpOnly` and `SameSite=Lax` attributes to block client-side scripts from reading session tokens.
3. **Input Sanitization**: Special HTML and scripting characters in inputs are escaped to prevent Cross-Site Scripting (XSS).
4. **SQL Injection Mitigation**: All SQL operations use parameterized queries (`?` placeholders) rather than raw string concatenation.
5. **Decentralized Cryptography**: If database records are altered (e.g. through SQL updates outside the app), the next integrity check detects the hash mismatch and flags the ledger as compromised.

---

## 14. Testing

### Test Strategy
Our testing strategy targets four key areas of the application:
1. **Ledger Integrity**: Confirming the blockchain correctly identifies tampering when a database column is modified manually.
2. **Security Gateway**: Testing syntax limits and blocking requests that contain injection signatures.
3. **Admin Authentication**: Ensuring registration and bcrypt credentials work as expected.
4. **Offline Heuristics**: Verifying that the local heuristics engine generates appropriate threat scores when the external API is offline.

### Executing Tests
A custom validation suite is provided in the project resources:
`C:\Users\Lenovo\.gemini\antigravity\brain\bb25f0aa-81a4-431f-827a-79b324ea3727\scratch\verify_system.py`

Run the script from your terminal using Python:
```bash
python C:\Users\Lenovo\.gemini\antigravity\brain\bb25f0aa-81a4-431f-827a-79b324ea3727\scratch\verify_system.py
```

---

## 15. Screens and Modules

### 1. Voter Portal (`templates/vote.html`)
- **Portal Card**: Contains a form with input fields for a Voter ID and a dropdown selector for the candidate selection.
- **Auditor Report Widget**: A hidden container that transitions into view once a vote is cast, displaying the real-time AI security audit report.

### 2. Admin Portal (`templates/admin.html`)
- **Authentication Panel**: Displays tabbed login and registration forms.
- **Metrics Dashboard**: Four cards summarizing total votes, ledger integrity, system alerts, and AI status.
- **Data Standings Chart**: Renders candidate vote shares using Chart.js.
- **Blockchain Explorer**: Renders a horizontal carousel showing blocks linked with interactive transition arrows.
- **Security Logs Console**: Renders a tabular list of audit logs color-coded by security threat status.

---

## 16. Challenges and Solutions

### Challenge 1: Restricting Double Voting in a Stateless Web Environment
- **Description**: Ensuring a voter cannot cast multiple votes under different names or by reloading the page.
- **Solution**: We implemented database-level unique primary keys on `voter_id` in the `votes` table. The transaction verifies if the Voter ID already exists in the database and blockchain ledger before allowing the vote to proceed, rejecting any duplicates.

### Challenge 2: Sandbox Network Restrictions & Offline Reliability
- **Description**: The application sandbox environment blocks outgoing internet access. When testing or deploying offline, calling the Groq API would raise network timeouts, preventing votes from being processed.
- **Solution**: Implemented a local cybersecurity rules engine (`security_groq.py`). When the system detects the absence of a `GROQ_API_KEY` or catches an HTTP timeout, it automatically processes the transaction locally. This keeps the application fully functional offline while preserving the API schema.

### Challenge 3: Verification Script Database-Level Validation Mismatch
- **Description**: During testing, simulating blockchain tampering in memory was overwritten because the validation method fetched records directly from the database, missing the in-memory alterations.
- **Solution**: Updated the test suite to execute a direct SQL query to update the database table before validating. This accurately simulates an SQL intrusion attack and tests database-level tampering detection.

---

## 17. Future Enhancements

1. **True Peer-to-Peer Consensus**: Distribute the blockchain across multiple nodes using consensus algorithms (e.g., Proof of Authority) to remove single points of database failure.
2. **Zero-Knowledge Proofs (ZKP)**: Implement cryptographic ZKPs to verify that a voter is authorized without revealing their Voter ID, ensuring voter anonymity.
3. **Multi-Factor Authentication (MFA)**: Require SMS or email OTP verification to associate a voter ID with a physical person.

---

## 18. Conclusion
The **CyberSecure Blockchain Voting System** demonstrates how modern web applications can combine cryptographic ledgers with artificial intelligence to protect election integrity. By combining input filters, duplicate vote prevention, cryptographic block minting, and AI audits, the system provides a secure electronic voting framework suitable for corporate, academic, and municipal elections.
