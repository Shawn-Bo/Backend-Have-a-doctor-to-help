import datetime
import json
import time
import psycopg2


class DoctorDao(object):
    def __init__(self):
        self.conn = psycopg2.connect(host="localhost", port=5432, user="postgres", database="HaveADoctorToHelp",
                                     password="0")
        self.cursor = self.conn.cursor()

    def user_not_exists(self, username):
        self.cursor.execute(f"SELECT * FROM UsersLogin WHERE username='{username}';")
        result = self.cursor.fetchall()
        return len(result) == 0

    def get_doctors(self):
        # 返回所有认证医生的列表，其中还要包括医生头像等内容
        self.cursor.execute(f"SELECT * FROM Doctors;")
        doctor_list = self.cursor.fetchall()
        doctor_dict_list = []
        for doctor in doctor_list:
            username = doctor[0]
            self.cursor.execute(f"SELECT avatar FROM UsersInfo WHERE username='{username}';")
            avatar_url = self.cursor.fetchall()[0][0]
            doctor_dict = {
                "username": username,
                "real_name": doctor[1],
                "career_year": doctor[2],
                "hospital": doctor[3],
                "post": doctor[4],
                "good_at": doctor[5],
                "wechat": doctor[6],
                "avatar_url": avatar_url

            }
            doctor_dict_list.append(doctor_dict)
        return {
            "code": "success",
            "data": doctor_dict_list
        }


doctor_dao = DoctorDao()

if __name__ == "__main__":
    res = doctor_dao.get_doctors()
    print(res)
