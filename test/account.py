import bcrypt
# 原始密码
password = "password_123456".encode('utf-8')
# 生成盐并哈希密码
salt = bcrypt.gensalt()
hashed_password = bcrypt.hashpw(password, salt)
# 打印出哈希后的密码，用于插入数据库
print(hashed_password.decode('utf-8'))