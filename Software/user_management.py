import sqlite3                              # 导入SQLite数据库
import bcrypt                               # 加密算法
from datetime import datetime

class UserManagement:
    """ 用户管理逻辑 """
    def __init__(self, db_path='users.db'):
        # 连接到数据库，如果不存在则创建
        self.conn = sqlite3.connect(db_path)
        self.create_user_table()
        self.current_user = None        # 用于保存当前登录的用户名

    def create_user_table(self):
        """ 创建用户表 """
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                last_login_time TIMESTAMP,
                login_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def hash_password(self, password):
        """ 使用 bcrypt 哈希密码 """
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return hashed_password.decode('utf-8')

    def authenticate(self, username, password):
        """ 用户认证 """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username=?', (username,))
        user = cursor.fetchone()
        if user:
            stored_password_hash = user[2]
            if bcrypt.checkpw(password.encode(), stored_password_hash.encode()):
                self.update_login_info(username)    # 更新最近登录时间和登录次数
                return True
        return False

    def register(self, username, password, age, gender):
        """ 用户注册 """
        hashed_password = self.hash_password(password)
        cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password_hash, age, gender) VALUES (?, ?, ?, ?)', (username, hashed_password, age, gender))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # 用户名重复
            return False

    def set_current_user(self, username):
        """ 设置当前用户 """
        self.current_user = username
        print(f"当前用户设置为：{self.current_user}")

    def get_current_user(self):
        """ 返回当前用户名 """
        return self.current_user

    def get_current_user_info(self):
        """ 获取当前用户的详细信息 """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username=?', (self.current_user,))
        user = cursor.fetchone()
        if user:
            user_info = {
                'id': user[0],
                'username': user[1],
                'password_hash': user[2],
                'age': user[3],
                'gender': user[4],
                'last_login_time':user[5],
                'login_count':user[6],
                'created_at': user[7]
            }
            return user_info
        return None

    def update_login_info(self, username):
        """ 更新最近登录时间和登录次数 """
        cursor = self.conn.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 更新最近登录时间和登录次数
        cursor.execute('UPDATE users SET last_login_time=?, login_count=login_count+1 WHERE username=?', (current_time, username))
        self.conn.commit()

    def close(self):
        """ 关闭数据库连接 """
        self.conn.close()