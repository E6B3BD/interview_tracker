# models.py
import pymysql
import bcrypt

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',          # ← 保持和你原来一致
    'database': 'interview_system',
    'charset': 'utf8mb4'
}

def get_db():
    return pymysql.connect(**DB_CONFIG)

# === 用户相关 ===
def get_user_by_username(username):
    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def verify_password(stored_hash, password):
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))

# === 公司相关 ===
def get_all_companies():
    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM companies ORDER BY id DESC")
    companies = cursor.fetchall()
    conn.close()
    return companies

def get_company_by_id(cid):
    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM companies WHERE id = %s", (cid,))
    company = cursor.fetchone()
    conn.close()
    return company

def add_company(name, city, nature, address, description):  # ← 参数改为 nature
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO companies (name, city, nature, address, description)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, city, nature, address, description))
        conn.commit()
        return True
    except Exception as e:
        print("❌ 添加公司失败:", str(e))
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_company(cid):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM companies WHERE id = %s", (cid,))
        conn.commit()
        return True
    finally:
        conn.close()

# === 面试记录 ===
def add_interview_record(user_id, company_id, question, answer):
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO interviews (user_id, company_id, question, answer)
            VALUES (%s, %s, %s, %s)
        """, (user_id, company_id, question, answer))
        conn.commit()
        return True
    except Exception as e:
        print("❌ 添加面试记录失败:", e)
        conn.rollback()
        return False
    finally:
        conn.close()

def get_interview_records_by_company(company_id):
    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT ir.*, u.username 
        FROM interviews ir 
        JOIN users u ON ir.user_id = u.id 
        WHERE ir.company_id = %s 
        ORDER BY ir.created_at DESC
    """, (company_id,))
    records = cursor.fetchall()
    conn.close()
    return records

def get_interview_records_by_user(user_id):
    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT ir.*, c.name AS company_name 
        FROM interviews ir 
        JOIN companies c ON ir.company_id = c.id 
        WHERE ir.user_id = %s 
        ORDER BY ir.created_at DESC
    """, (user_id,))
    records = cursor.fetchall()
    conn.close()
    return records

def delete_interview_record(record_id):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM interviews WHERE id = %s", (record_id,))
        conn.commit()
        return True
    finally:
        conn.close()