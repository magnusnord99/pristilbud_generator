import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

DATABASE_PATH = "app.db"

def init_database():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            google_id TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin')),
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Invitations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invitations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            used_at TIMESTAMP NULL,
            is_used BOOLEAN DEFAULT 0,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Rate limiting table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rate_limits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            endpoint TEXT NOT NULL,
            count INTEGER DEFAULT 1,
            window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            window_end TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_invitations_code ON invitations(code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_rate_limits_user_endpoint ON rate_limits(user_id, endpoint)')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

# User management functions
def create_user(google_id: str, email: str, name: str, is_first_user: bool = False) -> int:
    """Create a new user, first user becomes admin"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    role = 'admin' if is_first_user else 'user'
    
    cursor.execute('''
        INSERT INTO users (google_id, email, name, role)
        VALUES (?, ?, ?, ?)
    ''', (google_id, email, name, role))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_user_by_google_id(google_id: str) -> Optional[Dict[str, Any]]:
    """Get user by Google ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE google_id = ?', (google_id,))
    user = cursor.fetchone()
    
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    return dict(user) if user else None

def is_first_user() -> bool:
    """Check if this is the first user to register"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users')
    count = cursor.fetchone()[0]
    
    conn.close()
    return count == 0

# Invitation management functions
def create_invitation(code: str, email: str, created_by: int) -> int:
    """Create a new invitation"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO invitations (code, email, created_by)
        VALUES (?, ?, ?)
    ''', (code, email, created_by))
    
    invitation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return invitation_id

def get_invitation_by_code(code: str) -> Optional[Dict[str, Any]]:
    """Get invitation by code"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM invitations WHERE code = ? AND is_used = 0', (code,))
    invitation = cursor.fetchone()
    
    conn.close()
    return dict(invitation) if invitation else None

def mark_invitation_used(invitation_id: int, used_at: datetime):
    """Mark invitation as used"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE invitations 
        SET is_used = 1, used_at = ? 
        WHERE id = ?
    ''', (used_at, invitation_id))
    
    conn.commit()
    conn.close()

# Rate limiting functions
def check_rate_limit(user_id: int, endpoint: str, max_requests: int, window_minutes: int) -> bool:
    """Check if user has exceeded rate limit for an endpoint"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = datetime.now()
    window_start = now - timedelta(minutes=window_minutes)
    
    # Clean up old rate limit records
    cursor.execute('''
        DELETE FROM rate_limits 
        WHERE window_end < ?
    ''', (now,))
    
    # Get current count for this user and endpoint
    cursor.execute('''
        SELECT COUNT(*) FROM rate_limits 
        WHERE user_id = ? AND endpoint = ? AND window_start >= ?
    ''', (user_id, endpoint, window_start))
    
    current_count = cursor.fetchone()[0]
    
    if current_count >= max_requests:
        conn.close()
        return False  # Rate limit exceeded
    
    # Record this request
    window_end = now + timedelta(minutes=window_minutes)
    cursor.execute('''
        INSERT INTO rate_limits (user_id, endpoint, window_start, window_end)
        VALUES (?, ?, ?, ?)
    ''', (user_id, endpoint, now, window_end))
    
    conn.commit()
    conn.close()
    return True  # Request allowed

# Admin functions
def get_all_users() -> List[Dict[str, Any]]:
    """Get all users (admin only)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
    users = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return users

def delete_user(user_id: int) -> bool:
    """Delete a user (admin only)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def promote_to_admin(user_id: int) -> bool:
    """Promote user to admin (admin only)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('UPDATE users SET role = "admin" WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

# Initialize database when module is imported
init_database()
