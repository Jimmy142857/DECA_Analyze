import sqlite3                              # 导入SQLite数据库
import bcrypt                               # 加密算法


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
                password_hash TEXT NOT NULL
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
            return bcrypt.checkpw(password.encode(), stored_password_hash.encode())
        return False

    def register(self, username, password):
        """ 用户注册 """
        hashed_password = self.hash_password(password)
        cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, hashed_password))
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
        """ 返回当前用户 """
        return self.current_user

    def close(self):
        """ 关闭数据库连接 """
        self.conn.close()