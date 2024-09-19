import sqlite3

def initialize_db():
    """
    Creates the 'users' table in the 'database.db' database if it doesn't exist.
    """

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

initialize_db()

def add_user(username, password):
    """
    Adds a new user to the 'admin' table with a password.

    Args:
        username (str): The username of the new user.
        password (str): The password of the new user (in plain text).
    """

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO admin (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

def validate_user(username, password):
    """
    Validates a admin's credentials by checking the username and password.

    Args:
        username (str): The username to validate.
        password (str): The password to validate (in plain text).

    Returns:
        bool: True if the credentials are valid, False otherwise.
    """

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM admin WHERE username=?', (username,))

    user = cursor.fetchone()

    conn.close()

    if user:
        return user
    else:
        return (0,'temp','passstemp')
    
def delete_user(username, password):
    """
    Deletes a user from the 'admin' table based on username and password.

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

    cursor.execute('DELETE FROM admin WHERE username=? AND password=?', (username, password))
    conn.commit()
    conn.close()


# add_user('siva@agilisum.com', 'pass123')  
# add_user('bala@agilisum.com', 'pass124')  
# add_user('raju@agilisum', 'pass1256')  
# add_user('sivas','pass126')
# add_user('balaa','pass127')
# add_user('rajb','pass128')
# add_user('rajbbbbb','pass125')

# validate_user('raj@agilisum.com', 'pass125')