import datetime
import json
import time
import psycopg2

import kgqa.api


class QueryDao(object):
    def __init__(self):
        self.conn = lambda :psycopg2.connect(host="localhost", port=5432, user="postgres", database="HaveADoctorToHelp",
                                     password="0")

    def user_not_exists(self, username):
        conn = self.conn()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM UsersLogin WHERE username='{username}';")
        result = cursor.fetchall()
        return len(result) == 0

    def query_get_session(self, username, session_id):

        conn = self.conn()
        cursor = conn.cursor()
        cursor.execute(f"SELECT session_json FROM GoingSessions WHERE session_id='{session_id}'")
        session_json = cursor.fetchall()
        print(session_json)
        return {"code": "success", "session": session_json}

    def query_go_session(self, username, session_id, query_message):
        conn = self.conn()
        cursor = conn.cursor()
        print(username, session_id, query_message)
        if self.user_not_exists(username):
            return {"code": "user_not_exist"}
        else:
            # 先为query_message赋予时间
            message_time = str(datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M"))
            # 再搜索已有对话
            cursor.execute(f"SELECT session_json FROM GoingSessions WHERE session_id='{session_id}'")
            session_json = cursor.fetchall()
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
            cursor.execute(
                f"UPDATE GoingSessions SET session_json = '{json.dumps(response_session_json, ensure_ascii=False)}' WHERE session_id = '{session_id}';")
            conn.commit()
            conn.close()
            return {"code": "success"}

    def query_go_exported_session(self, username, session_id, query_message):
        conn = self.conn()
        cursor = conn.cursor()
        print(username, session_id, query_message)
        if self.user_not_exists(username):
            return {"code": "user_not_exist"}
        else:
            # 先为query_message赋予时间
            message_time = str(datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M"))
            # 再搜索已有对话
            cursor.execute(f"SELECT session_json FROM ExportedSessions WHERE session_id='{session_id}'")
            session_json = cursor.fetchall()
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
            cursor.execute(
                f"UPDATE ExportedSessions SET session_json = '{json.dumps(session_json, ensure_ascii=False)}' WHERE "
                f"session_id = '{session_id}';")
            conn.commit()
            conn.close()
            return {"code": "success"}

    def query_export_session(self, username, session_id):
        conn = self.conn()
        cursor = conn.cursor()
        print("导出会话：", username, session_id)
        if self.user_not_exists(username):
            return {"code": "user_not_exist"}
        else:  # 用户存在，合法什么的
            # 1. 这段代码将用户的当前session导出来
            # 1.1 查询用户目前的session，通过session_id
            cursor.execute(f"SELECT session_json FROM GoingSessions WHERE session_id='{session_id}'")
            session_json = cursor.fetchall()
            session_json = session_json[0][0]  # 直接就是个字符串，拿出来又放回去了
            # GoingSessions(username TEXT, session_id TEXT, session_json TEXT);
            # 1.2 将用户的会话内容保存至ExportedSessions中
            cursor.execute(f"INSERT INTO ExportedSessions VALUES('{username}','{session_id}', '{session_json}');")
            conn.commit()
            conn.close()
            print("导出成功了")
            return {"code": "success"}

    def query_publish_session(self, username, session_id):
        conn = self.conn()
        cursor = conn.cursor()
        print("发布会话：", username, session_id)
        if self.user_not_exists(username):
            return {"code": "user_not_exist"}
        else:  # 用户存在，合法什么的
            # 1. 这段代码将用户的当前session发布出来
            # 1.1 查询用户目前的session，通过session_id
            cursor.execute(f"SELECT session_json FROM ExportedSessions WHERE session_id='{session_id}'")
            session_json = cursor.fetchall()
            session_json = session_json[0][0]  # 直接就是个字符串，拿出来又放回去了
            # ExportedSessions(username TEXT, session_id TEXT, session_json TEXT);
            # 1.2 确保会话之前没有公开过
            cursor.execute(f"SELECT session_json FROM PublicSessions WHERE session_id='{session_id}'")
            if len(cursor.fetchall()) > 0:
                return {"code": "session_already_published"}
            # 1.3 将用户的会话内容保存至ExportedSessions中
            cursor.execute(f"INSERT INTO PublicSessions VALUES('{username}','{session_id}', '{session_json}');")
            conn.commit()
            conn.close()
            print("发布成功了")
            return {"code": "success"}

    def query_mark_publish_session(self, username, session_id):
        conn = self.conn()
        cursor = conn.cursor()
        print("收藏问答：", username, session_id)
        if self.user_not_exists(username):
            print(username, "不存在！")
            return {"code": "user_not_exist"}
        else:  # 用户存在，合法什么的
            # 1. 这段代码将用户的当前session发布出来
            # 1.1 查询用户目前的session，通过session_id
            cursor.execute(f"SELECT session_json FROM PublicSessions WHERE session_id='{session_id}'")
            session_json = cursor.fetchall()
            session_json = session_json[0][0]  # 直接就是个字符串，拿出来又放回去了
            # PublicSessions(username TEXT, session_id TEXT, session_json TEXT);
            # 1.2 确保会话之前没有收藏过
            cursor.execute(f"SELECT session_json FROM ExportedSessions WHERE session_id='{session_id}' AND "
                           f"username='{username}'")
            if len(cursor.fetchall()) > 0:
                print("session_already_marked_or_from_yourself")
                return {"code": "session_already_marked_or_from_yourself"}
            # 1.3 将用户的会话内容保存至ExportedSessions中
            cursor.execute(f"INSERT INTO ExportedSessions VALUES('{username}','{session_id}', '{session_json}');")
            conn.commit()
            conn.close()
            print("收藏成功了")
            return {"code": "success"}

    def query_new_session(self, username: str):
        conn = self.conn()
        cursor = conn.cursor()
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
            cursor.execute(f"DELETE FROM GoingSessions WHERE username = '{username}';")
            cursor.execute(f"INSERT INTO GoingSessions VALUES('{username}','{session_id}', '{session_json}');")
        conn.commit()
        conn.close()
        print("新建会话完毕")
        return {"code": "success", "session_id": session_id}

    def query_get_exported_session(self, session_id: str):
        conn = self.conn()
        cursor = conn.cursor()
        cursor.execute(f"SELECT session_json FROM ExportedSessions WHERE session_id = '{session_id}';")
        session_json = cursor.fetchall()
        return {"code": "success", "data": session_json}

    def query_delete_export_session(self, username, exported_session_id: str):
        conn = self.conn()
        cursor = conn.cursor()
        if self.user_not_exists(username):
            return {"code": "user_not_exist"}
        else:  # 用户存在，性别合法什么的
            cursor.execute(
                f"DELETE FROM ExportedSessions WHERE username = '{username}' AND session_id = '{exported_session_id}';")
            conn.commit()
            conn.close()
            return {"code": "success"}

    def query_get_exported_sessions(self, username: str):
        conn = self.conn()
        cursor = conn.cursor()
        if self.user_not_exists(username):
            return {"code": "user_not_exist"}
        else:  # 用户存在什么的
            # 1. 查表并返回即可
            cursor.execute(f"SELECT * FROM ExportedSessions WHERE username = '{username}';")
            res = cursor.fetchall()
            session_list = [json.loads(row[2]) for row in res]
            conn.commit()
            conn.close()
            return {"code": "success", "session_list": session_list}

    def query_get_public_sessions(self):
        conn = self.conn()
        cursor = conn.cursor()
        # 1. 查表并返回即可
        cursor.execute(f"SELECT * FROM PublicSessions;")
        res = cursor.fetchall()
        session_list = []
        for row in res:
            username = row[0]
            cursor.execute(f"SELECT avatar FROM UsersInfo WHERE username = '{username}';")
            avatar = cursor.fetchall()[0][0]
            session_list.append({
                "avatar": avatar,
                "username": row[0],
                "start_time": row[1],
                "session_detail": json.loads(row[2])
            })

        return {"code": "success", "session_list": session_list}

    def update_doctor_inquery(self, username: str, session_id: str, status: str):
        conn = self.conn()
        cursor = conn.cursor()
        print(username, session_id, session_id)
        # 1. 确保条目存在，否则创建条目
        cursor.execute(f"SELECT * FROM InquerySessions "
                       f"WHERE username='{username}' AND session_id='{session_id}';")
        records = cursor.fetchall()
        if len(records) == 0:
            cursor.execute(
                f"INSERT INTO InquerySessions "
                f"VALUES ('{username}', '{session_id}', '{status}');")
            conn.commit()
            conn.close()
        else:
            # 已有条目，则是更新表单
            cursor.execute(
                f"UPDATE InquerySessions SET status='{status}' "
                f"WHERE username='{username}' AND session_id='{session_id}';")
            conn.commit()
            conn.close()

        return {"code": "success"}

    def get_inquiry_not_viewed(self, username, detailed):
        conn = self.conn()
        cursor = conn.cursor()
        # 获取用户目前没有查看的条目
        cursor.execute(f"SELECT session_id FROM InquerySessions "
                       f"WHERE username='{username}' AND status='not_viewed';")
        if not detailed:  # 只返回用户名、session_list、状态
            return {"code": "success", "data": cursor.fetchall()}
        else:  # 根据session_list 返回所有的详情
            records = cursor.fetchall()
            session_ids = [record[0] for record in records]
            if len(session_ids) == 0:
                # 没有未读的消息
                return {"code": "success", "data": []}

            cursor.execute(f"SELECT * FROM ExportedSessions "
                           f"WHERE session_id in ({str(session_ids)[1:-1]});")
            session_list = cursor.fetchall()
            return {"code": "success", "data": [
                {
                    "username": session_item[0],
                    "session_id": session_item[1],
                    "session_messages": json.loads(session_item[2])
                }
                for session_item in session_list
            ]}


query_dao = QueryDao()

if __name__ == "__main__":
    pass
