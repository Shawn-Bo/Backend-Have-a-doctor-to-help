import psycopg2


class LoginDao(object):
    def __init__(self):
        self.conn = psycopg2.connect(host="localhost", port=5432, user="postgres", database="HaveADoctorToHelp",
                                     password="0")
        self.cursor = self.conn.cursor()

    def user_not_exists(self, username):
        self.cursor.execute(f"SELECT * FROM UsersLogin WHERE username='{username}';")
        result = self.cursor.fetchall()
        return len(result) == 0

    def get_password_by_username(self, username):
        self.cursor.execute(f"SELECT * FROM UsersLogin WHERE username='{username}';")

        return self.cursor.fetchall()[0][1]





login_dao = LoginDao()

if __name__ == "__main__":
    pass

