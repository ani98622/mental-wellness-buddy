import mysql.connector
from datetime import datetime

conn = mysql.connector.connect(
    host="34.136.193.138",
    user="nooh-mindmate",
    password="ABCabc123@#$",
    database="NoohMindmateDB"
)

def Add_Admin(user_id,pin):
    cursor = conn.cursor()
    sql_query = "SELECT * FROM administrators WHERE user_name = %s;"
    values = (user_id,)
    cursor.execute(sql_query, values)
    result = cursor.fetchone()
    if result:
        return False
    sql_query = "INSERT INTO administrators (user_name, pin) VALUES (%s, %s);"
    values = (user_id, pin)
    cursor.execute(sql_query, values)
    conn.commit()
    return True
    
def Admin_Login(user_id,pin):
    cursor = conn.cursor()
    sql_query = "SELECT 1 FROM administrators WHERE user_name = %s AND pin = %s;"
    values = (user_id, pin)
    cursor.execute(sql_query, values)
    result = cursor.fetchone()
    if result:
        return True
    return False

def Check_System(s_id):
    cursor = conn.cursor()
    sql_query = "SELECT 1 FROM systems WHERE s_id = %s;"
    values = (s_id,)
    cursor.execute(sql_query, values)
    result = cursor.fetchone()
    if result:
        return True
    return False

def Add_System(s_id):
    if Check_System(s_id):
        return False
    cursor = conn.cursor()
    sql_query = "INSERT INTO systems (s_id) VALUES (%s);"
    values = (s_id,)
    cursor.execute(sql_query, values)
    conn.commit() 
    return True

def Add_Chathistory(s_id,speaker,chat):
    if Check_System(s_id) and speaker in ["User","AI"]:
        cursor = conn.cursor()
        sql_query = "INSERT INTO chathistory (s_id,speaker,chat) VALUES (%s,%s,%s);"
        values = (s_id, speaker, chat)
        cursor.execute(sql_query, values)
        conn.commit() 
        return True
    return False

def Get_Chathistory(s_id, fromdate = 0, tilldate = 0):
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
    if results:
        return results
    else:
        return []

def Add_Data(s_id, summary = "", work_stress = "Unclear", work_discontent = "Unclear", anxiety = "Unclear", depression = "Unclear", compensation_frustration = "Unclear", suicidal_thoughts = "Unclear", workplace_bullying = "Unclear", toxic_work_environment = "Unclear", underappreciation = "Unclear", time_deprivation = "Unclear"):
    allowedresponse = ["Critical","Moderate","Unclear"]
    fields_to_check = [work_stress, work_discontent, anxiety, depression, compensation_frustration, suicidal_thoughts, workplace_bullying, toxic_work_environment, underappreciation, time_deprivation]
    if not Check_System(s_id) or any(field not in allowedresponse for field in fields_to_check):
        return False
    cursor = conn.cursor()
    sql_query = "INSERT INTO data_ (s_id,summary, work_stress, work_discontent, anxiety, depression, compensation_frustration, suicidal_thoughts, workplace_bullying, toxic_work_environment, underappreciation, time_deprivation) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    values = (s_id,summary, work_stress, work_discontent, anxiety, depression, compensation_frustration, suicidal_thoughts, workplace_bullying, toxic_work_environment, underappreciation, time_deprivation)
    cursor.execute(sql_query, values)
    conn.commit() 
    return True

def Get_Stats(fromdate = 0, tilldate = 0):
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
    if results:
        return results
    else:
        return []

def Get_ProblemSpecificSummary(problem, fromdate = 0, tilldate = 0):
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
    if results:
        return results
    else:
        return []

def Get_PersonalInfo(s_id):
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
    if result:
        return result
    return False

def UpdateOrAdd_PersonalInfo(s_id, info):
    if Get_PersonalInfo(s_id) != False:
        cursor = conn.cursor()
        sql_query = """
            UPDATE personal_info
            SET info = %s
            WHERE s_id = %s;
            """
        values = (info, s_id)
        cursor.execute(sql_query, values)
        conn.commit()
        return True
    if Check_System(s_id):
        ursor = conn.cursor()
        sql_query = "INSERT INTO personal_info (s_id, info) VALUES (%s, %s);"
        values = (s_id, info)
        cursor.execute(sql_query, values)
        conn.commit()
        return True
    return False