import sqlite3

def initialize_db():
    """
    Creates the 'users','chathistory', 'data_','personal_info' table in the 'database.db' database if it doesn't exist.
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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chathistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            chat_text TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute(''' CREATE TABLE IF NOT EXISTS data_ (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        s_id TEXT NOT NULL,  
        summary TEXT, 
        work_stress TEXT CHECK(work_stress IN ('Critical', 'Moderate', 'Unclear')),
        work_discontent TEXT CHECK(work_discontent IN ('Critical', 'Moderate', 'Unclear')),
        anxiety TEXT CHECK(anxiety IN ('Critical', 'Moderate', 'Unclear')), 
        depression TEXT CHECK(depression IN ('Critical', 'Moderate', 'Unclear')),  
        compensation_frustration TEXT CHECK(compensation_frustration IN ('Critical', 'Moderate', 'Unclear')),  
        suicidal_thoughts TEXT CHECK(suicidal_thoughts IN ('Critical', 'Moderate', 'Unclear')),  
        workplace_bullying TEXT CHECK(workplace_bullying IN ('Critical', 'Moderate', 'Unclear')),  
        toxic_work_environment TEXT CHECK(toxic_work_environment IN ('Critical', 'Moderate', 'Unclear')),  
        underappreciation TEXT CHECK(underappreciation IN ('Critical', 'Moderate', 'Unclear')), 
        time_deprivation TEXT CHECK(time_deprivation IN ('Critical', 'Moderate', 'Unclear')), 
        time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP )'''
        )

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS personal_info (
        s_id TEXT PRIMARY KEY, 
        info TEXT NOT NULL  
    )''' )

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

def Add_Chathistory(s_id,speaker,chat):
    if Check_System(s_id) and speaker in ["User","AI"]:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        sql_query = "INSERT INTO chathistory (s_id,speaker,chat) VALUES (%s,%s,%s);"
        values = (s_id, speaker, chat)
        cursor.execute(sql_query, values)
        conn.commit() 
        conn.close()
        return True
    return False

def Get_Chathistory(s_id, fromdate = 0, tilldate = 0):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    if fromdate != 0:
        from_timestamp = datetime.strptime(fromdate, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
    if tilldate != 0:
        till_timestamp = datetime.strptime(tilldate, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
    if fromdate != 0 and tilldate != 0:
        sql_query = """
        SELECT speaker, chat
        FROM chathistory
        WHERE s_id = %s AND time_stamp BETWEEN %s AND %s;
        """
        values = (s_id, from_timestamp, till_timestamp)
        cursor.execute(sql_query, values)
        results = cursor.fetchall()
    elif fromdate == 0 and tilldate != 0:
        sql_query = """
        SELECT speaker, chat
        FROM chathistory
        WHERE s_id = %s AND time_stamp <= %s;
        """
        values = (s_id, till_timestamp)
        cursor.execute(sql_query, values)
        results = cursor.fetchall()
    elif fromdate != 0 and tilldate == 0:
        sql_query = """
        SELECT speaker, chat
        FROM chathistory
        WHERE s_id = %s AND time_stamp >= %s;
        """
        values = (s_id, from_timestamp)
        cursor.execute(sql_query, values)
        results = cursor.fetchall()
    else:
        sql_query = """
        SELECT speaker, chat
        FROM chathistory
        WHERE s_id = %s;
        """
        values = (s_id,)
        cursor.execute(sql_query, values)
        results = cursor.fetchall()
    conn.commit() 
    conn.close()
    if results:
        return results
    else:
        return []

def Add_Data(s_id, summary = "", work_stress = "Unclear", work_discontent = "Unclear", anxiety = "Unclear", depression = "Unclear", compensation_frustration = "Unclear", suicidal_thoughts = "Unclear", workplace_bullying = "Unclear", toxic_work_environment = "Unclear", underappreciation = "Unclear", time_deprivation = "Unclear"):
    conn = sqlite3.connect('database.db')
    allowedresponse = ["Critical","Moderate","Unclear"]
    fields_to_check = [work_stress, work_discontent, anxiety, depression, compensation_frustration, suicidal_thoughts, workplace_bullying, toxic_work_environment, underappreciation, time_deprivation]
    if not Check_System(s_id) or any(field not in allowedresponse for field in fields_to_check):
        return False
    cursor = conn.cursor()
    sql_query = "INSERT INTO data_ (s_id,summary, work_stress, work_discontent, anxiety, depression, compensation_frustration, suicidal_thoughts, workplace_bullying, toxic_work_environment, underappreciation, time_deprivation) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    values = (s_id,summary, work_stress, work_discontent, anxiety, depression, compensation_frustration, suicidal_thoughts, workplace_bullying, toxic_work_environment, underappreciation, time_deprivation)
    cursor.execute(sql_query, values)
    conn.commit() 
    conn.close()
    return True

def Get_Stats(fromdate = 0, tilldate = 0):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    columns = [
                'work_stress', 'work_discontent', 'anxiety', 'depression',
                'compensation_frustration', 'suicidal_thoughts', 'workplace_bullying',
                'toxic_work_environment', 'underappreciation', 'time_deprivation'
            ]
    result = {col: (0, 0, 0) for col in columns}
    if fromdate != 0:
        from_timestamp = datetime.strptime(fromdate, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
    if tilldate != 0:
        till_timestamp = datetime.strptime(tilldate, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
    if fromdate != 0 and tilldate != 0:
        for col in columns:
            sql_select = f"""
            SELECT s_id, {col}
            FROM data_
            WHERE time_stamp BETWEEN %s AND %s
            """
            cursor.execute(sql_select, (from_timestamp, till_timestamp))
            rows = cursor.fetchall()
            critical_s_ids = set()
            moderate_s_ids = set()
            unclear_s_ids = set()
            for s_id, value in rows:
                if value == 'Critical':
                    critical_s_ids.add(s_id)
                elif value == 'Moderate' :
                    moderate_s_ids.add(s_id)
                elif value == 'Unclear' :
                    unclear_s_ids.add(s_id)
            critical_count = len(critical_s_ids)
            moderate_count = len(moderate_s_ids - critical_s_ids)
            unclear_count = len(unclear_s_ids - critical_s_ids - moderate_s_ids) 
            result[col] = (critical_count, moderate_count, unclear_count)
    elif fromdate == 0 and tilldate != 0:
        for col in columns:
            sql_select = f"""
            SELECT s_id, {col}
            FROM data_
            WHERE time_stamp <= %s
            """
            cursor.execute(sql_select, (till_timestamp,))
            rows = cursor.fetchall()
            critical_s_ids = set()
            moderate_s_ids = set()
            unclear_s_ids = set()
            for s_id, value in rows:
                if value == 'Critical':
                    critical_s_ids.add(s_id)
                elif value == 'Moderate' :
                    moderate_s_ids.add(s_id)
                elif value == 'Unclear' :
                    unclear_s_ids.add(s_id)
            critical_count = len(critical_s_ids)
            moderate_count = len(moderate_s_ids - critical_s_ids)
            unclear_count = len(unclear_s_ids - critical_s_ids - moderate_s_ids) 
            result[col] = (critical_count, moderate_count, unclear_count)
    elif fromdate != 0 and tilldate == 0:
        for col in columns:
            sql_select = f"""
            SELECT s_id, {col}
            FROM data_
            WHERE time_stamp >= %s
            """
            cursor.execute(sql_select, (from_timestamp,))
            rows = cursor.fetchall()
            critical_s_ids = set()
            moderate_s_ids = set()
            unclear_s_ids = set()
            for s_id, value in rows:
                if value == 'Critical':
                    critical_s_ids.add(s_id)
                elif value == 'Moderate' :
                    moderate_s_ids.add(s_id)
                elif value == 'Unclear' : 
                    unclear_s_ids.add(s_id)
            critical_count = len(critical_s_ids)
            moderate_count = len(moderate_s_ids - critical_s_ids)
            unclear_count = len(unclear_s_ids - critical_s_ids - moderate_s_ids) 
            result[col] = (critical_count, moderate_count, unclear_count)
    else:
        for col in columns:
            sql_select = f"""
            SELECT s_id, {col}
            FROM data_
            """
            cursor.execute(sql_select, ())
            rows = cursor.fetchall()
            critical_s_ids = set()
            moderate_s_ids = set()
            unclear_s_ids = set()
            for s_id, value in rows:
                if value == 'Critical':
                    critical_s_ids.add(s_id)
                elif value == 'Moderate' :
                    moderate_s_ids.add(s_id)
                elif value == 'Unclear' : 
                    unclear_s_ids.add(s_id)
            critical_count = len(critical_s_ids)
            moderate_count = len(moderate_s_ids - critical_s_ids)
            unclear_count = len(unclear_s_ids - critical_s_ids - moderate_s_ids) 
            result[col] = (critical_count, moderate_count, unclear_count)
    conn.commit() 
    return result

def Get_UserSpecificSummary(s_id, fromdate = 0, tilldate = 0):
    cursor = conn.cursor()
    if fromdate != 0:
        from_timestamp = datetime.strptime(fromdate, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
    if tilldate != 0:
        till_timestamp = datetime.strptime(tilldate, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
    if fromdate != 0 and tilldate != 0:
        sql_query = """
        SELECT summary
        FROM data_
        WHERE s_id = %s AND time_stamp BETWEEN %s AND %s
        """
        values = (s_id, from_timestamp, till_timestamp)
        cursor.execute(sql_query, values)
        results = cursor.fetchall()
    elif fromdate == 0 and tilldate != 0:
        sql_query = """
        SELECT summary
        FROM data_
        WHERE s_id = %s AND time_stamp <= %s
        """
        values = (s_id, till_timestamp)
        cursor.execute(sql_query, values)
        results = cursor.fetchall()
    elif fromdate != 0 and tilldate == 0:
        sql_query = """
        SELECT summary
        FROM data_
        WHERE s_id = %s AND time_stamp >= %s
        """
        values = (s_id, from_timestamp)
        cursor.execute(sql_query, values)
        results = cursor.fetchall()
    else:
        sql_query = """
        SELECT summary
        FROM data_
        WHERE s_id = %s;
        """
        values = (s_id)
        cursor.execute(sql_query, values)
        results = cursor.fetchall()
    conn.commit() 
    conn.close()
    if results:
        return results
    else:
        return []

def Get_ProblemSpecificSummary(problem, fromdate = 0, tilldate = 0):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    if fromdate != 0:
        from_timestamp = datetime.strptime(fromdate, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
    if tilldate != 0:
        till_timestamp = datetime.strptime(tilldate, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
    if fromdate != 0 and tilldate != 0:
        sql_query = f"""
        SELECT summary 
        FROM data_ 
        WHERE {problem} != "Unclear" AND time_stamp BETWEEN %s AND %s
        """
    
        values = (s_id, from_timestamp, till_timestamp)
        cursor.execute(sql_query, values)
        results = cursor.fetchall()
    elif fromdate == 0 and tilldate != 0:
        sql_query = f"""
        SELECT summary
        FROM data_
        WHERE {problem} != "Unclear" AND time_stamp <= %s
        """
        values = (s_id, till_timestamp)
        cursor.execute(sql_query, values)
        results = cursor.fetchall()
    elif fromdate != 0 and tilldate == 0:
        sql_query = f"""
        SELECT summary
        FROM data_
        WHERE {problem} != "Unclear" AND time_stamp >= %s
        """
        values = (s_id, from_timestamp)
        cursor.execute(sql_query, values)
        results = cursor.fetchall()
    else:
        sql_query = f"""
        SELECT summary
        FROM data_
        WHERE {problem} != "Unclear";
        """
        values = (s_id)
        cursor.execute(sql_query, values)
        results = cursor.fetchall()
    conn.commit() 
    conn.close()
    if results:
        return results
    else:
        return []

def Get_PersonalInfo(s_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    sql_query = """
        SELECT info
        FROM personal_info
        WHERE s_id = %s;
        """
    values = (s_id)
    cursor.execute(sql_query, values)
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    if result:
        return result
    return False

def UpdateOrAdd_PersonalInfo(s_id, info):
    if Get_PersonalInfo(s_id) != False:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        sql_query = """
            UPDATE personal_info
            SET info = %s
            WHERE s_id = %s;
            """
        values = (info, s_id)
        cursor.execute(sql_query, values)
        conn.commit()
        conn.close()
        return True
    if Check_System(s_id):
        conn = sqlite3.connect('database.db')
        ursor = conn.cursor()
        sql_query = "INSERT INTO personal_info (s_id, info) VALUES (%s, %s);"
        values = (s_id, info)
        cursor.execute(sql_query, values)
        conn.commit()
        conn.close()
        return True
    return False