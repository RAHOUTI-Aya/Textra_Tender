import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, timedelta
import re
import secrets
import bcrypt

# Database path
DB_PATH = "textra_tender.db"

def is_valid_email(email):
    """Enhanced email validation with comprehensive regex pattern."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Basic format check
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    # Length checks
    if len(email) > 254:
        return False, "Email address too long"
    
    local_part, domain = email.rsplit('@', 1)
    if len(local_part) > 64:
        return False, "Email local part too long"
    
    # Domain validation
    if not re.match(r'^[a-zA-Z0-9.-]+$', domain):
        return False, "Invalid domain format"
    
    # Check for consecutive dots
    if '..' in email:
        return False, "Consecutive dots not allowed"
    
    # Check for leading/trailing dots in local part
    if local_part.startswith('.') or local_part.endswith('.'):
        return False, "Email cannot start or end with a dot"
    
    return True, "Valid email"

def validate_password_strength(password):
    """Comprehensive password strength validation."""
    errors = []
    
    # Length check
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if len(password) > 128:
        errors.append("Password must be less than 128 characters long")
    
    # Character type checks
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one number")
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>?]', password):
        errors.append("Password must contain at least one special character")
    
    # Check for common patterns
    common_patterns = [
        r'(.)\1{2,}',  # Repeated characters (3 or more)
        r'123456',     # Sequential numbers
        r'abcdef',     # Sequential letters
        r'qwerty',     # Keyboard patterns
        r'password',   # Common word
        r'admin',      # Common word
    ]
    
    for pattern in common_patterns:
        if re.search(pattern, password.lower()):
            errors.append("Password contains common patterns that make it weak")
            break
    
    # Check for username in password (if available)
    # This would be checked during registration/update
    
    if errors:
        return False, errors
    
    return True, ["Password meets all security requirements"]

def hash_password_secure(password):
    """Create a secure bcrypt hash of the password with salt."""
    # Generate a salt and hash the password
    salt = bcrypt.gensalt(rounds=12)  # 12 rounds is a good balance of security and performance
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password_secure(password, hashed):
    """Verify password against bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except:
        return False

def migrate_existing_passwords():
    """Migrate existing SHA-256 passwords to bcrypt (optional upgrade function)."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT username, password FROM users")
            users_to_migrate = cursor.fetchall()
            
            for username, old_hash in users_to_migrate:
                # Check if it's already bcrypt (bcrypt hashes start with $2b$)
                if not old_hash.startswith('$2b$'):
                    st.warning(f"User {username} needs to reset password for enhanced security")
                    # You could implement a forced password reset here
                    
        except sqlite3.Error as e:
            st.error(f"Migration error: {e}")
        finally:
            conn.close()

def register_user(username, password, role="user"):
    """Register a new user with enhanced validation."""
    conn = create_connection()
    if conn is not None:
        try:
            # Enhanced email validation
            email_valid, email_message = is_valid_email(username)
            if not email_valid:
                return False, f"Email validation failed: {email_message}"

            # Enhanced password validation
            password_valid, password_messages = validate_password_strength(password)
            if not password_valid:
                return False, f"Password validation failed: {'; '.join(password_messages)}"

            # Check if username contains password or vice versa
            if username.lower() in password.lower() or password.lower() in username.lower():
                return False, "Password cannot contain the email address or vice versa"

            # Check if username exists
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            if cursor.fetchone()[0] > 0:
                conn.close()
                return False, "Email address already registered"

            # Insert new user with secure password hash
            hashed_password = hash_password_secure(password)
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute(
                "INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
                (username, hashed_password, role, created_at)
            )
            conn.commit()
            conn.close()
            return True, "User registered successfully with enhanced security"
        except sqlite3.Error as e:
            conn.close()
            return False, f"Database error: {e}"
    return False, "Could not connect to database"

def authenticate(username, password):
    """Enhanced authentication with both old and new password formats."""
    conn = create_connection()
    if conn is not None:
        try:
            # Enhanced email validation during login
            email_valid, _ = is_valid_email(username)
            if not email_valid:
                return False, "Please enter a valid email address"

            cursor = conn.cursor()
            cursor.execute(
                "SELECT password FROM users WHERE username = ?", 
                (username,)
            )
            result = cursor.fetchone()
            
            if result:
                stored_hash = result[0]
                
                # Check if it's a bcrypt hash (new format)
                if stored_hash.startswith('$2b$'):
                    if verify_password_secure(password, stored_hash):
                        conn.close()
                        return True, "Authentication successful"
                else:
                    # Legacy SHA-256 hash - verify and potentially upgrade
                    if stored_hash == hashlib.sha256(password.encode()).hexdigest():
                        # Optionally upgrade to bcrypt
                        new_hash = hash_password_secure(password)
                        cursor.execute(
                            "UPDATE users SET password = ? WHERE username = ?",
                            (new_hash, username)
                        )
                        conn.commit()
                        conn.close()
                        return True, "Authentication successful (password upgraded)"
                        
            conn.close()
            return False, "Invalid email or password"
            
        except sqlite3.Error as e:
            conn.close()
            return False, f"Authentication error: {e}"
    return False, "Could not connect to database"

def initialize_app():
    """Initialize app state and session variables with enhanced security."""
    # Initialize session state variables for login management
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None
    if 'failed_attempts' not in st.session_state:
        st.session_state.failed_attempts = 0
    if 'last_failed_attempt' not in st.session_state:
        st.session_state.last_failed_attempt = None
    if 'account_locked' not in st.session_state:
        st.session_state.account_locked = False
    if 'lock_time' not in st.session_state:
        st.session_state.lock_time = None
    if 'show_register' not in st.session_state:
        st.session_state.show_register = False
    
    # Initialize the database if it doesn't exist
    initialize_database()

def is_account_locked():
    """Check if account is temporarily locked due to failed attempts."""
    if st.session_state.account_locked and st.session_state.lock_time:
        # Check if 15 minutes have passed since lock
        if datetime.now() - st.session_state.lock_time > timedelta(minutes=15):
            st.session_state.account_locked = False
            st.session_state.failed_attempts = 0
            st.session_state.lock_time = None
            return False
        return True
    return False

def auth_interface():
    """Main authentication interface that handles both login and registration."""
    
    # Check if account is locked
    if is_account_locked():
        remaining_time = 15 - int((datetime.now() - st.session_state.lock_time).total_seconds() / 60)
        st.error(f" Account temporarily locked. Try again in {remaining_time} minutes.")
        return

    # Toggle between login and register
    col1, col2 = st.columns(2)
    with col1:
        if st.button(" Login", type="primary" if not st.session_state.show_register else "secondary"):
            st.session_state.show_register = False
    with col2:
        if st.button(" Register", type="primary" if st.session_state.show_register else "secondary"):
            st.session_state.show_register = True
    
    st.divider()
    
    if st.session_state.show_register:
        register_form()
    else:
        login_form()

def login_form():
    """Enhanced login form with security features."""
    with st.form("login_form"):
        st.subheader(" Secure Login to Textra Tender")
        
        # Add security notice
        st.info(" For your security, please use your registered email address and strong password.")
        
        username = st.text_input("Email Address", placeholder="your.email@domain.com")
        password = st.text_input("Password", type="password")
        
        login_button = st.form_submit_button(" Login", type="primary")
        
        if login_button:
            if not username or not password:
                st.error("Please enter both email and password")
            else:
                # Enhanced email validation
                email_valid, email_message = is_valid_email(username)
                if not email_valid:
                    st.error(f"{email_message}")
                else:
                    # Attempt authentication
                    auth_result, auth_message = authenticate(username, password)
                    if auth_result:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.login_time = datetime.now()
                        st.session_state.failed_attempts = 0
                        st.session_state.account_locked = False
                        st.session_state.show_register = False
                        st.success(f" Welcome {username}!")
                        st.rerun()
                    else:
                        st.session_state.failed_attempts += 1
                        st.session_state.last_failed_attempt = datetime.now()
                        
                        # Progressive lockout
                        if st.session_state.failed_attempts >= 5:
                            st.session_state.account_locked = True
                            st.session_state.lock_time = datetime.now()
                            st.error(" Too many failed attempts. Account locked for 15 minutes.")
                        elif st.session_state.failed_attempts >= 3:
                            st.warning(f" {auth_message}. {5 - st.session_state.failed_attempts} attempts remaining before lockout.")
                        else:
                            st.error(f"{auth_message}. Attempts: {st.session_state.failed_attempts}/5")

def register_form():
    """Enhanced registration form with real-time validation."""
    with st.form("register_form"):
        st.subheader(" Create New Account")
        st.info(" Your account will be secured with industry-standard encryption.")
        
        new_username = st.text_input("Email Address", placeholder="your.email@domain.com")
        
        # Real-time email validation display
        if new_username:
            email_valid, email_message = is_valid_email(new_username)
            if email_valid:
                st.success(" Valid email format")
            else:
                st.error(f"{email_message}")
        
        new_password = st.text_input("Password", type="password", 
                                   help="Password must be at least 8 characters with uppercase, lowercase, numbers, and special characters")
        
        # Real-time password validation display
        if new_password:
            password_valid, password_messages = validate_password_strength(new_password)
            if password_valid:
                st.success("Strong password")
            else:
                for msg in password_messages:
                    st.error(f"{msg}")
        
        confirm_password = st.text_input("Confirm Password", type="password")
        
        # Password match validation
        if new_password and confirm_password:
            if new_password == confirm_password:
                st.success("Passwords match")
            else:
                st.error("Passwords do not match")

        register_button = st.form_submit_button(" Create Account", type="primary")

        if register_button:
            if not new_username or not new_password or not confirm_password:
                st.error("All fields are required")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                success, message = register_user(new_username, new_password)
                if success:
                    st.success(f" {message}")
                    st.info("Please switch to login tab to access your account")
                    st.balloons()  # Celebration effect
                    st.session_state.show_register = False  # Switch back to login
                    st.rerun()
                else:
                    st.error(f" {message}")

# Additional utility functions remain the same as in your original code
def create_connection():
    """Create a database connection to the SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
    return conn

def initialize_database():
    """Create tables if they don't exist and add default admin user"""
    conn = create_connection()
    if conn is not None:
        try:
            # Create users table
            conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            ''')
            
            # Check if admin exists, create if not
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin@textra.com'")
            if cursor.fetchone()[0] == 0:
                # Create admin with secure password
                admin_password = hash_password_secure("Admin123!@#")  # Strong default password
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn.execute(
                    "INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
                    ("admin@textra.com", admin_password, "admin", created_at)
                )
                st.info("Default admin created: admin@textra.com / Admin123!@#")
            conn.commit()
        except sqlite3.Error as e:
            st.error(f"Database error: {e}")
        finally:
            conn.close()
    else:
        st.error("Error: Cannot create the database connection.")

def get_user_role(username):
    """Get user role from database"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            if result:
                return result[0]
        except sqlite3.Error as e:
            st.error(f"Database error: {e}")
        finally:
            conn.close()
    return None

def logout():
    """Log out user and reset session state"""
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.login_time = None
    st.rerun()

def is_session_expired():
    """Check if the user session is expired (30 minutes of inactivity)"""
    if st.session_state.login_time:
        session_duration = datetime.now() - st.session_state.login_time
        if session_duration > timedelta(minutes=30):
            return True
    return False

def check_session():
    """Check if user is logged in and session is valid"""
    if st.session_state.logged_in:
        if is_session_expired():
            st.warning("Your session has expired. Please log in again.")
            logout()
            return False
        return True
    return False