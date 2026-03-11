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
    
    # Customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            company TEXT,
            phone TEXT,
            address TEXT,
            notes TEXT,
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled', 'on_hold')),
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Quotes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            quote_number TEXT UNIQUE,
            sheet_id TEXT NOT NULL,
            quote_data TEXT NOT NULL,  -- JSON med alle detaljer
            status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'sent', 'accepted', 'rejected', 'expired')),
            version INTEGER DEFAULT 1,
            language TEXT DEFAULT 'NO',
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accepted_at TIMESTAMP NULL,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Contracts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_id INTEGER NOT NULL,
            project_id INTEGER NOT NULL,
            contract_number TEXT UNIQUE,
            contract_data TEXT NOT NULL,  -- JSON med alle detaljer
            status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'pending_signature', 'signed', 'cancelled')),
            signing_request_id TEXT,  -- SignRequest/DocuSign ID
            contract_pdf_path TEXT,
            signed_pdf_path TEXT,
            sent_at TIMESTAMP NULL,
            customer_signed_at TIMESTAMP NULL,
            company_signed_at TIMESTAMP NULL,
            signed_at TIMESTAMP NULL,
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quote_id) REFERENCES quotes (id),
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Project descriptions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_descriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            project_type TEXT,
            generated_content TEXT,  -- JSON
            images TEXT,  -- JSON array
            pdf_path TEXT,
            language TEXT DEFAULT 'NO',
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_invitations_code ON invitations(code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_rate_limits_user_endpoint ON rate_limits(user_id, endpoint)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_customer ON projects(customer_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_quotes_project ON quotes(project_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_quotes_number ON quotes(quote_number)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_contracts_quote ON contracts(quote_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_contracts_project ON contracts(project_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_project_descriptions_project ON project_descriptions(project_id)')
    
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

def create_test_user(email: str, name: str, role: str = 'admin') -> int:
    """Create a test user without Google ID requirement"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO users (google_id, email, name, role)
        VALUES (?, ?, ?, ?)
    ''', (f"test_{email}", email, name, role))
    
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

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
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

# Customer management functions
def create_customer(name: str, email: Optional[str], company: Optional[str], 
                   phone: Optional[str], address: Optional[str], notes: Optional[str],
                   created_by: int) -> int:
    """Create a new customer"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO customers (name, email, company, phone, address, notes, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, email, company, phone, address, notes, created_by))
    
    customer_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return customer_id

def get_customer_by_id(customer_id: int) -> Optional[Dict[str, Any]]:
    """Get customer by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
    customer = cursor.fetchone()
    
    conn.close()
    return dict(customer) if customer else None

def get_customer_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get customer by email"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM customers WHERE email = ?', (email,))
    customer = cursor.fetchone()
    
    conn.close()
    return dict(customer) if customer else None

def get_all_customers() -> List[Dict[str, Any]]:
    """Get all customers"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM customers ORDER BY name ASC')
    customers = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return customers

def update_customer(customer_id: int, **kwargs) -> bool:
    """Update customer information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    allowed_fields = ['name', 'email', 'company', 'phone', 'address', 'notes']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        conn.close()
        return False
    
    updates['updated_at'] = datetime.now()
    set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [customer_id]
    
    cursor.execute(f'UPDATE customers SET {set_clause} WHERE id = ?', values)
    conn.commit()
    conn.close()
    return True

# Project management functions
def create_project(customer_id: int, name: str, description: Optional[str],
                  status: str, created_by: int) -> int:
    """Create a new project"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO projects (customer_id, name, description, status, created_by)
        VALUES (?, ?, ?, ?, ?)
    ''', (customer_id, name, description, status, created_by))
    
    project_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return project_id

def get_project_by_id(project_id: int) -> Optional[Dict[str, Any]]:
    """Get project by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
    project = cursor.fetchone()
    
    conn.close()
    return dict(project) if project else None

def get_projects_by_customer(customer_id: int) -> List[Dict[str, Any]]:
    """Get all projects for a customer"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM projects WHERE customer_id = ? ORDER BY created_at DESC', (customer_id,))
    projects = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return projects

def get_all_projects() -> List[Dict[str, Any]]:
    """Get all projects"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM projects ORDER BY created_at DESC')
    projects = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return projects

def update_project(project_id: int, **kwargs) -> bool:
    """Update project information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    allowed_fields = ['name', 'description', 'status']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        conn.close()
        return False
    
    updates['updated_at'] = datetime.now()
    set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [project_id]
    
    cursor.execute(f'UPDATE projects SET {set_clause} WHERE id = ?', values)
    conn.commit()
    conn.close()
    return True

# Quote management functions
def create_quote(project_id: int, sheet_id: str, quote_data: str, 
                quote_number: Optional[str], version: int, language: str,
                created_by: int) -> int:
    """Create a new quote"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO quotes (project_id, sheet_id, quote_data, quote_number, version, language, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (project_id, sheet_id, quote_data, quote_number, version, language, created_by))
    
    quote_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return quote_id

def get_quote_by_id(quote_id: int) -> Optional[Dict[str, Any]]:
    """Get quote by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM quotes WHERE id = ?', (quote_id,))
    quote = cursor.fetchone()
    
    conn.close()
    return dict(quote) if quote else None

def get_quotes_by_project(project_id: int) -> List[Dict[str, Any]]:
    """Get all quotes for a project"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM quotes WHERE project_id = ? ORDER BY version DESC', (project_id,))
    quotes = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return quotes

def update_quote_status(quote_id: int, status: str, accepted_at: Optional[datetime] = None) -> bool:
    """Update quote status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if accepted_at:
        cursor.execute('UPDATE quotes SET status = ?, accepted_at = ? WHERE id = ?', 
                      (status, accepted_at, quote_id))
    else:
        cursor.execute('UPDATE quotes SET status = ? WHERE id = ?', (status, quote_id))
    
    conn.commit()
    conn.close()
    return True

# Contract management functions
def create_contract(quote_id: int, project_id: int, contract_data: str,
                   contract_number: Optional[str], created_by: int) -> int:
    """Create a new contract"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO contracts (quote_id, project_id, contract_data, contract_number, created_by)
        VALUES (?, ?, ?, ?, ?)
    ''', (quote_id, project_id, contract_data, contract_number, created_by))
    
    contract_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return contract_id

def get_contract_by_id(contract_id: int) -> Optional[Dict[str, Any]]:
    """Get contract by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM contracts WHERE id = ?', (contract_id,))
    contract = cursor.fetchone()
    
    conn.close()
    return dict(contract) if contract else None

def get_contracts_by_project(project_id: int) -> List[Dict[str, Any]]:
    """Get all contracts for a project"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM contracts WHERE project_id = ? ORDER BY created_at DESC', (project_id,))
    contracts = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return contracts

def update_contract(contract_id: int, **kwargs) -> bool:
    """Update contract information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    allowed_fields = ['status', 'signing_request_id', 'contract_pdf_path', 'signed_pdf_path',
                     'sent_at', 'customer_signed_at', 'company_signed_at', 'signed_at']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        conn.close()
        return False
    
    updates['updated_at'] = datetime.now()
    set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [contract_id]
    
    cursor.execute(f'UPDATE contracts SET {set_clause} WHERE id = ?', values)
    conn.commit()
    conn.close()
    return True

# Project description management functions
def create_project_description(project_id: int, project_type: Optional[str],
                              generated_content: str, images: str, pdf_path: Optional[str],
                              language: str, created_by: int) -> int:
    """Create a new project description"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO project_descriptions (project_id, project_type, generated_content, images, pdf_path, language, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (project_id, project_type, generated_content, images, pdf_path, language, created_by))
    
    desc_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return desc_id

def get_project_description_by_project(project_id: int) -> Optional[Dict[str, Any]]:
    """Get project description for a project"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM project_descriptions WHERE project_id = ? ORDER BY created_at DESC LIMIT 1', (project_id,))
    desc = cursor.fetchone()
    
    conn.close()
    return dict(desc) if desc else None

# Helper function to get project overview
def get_project_overview(project_id: int) -> Optional[Dict[str, Any]]:
    """Get complete project overview with customer, quotes, contracts, and descriptions"""
    project = get_project_by_id(project_id)
    if not project:
        return None
    
    customer = get_customer_by_id(project['customer_id'])
    quotes = get_quotes_by_project(project_id)
    contracts = get_contracts_by_project(project_id)
    description = get_project_description_by_project(project_id)
    
    return {
        'project': project,
        'customer': customer,
        'quotes': quotes,
        'contracts': contracts,
        'description': description
    }

# Initialize database when module is imported
init_database()
