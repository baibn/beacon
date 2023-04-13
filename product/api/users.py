from flask import request, jsonify
from product.users.models import User
from product.utils.tools import create_token, login_required, get_user
from product import db
from flask import Blueprint
from product.utils.tools import verify_token
from product.config import Config

login = Blueprint('login', __name__)
user = Blueprint('user', __name__)


@login.route('', methods=('POST',))
def user_login():
    re_user = request.get_json().get('userName')
    password = request.get_json().get("password")
    user_data = User.query.filter_by(user=re_user).first()
    if user_data and user_data.pwd == password:
        token = create_token(user_data.id)
        return jsonify({'message': 'OK', "code": 200,
                        'content': {'token': token}})
    else:
        return jsonify({"code": '401', "message": "用户名或密码错误"})


@user.route('/detail', methods=('POST',))
@login_required
def user_detail():
    token = request.headers["token"]
    user_id = verify_token(token)
    user_data = User.query.filter_by(id=user_id).first()
    if user_data is not None:
        return jsonify({"code": 200, "message": "查询成功",
                        "content": {"userId": user_data.id, "userName": user_data.user, "role": user_data.role}})
    else:
        return jsonify({"code": 200, "message": "超时或用户不存在"})


@user.route('/add', methods=('POST',))
@login_required
def user_add():
    token = request.headers["token"]
    if get_user(token) != "superman":
        return jsonify({"code": 401, "message": "只有超级用户可以新建用户！"})
    user = request.get_json().get('userName')
    password = request.get_json().get('password')
    role = request.get_json().get('role')
    if role == "admin":
        return jsonify({"code": 401, "message": "只能有一个超级用户！"})
    user_data = User.query.filter_by(user=user).first()
    if user_data:
        return jsonify({"code": 401, "message": "用户已存在！"})
    else:
        user = User(user=user, pwd=password, role=role)
        db.session.add(user)
        db.session.commit()
        return jsonify({"code": 200, "message": "添加成功"})


@user.route('/update', methods=('POST',))
@login_required
def user_update():
    user = request.get_json().get('userName')
    password = request.get_json().get('password')
    role = request.get_json().get('role')
    if role == "admin":
        return jsonify({"code": 401, "message": "只能有一个超级用户！"})
    user_data = User.query.filter_by(user=user).first()
    if user_data.pwd == password:
        return jsonify({"code": 401, "message": "修改密码不能与原密码一致！"})
    else:
        user_data.pwd = password
        user_data.role = role
        db.session.commit()
        return jsonify({"code": 200, "message": "密码修改成功"})


@user.route('/list', methods=('POST',))
@login_required
def user_list():
    user_list = []
    limit = int(request.get_json().get('limit'))
    if limit == '':
        return jsonify({"code": 200, "message": "参数非法！"})
    page = int(request.get_json().get('page'))
    if page == '':
        return jsonify({"code": 200, "message": "参数非法！"})
    if 'userName' not in request.get_json().keys():
        db_users = User.query.all()
        if len(db_users) != 0:
            for data in db_users:
                user = {"userId": data.id, "userName": data.user, "role": data.role}
                user_list.append(user)
            start = (page - 1) * limit
            end = page * limit if len(user_list) > page * limit else start + len(user_list)
            ret = user_list[start:end]
            return jsonify({"code": 200, "message": "查询成功", "totalCount": len(user_list), "contents": ret})
        else:
            return jsonify(
                {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})
    else:
        user_name = request.get_json().get('userNmae')
        db_users = User.query.filter(User.user.like('%{keyword}%'.format(keyword=user_name))).all()
        if len(db_users) != 0:
            for data in db_users:
                user = {"userId": data.id, "userName": data.user, "role": data.role}
                user_list.append(user)
            start = (page - 1) * limit
            end = page * limit if len(user_list) > page * limit else start + len(user_list)
            ret = user_list[start:end]
            return jsonify({"code": 200, "message": "查询成功", "totalCount": len(user_list), "contents": ret})
        else:
            return jsonify(
                {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})


@user.route('/delete', methods=('POST',))
@login_required
def user_delete():
    token = request.headers["token"]
    if get_user(token) != "superman":
        return jsonify({"code": 401, "message": "只有超级用户可以删除用户！"})
    user_id = request.get_json().get('userId')
    user_data = User.query.filter_by(id=user_id).first()
    if user_data is None:
        return jsonify({"code": 401, "message": "用户不存在！"})
    if user_data.user == 'superman':
        return jsonify({"code": 401, "message": "超级管理员账户不允许删除！"})
    else:
        db.session.delete(user_data)
        db.session.commit()
        return jsonify({"code": 200, "message": "OK"})


@user.route('/service_list', methods=('POST',))
@login_required
def user_server_list():
    service_list = []
    for sevice in Config.service_list:
        for key, value in sevice.items():
            key_value = {"serviceKey": key, "serviceValue": value}
            service_list.append(key_value)
    return jsonify(
        {"code": 200, "totalCount": len(service_list), "message": "查询成功!",
         "contents": service_list})
