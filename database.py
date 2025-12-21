import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import hashlib
import shutil
import os

DATABASE_NAME = 'finance.db'

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Initialize database with tables and perform migration if needed"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if users table exists (Migration check)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    users_exist = cursor.fetchone()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            currency TEXT DEFAULT 'INR',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Transactions table - Add user_id if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT,
            amount REAL NOT NULL,
            description TEXT,
            account TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Check if user_id column exists in transactions
    cursor.execute("PRAGMA table_info(transactions)")
    columns = [column[1] for column in cursor.fetchall()]
    first = False
    if 'user_id' not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN user_id INTEGER")
        first = True
    
    if 'is_repaid' not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN is_repaid INTEGER DEFAULT 0")
        
    if 'linked_id' not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN linked_id INTEGER")

    if 'is_credit_card_payment' not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN is_credit_card_payment INTEGER DEFAULT 0")

    if 'paid_amount' not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN paid_amount REAL DEFAULT 0")
        # Migration: Set paid_amount = amount for already repaid items
        cursor.execute("UPDATE transactions SET paid_amount = amount WHERE is_repaid = 1 AND paid_amount = 0")

    # Loan related columns
    if 'loan_interest_rate' not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN loan_interest_rate REAL")
    if 'loan_tenure_months' not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN loan_tenure_months INTEGER")
    if 'loan_emi' not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN loan_emi REAL")
    if 'loan_start_date' not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN loan_start_date TEXT")
    if 'loan_end_date' not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN loan_end_date TEXT")
    if 'loan_lender_bank' not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN loan_lender_bank TEXT")
    
    # Reinvestment Flag
    if 'is_reinvestment' not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN is_reinvestment INTEGER DEFAULT 0")

    # Self Expense Flag
    if 'is_self' not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN is_self INTEGER DEFAULT 0")
    
    # Categories table - Add user_id if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            is_loan INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Check if user_id column exists in categories
    cursor.execute("PRAGMA table_info(categories)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'user_id' not in columns:
        cursor.execute("ALTER TABLE categories ADD COLUMN user_id INTEGER")
    if 'is_loan' not in columns:
        cursor.execute("ALTER TABLE categories ADD COLUMN is_loan INTEGER DEFAULT 0")

    # Accounts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            balance REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Check if user_id column exists in accounts
    cursor.execute("PRAGMA table_info(accounts)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'user_id' not in columns:
        cursor.execute("ALTER TABLE accounts ADD COLUMN user_id INTEGER")
    
    # Recurring Items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recurring_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            request_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()

    # --- MIGRATION LOGIC ---
    # Check if we need to create a default user (if no users exist)
    cursor.execute("SELECT count(*) FROM users")
    user_count = cursor.fetchone()[0]

    if user_count == 0:
        # Create default admin user 'shijo'
        shijo_pass = hash_password('admin123')
        try:
            cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", 
                          ('shijo', shijo_pass, 1))
            shijo_id = cursor.lastrowid
            
            # Assign ALL existing data to shijo
            cursor.execute("UPDATE transactions SET user_id = ? WHERE user_id IS NULL", (shijo_id,))
            cursor.execute("UPDATE categories SET user_id = ? WHERE user_id IS NULL", (shijo_id,))
            
            conn.commit()
            print("Migration completed: Assigned existing data to user 'shijo'")
            
            # Initialize default categories
            init_default_categories(shijo_id)
            
        except sqlite3.IntegrityError:
            pass # User might already exist if re-running
            
    conn.close()

def request_password_reset(username: str) -> bool:
    """Create a password reset request for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check user exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return False
        
    # Check if pending request already exists
    cursor.execute("SELECT id FROM password_requests WHERE user_id = ? AND status = 'PENDING'", (user['id'],))
    existing = cursor.fetchone()
    
    if not existing:
        cursor.execute("INSERT INTO password_requests (user_id, username, request_date) VALUES (?, ?, ?)", 
                      (user['id'], username, str(datetime.now())))
        conn.commit()
        
    conn.close()
    return True

def get_pending_password_requests() -> pd.DataFrame:
    """Get all pending password reset requests"""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM password_requests WHERE status = 'PENDING' ORDER BY request_date DESC", conn)
    conn.close()
    return df

def resolve_password_request(request_id: int, new_password: str, admin_id: int) -> bool:
    """Resolve a password request by updating the user's password"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Get request details
        cursor.execute("SELECT user_id FROM password_requests WHERE id = ?", (request_id,))
        req = cursor.fetchone()
        
        if not req:
            return False
            
        # Update User Password
        hashed = hashlib.sha256(new_password.encode()).hexdigest()
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, req['user_id']))
        
        # Mark Request as Resolved
        cursor.execute("UPDATE password_requests SET status = 'RESOLVED' WHERE id = ?", (request_id,))
        
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()



def init_default_categories(user_id: int):
    """Initialize default categories for a specific user"""
    default_categories = [
        # Income categories
        ('Salary', 'Income'),
        ('Bonus', 'Income'),
        ('Other Income', 'Income'),
        ('Interest', 'Income'),
        
        # Expense categories
        ('Rent', 'Expense'),
        ('EMI', 'Expense'),
        ('Insurance', 'Expense'),
        ('Utilities', 'Expense'),
        ('Groceries', 'Expense'),
        ('Transport', 'Expense'),
        ('Entertainment', 'Expense'),
        ('Healthcare', 'Expense'),
        ('Education', 'Expense'),
        ('Shopping', 'Expense'),
        ('Other Expense', 'Expense'),
        
        # Investment categories
        ('SIP', 'Investment'),
        ('Stocks', 'Investment'),
        ('Mutual Funds', 'Investment'),
        ('FD/RD', 'Investment'),
        ('Gold', 'Investment'),
        ('PPF/EPF', 'Investment'),
        
        # Credit Card categories
        ('HDFC Credit Card', 'Credit Card'),
        ('ICICI Credit Card', 'Credit Card'),
        ('Other Credit Card', 'Credit Card'),
        
        # Banking categories
        ('Bank Transfer', 'Banking'),
        ('Cash Withdrawal', 'Banking'),
        ('Deposit', 'Banking'),
        
        # Vehicle categories (Tracking only)
        ('Car Fuel', 'Vehicle'),
        ('Bike Fuel', 'Vehicle'),
        ('Garage', 'Vehicle'),
        ('Vehicle Insurance', 'Vehicle'),

        # Debt categories
        ('Personal Loan', 'Debt'),
        ('Home Loan', 'Debt'),
        ('Education Loan', 'Debt'),
        ('Car Loan', 'Debt'),
        ('Credit Card Payment', 'Debt'),
        ('Friends', 'Debt'),
    ]
    
    conn = get_connection()
    cursor = conn.cursor()
    
    for name, cat_type in default_categories:
        try:
            # Check if exists for this user to avoid duplicates
            cursor.execute("SELECT id FROM categories WHERE user_id = ? AND name = ? AND type = ?", (user_id, name, cat_type))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO categories (user_id, name, type) VALUES (?, ?, ?)', (user_id, name, cat_type))
        except:
            pass
    
    conn.commit()
    conn.close()

# ========== USER MANAGEMENT ==========

def create_user(username, password, is_admin=0, currency='INR'):
    """Create a new user"""
    conn = get_connection()
    cursor = conn.cursor()
    hashed_pw = hash_password(password)
    
    try:
        cursor.execute("INSERT INTO users (username, password, is_admin, currency) VALUES (?, ?, ?, ?)", 
                      (username, hashed_pw, is_admin, currency))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Initialize categories for new user
        init_default_categories(user_id)
        
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def verify_user(username, password):
    """Verify user credentials"""
    conn = get_connection()
    cursor = conn.cursor()
    hashed_pw = hash_password(password)
    
    cursor.execute("SELECT id, username, is_admin, currency FROM users WHERE username = ? AND password = ?", (username, hashed_pw))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return dict(user)
    return None

def user_exists(username: str) -> bool:
    """Check if a user exists by username"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def update_user_currency(user_id: int, currency: str):
    """Update user's preferred currency"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET currency = ? WHERE id = ?", (currency, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating currency: {e}")
        return False
    finally:
        conn.close()

def get_all_users():
    """Get all users (for admin)"""
    conn = get_connection()
    df = pd.read_sql_query("SELECT id, username, is_admin, created_at FROM users", conn)
    conn.close()
    return df

def update_user_password(user_id: int, old_password: str, new_password: str):
    """Update user password after verifying old password"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verify old password
    old_hash = hash_password(old_password)
    cursor.execute("SELECT id FROM users WHERE id = ? AND password = ?", (user_id, old_hash))
    if not cursor.fetchone():
        conn.close()
        return False
    
    # Update to new password
    new_hash = hash_password(new_password)
    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_hash, user_id))
    conn.commit()
    conn.close()
    return True

def reset_user_password(user_id: int, new_password: str):
    """Reset user password (admin only, no verification of old password)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    new_hash = hash_password(new_password)
    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_hash, user_id))
    conn.commit()
    conn.close()
    return True

def delete_user(user_id: int):
    """Delete a user and all their data (admin only)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Delete user's transactions
    cursor.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
    # Delete user's categories
    cursor.execute("DELETE FROM categories WHERE user_id = ?", (user_id,))
    # Delete user's accounts
    cursor.execute("DELETE FROM accounts WHERE user_id = ?", (user_id,))
    # Delete user
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    
    conn.commit()
    conn.close()
    return True

# ========== TRANSACTION OPERATIONS ==========

def add_transaction(user_id: int, date: str, trans_type: str, category: str, amount: float, 
                   subcategory: str = None, description: str = None, account: str = None, 
                   is_repaid: int = 0, linked_id: int = None, is_credit_card_payment: int = 0,
                   paid_amount: float = 0.0, loan_interest_rate: float = None, 
                   loan_tenure_months: int = None, loan_emi: float = None, 
                   loan_start_date: str = None, loan_end_date: str = None, loan_lender_bank: str = None,
                   is_reinvestment: int = 0, is_self: int = 0):
    """Add a new transaction for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO transactions (user_id, date, type, category, subcategory, amount, description, account, 
                                is_repaid, linked_id, is_credit_card_payment, paid_amount,
                                loan_interest_rate, loan_tenure_months, loan_emi, loan_start_date, loan_end_date, loan_lender_bank,
                                is_reinvestment, is_self)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, date, trans_type, category, subcategory, amount, description, account, 
          is_repaid, linked_id, is_credit_card_payment, paid_amount,
          loan_interest_rate, loan_tenure_months, loan_emi, loan_start_date, loan_end_date, loan_lender_bank,
          is_reinvestment, is_self))
    
    conn.commit()
    trans_id = cursor.lastrowid
    conn.close()
    return trans_id

def get_transactions(user_id: int, start_date: str = None, end_date: str = None, 
                    trans_type: str = None, category: str = None) -> pd.DataFrame:
    """Get transactions for a user with optional filters"""
    conn = get_connection()
    
    query = 'SELECT * FROM transactions WHERE user_id = ?'
    params = [user_id]
    
    if start_date:
        query += ' AND date >= ?'
        params.append(start_date)
    
    if end_date:
        query += ' AND date <= ?'
        params.append(end_date)
    
    if trans_type:
        query += ' AND type = ?'
        params.append(trans_type)
    
    if category:
        query += ' AND category = ?'
        params.append(category)
    
    query += ' ORDER BY date DESC, id DESC'
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df

def update_transaction(user_id: int, trans_id: int, date: str = None, trans_type: str = None, 
                      category: str = None, amount: float = None, 
                      subcategory: str = None, description: str = None, account: str = None,
                      is_credit_card_payment: int = None, paid_amount: float = None,
                      loan_interest_rate: float = None, loan_tenure_months: int = None, 
                      loan_emi: float = None, loan_start_date: str = None, 
                      loan_end_date: str = None, loan_lender_bank: str = None,
                      is_reinvestment: int = None, is_self: int = None):
    """Update an existing transaction for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verify ownership
    cursor.execute("SELECT id FROM transactions WHERE id = ? AND user_id = ?", (trans_id, user_id))
    if not cursor.fetchone():
        conn.close()
        return False
    
    updates = []
    params = []
    
    if date is not None:
        updates.append('date = ?')
        params.append(date)
    if trans_type is not None:
        updates.append('type = ?')
        params.append(trans_type)
    if category is not None:
        updates.append('category = ?')
        params.append(category)
    if subcategory is not None:
        updates.append('subcategory = ?')
        params.append(subcategory)
    if amount is not None:
        updates.append('amount = ?')
        params.append(amount)
    if description is not None:
        updates.append('description = ?')
        params.append(description)
    if account is not None:
        updates.append('account = ?')
        params.append(account)
    if is_credit_card_payment is not None:
        updates.append('is_credit_card_payment = ?')
        params.append(is_credit_card_payment)
    if paid_amount is not None:
        updates.append('paid_amount = ?')
        params.append(paid_amount)
    if loan_interest_rate is not None:
        updates.append('loan_interest_rate = ?')
        params.append(loan_interest_rate)
    if loan_tenure_months is not None:
        updates.append('loan_tenure_months = ?')
        params.append(loan_tenure_months)
    if loan_emi is not None:
        updates.append('loan_emi = ?')
        params.append(loan_emi)
    if loan_start_date is not None:
        updates.append('loan_start_date = ?')
        params.append(loan_start_date)
    if loan_end_date is not None:
        updates.append('loan_end_date = ?')
        params.append(loan_end_date)
    if loan_lender_bank is not None:
        updates.append('loan_lender_bank = ?')
        params.append(loan_lender_bank)
    if is_reinvestment is not None:
        updates.append('is_reinvestment = ?')
        params.append(is_reinvestment)
    if is_self is not None:
        updates.append('is_self = ?')
        params.append(is_self)
    
    if updates:
        params.append(trans_id)
        # user_id check is redundant due to initial check but good for safety
        params.append(user_id) 
        query = f"UPDATE transactions SET {', '.join(updates)} WHERE id = ? AND user_id = ?"
        cursor.execute(query, params)
        conn.commit()
    
    conn.close()
    return True

def delete_transaction(user_id: int, trans_id: int):
    """Delete a transaction for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions WHERE id = ? AND user_id = ?', (trans_id, user_id))
    conn.commit()
    conn.commit()
    conn.close()

def delete_transaction_by_link(user_id: int, linked_id: int):
    """Delete a transaction that is linked to another id"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions WHERE linked_id = ? AND user_id = ?', (linked_id, user_id))
    conn.commit()
    conn.close()

# ========== CATEGORY OPERATIONS ==========

def get_categories(user_id: int, cat_type: str = None) -> pd.DataFrame:
    """Get categories for a user, optionally filtered by type"""
    conn = get_connection()
    
    query = 'SELECT * FROM categories WHERE user_id = ? AND is_active = 1'
    params = [user_id]
    
    if cat_type:
        query += ' AND type = ?'
        params.append(cat_type)
        
    query += ' ORDER BY type, name'
    
    df = pd.read_sql_query(query, conn, params=params)
    
    conn.close()
    return df

def add_category(user_id: int, name: str, cat_type: str, is_loan: int = 0):
    """Add a new category for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check for duplicates for this user
        cursor.execute("SELECT id, is_active FROM categories WHERE user_id = ? AND name = ? AND type = ?", (user_id, name, cat_type))
        existing = cursor.fetchone()
        
        if existing:
            cat_id, is_active = existing
            if is_active == 1:
                conn.close()
                return None
            else:
                # Reactivate soft-deleted category
                cursor.execute("UPDATE categories SET is_active = 1 WHERE id = ?", (cat_id,))
                conn.commit()
                conn.close()
                return cat_id
            
        cursor.execute('INSERT INTO categories (user_id, name, type, is_loan) VALUES (?, ?, ?, ?)', (user_id, name, cat_type, is_loan))
        conn.commit()
        cat_id = cursor.lastrowid
        conn.close()
        return cat_id
    except sqlite3.IntegrityError as e:
        print(f"DEBUG: add_category error: {e}")
        conn.close()
        return None

def update_category(user_id: int, cat_id: int, name: str, cat_type: str, is_loan: int = 0):
    """Update a category for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('UPDATE categories SET name = ?, type = ?, is_loan = ? WHERE id = ? AND user_id = ?', (name, cat_type, is_loan, cat_id, user_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def delete_category(user_id: int, cat_id: int):
    """Soft delete a category for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE categories SET is_active = 0 WHERE id = ? AND user_id = ?', (cat_id, user_id))
    conn.commit()
    conn.close()

# ========== RECURRING ITEMS OPERATIONS ==========

def add_recurring_item(user_id: int, name: str, trans_type: str, category: str, amount: float, is_active: int = 1):
    """Add a new recurring item"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO recurring_items (user_id, name, type, category, amount, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, name, trans_type, category, amount, is_active))
    
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return item_id

def get_recurring_items(user_id: int) -> pd.DataFrame:
    """Get all recurring items for a user"""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM recurring_items WHERE user_id = ? ORDER BY type, amount DESC", conn, params=[user_id])
    conn.close()
    return df

def update_recurring_item(item_id: int, user_id: int, name: str, trans_type: str, category: str, amount: float, is_active: int):
    """Update a recurring item"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE recurring_items 
        SET name = ?, type = ?, category = ?, amount = ?, is_active = ?
        WHERE id = ? AND user_id = ?
    ''', (name, trans_type, category, amount, is_active, item_id, user_id))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def delete_recurring_item(item_id: int, user_id: int):
    """Delete a recurring item"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM recurring_items WHERE id = ? AND user_id = ?", (item_id, user_id))
    conn.commit()
    conn.close()

# ========== SUMMARY & ANALYTICS ==========

def get_summary(user_id: int, start_date: str = None, end_date: str = None) -> Dict:
    """Get summary statistics for a user"""
    conn = get_connection()
    
    # Exclude Friends Debt and Credit Card marked Expenses from generic summary
    query = """
        SELECT type, SUM(amount) as total 
        FROM transactions 
        WHERE user_id = ? 
        AND NOT (type = 'Debt' AND category = 'Friends')
        AND NOT (type = 'Expense' AND is_credit_card_payment = 1)
        AND NOT (type = 'Subscriptions' AND is_credit_card_payment = 1)
        AND is_reinvestment = 0
    """
    params = [user_id]
    
    if start_date:
        query += ' AND date >= ?'
        params.append(start_date)
    
    if end_date:
        query += ' AND date <= ?'
        params.append(end_date)
    query += ' GROUP BY type'
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    summary = {
        'total_income': 0,
        'total_expense': 0,
        'total_investment': 0,
        'total_credit_card': 0,
        'total_debt': 0,
        'total_vehicle': 0,
        'total_banking': 0,
        'net_savings': 0
    }
    
    for _, row in df.iterrows():
        if row['type'] == 'Income':
            summary['total_income'] = row['total']
        elif row['type'] == 'Expense':
            summary['total_expense'] = row['total']
        elif row['type'] == 'Investment':
            summary['total_investment'] = row['total']
        elif row['type'] == 'Credit Card':
            summary['total_credit_card'] = row['total']
        elif row['type'] == 'Debt':
            summary['total_debt'] = row['total']
        elif row['type'] == 'Vehicle':
            summary['total_vehicle'] = row['total']
        elif row['type'] == 'Banking':
            summary['total_banking'] = row['total']
        elif row['type'] == 'Subscriptions':
            summary['total_subs'] = row['total']
    
    # Calculate Debt Repayments (Expenses that are EMI or Loan Repayments)
    # We define Repayments as Expenses with category='EMI', subcategory='Loan Repayment', or linked_id is not null
    # For now, let's query specifically for this
    query_repay = '''
        SELECT SUM(amount) as total 
        FROM transactions 
        WHERE user_id = ? 
        AND type = 'Expense' 
        AND (category = 'EMI' OR subcategory = 'Loan Repayment' OR linked_id IS NOT NULL)
    '''
    params_repay = [user_id]
    if start_date:
        query_repay += ' AND date >= ?'
        params_repay.append(start_date)
    if end_date:
        query_repay += ' AND date <= ?'
        params_repay.append(end_date)
        
    conn = get_connection()
    df_repay = pd.read_sql_query(query_repay, conn, params=params_repay)
    conn.close()
    
    total_repaid = df_repay['total'].iloc[0] if not df_repay.empty and pd.notnull(df_repay['total'].iloc[0]) else 0.0
    summary['total_debt_repayment'] = total_repaid

    # Calculate Vehicle expenses paid via Credit Card (to exclude from savings deduction)
    query_vehicle_cc = "SELECT SUM(amount) as total FROM transactions WHERE user_id = ? AND type = 'Vehicle' AND is_credit_card_payment = 1"
    params_vcc = [user_id]
    if start_date:
        query_vehicle_cc += ' AND date >= ?'
        params_vcc.append(start_date)
    if end_date:
        query_vehicle_cc += ' AND date <= ?'
        params_vcc.append(end_date)
        
    conn = get_connection()
    df_vcc = pd.read_sql_query(query_vehicle_cc, conn, params=params_vcc)
    conn.close()
    vehicle_cc = df_vcc['total'].iloc[0] if not df_vcc.empty and pd.notnull(df_vcc['total'].iloc[0]) else 0.0

    # Include Banking and OTT in expense calculation for net savings
    # FIX: Do NOT subtract total_debt (New Debt) from savings. Borrowing is not an expense.
    # Repayments are already in total_expense.
    # Updated: Investments are considered CASH OUTFLOWS (User wants 'Current Balance' logic), so we SUBTRACT them.
    # Updated: Deduct Vehicle expenses (Cash/Bank only) -> Total Vehicle - Vehicle CC
    summary['net_savings'] = summary['total_income'] - summary['total_expense'] - summary['total_banking'] - summary['total_investment'] - summary['total_credit_card'] - summary.get('total_subs', 0) - (summary['total_vehicle'] - vehicle_cc)
    
    return summary

def get_category_breakdown(user_id: int, trans_type: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """Get breakdown by category for a specific transaction type and user"""
    conn = get_connection()
    
    query = 'SELECT category, SUM(amount) as total FROM transactions WHERE user_id = ?'
    params = [user_id]
    
    if trans_type == 'Expense':
        # Aggregate all expense types, excluding CC payments for Vehicle/Subs
        query += """ AND (
            type IN ('Expense', 'Banking') 
            OR (type IN ('Vehicle', 'Subscriptions') AND is_credit_card_payment != 1)
        )"""
    else:
        query += ' AND type = ?'
        params.append(trans_type)
    
    if start_date:
        query += ' AND date >= ?'
        params.append(start_date)
    
    if end_date:
        query += ' AND date <= ?'
        params.append(end_date)
    
    query += ' GROUP BY category ORDER BY total DESC'
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df

def get_portfolio_status(user_id: int) -> dict:
    """Get overall portfolio status (Assets vs Liabilities) for a user"""
    conn = get_connection()
    
    # 1. Fetch Lifetime Totals for Cash Flow calc
    # Group by Type AND is_credit_card_payment to exclude CC expenses from Cash deduction
    query_totals = '''
        SELECT type, is_credit_card_payment, SUM(amount) as total 
        FROM transactions 
        WHERE user_id = ?
        GROUP BY type, is_credit_card_payment
    '''
    df_totals = pd.read_sql_query(query_totals, conn, params=[user_id])
    
    lifetime_income = 0
    lifetime_expense = 0
    lifetime_investment = 0
    lifetime_vehicle = 0
    lifetime_banking = 0
    lifetime_cc_payment = 0
    lifetime_subs = 0
    
    for _, row in df_totals.iterrows():
        t = row['type']
        amt = row['total']
        is_cc = row['is_credit_card_payment'] == 1
        
        if t == 'Income':
            lifetime_income += amt
        elif t == 'Expense':
            if not is_cc: lifetime_expense += amt
        elif t == 'Investment':
            lifetime_investment += amt
        elif t == 'Vehicle':
            if not is_cc: lifetime_vehicle += amt
        elif t == 'Banking':
            lifetime_banking += amt
        elif t == 'Credit Card':
            lifetime_cc_payment += amt # These are Bill Payments (Outflows)
        elif t == 'Subscriptions':
            if not is_cc: lifetime_subs += amt
            
    # Cash = Income - Outflows (Expense, Invest, Vehicle, Banking, CC_Payments, OTT)
    cash_balance = lifetime_income - lifetime_expense - lifetime_investment - lifetime_vehicle - lifetime_banking - lifetime_cc_payment - lifetime_subs
    
    # 2. Calculate Outstanding Liabilities
    query_loans = '''
        SELECT * FROM transactions 
        WHERE user_id = ? AND type = 'Debt' AND is_repaid = 0
    '''
    df_loans = pd.read_sql_query(query_loans, conn, params=[user_id])
    
    query_cats = "SELECT name, is_loan FROM categories WHERE user_id = ?"
    df_cats = pd.read_sql_query(query_cats, conn, params=[user_id])
    loan_cats = df_cats[df_cats['is_loan'] == 1]['name'].tolist() if 'is_loan' in df_cats.columns else []
    
    total_loan_liability = 0
    total_friends_liability = 0
    
    for _, row in df_loans.iterrows():
        paid = row['paid_amount'] if pd.notnull(row['paid_amount']) else 0
        
        if row['category'] in loan_cats:
            if row['loan_emi'] and row['loan_tenure_months']:
                total_payable = row['loan_emi'] * row['loan_tenure_months']
                outstanding = total_payable - paid
            else:
                outstanding = row['amount'] - paid
            total_loan_liability += outstanding
        else:
            outstanding = row['amount'] - paid
            total_friends_liability += outstanding
            
    conn.close()
    
    assets = {
        'Cash': cash_balance, # Allow negative to show overspending/unaccounted sources
        'Investments': lifetime_investment
    }
    
    liabilities = {
        'Loans': total_loan_liability,
        'Friends Debt': total_friends_liability
    }
    
    return {
        'assets': assets,
        'liabilities': liabilities,
        'net_worth': sum(assets.values()) - sum(liabilities.values())
    }

def get_monthly_trend(user_id: int, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """Get monthly trend data for a user"""
    conn = get_connection()
    
    query = '''
        SELECT month, mapped_type as type, SUM(amount) as total
        FROM (
            SELECT 
                strftime('%Y-%m', date) as month,
                CASE 
                    WHEN type IN ('Expense', 'Banking') THEN 'Expense'
                    WHEN (type IN ('Vehicle', 'Subscriptions') AND is_credit_card_payment != 1) THEN 'Expense'
                    ELSE type 
                END as mapped_type,
                amount
            FROM transactions
            WHERE user_id = ?
    '''
    params = [user_id]
    
    if start_date:
        query += ' AND date >= ?'
        params.append(start_date)
    
    if end_date:
        query += ' AND date <= ?'
        params.append(end_date)
    
    query += ') GROUP BY month, mapped_type ORDER BY month'
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df

def get_monthly_category_trend(user_id: int, trans_type: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """Get monthly trend data broken down by category for a user"""
    conn = get_connection()
    
    query = '''
        SELECT 
            strftime('%Y-%m', date) as month,
            category,
            SUM(amount) as total
        FROM transactions
        WHERE user_id = ? AND type = ?
    '''
    params = [user_id, trans_type]
    
    if start_date:
        query += ' AND date >= ?'
        params.append(start_date)
    
    if end_date:
        query += ' AND date <= ?'
        params.append(end_date)
    
    query += ' GROUP BY month, category ORDER BY month'
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df

def repay_debt(user_id: int, debt_id: int, repay_amount: float, account_name: str, date_str: str) -> bool:
    """Process a partial or full repayment of a debt"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Get Debt Details
    cursor.execute("SELECT amount, paid_amount, description FROM transactions WHERE id = ? AND user_id = ?", (debt_id, user_id))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return False
        
    total_amount, paid_so_far, desc = row
    
    # 2. Validate Amount
    remaining = total_amount - paid_so_far
    # Allow float precision tolerance
    if repay_amount <= 0 or repay_amount > (remaining + 0.1): 
        conn.close()
        return False
        
    # 3. Add Expense Transaction
    expense_desc = f"Repayment to {desc} (Part)" if repay_amount < (remaining - 0.1) else f"Repayment to {desc} (Final)"
    
    cursor.execute('''
        INSERT INTO transactions (user_id, date, type, category, subcategory, amount, description, account, linked_id)
        VALUES (?, ?, 'Expense', 'Friends Payment', 'Repayment', ?, ?, ?, ?)
    ''', (user_id, date_str, repay_amount, expense_desc, account_name, debt_id))
    
    # 4. Update Debt Transaction
    new_paid_amount = paid_so_far + repay_amount
    is_fully_repaid = 1 if new_paid_amount >= (total_amount - 0.1) else 0
    
    cursor.execute("UPDATE transactions SET paid_amount = ?, is_repaid = ? WHERE id = ?", 
                  (new_paid_amount, is_fully_repaid, debt_id))
    
    conn.commit()
    conn.close()
    return True

def toggle_transaction_repaid(user_id: int, trans_id: int):
    """Toggle the repaid status of a transaction"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT is_repaid FROM transactions WHERE id = ? AND user_id = ?", (trans_id, user_id))
    result = cursor.fetchone()
    
    if result:
        new_status = 1 if result['is_repaid'] == 0 else 0
        cursor.execute("UPDATE transactions SET is_repaid = ? WHERE id = ?", (new_status, trans_id))
        conn.commit()
        conn.close()
        return True
        
    conn.close()
    return False

def get_friends_debts(user_id: int) -> pd.DataFrame:
    """Get all Friends Debt transactions"""
    conn = get_connection()
    query = "SELECT * FROM transactions WHERE user_id = ? AND type = 'Debt' AND category = 'Friends' ORDER BY date DESC"
    df = pd.read_sql_query(query, conn, params=[user_id])
    conn.close()
    return df

def check_integrity() -> bool:
    """Check database integrity"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        conn.close()
        return result[0] == "ok"
    except:
        return False

def perform_backup() -> str:
    """Perform a safe backup of the database"""
    if not check_integrity():
        return "CRITICAL: Database integrity check failed. Backup aborted."
    
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"finance_backup_{timestamp}.db")
    
    try:
        shutil.copy2(DATABASE_NAME, backup_file)
        
        # Rotation Logic: Keep last 5
        backups = sorted([os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.endswith('.db')], key=os.path.getmtime)
        
        while len(backups) > 5:
            os.remove(backups[0])
            backups.pop(0)
            
        return "Backup successful"
    except Exception as e:
        return f"Backup failed: {str(e)}"
