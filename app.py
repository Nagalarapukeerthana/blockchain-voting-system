import os
import bcrypt
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from database import (
    init_db, add_user, get_user, add_vote, voter_exists, 
    add_audit_log, get_audit_logs, get_vote_stats, get_blockchain
)
from blockchain import Blockchain
from security_groq import sanitize_input, validate_voter_id, analyze_vote_security

app = Flask(__name__)

# Configure session security parameters
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24).hex())
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize database tables
init_db()

# Initialize Blockchain
blockchain = Blockchain()

# Helper function to check login
def is_logged_in():
    return session.get('logged_in', False)

@app.route('/')
def vote_page():
    """Serves the main voting interface to voters."""
    return render_template('vote.html')

@app.route('/vote', methods=['POST'])
def cast_vote():
    """Handles vote casting with input verification, duplicate checks, and AI auditing."""
    raw_voter_id = request.form.get('voter_id', '')
    raw_candidate = request.form.get('candidate', '')
    
    # 1. Sanitize inputs to prevent XSS
    voter_id = sanitize_input(raw_voter_id)
    candidate = sanitize_input(raw_candidate)
    
    # 2. Syntax validation
    is_valid, err_msg = validate_voter_id(voter_id)
    ip_addr = request.remote_addr or "127.0.0.1"
    user_agent = request.user_agent.string or "Unknown"

    if not is_valid:
        # Log blocked attempt for syntax validation failure
        add_audit_log(
            voter_id=voter_id or "INVALID_INPUT",
            ip_address=ip_addr,
            user_agent=user_agent,
            status="BLOCKED",
            fraud_score=0.95,
            security_explanation=f"Voter ID validation error: {err_msg}",
            recommendations="Ensure Voter ID contains only alphanumeric characters (4-24 length)."
        )
        return jsonify({"success": False, "message": err_msg}), 400

    # Validate Candidate selection
    allowed_candidates = ["Candidate A", "Candidate B", "Candidate C"]
    if candidate not in allowed_candidates:
        add_audit_log(
            voter_id=voter_id,
            ip_address=ip_addr,
            user_agent=user_agent,
            status="BLOCKED",
            fraud_score=1.0,
            security_explanation=f"Illegal candidate selection attempted: '{candidate}'",
            recommendations="Ensure election candidates align with approved dropdown choices."
        )
        return jsonify({"success": False, "message": "Invalid candidate selected."}), 400

    # 3. Check duplicates
    is_duplicate = voter_exists(voter_id)

    # 4. Perform AI Security Audit and Fraud Detection
    analysis = analyze_vote_security(voter_id, ip_addr, user_agent, candidate, is_duplicate)

    # 5. Record event in the Audit Logs
    add_audit_log(
        voter_id=voter_id,
        ip_address=ip_addr,
        user_agent=user_agent,
        status=analysis["status"],
        fraud_score=analysis["fraud_score"],
        security_explanation=analysis["security_explanation"],
        recommendations=analysis["recommendations"]
    )

    # 6. Reject if status is BLOCKED (covers duplicates, injection signatures, botstorms)
    if analysis["status"] == "BLOCKED":
        return jsonify({
            "success": False, 
            "message": "Vote transaction blocked by security rules.",
            "reason": analysis["security_explanation"]
        }), 403

    # 7. Cast and commit vote to Database & Mint block in Blockchain
    # Double check db write to ensure integrity
    db_success = add_vote(voter_id, candidate)
    if not db_success:
        return jsonify({"success": False, "message": "Database transaction mismatch: Vote already logged."}), 400

    try:
        blockchain.mint_block(voter_id, candidate)
    except Exception as e:
        # Fallback or rollback: in a full production system, we would perform db transaction rollbacks here.
        # Since SQLite doesn't support complex distributed rollbacks out of the box, we output the error.
        return jsonify({"success": False, "message": f"Blockchain minting failure: {str(e)}"}), 500

    return jsonify({
        "success": True,
        "message": "Vote securely cast and verified by blockchain consensus.",
        "analysis": {
            "status": analysis["status"],
            "fraud_score": analysis["fraud_score"],
            "security_explanation": analysis["security_explanation"]
        }
    })

@app.route('/chain')
def view_chain():
    """Exposes the raw blockchain ledger in JSON format."""
    chain_data = [block.to_dict() for block in blockchain.chain]
    return jsonify({
        "length": len(chain_data),
        "chain": chain_data,
        "valid": blockchain.is_chain_valid()
    })

@app.route('/admin')
def admin_page():
    """Serves the Admin Panel. If not authenticated, renders admin login/registration UI."""
    if not is_logged_in():
        return render_template('admin.html', logged_in=False)
    return render_template('admin.html', logged_in=True, username=session.get('username'))

@app.route('/admin/register', methods=['POST'])
def admin_register():
    """Handles secure admin account registration using bcrypt."""
    username = sanitize_input(request.form.get('username', ''))
    password = request.form.get('password', '')

    if not username or len(username) < 4:
        return jsonify({"success": False, "message": "Username must be at least 4 characters."}), 400
    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters."}), 400

    # Hash password with bcrypt
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    success = add_user(username, password_hash)
    if success:
        return jsonify({"success": True, "message": "Admin user registered successfully."})
    else:
        return jsonify({"success": False, "message": "Username already exists."}), 400

@app.route('/admin/login', methods=['POST'])
def admin_login():
    """Authenticates admin user and establishes session."""
    username = sanitize_input(request.form.get('username', ''))
    password = request.form.get('password', '')

    user = get_user(username)
    if not user:
        return jsonify({"success": False, "message": "Invalid credentials."}), 401

    # Verify password hash
    stored_hash = user['password_hash']
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        session['logged_in'] = True
        session['username'] = username
        return jsonify({"success": True, "message": "Logged in successfully."})
    else:
        return jsonify({"success": False, "message": "Invalid credentials."}), 401

@app.route('/admin/logout')
def admin_logout():
    """Terminates admin session."""
    session.clear()
    return redirect(url_for('admin_page'))

@app.route('/admin/stats')
def admin_stats():
    """API endpoint providing real-time data metrics for admin dashboard panel."""
    if not is_logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    stats = get_vote_stats()
    logs = get_audit_logs(limit=30)
    blocks = get_blockchain()
    is_valid = blockchain.is_chain_valid()

    return jsonify({
        "total_votes": stats["total"],
        "breakdown": stats["breakdown"],
        "chain_valid": is_valid,
        "blocks": blocks,
        "logs": logs
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # In production, do not run with debug mode enabled
    app.run(host='0.0.0.0', port=port, debug=False)
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Blockchain Voting System is running"

if __name__ == "__main__":
    app.run(debug=True)