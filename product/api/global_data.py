from product.global_data.models import GlobalData
from product.case.models import CaseGroup
from product.utils.tools import login_required, get_user
from product import db
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from flask import Blueprint
from product.config import Config

global_data = Blueprint('globaldata', __name__)


@global_data.route('/create', methods=('POST',))
@login_required
def global_data_create():
    token = request.headers["token"]
    name = request.get_json().get('name')
    value = request.get_json().get('value')
    create_by = get_user(token)
    type = request.get_json().get('type')
    category = request.get_json().get('category')
    scope = request.get_json().get('scope')
    data_by_name = GlobalData.query.filter_by(name=name).first()
    if data_by_name:
        return jsonify({"code": 300, "message": "变量名称重复！"})
    if scope == "group":
        group_id = request.get_json().get('groupId')
        group_id_string = ",".join('%s' % id for id in group_id)
        data = GlobalData(name=name, value=value, type=type, category=category, create_by=create_by, scope=scope,
                          update_by=create_by, group_id=group_id_string)
    else:
        data = GlobalData(name=name, value=value, type=type, create_by=create_by, category=category,
                          update_by=create_by)
    try:
        db.session.add(data)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"code": 300, "message": str(e)})
    insert_data = GlobalData.query.filter_by(name=name).first()
    data = {"dataId": insert_data.data_id, "name": insert_data.name, "value": insert_data.value,
            "type": insert_data.type, "category": insert_data.category, "scope": insert_data.scope,
            "group": insert_data.group_id, "createBy": insert_data.create_by, "updateBy": insert_data.update_by,
            "createAt": insert_data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updateAt": insert_data.update_at.strftime("%Y-%m-%d %H:%M:%S")}
    return jsonify({"code": 200, "message": "添加成功", "content": data})


@global_data.route('/update', methods=('POST',))
@login_required
def global_data_update():
    token = request.headers["token"]
    data_id = request.get_json().get('dataId')
    name = request.get_json().get('name')
    value = request.get_json().get('value')
    update_by = get_user(token)
    type = request.get_json().get('type')
    category = request.get_json().get('category')
    scope = request.get_json().get('scope')
    db_data_name = GlobalData.query.filter_by(name=name).first()
    if db_data_name and db_data_name.data_id != data_id:
        return jsonify({"code": 300, "message": "变量名称重复！"})
    db_data = GlobalData.query.filter_by(data_id=data_id).first()
    if db_data:
        if scope == "group":
            group_id = request.get_json().get('groupId')
            group_id_string = ",".join('%s' % id for id in group_id)
            db_data.name = name
            db_data.value = value
            db_data.update_by = update_by
            db_data.type = type
            db_data.group_id = group_id_string
            db_data.scope = scope
            db_data.category = category
        else:
            db_data.name = name
            db_data.value = value
            db_data.update_by = update_by
            db_data.type = type
            db_data.group_id = "0"
            db_data.scope = scope
            db_data.category = category
            try:
                db.session.add(db_data)
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                return jsonify({"code": 200, "message": str(e)})
        update_data = GlobalData.query.filter_by(data_id=data_id).first()
        if update_data.group_id == "0":
            group = []
        else:
            group = update_data.group_id
        data = {"dataId": update_data.data_id, "name": update_data.name, "value": update_data.value,
                "type": update_data.type, "scope": update_data.scope, "group": group, "category": update_data.category,
                "createBy": update_data.create_by, "updateBy": update_data.update_by,
                "createAt": update_data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updateAt": update_data.update_at.strftime("%Y-%m-%d %H:%M:%S")}
        return jsonify({"code": 200, "message": "修改成功", "content": data})
    else:
        return jsonify({"code": 200, "message": "变量不存在"})


@global_data.route('/list', methods=('POST',))
@login_required
def global_data_list():
    data_list = []
    limit = int(request.get_json().get('limit'))
    if limit == '':
        return jsonify({"code": 200, "message": "参数非法！"})
    page = int(request.get_json().get('page'))
    if page == '':
        return jsonify({"code": 200, "message": "参数非法！"})
    if 'name' not in request.get_json().keys():
        db_datas = GlobalData.query.all()
        if len(db_datas) != 0:
            for data in db_datas:
                if data.group_id != "0":
                    group_id_list = [int(s) for s in data.group_id.split(',')]
                    group_name_list = []
                    for i in group_id_list:
                        name = CaseGroup.query.filter_by(group_id=i).first().group_name
                        group_name_list.append(name)
                    group_name_string = ",".join(group_name_list)
                    content_data = {"dataId": data.data_id, "name": data.name, "value": data.value,
                                    "type": data.type, "scope": data.scope, "groupId": group_id_list,
                                    "groupIdString": group_name_string, "category": data.category,
                                    "createBy": data.create_by, "updateBy": data.update_by,
                                    "createAt": data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                    "updateAt": data.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                else:
                    group_name_string = "全局"
                    content_data = {"dataId": data.data_id, "name": data.name, "value": data.value,
                                    "type": data.type, "scope": data.scope, "groupId": [],
                                    "groupIdString": group_name_string, "category": data.category,
                                    "createBy": data.create_by, "updateBy": data.update_by,
                                    "createAt": data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                    "updateAt": data.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                data_list.append(content_data)
            start = (page - 1) * limit
            end = page * limit if len(data_list) > page * limit else start + len(data_list)
            ret = data_list[start:end]
            return jsonify({"code": 200, "message": "查询成功", "totalCount": len(data_list), "contents": ret})
        else:
            return jsonify(
                {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})
    else:
        name = request.get_json().get('name')
        db_datas = GlobalData.query.filter(GlobalData.name.like('%{keyword}%'.format(keyword=name))).all()
        if len(db_datas) != 0:
            for data in db_datas:
                if data.group_id != "0":
                    group_id_list = [int(s) for s in data.group_id.split(',')]
                    group_name_list = []
                    for i in group_id_list:
                        name = CaseGroup.query.filter_by(group_id=i).first().group_name
                        group_name_list.append(name)
                    group_name_string = ",".join(group_name_list)
                    content_data = {"dataId": data.data_id, "name": data.name, "value": data.value,
                                    "type": data.type, "scope": data.scope, "groupId": group_id_list,
                                    "groupIdString": group_name_string, "category": data.category,
                                    "createBy": data.create_by, "updateBy": data.update_by,
                                    "createAt": data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                    "updateAt": data.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                else:
                    group_name_string = "全局"
                    content_data = {"dataId": data.data_id, "name": data.name, "value": data.value,
                                    "type": data.type, "scope": data.scope, "groupId": [],
                                    "groupIdString": group_name_string, "category": data.category,
                                    "createBy": data.create_by, "updateBy": data.update_by,
                                    "createAt": data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                    "updateAt": data.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                data_list.append(content_data)
            start = (page - 1) * limit
            end = page * limit if len(data_list) > page * limit else start + len(data_list)
            ret = data_list[start:end]
            return jsonify({"code": 200, "message": "查询成功", "totalCount": len(data_list), "contents": ret})
        else:
            return jsonify({"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})


@global_data.route('/detail', methods=('POST',))
@login_required
def global_data_detail():
    data_id = request.get_json().get('dataId')
    db_data = GlobalData.query.get(data_id=data_id).first()
    if db_data:
        data = {"dataId": db_data.data_id, "name": db_data.name, "value": db_data.value,
                "type": db_data.type, "scope": db_data.scope, "group": db_data.group_id,
                "createBy": db_data.create_by, "updateBy": db_data.update_by, "category": db_data.category,
                "createAt": db_data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updateAt": db_data.update_at.strftime("%Y-%m-%d %H:%M:%S")}
        return jsonify({"code": 200, "message": "查询成功", "content": data})
    else:
        return jsonify({"code": 200, "message": "变量不存在"})


@global_data.route('/delete', methods=('POST',))
@login_required
def global_data_delete():
    data_id = request.get_json().get('dataId')
    data = GlobalData.query.filter_by(data_id=data_id).first()
    if data:
        try:
            db.session.delete(data)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"code": 200, "message": str(e)})
        return jsonify({"code": 200, "message": "删除成功！"})
    else:
        return jsonify({"code": 200, "message": "变量不存在！"})


@global_data.route('/category_list', methods=('POST',))
@login_required
def user_server_list():
    category_list = Config.category_list
    return jsonify(
        {"code": 200, "totalCount": len(category_list), "message": "查询成功!",
         "contents": category_list})
