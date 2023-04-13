from product.case.models import CaseGroup, CaseManage, CaseTask
from product.utils.tools import login_required, get_user, string_to_md5
from product import db
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from flask import Blueprint
from product.config import Config
from product.users.models import User

case_group = Blueprint('casegroup', __name__)


@case_group.route('/create', methods=('POST',))
@login_required
def case_group_create():
    token = request.headers["token"]
    group_name = request.get_json().get('groupName')
    group_code = string_to_md5(group_name)
    if 'projType' not in request.get_json().keys():
        proj_type = ""
    else:
        proj_type = request.get_json().get('projType')
    if 'encodeType' not in request.get_json().keys():
        encode_type = ""
    else:
        encode_type = request.get_json().get('encodeType')
    if "service" not in request.get_json().keys():
        service = ""
    else:
        service = request.get_json().get('service')
    ext = request.get_json().get('ext')
    status = request.get_json().get('status')
    create_by = get_user(token)
    data_by_name = CaseGroup.query.filter_by(group_name=group_name).first()
    if data_by_name:
        return jsonify({"code": 300, "message": "用例名称重复！"})
    data_by_code = CaseGroup.query.filter_by(group_code=group_code).first()
    if data_by_code:
        return jsonify({"code": 300, "message": "用例集编号重复！"})
    group = CaseGroup(group_name=group_name, group_code=group_code, proj_type=proj_type, encode_type=encode_type,
                      service=service, ext=ext, create_by=create_by, update_by=create_by, status=status)
    try:
        db.session.add(group)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"code": 300, "message": str(e)})
    insert_group_data = CaseGroup.query.filter_by(group_code=group_code).first()
    data = {"groupId": insert_group_data.group_id, "groupName": insert_group_data.group_name,
            "groupCode": insert_group_data.group_code, "projType": insert_group_data.proj_type,
            "encodeType": insert_group_data.encode_type,
            "service": insert_group_data.service,
            "ext": insert_group_data.ext, "createBy": insert_group_data.create_by,
            "updateBy": insert_group_data.update_by,
            "createAt": insert_group_data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updateAt": insert_group_data.update_at.strftime("%Y-%m-%d %H:%M:%S"),
            "status": insert_group_data.status, "isDel": insert_group_data.is_del}
    return jsonify({"code": 200, "message": "添加成功", "content": data})


@case_group.route('/update', methods=('POST',))
@login_required
def case_group_update():
    token = request.headers["token"]
    group_id = request.get_json().get('groupId')
    group_name = request.get_json().get('groupName')
    if 'projType' not in request.get_json().keys():
        proj_type = ""
    else:
        proj_type = request.get_json().get('projType')
    if 'encodeType' not in request.get_json().keys():
        encode_type = ""
    else:
        encode_type = request.get_json().get('encodeType')
    if "service" not in request.get_json().keys():
        service = ""
    else:
        service = request.get_json().get('service')
    ext = request.get_json().get('ext')
    update_by = get_user(token)
    status = request.get_json().get('status')
    db_group_name = CaseGroup.query.filter_by(group_name=group_name).first()
    if db_group_name and db_group_name.group_id != group_id:
        return jsonify({"code": 300, "message": "用例集已被占用，请更换后重新提交！"})
    db_group = CaseGroup.query.filter_by(group_id=group_id).first()
    if db_group:
        db_group.group_name = group_name
        db_group.proj_type = proj_type
        db_group.encode_type = encode_type
        db_group.service = service
        db_group.ext = ext
        db_group.update_by = update_by
        db_group.status = status
        try:
            db.session.add(db_group)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"code": 300, "message": str(e)})
        update_group_data = CaseGroup.query.filter_by(group_id=group_id).first()
        data = {"groupId": update_group_data.group_id, "groupName": update_group_data.group_name,
                "groupCode": update_group_data.group_code, "projType": update_group_data.proj_type,
                "encodeType": update_group_data.encode_type, "service": update_group_data.service,
                "ext": update_group_data.ext, "createBy": update_group_data.create_by,
                "updateBy": update_group_data.update_by,
                "createAt": update_group_data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updateAt": update_group_data.update_at.strftime("%Y-%m-%d %H:%M:%S"),
                "status": update_group_data.status, "isDel": update_group_data.is_del}
        return jsonify({"code": 200, "message": "修改成功", "content": data})
    else:
        return jsonify({"code": 300, "message": "用例不存在"})


@case_group.route('/list', methods=('POST',))
@login_required
def case_group_list():
    token = request.headers["token"]
    user = get_user(token)
    role = User.query.filter_by(user=user).first().role
    groups_data = []
    limit = int(request.get_json().get('limit'))
    if limit == '':
        return jsonify({"code": 300, "message": "参数非法！"})
    page = int(request.get_json().get('page'))
    if page == '':
        return jsonify({"code": 300, "message": "参数非法！"})
    if role == "admin":
        if 'groupName' not in request.get_json().keys():
            db_groups = CaseGroup.query.filter_by(is_del=0).order_by(
                CaseGroup.update_at.desc()).all()
            if len(db_groups) != 0:
                for group in db_groups:
                    cases = CaseManage.query.filter_by(group_id=group.group_id).all()
                    gruop_data = {"groupId": group.group_id, "groupName": group.group_name,
                                  "groupCode": group.group_code, "projType": group.proj_type,
                                  "encodeType": group.encode_type, "service": group.service, "ext": group.ext,
                                  "createBy": group.create_by, "updateBy": group.update_by,
                                  "createAt": group.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                  "updateAt": group.update_at.strftime("%Y-%m-%d %H:%M:%S"),
                                  "status": group.status, "isDel": group.is_del, "caseCount": len(cases)}
                    groups_data.append(gruop_data)
                start = (page - 1) * limit
                end = page * limit if len(groups_data) > page * limit else start + len(groups_data)
                ret = groups_data[start:end]
                return jsonify({"code": 200, "message": "查询成功", "totalCount": len(groups_data), "contents": ret})
            else:
                return jsonify(
                    {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})
        else:
            group_name = request.get_json().get('groupName')
            db_groups = CaseGroup.query.filter(CaseGroup.is_del == 0,
                                               CaseGroup.group_name.like(
                                                   '%{keyword}%'.format(keyword=group_name))).order_by(
                CaseGroup.update_at.desc()).all()
            if len(db_groups) != 0:
                for group in db_groups:
                    cases = CaseManage.query.filter_by(group_id=group.group_id).all()
                    gruop_data = {"groupId": group.group_id, "groupName": group.group_name,
                                  "groupCode": group.group_code, "projType": group.proj_type,
                                  "encodeType": group.encode_type, "service": group.service, "ext": group.ext,
                                  "createBy": group.create_by, "updateBy": group.update_by,
                                  "createAt": group.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                  "updateAt": group.update_at.strftime("%Y-%m-%d %H:%M:%S"),
                                  "status": group.status, "isDel": group.is_del, "caseCount": len(cases)}
                    groups_data.append(gruop_data)
                start = (page - 1) * limit
                end = page * limit if len(groups_data) > page * limit else start + len(groups_data)
                ret = groups_data[start:end]
                return jsonify({"code": 200, "message": "查询成功", "totalCount": len(groups_data), "contents": ret})
            else:
                return jsonify(
                    {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})
    else:
        if 'groupName' not in request.get_json().keys():
            db_groups_role = CaseGroup.query.filter(CaseGroup.is_del == 0, CaseGroup.service == role).order_by(
                CaseGroup.update_at.desc()).all()
            if len(db_groups_role) != 0:
                for group in db_groups_role:
                    cases = CaseManage.query.filter_by(group_id=group.group_id).all()
                    gruop_data = {"groupId": group.group_id, "groupName": group.group_name,
                                  "groupCode": group.group_code, "projType": group.proj_type,
                                  "encodeType": group.encode_type, "service": group.service, "ext": group.ext,
                                  "createBy": group.create_by, "updateBy": group.update_by,
                                  "createAt": group.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                  "updateAt": group.update_at.strftime("%Y-%m-%d %H:%M:%S"),
                                  "status": group.status, "isDel": group.is_del, "caseCount": len(cases)}
                    groups_data.append(gruop_data)
                start = (page - 1) * limit
                end = page * limit if len(groups_data) > page * limit else start + len(groups_data)
                ret = groups_data[start:end]
                return jsonify({"code": 200, "message": "查询成功", "totalCount": len(groups_data), "contents": ret})
            else:
                return jsonify(
                    {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})
        else:
            group_name = request.get_json().get('groupName')
            db_groups_role = CaseGroup.query.filter(CaseGroup.is_del == 0, CaseGroup.service == role,
                                                    CaseGroup.group_name.like(
                                                        '%{keyword}%'.format(keyword=group_name))).order_by(
                CaseGroup.update_at.desc()).all()
            if len(db_groups_role) != 0:
                for group in db_groups_role:
                    cases = CaseManage.query.filter_by(group_id=group.group_id).all()
                    gruop_data = {"groupId": group.group_id, "groupName": group.group_name,
                                  "groupCode": group.group_code, "projType": group.proj_type,
                                  "encodeType": group.encode_type, "service": group.service, "ext": group.ext,
                                  "createBy": group.create_by, "updateBy": group.update_by,
                                  "createAt": group.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                  "updateAt": group.update_at.strftime("%Y-%m-%d %H:%M:%S"),
                                  "status": group.status, "isDel": group.is_del, "caseCount": len(cases)}
                    groups_data.append(gruop_data)
                start = (page - 1) * limit
                end = page * limit if len(groups_data) > page * limit else start + len(groups_data)
                ret = groups_data[start:end]
                return jsonify({"code": 200, "message": "查询成功", "totalCount": len(groups_data), "contents": ret})
            else:
                return jsonify(
                    {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})


@case_group.route('/all', methods=('POST',))
@login_required
def case_group_all():
    token = request.headers["token"]
    user = get_user(token)
    role = User.query.filter_by(user=user).first().role
    groups_data = []
    if role == "admin":
        db_groups = CaseGroup.query.filter_by(is_del=0).all()
        if len(db_groups) != 0:
            for group in db_groups:
                gruop_data = {"groupId": group.group_id, "groupName": group.group_name,
                              "groupCode": group.group_code, "projType": group.proj_type,
                              "encodeType": group.encode_type, "service": group.service,
                              "ext": group.ext, "createBy": group.create_by,
                              "updateBy": group.update_by,
                              "createAt": group.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                              "updateAt": group.update_at.strftime("%Y-%m-%d %H:%M:%S"),
                              "status": group.status, "isDel": group.is_del}
                groups_data.append(gruop_data)
            return jsonify({"code": 200, "message": "查询成功", "totalCount ": len(groups_data), "contents": groups_data})
        else:
            return jsonify(
                {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})
    else:
        db_groups = CaseGroup.query.filter(CaseGroup.is_del == 0, CaseGroup.service == role).all()
        if len(db_groups) != 0:
            for group in db_groups:
                gruop_data = {"groupId": group.group_id, "groupName": group.group_name,
                              "groupCode": group.group_code, "projType": group.proj_type,
                              "encodeType": group.encode_type, "service": group.service,
                              "ext": group.ext, "createBy": group.create_by,
                              "updateBy": group.update_by,
                              "createAt": group.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                              "updateAt": group.update_at.strftime("%Y-%m-%d %H:%M:%S"),
                              "status": group.status, "isDel": group.is_del}
                groups_data.append(gruop_data)
            return jsonify({"code": 200, "message": "查询成功", "totalCount ": len(groups_data), "contents": groups_data})
        else:
            return jsonify(
                {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})


@case_group.route('/detail', methods=('POST',))
@login_required
def case_group_detail():
    group_id = request.get_json().get('groupId')
    db_group = CaseGroup.query.get(group_id=group_id).first()
    if db_group:
        data = {"groupId": db_group.group_id, "groupName": db_group.group_name,
                "groupCode": db_group.group_code, "projType": db_group.proj_type,
                "encodeType": db_group.encode_type, "service": db_group.service,
                "ext": db_group.ext, "createBy": db_group.create_by,
                "updateBy": db_group.update_by,
                "createAt": db_group.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updateAt": db_group.update_at.strftime("%Y-%m-%d %H:%M:%S"),
                "status": db_group.status, "isDel": db_group.is_del}
        return jsonify({"code": 200, "message": "查询成功", "content": data})
    else:
        return jsonify({"code": 200, "message": "用例不存在"})


@case_group.route('/delete', methods=('POST',))
@login_required
def case_group_delete():
    group_id = request.get_json().get('groupId')
    group = CaseGroup.query.filter_by(group_id=group_id).first()
    case_plan = CaseTask.query.filter_by(task_group=group_id).first()
    case = CaseManage.query.filter_by(group_id=group_id).first()
    if not group:
        return jsonify({"code": 300, "message": "用例集不存在"})
    if case:
        jsonify({"code": 300, "message": "该分组有关联的用例，不允许删除！"})
    if case_plan:
        return jsonify({"code": 300, "message": '该分组有关联的用例计划，不允许删除！'})
    if group.status == 1:
        return jsonify({"code": 300, "message": "启用状态的用例集不能删除！"})
    group.is_del = 1  # 逻辑删除
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"code": 300, "message": str(e)})
    return jsonify({"code": 200, "message": "删除成功！"})


@case_group.route('/proj_encode_type', methods=('POST',))
@login_required
def case_group_proj_type():
    proj_type_list = []
    for proj_type in Config.proj_type:
        if proj_type in ['Android_v3', 'iOS_v3', 'android_v4', 'iOS_v4', 'quickapp_v4']:
            encode_type_list = []
            for encode_type in Config.encode_type[proj_type]:
                key_value = {"projTypeKey": encode_type, "projTypeValue": encode_type}
                encode_type_list.append(key_value)
            key_value = {"projTypeKey": proj_type, "projTypeValue": proj_type, "children":
                encode_type_list}
        else:
            key_value = {"projTypeKey": proj_type, "projTypeValue": proj_type}
        proj_type_list.append(key_value)
    return jsonify(
        {"code": 200, "totalCount": len(proj_type_list), "message": "查询成功!", "contents": proj_type_list})
