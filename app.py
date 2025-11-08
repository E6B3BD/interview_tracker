# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import *  # ← 导入上面的 models.py
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    companies = get_all_companies()
    return render_template('index.html', companies=companies)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        if user and verify_password(user["password"], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        confirm = request.form['confirm_password']
        if not username or not password:
            flash('用户名和密码不能为空！')
        elif password != confirm:
            flash('两次密码不一致！')
        elif len(password) < 6:
            flash('密码至少6位！')
        elif get_user_by_username(username):
            flash('用户名已存在！')
        else:
            import bcrypt
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            conn = get_db()
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                              (username, hashed, 'user'))
                conn.commit()
                flash('注册成功！请登录。')
                return redirect(url_for('login'))
            except Exception as e:
                conn.rollback()
                flash(f'注册失败：{str(e)}')
            finally:
                conn.close()
    return render_template('register.html')

# ====== 公司与面试 ======
@app.route('/company/<int:cid>')
def company_detail(cid):
    company = get_company_by_id(cid)
    if not company:
        return "公司不存在", 404
    records = get_interview_records_by_company(cid)

    # 提取所有参与用户（去重）
    participants = list({r['username'] for r in records})

    # 按轮次分组
    from collections import defaultdict
    grouped = defaultdict(list)
    for r in records:
        # 问题格式: "一面: 介绍一下你自己"
        if ':' in r['question']:
            round_name, q = r['question'].split(':', 1)
            grouped[round_name.strip()].append({
                'question': q.strip(),
                'answer': r.get('answer') or '（未回答）',
                'username': r['username'],
                'created_at': r['created_at']
            })
        else:
            grouped['其他'].append(r)

    return render_template('company_detail.html',
                         company=company,
                         participants=participants,
                         grouped_records=grouped)

@app.route('/interview/add/<int:cid>', methods=['GET', 'POST'])
def add_interview(cid):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        round_name = request.form['round']
        questions = request.form.getlist('questions[]')
        answers = request.form.getlist('answers[]')
        success = True
        for q, a in zip(questions, answers):
            if q.strip():
                full_q = f"{round_name}: {q.strip()}"
                if not add_interview_record(session['user_id'], cid, full_q, a.strip()):
                    success = False
        flash('面试记录已保存' if success else '部分记录保存失败')
        return redirect(url_for('company_detail', cid=cid))
    company = get_company_by_id(cid)
    return render_template('add_interview.html', company=company)


# ====== 添加公司（所有用户可操作） ======
@app.route('/add_company', methods=['GET', 'POST'])
def add_company_route():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name'].strip()
        city = request.form['city'].strip()
        nature = request.form['nature'].strip()  # ← 关键：用 nature
        address = request.form['address'].strip()
        desc = request.form['description'].strip()
        if not name:
            flash('公司名称不能为空')
        elif add_company(name, city, nature, address, desc):
            flash('公司添加成功！')
            return redirect(url_for('index'))
        else:
            flash('添加失败，请重试')
    return render_template('add_company.html')

# ====== 删除（仅 root） ======
@app.route('/delete/company/<int:cid>')
def delete_company_route(cid):
    if session.get('role') != 'root':
        return "权限不足", 403
    delete_company(cid)
    flash('公司已删除')
    return redirect(url_for('index'))

@app.route('/delete/record/<int:rid>')
def delete_record(rid):
    if session.get('role') != 'root':
        return "权限不足", 403
    delete_interview_record(rid)
    flash('面试记录已删除')
    return redirect(request.referrer or url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)