import psycopg2


class RegisterDao(object):
    def __init__(self):
        self.conn = psycopg2.connect(host="localhost", port=5432, user="postgres", database="HaveADoctorToHelp",
                                     password="0")
        self.cursor = self.conn.cursor()

    def user_already_exists(self, username):
        self.cursor.execute(f"SELECT * FROM UsersLogin WHERE username='{username}';")
        result = self.cursor.fetchall()
        return len(result) > 0

    def add_user(self, username, password):
        # 确定id
        # 添加登录功能
        self.cursor.execute(f"INSERT INTO UsersLogin VALUES ('{username}', '{password}');")
        # 添加个人信息功能
        self.cursor.execute(f"INSERT INTO UsersInfo(username) VALUES ('{username}');")
        self.conn.commit()


register_dao = RegisterDao()

if __name__ == "__main__":
    print(register_dao.user_already_exists("fanvane"))
    print(register_dao.add_user("fxb", "0"))
