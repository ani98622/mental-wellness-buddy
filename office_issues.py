import sqlite3

def create_connection(db_file="database.db"):
    """Create a database connection to the SQLite database specified by db_file."""
    conn = sqlite3.connect(db_file)
    return conn

def create_table(conn):
    """Create the issues table if it doesn't already exist."""
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS issues (
        issue TEXT PRIMARY KEY,
        count INTEGER
    )
    ''')
    conn.commit()

def insert_initial_data(conn, issue_list):
    """Insert initial data into the issues table."""
    cursor = conn.cursor()
    for issue in issue_list:
        cursor.execute('''
        INSERT INTO issues (issue, count) VALUES (?, ?)
        ''', (issue, 6))  # Default count set to 6
    conn.commit()

def fetch_issue_data(conn):
    """Fetch data from the issues table."""
    cursor = conn.cursor()
    cursor.execute('SELECT issue, count FROM issues')
    data = cursor.fetchall()
    return data

def close_connection(conn):
    """Close the database connection."""
    conn.close()

# Usage example:
def main():
    issue_list = [
        "anger", "salary hike", "body shame", "suicidal tendency", "anxiety", 
        "depression", "sickness", "incompetency in office", "bad relationship"
    ]
    
    conn = create_connection()
    
    create_table(conn)
    insert_initial_data(conn, issue_list)
    issue_data = fetch_issue_data(conn)

    close_connection(conn)

if __name__ == "__main__":
    main()