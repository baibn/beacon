from product.schema.models import SchemaData
from product.utils.tools import login_required, get_user
from product import db
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from flask import Blueprint
from product.config import Config

schema_data = Blueprint('schema', __name__)


@schema_data.route('/create', methods=('POST',))
@login_required
def schema_data_create():
    token = request.headers["token"]
    obj_name = request.get_json().get('objName')
    name = request.get_json().get('name')
    value = request.get_json().get('value')
    create_by = get_user(token)
    data_by_name = SchemaData.query.filter_by(name=name).first()
    if data_by_name:
        return jsonify({"code": 300, "message": "模版名称重复！"})
    data = SchemaData(obj_name=obj_name, name=name, value=value, create_by=create_by,
                      update_by=create_by)
    try:
        db.session.add(data)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"code": 300, "message": str(e)})
    insert_data = SchemaData.query.filter_by(name=name).first()
    data = {"schemaId": insert_data.schema_id, "objName": insert_data.obj_name, "name": insert_data.name,
            "value": insert_data.value, "createBy": insert_data.create_by, "updateBy": insert_data.update_by,
            "createAt": insert_data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updateAt": insert_data.update_at.strftime("%Y-%m-%d %H:%M:%S")}
    return jsonify({"code": 200, "message": "添加成功", "content": data})


@schema_data.route('/update', methods=('POST',))
@login_required
def schema_data_update():
    token = request.headers["token"]
    schema_id = request.get_json().get('schemaId')
    obj_name = request.get_json().get('objName')
    name = request.get_json().get('name')
    value = request.get_json().get('value')
    update_by = get_user(token)
    db_data_name = SchemaData.query.filter_by(name=name).first()
    if db_data_name and db_data_name.schema_id != schema_id:
        return jsonify({"code": 300, "message": "模版名称重复！"})
    db_data = SchemaData.query.filter_by(schema_id=schema_id).first()
    if db_data:
        db_data.obj_name = obj_name
        db_data.name = name
        db_data.value = value
        db_data.update_by = update_by
        try:
            db.session.add(db_data)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"code": 200, "message": str(e)})
        update_data = SchemaData.query.filter_by(schema_id=schema_id).first()
        data = {"schemaId": update_data.schema_id, "objName": update_data.obj_name, "name": update_data.name,
                "value": update_data.value, "createBy": update_data.create_by, "updateBy": update_data.update_by,
                "createAt": update_data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updateAt": update_data.update_at.strftime("%Y-%m-%d %H:%M:%S")}
        return jsonify({"code": 200, "message": "修改成功", "content": data})
    else:
        return jsonify({"code": 200, "message": "模版不存在"})


@schema_data.route('/list', methods=('POST',))
@login_required
def schema_data_list():
    schema_list = []
    limit = int(request.get_json().get('limit'))
    if limit == '':
        return jsonify({"code": 200, "message": "参数非法！"})
    page = int(request.get_json().get('page'))
    if page == '':
        return jsonify({"code": 200, "message": "参数非法！"})
    if "objName" not in request.get_json().keys():
        if 'name' not in request.get_json().keys():
            db_schemas = SchemaData.query.all()
            if len(db_schemas) != 0:
                for schema in db_schemas:
                    data = {"schemaId": schema.schema_id, "objName": schema.obj_name, "name": schema.name,
                            "value": schema.value, "createBy": schema.create_by, "updateBy": schema.update_by,
                            "createAt": schema.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                            "updateAt": schema.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                    schema_list.append(data)
                start = (page - 1) * limit
                end = page * limit if len(schema_list) > page * limit else start + len(schema_list)
                ret = schema_list[start:end]
                return jsonify({"code": 200, "message": "查询成功", "totalCount": len(schema_list), "contents": ret})
            else:
                return jsonify(
                    {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})
        else:
            name = request.get_json().get('name')
            db_schemas = SchemaData.query.filter(SchemaData.name.like('%{keyword}%'.format(keyword=name))).all()
            if len(db_schemas) != 0:
                for schema in db_schemas:
                    data = {"schemaId": schema.schema_id, "objName": schema.obj_name, "name": schema.name,
                            "value": schema.value, "createBy": schema.create_by, "updateBy": schema.update_by,
                            "createAt": schema.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                            "updateAt": schema.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                    schema_list.append(data)
                start = (page - 1) * limit
                end = page * limit if len(schema_list) > page * limit else start + len(schema_list)
                ret = schema_list[start:end]
                return jsonify({"code": 200, "message": "查询成功", "totalCount": len(schema_list), "contents": ret})
            else:
                return jsonify(
                    {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})
    else:
        if 'name' not in request.get_json().keys():
            obj_name = request.get_json().get('objName')
            db_schemas = SchemaData.query.filter(SchemaData.obj_name.like('%{keyword}%'.format(keyword=obj_name))).all()
            if len(db_schemas) != 0:
                for schema in db_schemas:
                    data = {"schemaId": schema.schema_id,
                            "objName": schema.obj_name,
                            "name": schema.name,
                            "value": schema.value, "createBy": schema.create_by, "updateBy": schema.update_by,
                            "createAt": schema.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                            "updateAt": schema.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                    schema_list.append(data)
                start = (page - 1) * limit
                end = page * limit if len(schema_list) > page * limit else start + len(schema_list)
                ret = schema_list[start:end]
                return jsonify({"code": 200, "message": "查询成功", "totalCount": len(schema_list), "contents": ret})
            else:
                return jsonify(
                    {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})
        else:
            obj_name = request.get_json().get('objName')
            name = request.get_json().get('name')
            db_schemas = SchemaData.query.filter(SchemaData.obj_name.like('%{keyword}%'.format(keyword=obj_name)),
                                                 SchemaData.name.like('%{keyword}%'.format(keyword=name))).all()
            if len(db_schemas) != 0:
                for schema in db_schemas:
                    data = {"schemaId": schema.schema_id, "objName": schema.obj_name, "name": schema.name,
                            "value": schema.value, "createBy": schema.create_by, "updateBy": schema.update_by,
                            "createAt": schema.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                            "updateAt": schema.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                    schema_list.append(data)
                start = (page - 1) * limit
                end = page * limit if len(schema_list) > page * limit else start + len(schema_list)
                ret = schema_list[start:end]
                return jsonify({"code": 200, "message": "查询成功", "totalCount": len(schema_list), "contents": ret})
            else:
                return jsonify(
                    {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})


@schema_data.route('/detail', methods=('POST',))
@login_required
def schema_data_detail():
    schema_id = request.get_json().get('schemaId')
    db_data = SchemaData.query.filter_by(schema_id=schema_id).first()
    if db_data:
        data = {"schemaId": db_data.schema_id, "objName": db_data.obj_name, "name": db_data.name,
                "value": db_data.value, "createBy": db_data.create_by, "updateBy": db_data.update_by,
                "createAt": db_data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updateAt": db_data.update_at.strftime("%Y-%m-%d %H:%M:%S")}
        return jsonify({"code": 200, "message": "查询成功", "content": data})
    else:
        return jsonify({"code": 200, "message": "模版不存在"})


@schema_data.route('/delete', methods=('POST',))
@login_required
def schema_data_delete():
    schema_id = request.get_json().get('schemaId')
    data = SchemaData.query.filter_by(schema_id=schema_id).first()
    if data:
        try:
            db.session.delete(data)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"code": 200, "message": str(e)})
        return jsonify({"code": 200, "message": "删除成功！"})
    else:
        return jsonify({"code": 200, "message": "模版不存在！"})


@schema_data.route('/ssh_name_list', methods=('POST',))
@login_required
def ssh_name_list():
    ssh_name_list = []
    for ssh in Config.ssh_conf_dict.keys():
        key_value = {"sshKey": ssh, "sshValue": ssh}
        ssh_name_list.append(key_value)
    return jsonify(
        {"code": 200, "totalCount": len(ssh_name_list), "message": "查询成功!",
         "contents": ssh_name_list})


@schema_data.route('/obj_name_list', methods=('POST',))
@login_required
def obj_name_list():
    obj_name_list = []
    for obj_name in Config.obj_name_list:
        for key, value in obj_name.items():
            key_value = {"objKey": key, "objValue": value}
            obj_name_list.append(key_value)
    return jsonify(
        {"code": 200, "totalCount": len(obj_name_list), "message": "查询成功!",
         "contents": obj_name_list})


@schema_data.route('/schema_name_list', methods=('POST',))
@login_required
def schema_name_list():
    obj_name_list = []
    for obj_name in Config.obj_name_list:
        for key, value in obj_name.items():
            schema_name_list = []
            schema_datas = SchemaData.query.filter_by(obj_name=value).all()
            for schema in schema_datas:
                schema_data = {"key": schema.name, "value": schema.name}
                schema_name_list.append(schema_data)
            key_value = {"key": key, "value": value, "children": schema_name_list}
            obj_name_list.append(key_value)
    return jsonify(
        {"code": 200, "totalCount": len(obj_name_list), "message": "查询成功!",
         "contents": obj_name_list})
