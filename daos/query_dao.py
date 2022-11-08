import datetime
import json
import time
import psycopg2

import kgqa.api


class QueryDao(object):
    def __init__(self):
        self.conn = psycopg2.connect(host="localhost", port=5432, user="postgres", database="HaveADoctorToHelp",
                                     password="0")
        self.cursor = self.conn.cursor()

    def user_not_exists(self, username):
        self.cursor.execute(f"SELECT * FROM UsersLogin WHERE username='{username}';")
        result = self.cursor.fetchall()
        return len(result) == 0

    def query_get_session(self, username, session_id):
        self.cursor.execute(f"SELECT session_json FROM GoingSessions WHERE session_id='{session_id}'")
        session_json = self.cursor.fetchall()[0][0]
        return {"code": "success", "session": session_json}

    def query_go_session(self, username, session_id, query_message):
        print(username, session_id, query_message)
        if self.user_not_exists(username):
            return {"code": "user_not_exist"}
        else:
            # 先为query_message赋予时间
            message_time = str(datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M"))
            # 再搜索已有对话
            self.cursor.execute(f"SELECT session_json FROM GoingSessions WHERE session_id='{session_id}'")
            session_json = self.cursor.fetchall()
            session_json = json.loads(session_json[0][0])
            # 根据已有对话，插入新的对话
            session_json["session_messages"].append({
                "message_id": len(session_json['session_messages']),
                "message_sender": username,
                "message_time": message_time,
                "message_text": query_message["message_text"]
            })
            print("正在进行的对话", session_json)
            # 这部分对话拿去做预测
            response_session_json = kgqa.api.get_response(session_json)
            print("响应后的对话", response_session_json)
            # 保存对话到数据库
            self.cursor.execute(
                f"UPDATE GoingSessions SET session_json = '{json.dumps(response_session_json)}' WHERE session_id = '{session_id}';")
            self.conn.commit()
            return {"code": "success"}

    def query_export_session(self, username, sex):
        if self.user_not_exists(username):
            return {"code": "user_not_exist"}
        else:  # 用户存在，合法什么的
            self.cursor.execute(f"UPDATE UsersInfo SET sex={sex} WHERE username='{username}';")
        self.conn.commit()
        return {"code": "success"}

    def query_new_session(self, username: str):
        if self.user_not_exists(username):
            return {"code": "user_not_exist"}
        else:  # 用户存在，创建新的会话

            session_id = username + str(time.time_ns())
            session_start_time = str(datetime.datetime.now())
            session_json = json.dumps({
                "session_id": session_id,
                "session_start_time": session_start_time,
                "session_messages": []
            })
            # 删除用户已有的所有会话！
            self.cursor.execute(f"DELETE FROM GoingSessions WHERE username = '{username}';")
            self.cursor.execute(f"INSERT INTO GoingSessions VALUES('{username}','{session_id}', '{session_json}');")
        self.conn.commit()
        print("新建会话完毕")
        return {"code": "success", "session_id": session_id}

    def query_get_export_session(self, username, birthday: str):
        if self.user_not_exists(username):
            return {"code": "user_not_exist"}
        else:  # 用户存在，性别合法什么的
            self.cursor.execute(f"UPDATE UsersInfo SET birthday='{birthday}' WHERE username='{username}';")
        self.conn.commit()
        return {"code": "success"}

    def query_delete_export_session(self, username, region: str):
        if self.user_not_exists(username):
            return {"code": "user_not_exist"}
        else:  # 用户存在，性别合法什么的
            self.cursor.execute(f"UPDATE UsersInfo SET region='{region}' WHERE username='{username}';")
        self.conn.commit()
        return {"code": "success"}


query_dao = QueryDao()

if __name__ == "__main__":
    pass
