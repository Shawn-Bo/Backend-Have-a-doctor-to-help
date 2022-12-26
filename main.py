from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin

from daos.query_dao import query_dao
from daos.register_dao import register_dao
from daos.login_dao import login_dao
from daos.me_dao import me_dao
from daos.doctor_dao import doctor_dao

server = Flask(__name__)
cors = CORS(server)


@server.route('/register', methods=['post'])
def register_new_user():
    username = request.json.get("username")
    password = request.json.get("password")
    print(username, password)
    if register_dao.user_already_exists(username):
        return {"code": "user_already_exists"}
    else:
        register_dao.add_user(username, password)
        return {"code": "success"}


@server.route('/login', methods=['post'])
def login_user():
    username = request.json.get("username")
    password = request.json.get("password")
    print(username, password)
    if login_dao.user_not_exists(username):
        return {"code": "user_not_exist"}
    elif login_dao.get_password_by_username(username) != password:
        return {"code": "wrong_password"}
    else:
        return {"code": "success"}


# 用户编辑部分
@server.route('/user/get', methods=['post'])
def user_get():
    username = request.json.get("username")
    print("获取数据：", username)
    if me_dao.user_not_exists(username):
        return {"code": "user_not_exist"}
    else:
        return me_dao.user_get(username)


@server.route('/user/edit_sex', methods=['post'])
def user_edit_sex():
    username = request.json.get("username")
    sex = request.json.get("sex")
    print("修改性别：", username, sex)
    if me_dao.user_not_exists(username):
        return {"code": "user_not_exist"}
    else:
        return me_dao.user_edit_sex(username, sex)


@server.route('/user/edit_phone', methods=['post'])
def user_edit_phone():
    username = request.json.get("username")
    phone = request.json.get("phone")
    if me_dao.user_not_exists(username):
        return {"code": "user_not_exist"}
    else:
        return me_dao.user_edit_phone(username, phone)


@server.route('/user/edit_birth', methods=['post'])
def user_edit_birth():
    username = request.json.get("username")
    birth = request.json.get("birth")
    print(username, birth)
    if me_dao.user_not_exists(username):
        return {"code": "user_not_exist"}
    else:
        return me_dao.user_edit_birthday(username, birth)


@server.route('/user/edit_region', methods=['post'])
def user_edit_region():
    username = request.json.get("username")
    region = request.json.get("region")
    print(username, region)
    if me_dao.user_not_exists(username):
        return {"code": "user_not_exist"}
    else:
        return me_dao.user_edit_region(username, region)


@server.route('/user/edit_info', methods=['post'])
def user_edit_info():
    username = request.json.get("username")
    info = request.json.get("info")
    print(username, info)
    if me_dao.user_not_exists(username):
        return {"code": "user_not_exist"}
    else:
        return me_dao.user_edit_info(username, info)


@server.route('/user/edit_avatar', methods=['post'])
def user_edit_avatar():
    username = request.json.get("username")
    avatar = request.json.get("avatar")
    print(username, avatar)
    if me_dao.user_not_exists(username):
        return {"code": "user_not_exist"}
    else:
        return me_dao.user_edit_avatar(username, avatar)


@server.route('/user/certified_as_a_doctor', methods=['post'])
def user_certified_as_a_doctor():
    username = request.json.get("username")
    real_name = request.json.get("real_name")
    career_year = request.json.get("career_year")
    hospital = request.json.get("hospital")
    post = request.json.get("post")
    good_at = request.json.get("good_at")
    wechat = request.json.get("wechat")
    if me_dao.user_not_exists(username):
        return {"code": "user_not_exist"}
    else:
        return me_dao.certified_as_a_doctor(username, real_name, career_year, hospital, post, good_at, wechat)


# query的维护部分
"""
/query/get_session

/query/go_session

/query/export_session

/query/get_export_session

/query/delete_export_session
"""


@server.route('/query/new_session', methods=['post'])
def query_new_session():
    username = request.json.get("username")
    return query_dao.query_new_session(username)


@server.route('/query/get_session', methods=['post'])
def query_get_session():
    username = request.json.get("username")
    session_id = request.json.get("session_id")
    return query_dao.query_get_session(username, session_id)


@server.route('/query/go_session', methods=['post'])
def query_go_session():
    username = request.json.get("username")
    session_id = request.json.get("session_id")
    query_message = request.json.get("query_message")
    return query_dao.query_go_session(username, session_id, query_message)


@server.route('/query/export_session', methods=['post'])
def query_export_session():
    username = request.json.get("username")
    session_id = request.json.get("session_id")
    return query_dao.query_export_session(username, session_id)


@server.route('/query/publish_session', methods=['post'])
def query_publish_session():
    username = request.json.get("username")
    session_id = request.json.get("session_id")
    return query_dao.query_publish_session(username, session_id)


@server.route('/query/get_exported_sessions', methods=['post'])
def get_export_sessions():
    username = request.json.get("username")
    return query_dao.query_get_exported_sessions(username)


@server.route('/query/get_public_sessions', methods=['post'])
def get_public_sessions():
    return query_dao.query_get_public_sessions()


@server.route('/query/delete_export_session', methods=['post'])
def delete_export_session():
    username = request.json.get("username")
    exported_session_id = request.json.get("exported_session_id")
    return query_dao.query_delete_export_session(username, exported_session_id)


@server.route('/doctor/get_doctors', methods=['post'])
def doctor_get_doctors():
    return doctor_dao.get_doctors()


server.run(port=8888, host="0.0.0.0")
