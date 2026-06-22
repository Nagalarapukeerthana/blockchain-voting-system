import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'voting_system.db')

def get_db_connection():
    """Establishes a connection to the SQLite database with row factory enabled."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema if tables do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Users table for Admin registration & authentication (using bcrypt hashes)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'admin'
        )
    ''')
    
    # 2. Votes table to track cast votes locally and enforce one-vote-per-voter
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            voter_id TEXT PRIMARY KEY,
            candidate TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 3. Blockchain table to persist the blockchain blocks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blockchain (
            block_index INTEGER PRIMARY KEY,
            voter_id TEXT NOT NULL,
            candidate TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            previous_hash TEXT NOT NULL,
            hash TEXT NOT NULL
        )
    ''')
    
    # 4. Audit Logs table to track system events, including fraud analysis details
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            voter_id TEXT,
            ip_address TEXT,
            user_agent TEXT,
            status TEXT NOT NULL,
            fraud_score REAL NOT NULL,
            security_explanation TEXT,
            recommendations TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(username, password_hash, role='admin'):
    """Securely inserts a new user with password hash."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
            (username, password_hash, role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username):
    """Retrieves a user by username."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def add_vote(voter_id, candidate):
    """Saves a vote to the votes table. Enforces voter_id uniqueness."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO votes (voter_id, candidate) VALUES (?, ?)',
            (voter_id, candidate)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def voter_exists(voter_id):
    """Checks if a voter has already cast a vote."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM votes WHERE voter_id = ?', (voter_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def add_block(block_index, voter_id, candidate, timestamp, previous_hash, hash_val):
    """Appends a new block to the blockchain ledger table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            '''INSERT INTO blockchain 
               (block_index, voter_id, candidate, timestamp, previous_hash, hash) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            (block_index, voter_id, candidate, timestamp, previous_hash, hash_val)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_blockchain():
    """Retrieves all blocks in chronological order from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM blockchain ORDER BY block_index ASC')
    blocks = cursor.fetchall()
    conn.close()
    return [dict(b) for b in blocks]

def add_audit_log(voter_id, ip_address, user_agent, status, fraud_score, security_explanation, recommendations):
    """Inserts a security audit log event."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO audit_logs 
           (voter_id, ip_address, user_agent, status, fraud_score, security_explanation, recommendations) 
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (voter_id, ip_address, user_agent, status, fraud_score, security_explanation, recommendations)
    )
    conn.commit()
    conn.close()

def get_audit_logs(limit=50):
    """Retrieves recent audit logs ordered by timestamp desc."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?', (limit,))
    logs = cursor.fetchall()
    conn.close()
    return [dict(l) for l in logs]

def get_vote_stats():
    """Retrieves vote statistics including total count and candidate breakdowns."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as total FROM votes')
    total = cursor.fetchone()['total']
    
    cursor.execute('SELECT candidate, COUNT(*) as count FROM votes GROUP BY candidate')
    rows = cursor.fetchall()
    breakdown = {row['candidate']: row['count'] for row in rows}
    
    # Ensure all candidates are listed (Candidate A, B, C)
    for cand in ['Candidate A', 'Candidate B', 'Candidate C']:
        if cand not in breakdown:
            breakdown[cand] = 0
            
    conn.close()
    return {
        'total': total,
        'breakdown': breakdown
    }
