import re
import os
import json
import requests
import datetime
from database import get_db_connection

# Load Groq API configurations
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openapi/v1/chat/completions"
MODEL_NAME = "llama3-8b-8192"

def sanitize_input(value):
    """Sanitizes text inputs to prevent XSS and basic injection attacks."""
    if not value:
        return ""
    # Strip HTML tags
    value = re.sub(r'<[^>]*>', '', value)
    # Escape simple characters
    value = value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#x27;')
    return value.strip()

def validate_voter_id(voter_id):
    """
    Validates the syntax of the Voter ID.
    Must be alphanumeric, between 4 and 24 characters, allows hyphens or underscores.
    """
    if not voter_id:
        return False, "Voter ID cannot be empty."
    if len(voter_id) < 4 or len(voter_id) > 24:
        return False, "Voter ID must be between 4 and 24 characters."
    if not re.match(r"^[a-zA-Z0-9\-_]+$", voter_id):
        return False, "Voter ID contains invalid characters. Only alphanumeric, hyphens, and underscores are allowed."
    return True, ""

def detect_sql_injection(voter_id):
    """Heuristic check for common SQL injection payloads in Voter ID."""
    sql_patterns = [
        r"union\s+select",
        r"select\s+.*\s+from",
        r"insert\s+into",
        r"drop\s+table",
        r"delete\s+from",
        r"update\s+.*\s+set",
        r"or\s+1\s*=\s*1",
        r"or\s+['\"].*['\"]\s*=\s*['\"].*['\"]",
        r"--",
        r"/\*",
        r"\*/"
    ]
    lowered = voter_id.lower()
    for pattern in sql_patterns:
        if re.search(pattern, lowered):
            return True
    return False

def check_ip_rate_limit(ip_address, time_window_seconds=60, max_requests=5):
    """
    Checks if an IP address is making excessive vote submissions within a short window.
    Queries the audit_logs table for check.
    """
    if not ip_address:
        return False, 0
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Calculate time window
    time_limit = (datetime.datetime.now() - datetime.timedelta(seconds=time_window_seconds)).strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute(
        '''SELECT COUNT(*) as count FROM audit_logs 
           WHERE ip_address = ? AND timestamp > ?''',
        (ip_address, time_limit)
    )
    count = cursor.fetchone()['count']
    conn.close()
    
    if count >= max_requests:
        return True, count
    return False, count

def run_local_heuristics(voter_id, ip_address, user_agent, candidate, is_duplicate, is_rate_limited, rate_count):
    """
    Runs a rule-based cybersecurity scoring engine locally.
    Acts as the main processing step, and a fallback if Groq API is unavailable.
    """
    score = 0.0
    explanation_parts = []
    recommendations_parts = []
    status = "APPROVED"

    # Rule 1: Duplicate Vote Attempt
    if is_duplicate:
        score = 1.0
        explanation_parts.append("CRITICAL: Voter ID has already cast a vote in this election cycle.")
        recommendations_parts.append("Instantly reject transaction. Block the IP address if repeatedly attempted.")
        status = "BLOCKED"
        return {
            "status": status,
            "fraud_score": score,
            "security_explanation": " | ".join(explanation_parts),
            "recommendations": " | ".join(recommendations_parts)
        }

    # Rule 2: SQL Injection detection
    if detect_sql_injection(voter_id):
        score = 0.95
        explanation_parts.append("HIGH RISK: SQL Injection signature detected in the Voter ID input.")
        recommendations_parts.append("Block transaction immediately and inspect application firewall logs.")
        status = "BLOCKED"

    # Rule 3: Rate Limiting
    if is_rate_limited:
        score = max(score, 0.8)
        explanation_parts.append(f"HIGH RISK: IP rate limit exceeded ({rate_count} submissions in the last 60 seconds).")
        recommendations_parts.append("Temporarily restrict voting access for this IP address.")
        if status != "BLOCKED":
            status = "SUSPICIOUS"

    # Rule 4: Suspicious User Agent
    suspicious_agents = ["python", "curl", "wget", "postman", "brutus", "sqlmap", "nikto"]
    ua_lower = user_agent.lower() if user_agent else ""
    is_bot = any(agent in ua_lower for agent in suspicious_agents)
    if is_bot or not user_agent:
        score = max(score, 0.6)
        explanation_parts.append("MEDIUM RISK: Request made from non-browser program or automation framework.")
        recommendations_parts.append("Enforce CAPTCHA challenges or reject requests missing browser headers.")
        if status != "BLOCKED":
            status = "SUSPICIOUS"

    # Rule 5: Repetitive Voter ID pattern
    if re.match(r"^(.)\1{3,}$", voter_id): # e.g. "aaaa"
        score = max(score, 0.4)
        explanation_parts.append("LOW RISK: Voter ID contains highly repetitive keyboard spam patterns.")
        recommendations_parts.append("Verify physical identity via double authentication factors.")
        if status not in ["BLOCKED", "SUSPICIOUS"]:
            status = "SUSPICIOUS"

    # Default clean status
    if score == 0.0:
        score = 0.05
        explanation_parts.append("LOW RISK: General threat checks passed. Secure browser transaction.")
        recommendations_parts.append("Approve transaction and commit vote to the blockchain ledger.")

    return {
        "status": status,
        "fraud_score": score,
        "security_explanation": " ".join(explanation_parts),
        "recommendations": " ".join(recommendations_parts)
    }

def analyze_vote_security(voter_id, ip_address, user_agent, candidate, is_duplicate):
    """
    Performs AI-powered vote transaction auditing.
    Utilizes Groq Llama 3 if key is present, otherwise falls back to local rules-based engine.
    """
    # 1. Gather basic rates and metrics
    is_rate_limited, rate_count = check_ip_rate_limit(ip_address)
    
    # 2. Compute local rules first as a baseline and backup
    heuristics = run_local_heuristics(
        voter_id, ip_address, user_agent, candidate, is_duplicate, is_rate_limited, rate_count
    )
    
    # If the transaction is a duplicate, block immediately without invoking API to save costs/time
    if is_duplicate or heuristics["status"] == "BLOCKED":
        return heuristics

    # If Groq key is not configured, use local rule output
    if not GROQ_API_KEY:
        heuristics["security_explanation"] += " (Analyzed by Local Cybersecurity Engine - Groq API Key Offline)"
        return heuristics

    # 3. Formulate Prompt for Llama 3
    system_prompt = (
        "You are an AI Cybersecurity Auditor protecting an electronic voting system. "
        "Your task is to analyze vote metadata and identify bots, sybil attacks, fraudulent identities, or penetration attempts. "
        "You must output ONLY valid JSON, formatted exactly as follows: "
        "{\n"
        '  "status": "APPROVED" | "SUSPICIOUS" | "BLOCKED",\n'
        '  "fraud_score": float (between 0.0 and 1.0),\n'
        '  "security_explanation": "detailed explanation of parameters analyzed",\n'
        '  "recommendations": "security team recommendations"\n'
        "}"
    )

    user_prompt = f"""
    Analyze the following vote transaction payload:
    - Voter ID: {voter_id}
    - Chosen Candidate: {candidate}
    - Client IP: {ip_address}
    - Client User-Agent: {user_agent}
    - Duplicated Vote in DB: {is_duplicate}
    - Submission storm detected (60s limit): {is_rate_limited} (Submissions count: {rate_count})
    
    Local rule calculation:
    - Suggested Fraud Score: {heuristics['fraud_score']}
    - Suggested Status: {heuristics['status']}
    """

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }
        
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=5)
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            ai_data = json.loads(content)
            
            # Basic schema validation of AI response
            if "status" in ai_data and "fraud_score" in ai_data:
                # Ensure fields are of proper type
                ai_data["fraud_score"] = float(ai_data.get("fraud_score", 0.0))
                ai_data["status"] = str(ai_data.get("status", "APPROVED")).upper()
                ai_data["security_explanation"] = str(ai_data.get("security_explanation", "")) + " (AI Audited)"
                ai_data["recommendations"] = str(ai_data.get("recommendations", ""))
                return ai_data
                
        # If response was bad or failed, fallback
        heuristics["security_explanation"] += f" (Groq status code {response.status_code} - local fallback used)"
        return heuristics
    except Exception as e:
        heuristics["security_explanation"] += f" (API Error: {str(e)} - local fallback used)"
        return heuristics
