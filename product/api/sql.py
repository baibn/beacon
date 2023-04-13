from product.sql.models import SqlManage
from product.utils.tools import login_required, get_user
from product import db
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from flask import Blueprint

sql_manage = Blueprint('sqlmanage', __name__)


@sql_manage.route('/create', methods=('POST',))
@login_required
def sql_create():
    token = request.headers["token"]
    sql_name = request.get_json().get('sqlName')
    type = request.get_json().get('type')
    database = request.get_json().get('database')
    if "databases" not in request.get_json().keys():
        databases = "default"
    else:
        databases = request.get_json().get('databases')
    value = request.get_json().get('value')
    create_by = get_user(token)
    data_by_name = SqlManage.query.filter_by(sql_name=sql_name).first()
    if type not in ['select', 'delete', 'update', 'insert']:
        return jsonify({"code": 300, "message": "类型不合法！"})
    if data_by_name:
        return jsonify({"code": 300, "message": "sql名称重复！"})
    data = SqlManage(sql_name=sql_name, type=type, database=database, databases=databases, value=value,
                     create_by=create_by, update_by=create_by)
    try:
        db.session.add(data)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"code": 300, "message": str(e)})
    insert_data = SqlManage.query.filter_by(sql_name=sql_name).first()
    data = {"sqlId": insert_data.sql_id, "sqlName": insert_data.sql_name, "type": insert_data.type,
            "database": insert_data.database, "databases": insert_data.databases,
            "value": insert_data.value, "createBy": insert_data.create_by, "updateBy": insert_data.update_by,
            "createAt": insert_data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updateAt": insert_data.update_at.strftime("%Y-%m-%d %H:%M:%S")}
    return jsonify({"code": 200, "message": "添加成功", "content": data})


@sql_manage.route('/update', methods=('POST',))
@login_required
def sql_update():
    token = request.headers["token"]
    sql_id = request.get_json().get('sqlId')
    sql_name = request.get_json().get('sqlName')
    type = request.get_json().get('type')
    database = request.get_json().get('database')
    if "databases" not in request.get_json().keys():
        databases = "default"
    else:
        databases = request.get_json().get('databases')
    value = request.get_json().get('value')
    update_by = get_user(token)
    if type not in ['select', 'delete', 'update', 'insert']:
        return jsonify({"code": 300, "message": "类型不合法！"})
    db_data_name = SqlManage.query.filter_by(sql_name=sql_name).first()
    if db_data_name and db_data_name.sql_id != sql_id:
        return jsonify({"code": 300, "message": "sql名称重复！"})
    db_data = SqlManage.query.filter_by(sql_id=sql_id).first()
    if db_data:
        db_data.sql_name = sql_name
        db_data.type = type
        db_data.database = database
        db_data.databases = databases
        db_data.value = value
        db_data.update_by = update_by
        try:
            db.session.add(db_data)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"code": 200, "message": str(e)})
        update_data = SqlManage.query.filter_by(sql_id=sql_id).first()
        data = {"sqlId": update_data.sql_id, "sqlName": update_data.sql_name, "type": update_data.type,
                "value": update_data.value, "database": update_data.database, "databases": update_data.databases,
                "createBy": update_data.create_by, "updateBy": update_data.update_by,
                "createAt": update_data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updateAt": update_data.update_at.strftime("%Y-%m-%d %H:%M:%S")}
        return jsonify({"code": 200, "message": "修改成功", "content": data})
    else:
        return jsonify({"code": 200, "message": "sql不存在"})


@sql_manage.route('/list', methods=('POST',))
@login_required
def sql_list():
    sql_list = []
    limit = int(request.get_json().get('limit'))
    if limit == '':
        return jsonify({"code": 200, "message": "参数非法！"})
    page = int(request.get_json().get('page'))
    if page == '':
        return jsonify({"code": 200, "message": "参数非法！"})
    if 'sqlName' not in request.get_json().keys():
        if 'type' not in request.get_json().keys():
            db_sqls = SqlManage.query.all()
            if len(db_sqls) != 0:
                for sql in db_sqls:
                    data = {"sqlId": sql.sql_id, "sqlName": sql.sql_name, "type": sql.type,
                            "value": sql.value, "database": sql.database, "databases": sql.databases,
                            "createBy": sql.create_by, "updateBy": sql.update_by,
                            "createAt": sql.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                            "updateAt": sql.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                    sql_list.append(data)
                start = (page - 1) * limit
                end = page * limit if len(sql_list) > page * limit else start + len(sql_list)
                ret = sql_list[start:end]
                return jsonify({"code": 200, "message": "查询成功", "totalCount": len(sql_list), "contents": ret})
            else:
                return jsonify(
                    {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})
        else:
            type = request.get_json().get('type')
            db_sqls = SqlManage.query.filter(SqlManage.type.like('%{keyword}%'.format(keyword=type))).all()
            if len(db_sqls) != 0:
                for sql in db_sqls:
                    data = {"sqlId": sql.sql_id, "sqlName": sql.sql_name, "type": sql.type,
                            "value": sql.value, "database": sql.database, "databases": sql.databases,
                            "createBy": sql.create_by, "updateBy": sql.update_by,
                            "createAt": sql.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                            "updateAt": sql.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                    sql_list.append(data)
                start = (page - 1) * limit
                end = page * limit if len(sql_list) > page * limit else start + len(sql_list)
                ret = sql_list[start:end]
                return jsonify({"code": 200, "message": "查询成功", "totalCount": len(sql_list), "contents": ret})
            else:
                return jsonify(
                    {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})

    else:
        if 'type' not in request.get_json().keys():
            sql_name = request.get_json().get('sqlName')
            db_sqls = SqlManage.query.filter(SqlManage.sql_name.like('%{keyword}%'.format(keyword=sql_name))).all()
            if len(db_sqls) != 0:
                for sql in db_sqls:
                    data = {"sqlId": sql.sql_id, "sqlName": sql.sql_name, "type": sql.type,
                            "value": sql.value, "database": sql.database, "databases": sql.databases,
                            "createBy": sql.create_by, "updateBy": sql.update_by,
                            "createAt": sql.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                            "updateAt": sql.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                    sql_list.append(data)
                start = (page - 1) * limit
                end = page * limit if len(sql_list) > page * limit else start + len(sql_list)
                ret = sql_list[start:end]
                return jsonify({"code": 200, "message": "查询成功", "totalCount": len(sql_list), "contents": ret})
            else:
                return jsonify(
                    {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})
        else:
            sql_name = request.get_json().get('sqlName')
            type = request.get_json().get('type')
            db_sqls = SqlManage.query.filter(SqlManage.sql_name.like('%{keyword}%'.format(keyword=sql_name)),
                                             SqlManage.type.like('%{keyword}%'.format(keyword=type))).all()
            if len(db_sqls) != 0:
                for sql in db_sqls:
                    data = {"sqlId": sql.sql_id, "sqlName": sql.sql_name, "type": sql.type,
                            "value": sql.value, "database": sql.database, "databases": sql.databases,
                            "createBy": sql.create_by, "updateBy": sql.update_by,
                            "createAt": sql.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                            "updateAt": sql.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                    sql_list.append(data)
                start = (page - 1) * limit
                end = page * limit if len(sql_list) > page * limit else start + len(sql_list)
                ret = sql_list[start:end]
                return jsonify({"code": 200, "message": "查询成功", "totalCount": len(sql_list), "contents": ret})
            else:
                return jsonify(
                    {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})


@sql_manage.route('/detail', methods=('POST',))
@login_required
def sql_detail():
    sql_id = request.get_json().get('sqlId')
    db_data = SqlManage.query.filter_by(sql_id=sql_id).first()
    if db_data:
        data = {"sqlId": db_data.sql_id, "sqlName": db_data.sql_name, "type": db_data.type,
                "value": db_data.value, "database": db_data.database, "databases": db_data.databases,
                "createBy": db_data.create_by, "updateBy": db_data.update_by,
                "createAt": db_data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updateAt": db_data.update_at.strftime("%Y-%m-%d %H:%M:%S")}
        return jsonify({"code": 200, "message": "查询成功", "content": data})
    else:
        return jsonify({"code": 200, "message": "sql不存在"})


@sql_manage.route('/delete', methods=('POST',))
@login_required
def sql_delete():
    sql_id = request.get_json().get('sqlId')
    data = SqlManage.query.filter_by(sql_id=sql_id).first()
    if data:
        try:
            db.session.delete(data)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"code": 200, "message": str(e)})
        return jsonify({"code": 200, "message": "删除成功！"})
    else:
        return jsonify({"code": 200, "message": "sql不存在！"})
