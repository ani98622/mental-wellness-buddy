import sqlite3
import hashlib  # For password hashing

def initialize_db():
    """
    Creates the 'users' table in the 'admin.db' database if it doesn't exist.
    """

    conn = sqlite3.connect('admin.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

initialize_db()

def add_user(username, password):
    """
    Adds a new user to the 'users' table with a hashed password.

    Args:
        username (str): The username of the new user.
        password (str): The password of the new user (in plain text).
    """

    conn = sqlite3.connect('admin.db')
    cursor = conn.cursor()

    # Hash the password for better security
    # hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

def validate_user(username, password):
    """
    Validates a user's credentials by checking the username and password hash.

    Args:
        username (str): The username to validate.
        password (str): The password to validate (in plain text).

    Returns:
        bool: True if the credentials are valid, False otherwise.
    """

    conn = sqlite3.connect('admin.db')
    cursor = conn.cursor()

    # Hash the entered password for comparison

    cursor.execute('SELECT * FROM users WHERE username=?', (username,))

    user = cursor.fetchone()

    conn.close()

    if user:
        return user
    else:
        return (0,'temp','passstemp')
    

    

def delete_user(username, password):
    """
    Deletes a user from the 'users' table based on username and password.

    Args:
        username (str): The username of the user to delete.
        password (str): The password of the user to delete (in plain text).
    """

    conn = sqlite3.connect('admin.db')
    cursor = conn.cursor()

    # Validate credentials before deletion (optional)
    if not validate_user(username, password):
        print("Invalid credentials. Deletion failed.")
        conn.close()
        return

    cursor.execute('DELETE FROM users WHERE username=? AND password=?', (username, password))
    conn.commit()
    conn.close()

# Example usage (commented out for security reasons)
# add_user('siva@agilisum.com', 'pass123')  # Don't store passwords in plain text
# add_user('bala@agilisum.com', 'pass124')  # Don't store passwords in plain text
# add_user('raj@agilisum.com', 'pass125')  # Don't store passwords in plain text
# add_user('sivas','pass126')
# add_user('balaa','pass127')
# add_user('rajb','pass128')

# validate_user('raj@agilisum.com', 'pass125')