from product.case.models import CaseManage, CaseGroup
from product.utils.tools import login_required, get_user, generate_btid, generate_btid_list, time_yyyyy_MM_dd, \
    time_YMDHMS, local_time, local_time_13, release_jsonp, JsonCompare, extract_delete_key, SchemaDiff, model_to_dict, \
    refer_case_response
from product import db
from flask import request, jsonify
import re
import time
import requests
import json
from sqlalchemy.exc import SQLAlchemyError
import datetime
from flask import Blueprint
from jsonpath import jsonpath
from product.config import Config
from product.utils.excute import Execute, FindPath
from product.global_data.models import GlobalData
from product.utils_fp.FpEncoder import FpEncoder
from product.utils_fp.FpDataDealer import FpDataDealer
from product.users.models import User
from product.utils.server_lib import ServerLibrary
from product.schema.models import SchemaData
from product.sql.models import SqlManage
from product.utils.DB_lib import DbLibrary
from jsonschema import Draft7Validator

case = Blueprint('case', __name__)


@case.route('/create', methods=('POST',))
@login_required
def case_create():
    token = request.headers["token"]
    request_data = json.loads(request.data.decode('utf-8', 'ignore'))
    case_name = request_data['caseName']
    description = request_data['description']
    method = request_data['method']
    url = request_data['url']
    port = request_data['port']
    params = request_data['params']
    headers = request_data['headers']
    re_headers = {}
    for data in headers:
        re_headers[data['headerKey']] = data['headerValue']
    set_up = request_data['setUp']
    if set_up != "":
        for sql_name in set_up.split(','):
            if SqlManage.query.filter_by(sql_name=sql_name).first() is None:
                return jsonify({"code": 300, "message": "sql标识不存在！"})
    expect_res = request_data['expectRes']
    expect_res_str_list = []
    for expect in expect_res:
        expect_res_str_list.append(json.dumps(expect))
    expect_res_str = '|'.join(expect_res_str_list)
    create_by = get_user(token)
    status = request_data['status']
    group_id = request_data['groupId']
    code = CaseGroup.query.filter_by(group_id=group_id).first().group_code
    case_sign = "{0}_{1}".format(str(code), datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    data_by_sign = CaseManage.query.filter_by(case_sign=case_sign).first()
    if data_by_sign:
        return jsonify({"code": 300, "message": "用例编号重复！"})
    data_by_name = CaseManage.query.filter_by(case_name=case_name).first()
    if data_by_name:
        return jsonify({"code": 300, "message": "用例名称重复！"})
    re_url = re.match("(http|https)://[^\s]+", url)
    if re_url is None:
        return jsonify({"code": 300, "message": "url不合法！"})
    if int(status) not in {0, 1}:
        return jsonify({"code": 300, "message": "status不合法！"})
    if method not in ['GET', 'POST', 'DELETE', 'PATCH']:
        return jsonify({"code": 300, "message": "请求方法不合法！"})
    expect_keys = request_data["expectKeys"]
    unexpect_keys = request_data["unexpectKeys"]
    delay_time = request_data["delayTime"]
    if "historyCheck" in list(request_data.keys()):
        history_check = request_data['historyCheck']
        history_check_str_list = []
        for his in history_check:
            history_check_str_list.append(json.dumps(his))
        history_check_str = '|'.join(history_check_str_list)
        if method == "GET" or method == "DELETE":
            get_params_str_list = []
            for param in params:
                get_params_str_list.append(json.dumps(param))
            get_params_str = '|'.join(get_params_str_list)
            case = CaseManage(case_name=case_name, case_sign=case_sign, description=description, url=url, port=port,
                              params=get_params_str, method=method, headers=re_headers, set_up=set_up,
                              expect_res=expect_res_str, expect_keys=expect_keys, unexpect_keys=unexpect_keys,
                              create_by=create_by, update_by=create_by, status=status, delay_time=delay_time,
                              history_check=history_check_str, group_id=group_id)
        else:
            case = CaseManage(case_name=case_name, case_sign=case_sign, description=description, url=url, port=port,
                              params=json.dumps(params), method=method, headers=re_headers, expect_res=expect_res_str,
                              expect_keys=expect_keys, unexpect_keys=unexpect_keys, create_by=create_by, set_up=set_up,
                              history_check=history_check_str, update_by=create_by, status=status,
                              delay_time=delay_time, group_id=group_id)
    else:
        if method == "GET" or method == "DELETE":
            get_params_str_list = []
            for param in params:
                get_params_str_list.append(json.dumps(param))
            get_params_str = '|'.join(get_params_str_list)
            case = CaseManage(case_name=case_name, case_sign=case_sign, description=description, url=url, port=port,
                              params=get_params_str, method=method, headers=re_headers, set_up=set_up,
                              expect_res=expect_res_str, expect_keys=expect_keys, unexpect_keys=unexpect_keys,
                              create_by=create_by, update_by=create_by, status=status, delay_time=delay_time,
                              group_id=group_id)
        else:
            case = CaseManage(case_name=case_name, case_sign=case_sign, description=description, url=url, port=port,
                              params=json.dumps(params), method=method, headers=re_headers, expect_res=expect_res_str,
                              expect_keys=expect_keys, unexpect_keys=unexpect_keys, create_by=create_by, set_up=set_up,
                              update_by=create_by, status=status, delay_time=delay_time, group_id=group_id)
    try:
        db.session.add(case)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"code": 300, "message": str(e)})
    insert_case_data = CaseManage.query.filter_by(case_sign=case_sign).first()
    expect_res_list = []
    for expect in insert_case_data.expect_res.split('|'):
        expect_res_list.append(json.loads(expect))
    if insert_case_data.method == "GET" or insert_case_data.method == "DELETE":
        get_params_list = []
        for param in insert_case_data.params.split('|'):
            get_params_list.append(json.loads(param))
        if insert_case_data.history_check is None:
            data = {"caseId": insert_case_data.case_id, "caseName": insert_case_data.case_name,
                    "caseSign": insert_case_data.case_sign, "setUp": insert_case_data.set_up,
                    "description": insert_case_data.description, "method": insert_case_data.method,
                    "url": insert_case_data.url, "port": insert_case_data.port,
                    "params": get_params_list, "headers": insert_case_data.headers, "expectRes": expect_res_list,
                    "createBy": insert_case_data.create_by, "updateBy": insert_case_data.update_by,
                    "status": insert_case_data.status, "groupId": insert_case_data.group_id,
                    "expectKeys": insert_case_data.expect_keys,
                    "unexpectKeys": insert_case_data.unexpect_keys, "delayTime": insert_case_data.delay_time,
                    "historyCheck": insert_case_data.history_check,
                    "createAt": insert_case_data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updateAt": insert_case_data.update_at.strftime("%Y-%m-%d %H:%M:%S")}
            return jsonify({"code": 200, "message": "添加成功", "content": data})
        else:
            history_check_list = []
            for his in insert_case_data.history_check.split('|'):
                history_check_list.append(json.loads(his))
            data = {"caseId": insert_case_data.case_id, "caseName": insert_case_data.case_name,
                    "caseSign": insert_case_data.case_sign, "setUp": insert_case_data.set_up,
                    "description": insert_case_data.description, "method": insert_case_data.method,
                    "url": insert_case_data.url, "port": insert_case_data.port,
                    "params": get_params_list, "headers": insert_case_data.headers, "expectRes": expect_res_list,
                    "createBy": insert_case_data.create_by, "updateBy": insert_case_data.update_by,
                    "status": insert_case_data.status, "groupId": insert_case_data.group_id,
                    "expectKeys": insert_case_data.expect_keys, "unexpectKeys": insert_case_data.unexpect_keys,
                    "delayTime": insert_case_data.delay_time, "historyCheck": history_check_list,
                    "createAt": insert_case_data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updateAt": insert_case_data.update_at.strftime("%Y-%m-%d %H:%M:%S")}
            return jsonify({"code": 200, "message": "添加成功", "content": data})
    else:
        if insert_case_data.history_check is None:
            data = {"caseId": insert_case_data.case_id, "caseName": insert_case_data.case_name,
                    "caseSign": insert_case_data.case_sign, "setUp": insert_case_data.set_up,
                    "description": insert_case_data.description, "method": insert_case_data.method,
                    "url": insert_case_data.url, "port": insert_case_data.port,
                    "params": json.loads(insert_case_data.params),
                    "headers": insert_case_data.headers, "expectRes": expect_res_list,
                    "createBy": insert_case_data.create_by, "updateBy": insert_case_data.update_by,
                    "status": insert_case_data.status, "groupId": insert_case_data.group_id,
                    "expectKeys": insert_case_data.expect_keys,
                    "unexpectKeys": insert_case_data.unexpect_keys, "delayTime": insert_case_data.delay_time,
                    "historyCheck": insert_case_data.history_check,
                    "createAt": insert_case_data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updateAt": insert_case_data.update_at.strftime("%Y-%m-%d %H:%M:%S")}
            return jsonify({"code": 200, "message": "添加成功", "content": data})
        else:
            history_check_list = []
            for his in insert_case_data.history_check.split('|'):
                history_check_list.append(json.loads(his))
            data = {"caseId": insert_case_data.case_id, "caseName": insert_case_data.case_name,
                    "caseSign": insert_case_data.case_sign, "setUp": insert_case_data.set_up,
                    "description": insert_case_data.description, "method": insert_case_data.method,
                    "url": insert_case_data.url, "port": insert_case_data.port,
                    "params": json.loads(insert_case_data.params), "headers": insert_case_data.headers,
                    "expectRes": expect_res_list,
                    "createBy": insert_case_data.create_by, "updateBy": insert_case_data.update_by,
                    "status": insert_case_data.status, "groupId": insert_case_data.group_id,
                    "expectKeys": insert_case_data.expect_keys, "unexpectKeys": insert_case_data.unexpect_keys,
                    "delayTime": insert_case_data.delay_time, "historyCheck": history_check_list,
                    "createAt": insert_case_data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updateAt": insert_case_data.update_at.strftime("%Y-%m-%d %H:%M:%S")}
            return jsonify({"code": 200, "message": "添加成功", "content": data})


@case.route('/update', methods=('POST',))
@login_required
def case_update():
    token = request.headers["token"]
    request_data = json.loads(request.data.decode('utf-8', 'ignore'))
    case_id = request_data['caseId']
    case_name = request_data['caseName']
    description = request_data['description']
    method = request_data['method']
    url = request_data['url']
    port = request_data['port']
    params = request_data['params']
    headers = request_data['headers']
    re_headers = {}
    for data in headers:
        re_headers[data['headerKey']] = data['headerValue']
    set_up = request_data['setUp']
    if set_up != "":
        for sql_name in set_up.split(','):
            if SqlManage.query.filter_by(sql_name=sql_name).first() is None:
                return jsonify({"code": 300, "message": "sql标识不存在！"})
    expect_res = request_data['expectRes']
    expect_res_str_list = []
    for expect in expect_res:
        expect_res_str_list.append(json.dumps(expect))
    expect_res_str = '|'.join(expect_res_str_list)
    update_by = get_user(token)
    status = request_data['status']
    group_id = request_data['groupId']
    db_case_by_name = CaseManage.query.filter_by(case_name=case_name).first()
    if db_case_by_name and case_id != db_case_by_name.case_id:
        return jsonify({"code": 300, "message": "用例名称重复！"})
    db_case = CaseManage.query.filter_by(case_id=case_id).first()
    expect_keys = request_data["expectKeys"]
    unexpect_keys = request_data["unexpectKeys"]
    delay_time = request_data["delayTime"]
    if "historyCheck" not in list(request_data.keys()):
        if db_case:
            re_url = re.match("(http|https)://[^\s]+", url)
            if re_url is None:
                return jsonify({"code": 300, "message": "url不合法！"})
            if status not in [0, 1]:
                return jsonify({"code": 300, "message": "status不合法！"})
            if method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                return jsonify({"code": 300, "message": "请求方式不合法！"})
            if method == "GET" or method == "DELETE":
                get_params_str_list = []
                for param in params:
                    get_params_str_list.append(json.dumps(param))
                get_params_str = '|'.join(get_params_str_list)
                db_case.case_name = case_name
                db_case.description = description
                db_case.url = url
                db_case.port = port
                db_case.params = get_params_str
                db_case.headers = re_headers
                db_case.set_up = set_up
                db_case.expect_res = expect_res_str
                db_case.expect_keys = expect_keys
                db_case.unexpect_keys = unexpect_keys
                db_case.update_by = update_by
                db_case.status = status
                db_case.group_id = group_id
                db_case.method = method
                db_case.delay_time = delay_time
                db_case.history_check = None
            else:
                db_case.case_name = case_name
                db_case.description = description
                db_case.url = url
                db_case.port = port
                db_case.params = json.dumps(params)
                db_case.headers = re_headers
                db_case.set_up = set_up
                db_case.expect_res = expect_res_str
                db_case.expect_keys = expect_keys
                db_case.unexpect_keys = unexpect_keys
                db_case.update_by = update_by
                db_case.status = status
                db_case.group_id = group_id
                db_case.method = method
                db_case.delay_time = delay_time
                db_case.history_check = None
        else:
            return jsonify({"code": 200, "message": "用例不存在"})
    else:
        if db_case:
            re_url = re.match("(http|https)://[^\s]+", url)
            if re_url is None:
                return jsonify({"code": 300, "message": "url不合法！"})
            if status not in [0, 1]:
                return jsonify({"code": 300, "message": "status不合法！"})
            if method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                return jsonify({"code": 300, "message": "请求方式不合法！"})
            history_check = request_data['historyCheck']
            if history_check != None:
                history_check_str_list = []
                for his in history_check:
                    history_check_str_list.append(json.dumps(his))
                history_check_str = '|'.join(history_check_str_list)
                if method == "GET" or method == "DELETE":
                    get_params_str_list = []
                    for param in params:
                        get_params_str_list.append(json.dumps(param))
                    get_params_str = '|'.join(get_params_str_list)
                    db_case.case_name = case_name
                    db_case.description = description
                    db_case.url = url
                    db_case.port = port
                    db_case.params = get_params_str
                    db_case.headers = re_headers
                    db_case.set_up = set_up
                    db_case.expect_res = expect_res_str
                    db_case.expect_keys = expect_keys
                    db_case.unexpect_keys = unexpect_keys
                    db_case.update_by = update_by
                    db_case.status = status
                    db_case.group_id = group_id
                    db_case.method = method
                    db_case.delay_time = delay_time
                    db_case.history_check = history_check_str
                else:
                    db_case.case_name = case_name
                    db_case.description = description
                    db_case.url = url
                    db_case.port = port
                    db_case.params = json.dumps(params)
                    db_case.headers = re_headers
                    db_case.set_up = set_up
                    db_case.expect_res = expect_res_str
                    db_case.expect_keys = expect_keys
                    db_case.unexpect_keys = unexpect_keys
                    db_case.update_by = update_by
                    db_case.status = status
                    db_case.group_id = group_id
                    db_case.method = method
                    db_case.delay_time = delay_time
                    db_case.history_check = history_check_str
            else:
                if method == "GET" or method == "DELETE":
                    get_params_str_list = []
                    for param in params:
                        get_params_str_list.append(json.dumps(param))
                    get_params_str = '|'.join(get_params_str_list)
                    db_case.case_name = case_name
                    db_case.description = description
                    db_case.url = url
                    db_case.port = port
                    db_case.params = get_params_str
                    db_case.headers = re_headers
                    db_case.set_up = set_up
                    db_case.expect_res = expect_res_str
                    db_case.expect_keys = expect_keys
                    db_case.unexpect_keys = unexpect_keys
                    db_case.update_by = update_by
                    db_case.status = status
                    db_case.group_id = group_id
                    db_case.method = method
                    db_case.delay_time = delay_time
                    db_case.history_check = None
                else:
                    db_case.case_name = case_name
                    db_case.description = description
                    db_case.url = url
                    db_case.port = port
                    db_case.params = json.dumps(params)
                    db_case.headers = re_headers
                    db_case.set_up = set_up
                    db_case.expect_res = expect_res_str
                    db_case.expect_keys = expect_keys
                    db_case.unexpect_keys = unexpect_keys
                    db_case.update_by = update_by
                    db_case.status = status
                    db_case.group_id = group_id
                    db_case.method = method
                    db_case.delay_time = delay_time
                    db_case.history_check = None
        else:
            return jsonify({"code": 200, "message": "用例不存在"})
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"code": 300, "message": str(e)})
    update_case_data = CaseManage.query.filter_by(case_id=case_id).first()
    expect_res_list = []
    for expect in update_case_data.expect_res.split('|'):
        expect_res_list.append(json.loads(expect))
    if update_case_data.method == "GET" or update_case_data.method == "DELETE":
        get_params_list = []
        for param in update_case_data.params.split('|'):
            get_params_list.append(json.loads(param))
        if update_case_data.history_check is None:
            data = {"caseId": update_case_data.case_id, "caseName": update_case_data.case_name,
                    "caseSign": update_case_data.case_sign, "setUp": update_case_data.set_up,
                    "description": update_case_data.description, "method": update_case_data.method,
                    "url": update_case_data.url, "port": update_case_data.port,
                    "params": get_params_list, "headers": update_case_data.headers, "expectRes": expect_res_list,
                    "createBy": update_case_data.create_by, "updateBy": update_case_data.update_by,
                    "status": update_case_data.status, "groupId": update_case_data.group_id,
                    "expectKeys": update_case_data.expect_keys,
                    "unexpectKeys": update_case_data.unexpect_keys, "delayTime": update_case_data.delay_time,
                    "historyCheck": update_case_data.history_check,
                    "createAt": update_case_data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updateAt": update_case_data.update_at.strftime("%Y-%m-%d %H:%M:%S")}
            return jsonify({"code": 200, "message": "修改成功", "content": data})
        else:
            history_check_list = []
            for his in update_case_data.history_check.split('|'):
                history_check_list.append(json.loads(his))
            data = {"caseId": update_case_data.case_id, "caseName": update_case_data.case_name,
                    "caseSign": update_case_data.case_sign, "setUp": update_case_data.set_up,
                    "description": update_case_data.description, "method": update_case_data.method,
                    "url": update_case_data.url, "port": update_case_data.port,
                    "params": get_params_list, "headers": update_case_data.headers, "expectRes": expect_res_list,
                    "createBy": update_case_data.create_by, "updateBy": update_case_data.update_by,
                    "status": update_case_data.status, "groupId": update_case_data.group_id,
                    "expectKeys": update_case_data.expect_keys,
                    "unexpectKeys": update_case_data.unexpect_keys, "delayTime": update_case_data.delay_time,
                    "historyCheck": history_check_list,
                    "createAt": update_case_data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updateAt": update_case_data.update_at.strftime("%Y-%m-%d %H:%M:%S")}
            return jsonify({"code": 200, "message": "修改成功", "content": data})
    else:
        if update_case_data.history_check is None:
            data = {"caseId": update_case_data.case_id, "caseName": update_case_data.case_name,
                    "caseSign": update_case_data.case_sign, "setUp": update_case_data.set_up,
                    "description": update_case_data.description, "method": update_case_data.method,
                    "url": update_case_data.url, "port": update_case_data.port,
                    "params": json.loads(update_case_data.params), "headers": update_case_data.headers,
                    "expectRes": expect_res_list,
                    "createBy": update_case_data.create_by, "updateBy": update_case_data.update_by,
                    "status": update_case_data.status, "groupId": update_case_data.group_id,
                    "expectKeys": update_case_data.expect_keys,
                    "unexpectKeys": update_case_data.unexpect_keys, "delayTime": update_case_data.delay_time,
                    "historyCheck": update_case_data.history_check,
                    "createAt": update_case_data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updateAt": update_case_data.update_at.strftime("%Y-%m-%d %H:%M:%S")}
            return jsonify({"code": 200, "message": "修改成功", "content": data})
        else:
            history_check_list = []
            for his in update_case_data.history_check.split('|'):
                history_check_list.append(json.loads(his))
            data = {"caseId": update_case_data.case_id, "caseName": update_case_data.case_name,
                    "caseSign": update_case_data.case_sign, "setUp": update_case_data.set_up,
                    "description": update_case_data.description, "method": update_case_data.method,
                    "url": update_case_data.url, "port": update_case_data.port,
                    "params": json.loads(update_case_data.params), "headers": update_case_data.headers,
                    "expectRes": expect_res_list, "createBy": update_case_data.create_by,
                    "updateBy": update_case_data.update_by,
                    "status": update_case_data.status, "groupId": update_case_data.group_id,
                    "expectKeys": update_case_data.expect_keys,
                    "unexpectKeys": update_case_data.unexpect_keys, "delayTime": update_case_data.delay_time,
                    "historyCheck": history_check_list,
                    "createAt": update_case_data.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "updateAt": update_case_data.update_at.strftime("%Y-%m-%d %H:%M:%S")}
            return jsonify({"code": 200, "message": "修改成功", "content": data})


@case.route('/list', methods=('POST',))
@login_required
def case_list():
    token = request.headers["token"]
    user = get_user(token)
    role = User.query.filter_by(user=user).first().role
    cases_data = []
    limit = int(request.get_json().get('limit'))
    if limit == '':
        return jsonify({"code": 300, "message": "参数非法！"})
    page = int(request.get_json().get('page'))
    if page == '':
        return jsonify({"code": 300, "message": "参数非法！"})
    # 管理员权限展示
    if role == "admin":
        if "groupName" not in request.get_json().keys():
            if 'caseName' not in request.get_json().keys():
                db_cases = CaseManage.query.order_by(CaseManage.update_at.desc()).all()
                if len(db_cases) != 0:
                    for case in db_cases:
                        group_name = CaseGroup.query.filter_by(group_id=case.group_id).first().group_name
                        expect_res_list = []
                        for expect in case.expect_res.split('|'):
                            expect_res_list.append(json.loads(expect))
                        detail_headers = []
                        for key, value in eval(case.headers).items():
                            detail_header = {'headerKey': key, 'headerValue': value}
                            detail_headers.append(detail_header)
                        if case.method == "GET" or case.method == "DELETE":
                            get_params_list = []
                            for param in case.params.split('|'):
                                get_params_list.append(json.loads(param))
                            if case.history_check is None:
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": get_params_list, "headers": detail_headers,
                                             "groupName": group_name, "setUp": case.set_up,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupId": case.group_id,
                                             "expectKeys": case.expect_keys, "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": case.history_check,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                            else:
                                history_check_list = []
                                for his in case.history_check.split('|'):
                                    history_check_list.append(json.loads(his))
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": get_params_list, "headers": detail_headers, "setUp": case.set_up,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status, "groupName": group_name,
                                             "groupId": case.group_id, "expectKeys": case.expect_keys,
                                             "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": history_check_list,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                        else:
                            # params = ast.literal_eval(case.params)
                            if case.history_check is None:
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": json.loads(case.params), "headers": detail_headers,
                                             "groupName": group_name, "setUp": case.set_up,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupId": case.group_id,
                                             "expectKeys": case.expect_keys, "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": case.history_check,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                            else:
                                history_check_list = []
                                for his in case.history_check.split('|'):
                                    history_check_list.append(json.loads(his))
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": json.loads(case.params), "headers": detail_headers,
                                             "setUp": case.set_up,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status, "groupName": group_name,
                                             "groupId": case.group_id, "expectKeys": case.expect_keys,
                                             "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": history_check_list,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                        cases_data.append(case_data)
                    start = (page - 1) * limit
                    end = page * limit if len(cases_data) > page * limit else start + len(cases_data)
                    ret = cases_data[start:end]
                    return jsonify({"code": 200, "message": "查询成功", "totalCount": len(cases_data), "contents": ret})
                else:
                    return jsonify(
                        {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})
            else:
                case_name = request.get_json().get('caseName')
                db_cases = CaseManage.query.filter(
                    CaseManage.case_name.like('%{keyword}%'.format(keyword=case_name))).order_by(
                    CaseManage.update_at.desc()).all()
                if len(db_cases) != 0:
                    for case in db_cases:
                        group_name = CaseGroup.query.filter_by(group_id=case.group_id).first().group_name
                        expect_res_list = []
                        for expect in case.expect_res.split('|'):
                            expect_res_list.append(json.loads(expect))
                        detail_headers = []
                        for key, value in eval(case.headers).items():
                            detail_header = {'headerKey': key, 'headerValue': value}
                            detail_headers.append(detail_header)
                        if case.method == "GET" or case.method == "DELETE":
                            get_params_list = []
                            for param in case.params.split('|'):
                                get_params_list.append(json.loads(param))
                            if case.history_check is None:
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": get_params_list, "headers": detail_headers,
                                             "groupName": group_name, "setUp": case.set_up,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupId": case.group_id,
                                             "expectKeys": case.expect_keys, "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": case.history_check,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                            else:
                                history_check_list = []
                                for his in case.history_check.split('|'):
                                    history_check_list.append(json.loads(his))
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": get_params_list, "headers": detail_headers, "setUp": case.set_up,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status, "groupName": group_name,
                                             "groupId": case.group_id, "expectKeys": case.expect_keys,
                                             "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": history_check_list,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                        else:
                            # params = ast.literal_eval(case.params)
                            if case.history_check is None:
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": json.loads(case.params), "headers": detail_headers,
                                             "groupName": group_name, "setUp": case.set_up,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupId": case.group_id,
                                             "expectKeys": case.expect_keys, "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": case.history_check,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                            else:
                                history_check_list = []
                                for his in case.history_check.split('|'):
                                    history_check_list.append(json.loads(his))
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": json.loads(case.params), "headers": detail_headers,
                                             "setUp": case.set_up,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status, "groupName": group_name,
                                             "groupId": case.group_id, "expectKeys": case.expect_keys,
                                             "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": history_check_list,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                        cases_data.append(case_data)
                    start = (page - 1) * limit
                    end = page * limit if len(cases_data) > page * limit else start + len(cases_data)
                    ret = cases_data[start:end]
                    return jsonify({"code": 200, "message": "查询成功", "totalCount": len(cases_data), "contents": ret})
                else:
                    return jsonify(
                        {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})
        else:
            if 'caseName' not in request.get_json().keys():
                group_name = request.get_json().get('groupName')
                groups = CaseGroup.query.filter(
                    CaseGroup.group_name.like('%{keyword}%'.format(keyword=group_name))).all()
                group_id_list = [group.group_id for group in groups]
                db_cases = []
                for g_id in group_id_list:
                    db_cases.extend(CaseManage.query.filter(CaseManage.group_id == g_id).order_by(
                        CaseManage.update_at.desc()).all())
                if len(db_cases) != 0:
                    for case in db_cases:
                        group_name = CaseGroup.query.filter_by(group_id=case.group_id).first().group_name
                        expect_res_list = []
                        for expect in case.expect_res.split('|'):
                            expect_res_list.append(json.loads(expect))
                        detail_headers = []
                        for key, value in eval(case.headers).items():
                            detail_header = {'headerKey': key, 'headerValue': value}
                            detail_headers.append(detail_header)
                        if case.method == "GET" or case.method == "DELETE":
                            get_params_list = []
                            for param in case.params.split('|'):
                                get_params_list.append(json.loads(param))
                            if case.history_check is None:
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": get_params_list, "headers": detail_headers,
                                             "groupName": group_name, "setUp": case.set_up,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupId": case.group_id,
                                             "expectKeys": case.expect_keys, "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": case.history_check,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                            else:
                                history_check_list = []
                                for his in case.history_check.split('|'):
                                    history_check_list.append(json.loads(his))
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": get_params_list, "headers": detail_headers,
                                             "setUp": case.set_up, "groupName": group_name,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupId": case.group_id, "expectKeys": case.expect_keys,
                                             "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": history_check_list,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                        else:
                            # params = ast.literal_eval(case.params)
                            if case.history_check is None:
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": json.loads(case.params), "headers": detail_headers,
                                             "groupName": group_name, "setUp": case.set_up,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupId": case.group_id,
                                             "expectKeys": case.expect_keys, "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": case.history_check,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                            else:
                                history_check_list = []
                                for his in case.history_check.split('|'):
                                    history_check_list.append(json.loads(his))
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": json.loads(case.params), "headers": detail_headers,
                                             "setUp": case.set_up, "groupName": group_name,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupId": case.group_id, "expectKeys": case.expect_keys,
                                             "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": history_check_list,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                        cases_data.append(case_data)
                    start = (page - 1) * limit
                    end = page * limit if len(cases_data) > page * limit else start + len(cases_data)
                    ret = cases_data[start:end]
                    return jsonify({"code": 200, "message": "查询成功", "totalCount": len(cases_data), "contents": ret})
                else:
                    return jsonify(
                        {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})
            else:
                group_name = request.get_json().get('groupName')
                case_name = request.get_json().get('caseName')
                groups = CaseGroup.query.filter(
                    CaseGroup.group_name.like('%{keyword}%'.format(keyword=group_name))).all()
                group_id_list = [group.group_id for group in groups]
                db_cases = []
                for g_id in group_id_list:
                    db_cases.extend(CaseManage.query.filter(CaseManage.group_id == g_id, CaseManage.case_name.like(
                        '%{keyword}%'.format(keyword=case_name))).order_by(
                        CaseManage.update_at.desc()).all())
                if len(db_cases) != 0:
                    for case in db_cases:
                        group_name = CaseGroup.query.filter_by(group_id=case.group_id).first().group_name
                        expect_res_list = []
                        for expect in case.expect_res.split('|'):
                            expect_res_list.append(json.loads(expect))
                        detail_headers = []
                        for key, value in eval(case.headers).items():
                            detail_header = {'headerKey': key, 'headerValue': value}
                            detail_headers.append(detail_header)
                        if case.method == "GET" or case.method == "DELETE":
                            get_params_list = []
                            for param in case.params.split('|'):
                                get_params_list.append(json.loads(param))
                            if case.history_check is None:
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": get_params_list, "headers": detail_headers,
                                             "groupName": group_name, "setUp": case.set_up,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupId": case.group_id,
                                             "expectKeys": case.expect_keys, "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": case.history_check,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                            else:
                                history_check_list = []
                                for his in case.history_check.split('|'):
                                    history_check_list.append(json.loads(his))
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": get_params_list, "headers": detail_headers,
                                             "setUp": case.set_up, "groupName": group_name,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupId": case.group_id, "expectKeys": case.expect_keys,
                                             "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": history_check_list,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                        else:
                            # params = ast.literal_eval(case.params)
                            if case.history_check is None:
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": json.loads(case.params), "headers": detail_headers,
                                             "groupName": group_name, "setUp": case.set_up,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupId": case.group_id,
                                             "expectKeys": case.expect_keys, "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": case.history_check,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                            else:
                                history_check_list = []
                                for his in case.history_check.split('|'):
                                    history_check_list.append(json.loads(his))
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": json.loads(case.params), "headers": detail_headers,
                                             "setUp": case.set_up, "groupName": group_name,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupId": case.group_id, "expectKeys": case.expect_keys,
                                             "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": history_check_list,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                        cases_data.append(case_data)
                    start = (page - 1) * limit
                    end = page * limit if len(cases_data) > page * limit else start + len(cases_data)
                    ret = cases_data[start:end]
                    return jsonify({"code": 200, "message": "查询成功", "totalCount": len(cases_data), "contents": ret})
                else:
                    return jsonify(
                        {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})
    # 普通用户权限展示
    else:
        if "groupName" not in request.get_json().keys():
            if 'caseName' not in request.get_json().keys():
                db_groups_role = CaseGroup.query.filter(CaseGroup.is_del == 0, CaseGroup.service == role).all()
                group_id_list = [group.group_id for group in db_groups_role]
                db_cases = []
                for g_id in group_id_list:
                    db_cases.extend(CaseManage.query.filter(CaseManage.group_id == g_id).order_by(
                        CaseManage.update_at.desc()).all())
                if len(db_cases) != 0:
                    for case in db_cases:
                        group_name = CaseGroup.query.filter_by(group_id=case.group_id).first().group_name
                        expect_res_list = []
                        for expect in case.expect_res.split('|'):
                            expect_res_list.append(json.loads(expect))
                        detail_headers = []
                        for key, value in eval(case.headers).items():
                            detail_header = {'headerKey': key, 'headerValue': value}
                            detail_headers.append(detail_header)
                        if case.method == "GET" or case.method == "DELETE":
                            get_params_list = []
                            for param in case.params.split('|'):
                                get_params_list.append(json.loads(param))
                            if case.history_check is None:
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": get_params_list, "headers": detail_headers,
                                             "groupName": group_name, "setUp": case.set_up,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupId": case.group_id,
                                             "expectKeys": case.expect_keys, "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": case.history_check,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                            else:
                                history_check_list = []
                                for his in case.history_check.split('|'):
                                    history_check_list.append(json.loads(his))
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": get_params_list, "headers": detail_headers,
                                             "setUp": case.set_up, "groupName": group_name,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupId": case.group_id, "expectKeys": case.expect_keys,
                                             "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": history_check_list,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                        else:
                            # params = ast.literal_eval(case.params)
                            if case.history_check is None:
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": json.loads(case.params), "headers": detail_headers,
                                             "groupName": group_name, "setUp": case.set_up,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupId": case.group_id, "expectKeys": case.expect_keys,
                                             "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": case.history_check,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                            else:
                                history_check_list = []
                                for his in case.history_check.split('|'):
                                    history_check_list.append(json.loads(his))
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": json.loads(case.params), "headers": detail_headers,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupName": group_name, "setUp": case.set_up,
                                             "groupId": case.group_id, "expectKeys": case.expect_keys,
                                             "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": history_check_list,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                        cases_data.append(case_data)
                    start = (page - 1) * limit
                    end = page * limit if len(cases_data) > page * limit else start + len(cases_data)
                    ret = cases_data[start:end]
                    return jsonify({"code": 200, "message": "查询成功", "totalCount": len(cases_data), "contents": ret})
                else:
                    return jsonify(
                        {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})
            else:
                case_name = request.get_json().get('caseName')
                db_groups_role = CaseGroup.query.filter(CaseGroup.is_del == 0, CaseGroup.service == role).all()
                group_id_list = [group.group_id for group in db_groups_role]
                db_cases = []
                for g_id in group_id_list:
                    db_cases.extend(CaseManage.query.filter(CaseManage.group_id == g_id,
                                                            CaseManage.case_name == case_name).order_by(
                        CaseManage.update_at.desc()).all())
                if len(db_cases) != 0:
                    for case in db_cases:
                        group_name = CaseGroup.query.filter_by(group_id=case.group_id).first().group_name
                        expect_res_list = []
                        for expect in case.expect_res.split('|'):
                            expect_res_list.append(json.loads(expect))
                        detail_headers = []
                        for key, value in eval(case.headers).items():
                            detail_header = {'headerKey': key, 'headerValue': value}
                            detail_headers.append(detail_header)
                        if case.method == "GET" or case.method == "DELETE":
                            get_params_list = []
                            for param in case.params.split('|'):
                                get_params_list.append(json.loads(param))
                            if case.history_check is None:
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": get_params_list, "headers": detail_headers,
                                             "groupName": group_name, "setUp": case.set_up,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupId": case.group_id,
                                             "expectKeys": case.expect_keys, "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": case.history_check,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                            else:
                                history_check_list = []
                                for his in case.history_check.split('|'):
                                    history_check_list.append(json.loads(his))
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": get_params_list, "headers": detail_headers,
                                             "setUp": case.set_up, "groupName": group_name,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupId": case.group_id, "expectKeys": case.expect_keys,
                                             "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": history_check_list,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                        else:
                            # params = ast.literal_eval(case.params)
                            if case.history_check is None:
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": json.loads(case.params), "headers": detail_headers,
                                             "groupName": group_name, "setUp": case.set_up,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupId": case.group_id,
                                             "expectKeys": case.expect_keys, "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": case.history_check,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                            else:
                                history_check_list = []
                                for his in case.history_check.split('|'):
                                    history_check_list.append(json.loads(his))
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": json.loads(case.params), "headers": detail_headers,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupName": group_name, "setUp": case.set_up,
                                             "groupId": case.group_id, "expectKeys": case.expect_keys,
                                             "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": history_check_list,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                        cases_data.append(case_data)
                    start = (page - 1) * limit
                    end = page * limit if len(cases_data) > page * limit else start + len(cases_data)
                    ret = cases_data[start:end]
                    return jsonify({"code": 200, "message": "查询成功", "totalCount": len(cases_data), "contents": ret})
                else:
                    return jsonify(
                        {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})
        else:
            if 'caseName' not in request.get_json().keys():
                group_name = request.get_json().get('groupName')
                db_groups_role = CaseGroup.query.filter(CaseGroup.is_del == 0, CaseGroup.service == role,
                                                        CaseGroup.group_name.like(
                                                            '%{keyword}%'.format(keyword=group_name))).all()
                group_id_list = [group.group_id for group in db_groups_role]
                db_cases = []
                for g_id in group_id_list:
                    db_cases.extend(CaseManage.query.filter(CaseManage.group_id == g_id).order_by(
                        CaseManage.update_at.desc()).all())
                if len(db_cases) != 0:
                    for case in db_cases:
                        group_name = CaseGroup.query.filter_by(group_id=case.group_id).first().group_name
                        expect_res_list = []
                        for expect in case.expect_res.split('|'):
                            expect_res_list.append(json.loads(expect))
                        detail_headers = []
                        for key, value in eval(case.headers).items():
                            detail_header = {'headerKey': key, 'headerValue': value}
                            detail_headers.append(detail_header)
                        if case.method == "GET" or case.method == "DELETE":
                            get_params_list = []
                            for param in case.params.split('|'):
                                get_params_list.append(json.loads(param))
                            if case.history_check is None:
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": get_params_list, "headers": detail_headers,
                                             "groupName": group_name, "setUp": case.set_up,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupId": case.group_id,
                                             "expectKeys": case.expect_keys, "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": case.history_check,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                            else:
                                history_check_list = []
                                for his in case.history_check.split('|'):
                                    history_check_list.append(json.loads(his))
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": get_params_list, "headers": detail_headers,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupName": group_name, "setUp": case.set_up,
                                             "groupId": case.group_id, "expectKeys": case.expect_keys,
                                             "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": history_check_list,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                        else:
                            # params = ast.literal_eval(case.params)
                            if case.history_check is None:
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": json.loads(case.params), "headers": detail_headers,
                                             "groupName": group_name, "setUp": case.set_up,
                                             "groupId": case.group_id,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "expectKeys": case.expect_keys, "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": case.history_check,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                            else:
                                history_check_list = []
                                for his in case.history_check.split('|'):
                                    history_check_list.append(json.loads(his))
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": json.loads(case.params), "headers": detail_headers,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupName": group_name, "setUp": case.set_up,
                                             "groupId": case.group_id, "expectKeys": case.expect_keys,
                                             "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": history_check_list,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                        cases_data.append(case_data)
                    start = (page - 1) * limit
                    end = page * limit if len(cases_data) > page * limit else start + len(cases_data)
                    ret = cases_data[start:end]
                    return jsonify({"code": 200, "message": "查询成功", "totalCount": len(cases_data), "contents": ret})
                else:
                    return jsonify(
                        {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})
            else:
                group_name = request.get_json().get('groupName')
                case_name = request.get_json().get('caseName')
                db_groups_role = CaseGroup.query.filter(CaseGroup.is_del == 0, CaseGroup.service == role,
                                                        CaseGroup.group_name.like(
                                                            '%{keyword}%'.format(keyword=group_name))).all()
                group_id_list = [group.group_id for group in db_groups_role]
                db_cases = []
                for g_id in group_id_list:
                    db_cases.extend(
                        CaseManage.query.filter(CaseManage.group_id == g_id,
                                                CaseManage.case_name == case_name).order_by(
                            CaseManage.update_at.desc()).all())
                if len(db_cases) != 0:
                    for case in db_cases:
                        group_name = CaseGroup.query.filter_by(group_id=case.group_id).first().group_name
                        expect_res_list = []
                        for expect in case.expect_res.split('|'):
                            expect_res_list.append(json.loads(expect))
                        detail_headers = []
                        for key, value in eval(case.headers).items():
                            detail_header = {'headerKey': key, 'headerValue': value}
                            detail_headers.append(detail_header)
                        if case.method == "GET" or case.method == "DELETE":
                            get_params_list = []
                            for param in case.params.split('|'):
                                get_params_list.append(json.loads(param))
                            if case.history_check is None:
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": get_params_list, "headers": detail_headers,
                                             "groupName": group_name, "setUp": case.set_up,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupId": case.group_id,
                                             "expectKeys": case.expect_keys, "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": case.history_check,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                            else:
                                history_check_list = []
                                for his in case.history_check.split('|'):
                                    history_check_list.append(json.loads(his))
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": get_params_list, "headers": detail_headers,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupName": group_name, "setUp": case.set_up,
                                             "groupId": case.group_id, "expectKeys": case.expect_keys,
                                             "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": history_check_list,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                        else:
                            # params = ast.literal_eval(case.params)
                            if case.history_check is None:
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": json.loads(case.params), "headers": detail_headers,
                                             "groupName": group_name, "setUp": case.set_up,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupId": case.group_id,
                                             "expectKeys": case.expect_keys, "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": case.history_check,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                            else:
                                history_check_list = []
                                for his in case.history_check.split('|'):
                                    history_check_list.append(json.loads(his))
                                case_data = {"caseId": case.case_id, "caseName": case.case_name,
                                             "caseSign": case.case_sign, "description": case.description,
                                             "method": case.method, "url": case.url, "port": case.port,
                                             "params": json.loads(case.params), "headers": detail_headers,
                                             "expectRes": expect_res_list, "createBy": case.create_by,
                                             "updateBy": case.update_by, "status": case.status,
                                             "groupName": group_name, "setUp": case.set_up,
                                             "groupId": case.group_id, "expectKeys": case.expect_keys,
                                             "unexpectKeys": case.unexpect_keys,
                                             "delayTime": case.delay_time, "historyCheck": history_check_list,
                                             "createAt": case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                                             "updateAt": case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                        cases_data.append(case_data)
                    start = (page - 1) * limit
                    end = page * limit if len(cases_data) > page * limit else start + len(cases_data)
                    ret = cases_data[start:end]
                    return jsonify({"code": 200, "message": "查询成功", "totalCount": len(cases_data), "contents": ret})
                else:
                    return jsonify(
                        {"code": 200, "totalCount": 0, "message": "未查询到数据!", "contents": []})


@case.route('/detail', methods=('POST',))
@login_required
def case_detail():
    request_data = json.loads(request.data)
    case_id = request_data['caseId']
    db_case = CaseManage.query.filter_by(case_id=case_id).first()
    detail_headers = []
    for key, value in eval(db_case.headers).items():
        detail_header = {'headerKey': key, 'headerValue': value}
        detail_headers.append(detail_header)
    expect_res_list = []
    for expect in db_case.expect_res.split('|'):
        expect_res_list.append(json.loads(expect))
    if db_case:
        if db_case.method == "GET" or db_case.method == "DELETE":
            get_params_list = []
            for param in db_case.params.split('|'):
                get_params_list.append(json.loads(param))
            if db_case.history_check is None:
                data = {"caseId": db_case.case_id, "caseName": db_case.case_name, "caseSign": db_case.case_sign,
                        "description": db_case.description, "method": db_case.method, "setUp": db_case.set_up,
                        "url": db_case.url, "port": db_case.port, "params": get_params_list, "headers": detail_headers,
                        "expectRes": expect_res_list, "createBy": db_case.create_by, "updateBy": db_case.update_by,
                        "status": db_case.status, "groupId": db_case.group_id, "expectKeys": db_case.expect_keys,
                        "unexpectKeys": db_case.unexpect_keys, "delayTime": db_case.delay_time,
                        "historyCheck": db_case.history_check,
                        "createAt": db_case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "updateAt": db_case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                return jsonify({"code": 200, "message": "查询成功", "content": data})
            else:
                history_check_list = []
                for his in db_case.history_check.split('|'):
                    history_check_list.append(json.loads(his))
                data = {"caseId": db_case.case_id, "caseName": db_case.case_name, "caseSign": db_case.case_sign,
                        "description": db_case.description, "method": db_case.method, "setUp": db_case.set_up,
                        "url": db_case.url, "port": db_case.port, "params": get_params_list,
                        "headers": detail_headers, "expectRes": expect_res_list, "createBy": db_case.create_by,
                        "updateBy": db_case.update_by, "delayTime": db_case.delay_time,
                        "status": db_case.status, "groupId": db_case.group_id, "expectKeys": db_case.expect_keys,
                        "unexpectKeys": db_case.unexpect_keys, "historyCheck": history_check_list,
                        "createAt": db_case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "updateAt": db_case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                return jsonify({"code": 200, "message": "查询成功", "content": data})
        else:
            if db_case.history_check is None:
                data = {"caseId": db_case.case_id, "caseName": db_case.case_name, "caseSign": db_case.case_sign,
                        "description": db_case.description, "method": db_case.method,
                        "url": db_case.url, "port": db_case.port, "params": json.loads(db_case.params),
                        "headers": detail_headers, "setUp": db_case.set_up,
                        "expectRes": expect_res_list, "createBy": db_case.create_by, "updateBy": db_case.update_by,
                        "status": db_case.status, "groupId": db_case.group_id, "expectKeys": db_case.expect_keys,
                        "unexpectKeys": db_case.unexpect_keys, "delayTime": db_case.delay_time,
                        "historyCheck": db_case.history_check,
                        "createAt": db_case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "updateAt": db_case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                return jsonify({"code": 200, "message": "查询成功", "content": data})
            else:
                history_check_list = []
                for his in db_case.history_check.split('|'):
                    history_check_list.append(json.loads(his))
                data = {"caseId": db_case.case_id, "caseName": db_case.case_name, "caseSign": db_case.case_sign,
                        "description": db_case.description, "method": db_case.method, "setUp": db_case.set_up,
                        "url": db_case.url, "port": db_case.port, "params": json.loads(db_case.params),
                        "headers": detail_headers, "expectRes": expect_res_list, "createBy": db_case.create_by,
                        "updateBy": db_case.update_by, "delayTime": db_case.delay_time,
                        "status": db_case.status, "groupId": db_case.group_id, "expectKeys": db_case.expect_keys,
                        "unexpectKeys": db_case.unexpect_keys, "historyCheck": history_check_list,
                        "createAt": db_case.create_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "updateAt": db_case.update_at.strftime("%Y-%m-%d %H:%M:%S")}
                return jsonify({"code": 200, "message": "查询成功", "content": data})
    else:
        return jsonify({"code": 200, "message": "用例不存在"})


@case.route('/delete', methods=('POST',))
@login_required
def case_delete():
    case_id = request.get_json().get('caseId')
    status = request.get_json().get('status')
    tb_case = CaseManage.query.filter_by(case_id=case_id).first()
    if status == 1:
        return jsonify({"code": 200, "message": "启用状态的用例不能删除！"})
    if tb_case:
        try:
            db.session.delete(tb_case)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"code": 300, "message": str(e)})
        return jsonify({"code": 200, "message": "删除成功！"})
    else:
        return jsonify({"code": 300, "message": "用例不存在！"})


@case.route('/debug', methods=('POST',))
@login_required
def case_debug():
    e = Execute()
    request_data = json.loads(request.data.decode('utf-8', 'ignore'))
    case_name = request_data['caseName']
    delete_key_list = extract_delete_key(case_name)
    group_id = request_data['groupId']
    proj_type = CaseGroup.query.filter_by(group_id=group_id).first().proj_type
    encode_type = CaseGroup.query.filter_by(group_id=group_id).first().encode_type
    method = request_data['method']
    url = request_data['url']
    url_match = re.match("(http|https)://[^\s]+", url)
    if url_match is None:
        return jsonify({"code": 300, "message": "url不合法！"})
    # 处理URL，是否有全局变量，有就替换，可替换多个
    re_url = url
    if len(e.extract_variables(url)) != 0:
        for var in e.extract_variables(url):
            var_data = GlobalData.query.filter_by(name=var).first()
            if (var_data is not None and var_data.group_id == "0") or (
                    var_data is not None and str(group_id) in var_data.group_id):
                if var_data.type == "string":
                    real_value = eval('str')(var_data.value)
                else:
                    real_value = eval(var_data.type)(var_data.value.value)
                re_url = e.replace_var(re_url, var, real_value)
            else:
                return jsonify({"code": 300, "message": "url:{}全局变量不存在！或作用域不在此用例集!".format(var)})
    else:
        re_url = url
    if request_data['port'] != '':
        port_var_list = e.extract_variables(request_data['port'])
        if len(port_var_list) != 0:
            var_port = GlobalData.query.filter_by(name=port_var_list[0]).first().value
            re_url_list = re_url.split('//')
            url_path = re_url.split('//')[1]
            ip_str = url_path.split('/')[0]
            ip_port_str = ip_str + ':' + var_port
            re_url_path_list = url_path.split('/')
            re_url_path_list[0] = ip_port_str
            re_url_str_path = '/'.join(re_url_path_list)
            re_url_list[1] = re_url_str_path
            re_url = '//'.join(re_url_list)
        else:
            re_url_list = re_url.split('//')
            url_path = re_url.split('//')[1]
            ip_str = url_path.split('/')[0]
            ip_port_str = ip_str + ':' + request_data['port']
            re_url_path_list = url_path.split('/')
            re_url_path_list[0] = ip_port_str
            re_url_str_path = '/'.join(re_url_path_list)
            re_url_list[1] = re_url_str_path
            re_url = '//'.join(re_url_list)
    headers = request_data['headers']
    re_headers = {}
    for data in headers:
        re_headers[data['headerKey']] = data['headerValue']
    set_up = request_data['setUp']
    if set_up != "":
        for sql_name in set_up.split(','):
            sql = SqlManage.query.filter_by(sql_name=sql_name).first()
            if sql is None:
                return jsonify({"code": 300, "message": "sql标识不存在！"})
            else:
                db = DbLibrary(sql.database)
                if sql.type == "select":
                    db.db_select(sql.value)
                elif sql.type == "insert":
                    db.db_insert(sql.value)
                elif sql.type == "update":
                    db.db_update(sql.value)
                else:
                    db.db_delete(sql.value)
                db.db_close()
    # 处理header，是否有全局变量，有就替换
    for key, value in re_headers.items():
        if len(e.extract_variables(value)) != 0:
            var_data = GlobalData.query.filter_by(name=e.extract_variables(value)[0]).first()
            if (var_data is not None and var_data.group_id == "0") or (
                    var_data is not None and str(group_id) in var_data.group_id):
                if var_data.type == "string":
                    real_value = eval('str')(var_data.value)
                else:
                    real_value = eval(var_data.type)(var_data.value)
                re_headers[key] = e.replace_var(value, e.extract_variables(value)[0], real_value)
            else:
                return jsonify(
                    {"code": 300, "message": "header：{} 全局变量不存在！或作用域不在此用例集!".format(e.extract_variables(value)[0])})
    params = request_data['params']
    # params全局变量替换:嵌套字典中有多个变量时，变量名不能相同,一个键值对中一个key 对应一个全局变量（value）
    get_params = {}
    if method == "GET" or method == "DELETE":
        for param in params:
            get_params[param['methodKey']] = param['methodValue']
        # get请求替换全局变量
        for key, value in get_params.items():
            if len(e.extract_variables(value)) != 0:
                if e.extract_variables(value)[0] == "btid":
                    real_value = eval('generate_btid()')
                    get_params[key] = e.replace_var(value, e.extract_variables(value)[0], real_value)
                else:
                    var_data = GlobalData.query.filter_by(name=e.extract_variables(value)[0]).first()
                    if (var_data is not None and var_data.group_id == "0") or (
                            var_data is not None and str(group_id) in var_data.group_id):
                        var_value = var_data.value
                        var_category = var_data.category
                        # sql变量判断
                        if var_category == "SQL":
                            if isinstance(var_value, str):
                                for sql_name in var_value.split(','):
                                    sql = SqlManage.query.filter_by(sql_name=sql_name).first()
                                    if sql is None:
                                        return jsonify({"code": 300, "message": "sql标识不存在！"})
                                    else:
                                        db = DbLibrary(sql.database)
                                        if sql.type == "select":
                                            var_value = db.db_select(sql.value)
                                        elif sql.type == "insert":
                                            db.db_insert(sql.value)
                                        elif sql.type == "update":
                                            db.db_update(sql.value)
                                        else:
                                            db.db_update(sql.value)
                                        db.db_close()
                        # case变量判断
                        elif var_category == "CASE":
                            case_id = var_value.split("_")[0]
                            jsonpath_str = var_value.split("_")[-1]
                            case_data = model_to_dict(CaseManage.query.filter_by(case_id=case_id).first())
                            refer_case_res = refer_case_response(case_data)
                            var_value = jsonpath(refer_case_res, jsonpath_str)[0]
                        else:
                            pass
                        if var_data.type == "string":
                            real_value = eval('str')(var_value)
                        else:
                            real_value = eval(var_data.type)(var_value)
                        get_params[key] = e.replace_var(value, e.extract_variables(value)[0], real_value)
                    else:
                        return jsonify(
                            {"code": 300,
                             "message": "paeams:{},全局变量不存在！或作用域不在此用例集!".format(e.extract_variables(value)[0])})
        # 根据valueType修改value
        for param in params:
            for key, value in get_params.items():
                if param['methodKey'] == key:
                    if type(value) != Config.type_dict[param['valueType']]:
                        get_params[key] = eval(param['valueType'])(value)
        # 判断参数是否需要加密（设备指纹）
        if proj_type != '' and proj_type in ['Android_v3', 'iOS_v3', 'web_v3', 'weapp_v3', 'android_v4', 'iOS_v4',
                                             'quickapp_v4']:
            fp_encode = FpEncoder(Config.TOOL_PATH, Config.ORGANIZATION, Config.AINFOKEY, Config.KEY_PATH,
                                  Config.TEMP_PATH)
            if proj_type == 'Android_v3':
                if encode_type == 'Android_v3_0':
                    pass
                if encode_type == 'Android_v3_1':
                    pass
                if encode_type == 'Android_v3_3':
                    pass
                if encode_type == 'Android_v3_5':
                    pass
                if encode_type == 'Android_v3_7':
                    get_params = fp_encode.fpencode_7(json.dumps(get_params))
                if encode_type == 'Android_v3_9':
                    get_params = fp_encode.fpencode_9(json.dumps(get_params))
                if encode_type == 'Android_v3_11':
                    get_params = fp_encode.fpencode_11(json.dumps(get_params))
            if proj_type != 'iOS_v3':
                if encode_type == 'iOS_v3_0':
                    pass
                if encode_type == 'iOS_v3_2':
                    pass
                if encode_type == 'iOS_v3_4':
                    get_params = fp_encode.fpencode_4(json.dumps(get_params))
                if encode_type == 'iOS_v3_6':
                    pass
                if encode_type == 'iOS_v3_8':
                    pass
                if encode_type == 'iOS_v3_10':
                    get_params = fp_encode.fpencode_10(json.dumps(get_params))
            if proj_type != 'weapp_v3':
                get_params = fp_encode.fpencode_weapp(json.dumps(get_params))
            if proj_type != 'web_v3':
                get_params = fp_encode.fpencode_web(json.dumps(get_params))
            if proj_type == 'android_v4':
                pass
            if proj_type == 'iOS_v4':
                pass
            if proj_type == 'quickapp_v4':
                pass
            get_params = eval(get_params)
        # 判断参数中是否需要删除键值对
        if len(delete_key_list) != 0:
            fp_data_dealer = FpDataDealer()
            get_params = fp_data_dealer.data_delete(get_params, delete_key_list[0])
    else:
        f = FindPath(target=params)
        # 全局变量列表
        var_list = []
        values_list = e.get_dict_all(params)
        for value in values_list:
            if len(e.extract_variables(value)) != 0:
                # var_name = "${" + e.extract_variables(value)[0] + "}"
                # var_list.append(var_name)
                var_list.append(e.extract_variables(value)[0])
        # 替换全局变量
        for var in var_list:
            # 添加生成btid函数为全局变量
            if var == "btid":
                path_list = f.in_value_path(value=var)
                for path in path_list:
                    path_str = "params" + path
                    value = eval('generate_btid()')
                    expression = path_str + "='" + value + "'"
                    exec(expression)
            elif "generate_btid_list" in var:
                path_list = f.in_value_path(value=var)
                for path in path_list:
                    path_str = "params" + path
                    value = eval(var)
                    expression = path_str + '=' + str(value)
                    exec(expression)
            elif var == "time_yyyyy_MM_dd":
                path_list = f.in_value_path(value=var)
                for path in path_list:
                    path_str = "params" + path
                    value = eval('time_yyyyy_MM_dd()')
                    expression = path_str + "='" + value + "'"
                    exec(expression)
            elif var == "time_YMDHMS":
                path_list = f.in_value_path(value=var)
                for path in path_list:
                    path_str = "params" + path
                    value = eval('time_YMDHMS()')
                    expression = path_str + "='" + value + "'"
                    exec(expression)
            elif var == "local_time":
                path_list = f.in_value_path(value=var)
                for path in path_list:
                    path_str = "params" + path
                    value = eval("local_time()")
                    expression = path_str + '=' + str(value)
                    exec(expression)
            elif var == "local_time_13":
                path_list = f.in_value_path(value=var)
                for path in path_list:
                    path_str = "params" + path
                    value = eval("local_time_13()")
                    expression = path_str + '=' + str(value)
                    exec(expression)
            else:
                path_list = f.in_value_path(value=var)
                for path in path_list:
                    var_data = GlobalData.query.filter_by(name=var).first()
                    if (var_data is not None and var_data.group_id == "0") or (
                            var_data is not None and str(group_id) in var_data.group_id):
                        path_str = "params" + path
                        var_value = var_data.value
                        var_category = var_data.category
                        # sql变量判断
                        if var_category == "SQL":
                            if isinstance(var_value, str):
                                for sql_name in var_value.split(','):
                                    sql = SqlManage.query.filter_by(sql_name=sql_name).first()
                                    if sql is None:
                                        return jsonify({"code": 300, "message": "sql标识不存在！"})
                                    else:
                                        db = DbLibrary(sql.database)
                                        if sql.type == "select":
                                            var_value = db.db_select(sql.value)
                                        elif sql.type == "insert":
                                            db.db_insert(sql.value)
                                        elif sql.type == "update":
                                            db.db_update(sql.value)
                                        else:
                                            db.db_update(sql.value)
                                        db.db_close()
                        # case变量判断
                        elif var_category == "CASE":
                            case_id = var_value.split("_")[0]
                            jsonpath_str = var_value.split("_")[-1]
                            case_data = model_to_dict(CaseManage.query.filter_by(case_id=case_id).first())
                            refer_case_res = refer_case_response(case_data)
                            print(refer_case_res)
                            var_value = jsonpath(refer_case_res, jsonpath_str)[0]
                            print(var_value)
                        else:
                            pass
                        if var_data.type == "string":
                            value = eval("str")(var_value)
                            expression = path_str + "='" + value + "'"
                        else:
                            value = eval(var_data.type)(var_value)
                            expression = path_str + "=" + str(value)
                        exec(expression)
                    else:
                        return jsonify({"code": 300, "message": "paeams:{},全局变量不存在！或作用域不在此用例集!".format(var)})
        # 判断参数是否需要加密（设备指纹）
        if proj_type != '' and proj_type in ['Android_v3', 'iOS_v3', 'web_v3', 'weapp_v3', 'android_v4', 'iOS_v4',
                                             'quickapp_v4']:
            fp_encode = FpEncoder(Config.TOOL_PATH, Config.ORGANIZATION, Config.AINFOKEY, Config.KEY_PATH,
                                  Config.TEMP_PATH)
            if proj_type == 'Android_v3':
                if encode_type == 'Android_v3_0':
                    pass
                if encode_type == 'Android_v3_1':
                    pass
                if encode_type == 'Android_v3_3':
                    pass
                if encode_type == 'Android_v3_5':
                    pass
                if encode_type == 'Android_v3_7':
                    params = fp_encode.fpencode_7(json.dumps(params))
                if encode_type == 'Android_v3_9':
                    params = fp_encode.fpencode_9(json.dumps(params))
                if encode_type == 'Android_v3_11':
                    params = fp_encode.fpencode_11(json.dumps(params))
            if proj_type == 'iOS_v3':
                if encode_type == 'iOS_v3_0':
                    pass
                if encode_type == 'iOS_v3_2':
                    pass
                if encode_type == 'iOS_v3_4':
                    params = fp_encode.fpencode_4(json.dumps(params))
                if encode_type == 'iOS_v3_6':
                    pass
                if encode_type == 'iOS_v3_8':
                    pass
                if encode_type == 'iOS_v3_10':
                    params = fp_encode.fpencode_10(json.dumps(params))
            if proj_type == 'weapp_v3':
                params = fp_encode.fpencode_weapp(json.dumps(params))
            if proj_type == 'web_v3':
                params = fp_encode.fpencode_web(json.dumps(params))
            if proj_type == 'android_v4':
                pass
            if proj_type == 'iOS_v4':
                pass
            if proj_type == 'quickapp_v4':
                pass
            params = eval(params)
        # 判断参数中是否需要删除键值对
        if len(delete_key_list) != 0:
            fp_data_dealer = FpDataDealer()
            params = fp_data_dealer.data_delete(params, delete_key_list[0])
    expect_res = request_data['expectRes']
    if method not in ['GET', 'POST', 'DELETE', 'PATCH']:
        return jsonify({"code": 300, "message": "请求方法不合法！"})
    response = ""
    try:
        if method == "GET":
            res = requests.get(url=re_url, params=get_params, headers=re_headers)
            print(res.text)
            res.encoding = 'utf-8'
            if res.text.startswith('sm'):
                response = json.loads(release_jsonp(res.text))
            else:
                response = res.json()
        elif method == "POST":
            print(params)
            print(re_headers)
            res = requests.post(url=re_url, json=params, headers=re_headers)
            print(res.text)
            res.encoding = 'utf-8'
            if res.text.startswith('smCB'):
                response = json.loads(release_jsonp(res.text))
            else:
                response = res.json()
        elif method == "PATCH":
            res = requests.put(url=re_url, data=params, headers=re_headers)
            print(res.text)
            res.encoding = 'utf-8'
            response = res.json()
        elif method == "DELETE":
            res = requests.delete(url=re_url, params=get_params, headers=re_headers)
            print(res.text)
            res.encoding = 'utf-8'
            response = res.json()
    except Exception as e:
        print(str(e))
        return jsonify({"code": 300, "message": str(e)})
    # 断言结果校验
    for expect in expect_res:
        if expect['key'] == "$":
            value = response
        else:
            value = jsonpath(response, expect['key'])
        if value is not False:
            if expect['key'] != "$":
                if expect['type'] != "list":
                    value = jsonpath(response, expect['key'])[0]
            expect_value = expect["value"]
            if type(value) == Config.type_dict[expect['type']]:
                if isinstance(expect_value, str) and expect_value.startswith("SQL:"):
                    var_sql = expect_value.split(':')[1]
                    sql = SqlManage.query.filter_by(sql_name=var_sql).first()
                    if sql is None:
                        return jsonify({"code": 300, "message": "sql标识不存在！"})
                    else:
                        db = DbLibrary(sql.database)
                        if sql.type == "select":
                            expect_value = db.db_select(sql.value)
                        elif sql.type == "insert":
                            db.db_insert(sql.value)
                        elif sql.type == "update":
                            db.db_update(sql.value)
                        else:
                            db.db_update(sql.value)
                        db.db_close()
                # 预期结果value支持变量
                if isinstance(expect_value, str):
                    var_list = e.extract_variables(expect_value)
                    if len(var_list) != 0:
                        var_data = GlobalData.query.filter_by(name=var_list[0]).first()
                        if (var_data is not None and var_data.group_id == "0") or (
                                var_data is not None and str(group_id) in var_data.group_id):
                            if var_data.type == "string":
                                real_value = eval('str')(var_data.value)
                            else:
                                real_value = eval(var_data.type)(var_data.value)
                            expect_value = e.replace_var(value, var_list[0], real_value)
                            if expect['type'] == "string":
                                expect_value = eval("str")(expect_value)
                            else:
                                expect_value = eval(expect['type'])(expect_value)
                        else:
                            return jsonify(
                                {"code": 300,
                                 "message": "全局变量不存在！或作用域不在此用例集!".format(var_list[0])})
                if expect["assertType"] == "==":
                    if expect['type'] == "string":
                        if value != eval("str")(expect_value):
                            return jsonify(
                                {"code": 300, "response": response,
                                 "message": "{0} != {1},与预期结果不一致".format(value, eval("str")(expect_value))})
                    elif expect['type'] == "list":
                        if value != expect_value:
                            return jsonify(
                                {"code": 300, "response": response,
                                 "message": "{0} != {1},与预期结果不一致".format(value, expect_value)})
                    elif expect['type'] == "json":
                        json_cmp = JsonCompare()
                        if json_cmp.check_json_format(value) is False:
                            return jsonify({"code": 300, "message": "实际结果不是json格式！"})
                        if json_cmp.check_json_format(expect_value) is False:
                            return jsonify({"code": 300, "message": "预期结果不是json格式！"})
                        ans = json_cmp.compare(value, expect_value)
                        if len(ans) > 0:
                            return jsonify({"code": 300, "message": ans})
                    else:
                        if value != eval(expect['type'])(expect_value):
                            return jsonify(
                                {"code": 300, "response": response,
                                 "message": "{0} ！= {1},与预期结果不一致".format(value, eval(expect['type'])(
                                     expect_value))})
                if expect["assertType"] == ">=":
                    if expect['type'] == "string":
                        if value < eval("str")(expect_value):
                            return jsonify(
                                {"code": 300, "response": response,
                                 "message": "{0} < {1},与预期结果不一致".format(value, eval("str")(expect_value))})
                    else:
                        if value < eval(expect['type'])(expect_value):
                            return jsonify(
                                {"code": 300, "response": response,
                                 "message": "{0} < {1},与预期结果不一致".format(value, eval(expect['type'])(
                                     expect_value))})
                if expect["assertType"] == "<=":
                    if expect['type'] == "string":
                        if value > eval("str")(expect_value):
                            return jsonify(
                                {"code": 300, "response": response,
                                 "message": "{0} > {1},与预期结果不一致".format(value, eval("str")(expect_value))})
                    else:
                        if value > eval(expect['type'])(expect_value):
                            return jsonify(
                                {"code": 300, "response": response,
                                 "message": "{0} > {1},与预期结果不一致".format(value, eval(expect['type'])(
                                     expect_value))})
                if expect["assertType"] == "<":
                    if expect['type'] == "string":
                        if value >= eval("str")(expect_value):
                            return jsonify(
                                {"code": 300, "response": response,
                                 "message": "{0} >= {1},与预期结果不一致".format(value, eval("str")(expect_value))})
                    else:
                        if value >= eval(expect['type'])(expect_value):
                            return jsonify(
                                {"code": 300, "response": response,
                                 "message": "{0} >= {1},与预期结果不一致".format(value, eval(expect['type'])(
                                     expect_value))})
                if expect["assertType"] == ">":
                    if expect['type'] == "string":
                        if value <= eval("str")(expect_value):
                            return jsonify(
                                {"code": 300, "response": response,
                                 "message": "{0} <= {1},与预期结果不一致".format(value, eval("str")(expect_value))})
                    else:
                        if value <= eval(expect['type'])(expect_value):
                            return jsonify(
                                {"code": 300, "response": response,
                                 "message": "{0} <= {1},与预期结果不一致".format(value, eval(expect['type'])(
                                     expect_value))})
                if expect["assertType"] == "!=":
                    if expect['type'] == "string":
                        if value == eval("str")(expect_value):
                            return jsonify(
                                {"code": 300, "response": response,
                                 "message": "{0} = {1},与预期结果不一致".format(value, eval("str")(expect_value))})
                    else:
                        if value == eval(expect['type'])(expect_value):
                            return jsonify(
                                {"code": 300, "response": response,
                                 "message": "{0} = {1},与预期结果不一致".format(value, eval(expect['type'])(
                                     expect_value))})
                if expect["assertType"] == "match":
                    if expect['type'] == "string":
                        match_result = re.match(eval('str')(expect_value), value)
                        if match_result is None:
                            return jsonify(
                                {"code": 300, "response": response,
                                 "message": "返回结果中没有找到匹配的字符串"})
                    else:
                        return jsonify(
                            {"code": 300, "response": response,
                             "message": "正则表达式匹配目前只支持字符串"})
            else:
                if expect["assertType"] == "schema_match":
                    if expect['type'] == "json":
                        if expect['key'] == "$":
                            if len(expect_value.split("_")) != 2:
                                return jsonify(
                                    {"code": 300, "message": "检查预期结果格式(服务名称_模板名称)"})
                            schema_data = SchemaData.query.filter(SchemaData.obj_name == expect_value.split("_")[0],
                                                                  SchemaData.name == expect_value.split("_")[1]).first()
                            if schema_data is None:
                                return jsonify(
                                    {"code": 300, "message": "没有查询到模板信息,检查输入字符!"})
                            else:
                                schema = eval(schema_data.value)
                                schema_diff = SchemaDiff()
                                result = schema_diff.diff_data(response, schema)
                                if result != "PASS":
                                    return jsonify(
                                        {"code": 300, "response": response,
                                         "message": "返回结果与模板不匹配"})
                        else:
                            if len(expect_value.split("_")) != 2:
                                return jsonify(
                                    {"code": 300, "message": "检查预期结果格式(服务名称_模板名称)"})
                            schema_data = SchemaData.query.filter(SchemaData.obj_name == expect_value.split("_")[0],
                                                                  SchemaData.name == expect_value.split("_")[1]).first()
                            if schema_data is None:
                                return jsonify(
                                    {"code": 300, "message": "没有查询到模板信息,检查输入字符!"})
                            else:
                                schema = eval(schema_data.value)
                                schema_diff = SchemaDiff()
                                result = schema_diff.diff_data(value, schema)
                                if result != "PASS":
                                    return jsonify(
                                        {"code": 300, "response": response,
                                         "message": "返回结果与模板不匹配"})
                    else:
                        return jsonify(
                            {"code": 300, "response": response,
                             "message": "模板匹配类型须选择json"})
                # 处理json数组，字符串正则匹配
                elif type(value) == list and expect["assertType"] == "match" and expect['type'] == "json":
                    for json_value in value:
                        match_result = re.match(eval('str')(expect["value"]), json_value)
                        if match_result is None:
                            return jsonify(
                                {"code": 300, "response": response,
                                 "message": "返回结果中没有找到匹配的字符串"})
                elif type(value) == dict and expect["assertType"] == "==" and expect['type'] == "json":
                    expect_value = json.loads(expect_value.encode('utf-8', 'ignore'))
                    if value != expect_value:
                        return jsonify(
                            {"code": 300, "response": response,
                             "message": "{0} != {1},与预期结果不一致".format(value, expect_value)})

                else:
                    return jsonify({"code": 300, "response": response, "message": "断言类型不正确！"})
        else:
            return jsonify({"code": 300, "response": response, "message": "没有找到jsonpath！" + json.dumps(response)})
    if request_data["expectKeys"] != "":
        expect_keys = request_data["expectKeys"].split(',')
        response_keys = e.get_dict_all_keys(response)
        for key in expect_keys:
            if key not in [str(k) for k in response_keys]:
                return jsonify({"code": 300, "message": "返回结果中不存在key：{}!".format(key)})
    if request_data["unexpectKeys"] != "":
        unexpect_keys = request_data["unexpectKeys"].split(',')
        response_keys = e.get_dict_all_keys(response)
        for key in unexpect_keys:
            if key in [str(k) for k in response_keys]:
                return jsonify({"code": 300, "message": "返回结果中存在key：{}!".format(key)})
    delay_time = request_data["delayTime"]
    if delay_time != 0:
        time.sleep(delay_time)
        # 音视频关流操作
    if proj_type in ['Videostream_V2', 'Videostream_V4', 'Audiostream_V2', 'Audiostream_V4'] and response[
        'code'] == 1100:
        if proj_type == 'Videostream_V2':
            path = "/v3/saas/anti_fraud/finish_videostream"
            access_key = params['accessKey']
            request_id = response['requestId']
            finish_params = {
                "accessKey": access_key,
                "requestId": request_id
            }
            host = re_url.split('//')[1].split('/')[0]
            finish_url = "http://" + host + path
            requests.post(url=finish_url, json=finish_params, headers=re_headers)
        elif proj_type == 'Videostream_V4':
            path = "/finish_videostream/v4"
            access_key = params['accessKey']
            request_id = response['requestId']
            finish_params = {
                "accessKey": access_key,
                "requestId": request_id
            }
            host = re_url.split('//')[1].split('/')[0]
            finish_url = "http://" + host + path
            requests.post(url=finish_url, json=finish_params, headers=re_headers)
        elif proj_type == 'Audiostream_V2':
            path = "/v2/saas/anti_fraud/finish_audiostream"
            access_key = params['accessKey']
            request_id = response['requestId']
            finish_params = {
                "accessKey": access_key,
                "requestId": request_id
            }
            host = re_url.split('//')[1].split('/')[0]
            finish_url = "http://" + host + path
            requests.post(url=finish_url, json=finish_params, headers=re_headers)
        else:
            path = "/finish_audiostream/v4"
            access_key = params['accessKey']
            request_id = response['requestId']
            finish_params = {
                "accessKey": access_key,
                "requestId": request_id
            }
            host = re_url.split('//')[1].split('/')[0]
            finish_url = "http://" + host + path
            requests.post(url=finish_url, json=finish_params, headers=re_headers)
    # 历史记录校验
    if "historyCheck" in list(request_data.keys()):
        history_checks = request_data["historyCheck"]
        if proj_type in ['Videostream_V2', 'Videostream_V4', 'Audiostream_V2', 'Audiostream_V4']:
            time.sleep(33)
        for history_check in history_checks:
            server = ServerLibrary(Config.ssh_conf_dict[history_check["ip"]])
            server.server_connect()
            datas = server.server_query(history_check["filePath"], response['requestId'], history_check["grepStr"],
                                        history_check["regex"])
            if len(datas) == 0:
                return jsonify(
                    {"code": 300, "message": "历史记录数据列表为空", "response": response})
            print(datas)
            schema_str = SchemaData.query.filter_by(name=history_check["schema"][1]).first().value
            print(schema_str)
            schema = eval(schema_str)
            for data in datas:
                if isinstance(data, str):
                    json_data = json.loads(data)
                elif isinstance(data, dict):
                    json_data = data
                else:
                    raise Exception("输入不是字符串和字典")
                validator = Draft7Validator(schema)
                errors = validator.iter_errors(json_data)
                error_is_empty = True
                error_message_sum = ""
                for error in errors:
                    error_is_empty = False
                    e = error
                    suberror_is_empty = True
                    for suberror in (e.context):
                        suberror_is_empty = False
                        if 'False schema does not allow' in suberror.message:
                            suberror.message = '此参数不应该出现'
                        print("json数据不符合schema规定：\n出错字段：{}\n提示信息：{}".format(
                            " --> ".join(["%s" % i for i in suberror.absolute_path]), suberror.message))
                        error_message_sum = error_message_sum + "\njson数据不符合schema规定：\n出错字段：{}\n提示信息：{}".format(
                            " --> ".join(["%s" % i for i in suberror.absolute_path]), suberror.message)
                    if suberror_is_empty:
                        if 'False schema does not allow' in e.message:
                            e.message = '此参数不应该出现'
                        print("json数据不符合schema规定：\n出错字段：{}\n提示信息：{}".format(
                            " --> ".join(['%s' % i for i in e.absolute_path]),
                            e.message))
                        error_message_sum = error_message_sum + "\njson数据不符合schema规定：\n出错字段：{}\n提示信息：{}".format(
                            " --> ".join(['%s' % i for i in e.absolute_path]),
                            e.message)
                if error_is_empty:
                    pass
                else:
                    return jsonify(
                        {"code": 300,
                         "message": "流水号{0}的历史记录数据{1}与模板：\n{2}预期不符".format(response['requestId'], data, schema),
                         "errorMessage": error_message_sum})
            server.server_close()
            if "delayTime" in list(history_check.keys()):
                time.sleep(history_check["delayTime"])
    return jsonify({"code": 200, "message": True, "content": response})
