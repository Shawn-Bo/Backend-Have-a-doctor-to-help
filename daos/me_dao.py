import psycopg2


class MeDao(object):
    def __init__(self):
        self.conn = psycopg2.connect(host="localhost", port=5432, user="postgres", database="HaveADoctorToHelp",
                                     password="0")
        self.cursor = self.conn.cursor()

    def user_not_exists(self, username):
        self.cursor.execute(f"SELECT * FROM UsersLogin WHERE username='{username}';")
        result = self.cursor.fetchall()
        return len(result) == 0

    def user_get(self, username):
        self.cursor.execute(f"SELECT * FROM UsersInfo WHERE username='{username}';")
        result = self.cursor.fetchall()[0]
        return {
            "code": "success",
            "info": {
                "sex": result[1],
                "phone": result[4],
                "birthday": result[2],
                "region": result[3],
                "info": result[5],
                "avatar": result[6]
            }
        }

    def user_edit_sex(self, username, sex):
        if self.user_not_exists(username):
            return {"code": "user_not_exist"}
        else:  # 用户存在，性别合法什么的
            self.cursor.execute(f"UPDATE UsersInfo SET sex={sex} WHERE username='{username}';")
        self.conn.commit()
        return {"code": "success"}

    def user_edit_birthday(self, username, birthday: str):
        if self.user_not_exists(username):
            return {"code": "user_not_exist"}
        else:  # 用户存在，性别合法什么的
            self.cursor.execute(f"UPDATE UsersInfo SET birthday='{birthday}' WHERE username='{username}';")
        self.conn.commit()
        return {"code": "success"}

    def user_edit_region(self, username, region: str):
        if self.user_not_exists(username):
            return {"code": "user_not_exist"}
        else:  # 用户存在，性别合法什么的
            self.cursor.execute(f"UPDATE UsersInfo SET region='{region}' WHERE username='{username}';")
        self.conn.commit()
        return {"code": "success"}

    def user_edit_phone(self, username, phone: str):
        if self.user_not_exists(username):
            return {"code": "user_not_exist"}
        else:  # 用户存在，性别合法什么的
            self.cursor.execute(f"UPDATE UsersInfo SET phone='{phone}' WHERE username='{username}';")
        self.conn.commit()
        return {"code": "success"}

    def user_edit_info(self, username, info: str):
        if self.user_not_exists(username):
            return {"code": "user_not_exist"}
        else:  # 用户存在，性别合法什么的
            self.cursor.execute(f"UPDATE UsersInfo SET info='{info}' WHERE username='{username}';")
        self.conn.commit()
        return {"code": "success"}

    def user_edit_avatar(self, username, avatar: str):
        if self.user_not_exists(username):
            return {"code": "user_not_exist"}
        else:  # 用户存在，性别合法什么的
            self.cursor.execute(f"UPDATE UsersInfo SET avatar='{avatar}' WHERE username='{username}';")
        self.conn.commit()
        return {"code": "success"}


me_dao = MeDao()

if __name__ == "__main__":
    pass
