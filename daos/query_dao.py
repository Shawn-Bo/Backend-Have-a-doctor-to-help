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
        session_json = self.cursor.fetchall()
        print(session_json)
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
                f"UPDATE GoingSessions SET session_json = '{json.dumps(response_session_json, ensure_ascii=False)}' WHERE session_id = '{session_id}';")
            self.conn.commit()
            return {"code": "success"}

    def query_go_exported_session(self, username, session_id, query_message):
        print(username, session_id, query_message)
        if self.user_not_exists(username):
            return {"code": "user_not_exist"}
        else:
            # 先为query_message赋予时间
            message_time = str(datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M"))
            # 再搜索已有对话
            self.cursor.execute(f"SELECT session_json FROM ExportedSessions WHERE session_id='{session_id}'")
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
            # 这部分对话不用拿去做预测了
            # 保存询问到数据库
            self.cursor.execute(
                f"UPDATE ExportedSessions SET session_json = '{json.dumps(session_json, ensure_ascii=False)}' WHERE "
                f"session_id = '{session_id}';")
            self.conn.commit()
            return {"code": "success"}

    def query_export_session(self, username, session_id):
        print("导出会话：", username, session_id)
        if self.user_not_exists(username):
            return {"code": "user_not_exist"}
        else:  # 用户存在，合法什么的
            # 1. 这段代码将用户的当前session导出来
            # 1.1 查询用户目前的session，通过session_id
            self.cursor.execute(f"SELECT session_json FROM GoingSessions WHERE session_id='{session_id}'")
            session_json = self.cursor.fetchall()
            session_json = session_json[0][0]  # 直接就是个字符串，拿出来又放回去了
            # GoingSessions(username TEXT, session_id TEXT, session_json TEXT);
            # 1.2 将用户的会话内容保存至ExportedSessions中
            self.cursor.execute(f"INSERT INTO ExportedSessions VALUES('{username}','{session_id}', '{session_json}');")
            self.conn.commit()
            print("导出成功了")
            return {"code": "success"}

    def query_publish_session(self, username, session_id):
        print("发布会话：", username, session_id)
        if self.user_not_exists(username):
            return {"code": "user_not_exist"}
        else:  # 用户存在，合法什么的
            # 1. 这段代码将用户的当前session发布出来
            # 1.1 查询用户目前的session，通过session_id
            self.cursor.execute(f"SELECT session_json FROM ExportedSessions WHERE session_id='{session_id}'")
            session_json = self.cursor.fetchall()
            session_json = session_json[0][0]  # 直接就是个字符串，拿出来又放回去了
            # ExportedSessions(username TEXT, session_id TEXT, session_json TEXT);
            # 1.2 确保会话之前没有公开过
            self.cursor.execute(f"SELECT session_json FROM PublicSessions WHERE session_id='{session_id}'")
            if len(self.cursor.fetchall()) > 0:
                return {"code": "session_already_published"}
            # 1.3 将用户的会话内容保存至ExportedSessions中
            self.cursor.execute(f"INSERT INTO PublicSessions VALUES('{username}','{session_id}', '{session_json}');")
            self.conn.commit()
            print("发布成功了")
            return {"code": "success"}

    def query_mark_publish_session(self, username, session_id):
        print("收藏问答：", username, session_id)
        if self.user_not_exists(username):
            print(username, "不存在！")
            return {"code": "user_not_exist"}
        else:  # 用户存在，合法什么的
            # 1. 这段代码将用户的当前session发布出来
            # 1.1 查询用户目前的session，通过session_id
            self.cursor.execute(f"SELECT session_json FROM PublicSessions WHERE session_id='{session_id}'")
            session_json = self.cursor.fetchall()
            session_json = session_json[0][0]  # 直接就是个字符串，拿出来又放回去了
            # PublicSessions(username TEXT, session_id TEXT, session_json TEXT);
            # 1.2 确保会话之前没有收藏过
            self.cursor.execute(f"SELECT session_json FROM ExportedSessions WHERE session_id='{session_id}' AND "
                                f"username='{username}'")
            if len(self.cursor.fetchall()) > 0:
                print("session_already_marked_or_from_yourself")
                return {"code": "session_already_marked_or_from_yourself"}
            # 1.3 将用户的会话内容保存至ExportedSessions中
            self.cursor.execute(f"INSERT INTO ExportedSessions VALUES('{username}','{session_id}', '{session_json}');")
            self.conn.commit()
            print("收藏成功了")
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
            }, ensure_ascii=False)
            # 删除用户已有的所有会话！
            self.cursor.execute(f"DELETE FROM GoingSessions WHERE username = '{username}';")
            self.cursor.execute(f"INSERT INTO GoingSessions VALUES('{username}','{session_id}', '{session_json}');")
        self.conn.commit()
        print("新建会话完毕")
        return {"code": "success", "session_id": session_id}

    def query_get_exported_session(self, session_id: str):
        self.cursor.execute(f"SELECT session_json FROM ExportedSessions WHERE session_id = '{session_id}';")
        session_json = self.cursor.fetchall()
        self.conn.commit()
        return {"code": "success", "session_json": session_json}

    def query_delete_export_session(self, username, exported_session_id: str):
        if self.user_not_exists(username):
            return {"code": "user_not_exist"}
        else:  # 用户存在，性别合法什么的
            self.cursor.execute(
                f"DELETE FROM ExportedSessions WHERE username = '{username}' AND session_id = '{exported_session_id}';")
            self.conn.commit()
            return {"code": "success"}

    def query_get_exported_sessions(self, username: str):
        if self.user_not_exists(username):
            return {"code": "user_not_exist"}
        else:  # 用户存在什么的
            # 1. 查表并返回即可
            self.cursor.execute(f"SELECT * FROM ExportedSessions WHERE username = '{username}';")
            res = self.cursor.fetchall()
            session_list = [json.loads(row[2]) for row in res]
            self.conn.commit()
            return {"code": "success", "session_list": session_list}

    def query_get_public_sessions(self):
        # 1. 查表并返回即可
        self.cursor.execute(f"SELECT * FROM PublicSessions;")
        res = self.cursor.fetchall()
        session_list = []
        for row in res:
            username = row[0]
            self.cursor.execute(f"SELECT avatar FROM UsersInfo WHERE username = '{username}';")
            avatar = self.cursor.fetchall()[0][0]
            session_list.append({
                "avatar": avatar,
                "username": row[0],
                "start_time": row[1],
                "session_detail": json.loads(row[2])
            })

        return {"code": "success", "session_list": session_list}

    def update_doctor_inquery(self, username: str, session_id: str, status: str):
        # 1. 确保条目存在，否则创建条目
        self.cursor.execute(f"SELECT * FROM InquerySessions "
                            f"WHERE username='{username}' AND session_id='{session_id}';")
        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute(
                f"INSERT INTO InquerySessions "
                f"VALUES ('{username}', '{session_id}', '{status}');")
        else:
            # 已有条目，则是更新表单
            self.cursor.execute(
                f"UPDATE InquerySessions SET status='{session_id}' "
                f"WHERE username='{username}' AND session_id='{status}';")
        return {"code": "success"}


query_dao = QueryDao()

if __name__ == "__main__":
    pass
