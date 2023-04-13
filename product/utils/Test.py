import unittest
from jsonpath import jsonpath
from product.config import Config
from product.utils.excute import Execute, FindPath
from product.global_data.models import GlobalData
from flask import jsonify
import requests
import json
import re
from product.case.models import CaseGroup, CaseManage
from product.result.models import Result
from product.utils.tools import login_required, get_user, generate_btid, generate_btid_list, time_yyyyy_MM_dd, \
    time_YMDHMS, local_time, local_time_13, release_jsonp, JsonCompare, refer_case_response, extract_delete_key, \
    SchemaDiff, model_to_dict, send_mail
from datetime import datetime
import os
from product.utils.HTMLTestRunner import HTMLTestRunner
from product import db, app
from sqlalchemy.exc import SQLAlchemyError
from product.utils_fp.FpEncoder import FpEncoder
from product.utils_fp.FpDataDealer import FpDataDealer
import time
from product.utils.server_lib import ServerLibrary
from product.schema.models import SchemaData
from product.sql.models import SqlManage
from product.utils.DB_lib import DbLibrary


class Test(unittest.TestCase):

    def setUp(self):
        print("start")

    def demo(self, request_data):
        print("用例名称：{}".format(request_data['case_name']))
        e = Execute()
        case_name = request_data['case_name']
        delete_key_list = extract_delete_key(case_name)
        group_id = request_data['group_id']
        proj_type = CaseGroup.query.filter_by(group_id=group_id).first().proj_type
        encode_type = CaseGroup.query.filter_by(group_id=group_id).first().encode_type
        method = request_data['method']
        url = request_data['url']
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
                        real_value = eval(var_data.type)(var_data.value)
                    re_url = e.replace_var(re_url, var, real_value)
                else:
                    print("url:{}全局变量不存在！或作用域不在此用例集!".format(var))
        else:
            re_url = url
        if request_data['port'] != '':
            if len(e.extract_variables(request_data['port'])) != 0:
                var_port = GlobalData.query.filter_by(name=e.extract_variables(request_data['port'])[0]).first().value
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
        headers = eval(request_data['headers'])
        # 处理header，是否有全局变量，有就替换
        for key, value in headers.items():
            if len(e.extract_variables(value)) != 0:
                var_data = GlobalData.query.filter_by(name=e.extract_variables(value)[0]).first()
                if (var_data is not None and var_data.group_id == "0") or (
                        var_data is not None and str(group_id) in var_data.group_id):
                    if var_data.type == "string":
                        real_value = eval('str')(var_data.value)
                    else:
                        real_value = eval(var_data.type)(var_data.value)
                    headers[key] = e.replace_var(value, e.extract_variables(value)[0], real_value)
                else:
                    print("header：{} 全局变量不存在！或作用域不在此用例集!".format(e.extract_variables(value)[0]))
        set_up = request_data['set_up']
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
                        db.db_update(sql.value)
                    db.db_close()
        params = request_data['params']
        if method == "POST" or method == "PATCH":
            params = json.loads(params)
        get_params = {}
        # params全局变量替换:嵌套字典中有多个变量时，变量名不能相同,一个键值对中一个key 对应一个全局变量（value）
        if method == "GET" or method == "DELETE":
            get_params_list = []
            for param in params.split('|'):
                get_params_list.append(json.loads(param))
            for param in get_params_list:
                get_params[param['methodKey']] = param['methodValue']
            # get请求替换全局变量
            for key, value in get_params.items():
                if len(e.extract_variables(value)) != 0:
                    if e.extract_variables(value)[0] == "btid":
                        real_value = eval('generate_btid()')
                        params[key] = e.replace_var(value, e.extract_variables(value)[0], real_value)
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
                            params[key] = e.replace_var(value, e.extract_variables(value)[0], real_value)
                        else:
                            return jsonify(
                                {"code": 300,
                                 "message": "paeams:{},全局变量不存在！或作用域不在此用例集!".format(e.extract_variables(value)[0])})
            # 根据valueType修改value
            for param in get_params_list:
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
                            path_str = "params" + path
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
        expect_res = request_data['expect_res']
        response = ""
        try:
            if method == "GET":
                res = requests.get(url=re_url, params=get_params, headers=headers)
                res.encoding = 'utf-8'
                response = res.json()
            elif method == "POST":
                res = requests.post(url=re_url, json=params, headers=headers)
                res.encoding = 'utf-8'
                if res.text.startswith('smCB'):
                    response = json.loads(release_jsonp(res.text))
                else:
                    response = res.json()
            elif method == "PATCH":
                res = requests.put(url=re_url, data=params, headers=headers)
                res.encoding = 'utf-8'
                response = res.json()
            elif method == "DELETE":
                res = requests.delete(url=re_url, params=get_params, headers=headers)
                res.encoding = 'utf-8'
                response = res.json()
        except Exception as e:
            print(str(e))
        print("主接口返回结果：\n{}".format(response))
        # 断言结果校验
        expect_res_list = []
        for expect in expect_res.split('|'):
            expect_res_list.append(json.loads(expect))
        for expect in expect_res_list:
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
                            self.assertEqual(value, eval('str')(expect_value))
                        elif expect['type'] == "list":
                            expect_value = eval(expect_value)
                            if value != expect_value:
                                self.assertEqual(value, expect_value)
                        elif expect['type'] == "json":
                            json_cmp = JsonCompare()
                            msg_value = "实际结果不是json格式！"
                            self.assertTrue(json_cmp.check_json_format(value), msg_value)
                            msg_except = "预期结果不是json格式！"
                            self.assertTrue(json_cmp.check_json_format(expect_value), msg_except)
                            ans = json_cmp.compare(value, expect_value)
                            self.assertEqual(len(ans), 0, ans)
                        else:
                            self.assertEqual(value, eval(expect['type'])(expect_value))
                    if expect["assertType"] == ">=":
                        if expect['type'] == "string":
                            self.assertGreaterEqual(value, eval('str')(expect_value))
                        else:
                            self.assertGreaterEqual(value, eval(expect['type'])(expect_value))
                    if expect["assertType"] == "<=":
                        if expect['type'] == "string":
                            self.assertLessEqual(value, eval('str')(expect_value))
                        else:
                            self.assertLessEqual(value, eval(expect['type'])(expect_value))
                    if expect["assertType"] == "<":
                        if expect['type'] == "string":
                            self.assertLess(value, eval('str')(expect_value))
                        else:
                            self.assertLess(value, eval(expect['type'])(expect_value))
                    if expect["assertType"] == ">":
                        if expect['type'] == "string":
                            self.assertGreater(value, eval('str')(expect_value))
                        else:
                            self.assertGreater(value, eval(expect['type'])(expect_value))
                    if expect["assertType"] == "!=":
                        if expect['type'] == "string":
                            self.assertNotEqual(value, eval('str')(expect_value))
                        else:
                            self.assertNotEqual(value, eval(expect['type'])(expect_value))
                    if expect["assertType"] == "match":
                        if expect['type'] == "string":
                            match_result = re.match(eval('str')(expect_value), value)
                            msg = "没有找到匹配的字符串"
                            self.assertIsNotNone(match_result, msg)
                        else:
                            return jsonify(
                                {"code": 300,
                                 "message": "正则表达式匹配目前只支持字符串"})
                else:
                    if expect["assertType"] == "schema_match":
                        if expect['key'] == "$":
                            msg = "检查预期结果格式(服务名称_模板名称)"
                            self.assertEqual(len(expect_value.split("_")), 2, msg)
                            schema_data = SchemaData.query.filter(SchemaData.obj_name == expect_value.split("_")[0],
                                                                  SchemaData.name == expect_value.split("_")[1]).first()
                            if schema_data is None:
                                self.assertIsNotNone(schema_data, msg)
                            else:
                                schema = eval(schema_data.value)
                                schema_diff = SchemaDiff()
                                result = schema_diff.diff_data(response, schema)
                                self.assertEqual(result, "PASS")
                        else:
                            msg = "检查预期结果格式(服务名称_模板名称)"
                            self.assertEqual(len(expect_value.split("_")), 2, msg)
                            schema_data = SchemaData.query.filter(SchemaData.obj_name == expect_value.split("_")[0],
                                                                  SchemaData.name == expect_value.split("_")[1]).first()
                            if schema_data is None:
                                self.assertIsNotNone(schema_data, msg)
                            else:
                                schema = eval(schema_data.value)
                                schema_diff = SchemaDiff()
                                result = schema_diff.diff_data(value, schema)
                                self.assertEqual(result, "PASS")
                    # 处理json数组，字符串正则匹配
                    elif type(value) == list and expect["assertType"] == "match" and expect['type'] == "json":
                        for json_value in value:
                            match_result = re.match(eval('str')(expect["value"]), json_value)
                            msg = "没有找到匹配的字符串"
                            self.assertIsNotNone(match_result, msg)
                    elif type(value) == dict and expect["assertType"] == "==" and expect['type'] == "json":
                        expect_value = json.loads(expect_value.encode('utf-8', 'ignore'))
                        self.assertEqual(value, expect_value)
                    else:
                        msg = "实际结果与预期结果类型不一致！"
                        self.assertEqual(type(value), Config.type_dict[expect['type']], msg)
            else:
                self.assertTrue(jsonpath(response, expect['key']))
                print({"message": "没有找到jsonpath！" + json.dumps(response)})
        if request_data["expect_keys"] != "":
            expect_keys = request_data["expect_keys"].split(',')
            response_keys = e.get_dict_all_keys(response)
            for key in expect_keys:
                self.assertIn(key, [str(k) for k in response_keys])
        if request_data["unexpect_keys"] != "":
            unexpect_keys = request_data["unexpect_keys"].split(',')
            response_keys = e.get_dict_all_keys(response)
            for key in unexpect_keys:
                self.assertNotIn(key, [str(k) for k in response_keys])
        delay_time = request_data["delay_time"]
        if delay_time != 0:
            time.sleep(delay_time)
            # 历史记录校验
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
                requests.post(url=finish_url, json=finish_params, headers=headers)
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
                requests.post(url=finish_url, json=finish_params, headers=headers)
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
                requests.post(url=finish_url, json=finish_params, headers=headers)
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
                requests.post(url=finish_url, json=finish_params, headers=headers)
        if request_data["history_check"] is not None:
            history_check_list = []
            for his in request_data["history_check"].split('|'):
                history_check_list.append(json.loads(his))
            if proj_type in ['Videostream_V2', 'Videostream_V4', 'Audiostream_V2',
                             'Audiostream_V4']:
                time.sleep(33)
            result_unit_list = []  # 每个历史记录校验的结果集合
            result_end = "PASS"  # 最终的历史记录校验结果
            for history_check in history_check_list:
                server = ServerLibrary(Config.ssh_conf_dict[history_check["ip"]])
                server.server_connect()
                datas = server.server_query(history_check["filePath"], response['requestId'], history_check["grepStr"],
                                            history_check["regex"])
                schema = eval(SchemaData.query.filter_by(name=history_check["schema"][1]).first().value)
                schema_diff = SchemaDiff()
                result_list = schema_diff.batch_diff_data(datas, schema)
                for result in result_list:
                    if result == "FAIL":
                        msg = "数据与{0}预期不符".format(history_check["schema"][1])
                        # self.assertEqual(result, 'PASS', msg)
                        print("日志校验结果：{}".format(msg))
                        result_unit_list.append("FAIL")
                    else:
                        result_unit_list.append("PASS")
                server.server_close()
                if "delayTime" in list(history_check.keys()):
                    time.sleep(history_check["delayTime"])
            msg = "存在数据与预期模板不符"
            if "FAIL" in result_unit_list:
                result_end = "FAIL"
            self.assertEqual(result_end, 'PASS', msg)

    @staticmethod
    def getTestFunc(data):
        def func(self):
            self.demo(data)

        return func

    def tearDown(self):
        print("end")


# 根据测试数据动态添加测试函数
def __generate_testcases(data_list):
    for fun in dir(Test):
        if 'test_case_' in fun:
            delattr(Test, fun)
    for data in data_list:
        setattr(Test, "test_case_%s" % (data["case_id"]), Test.getTestFunc(data))


def run_case_0(db_task, operate_by, send_by):
    db_task = db.session.merge(db_task)
    group_id_list = [int(i) for i in db_task.task_group.split(',')]
    db_cases = []
    for group_id in group_id_list:
        if CaseGroup.query.filter_by(group_id=group_id).first().status != 0:
            db_cases_by_group = CaseManage.query.filter(CaseManage.group_id == group_id,
                                                        CaseManage.status == 1).all()
            db_cases += db_cases_by_group
        else:
            return jsonify({"code": 300, "message": "任务中有禁用状态的用例集！"})
    case_list = []
    for case in db_cases:
        case_dict = model_to_dict(case)
        case_list.append(case_dict)
    __generate_testcases(case_list)
    suit = unittest.makeSuite(Test)
    reportname = 'API_AutoTest_{0}_report{1}.html'.format(db_task.task_name,
                                                          datetime.now().strftime("%Y%m%d_%H%M%S"))
    report = os.path.join(Config.REPORT_PATH, reportname)
    title = '接口自动化测试报告%s' % datetime.now().strftime("%Y%m%d%H%M%S")
    fp = open(report, 'wb')
    runner = HTMLTestRunner(stream=fp, verbosity=2, title=title,
                            description='Test Description')
    runner.run(suit)
    case_run_way = 0
    report_link = "http://auto-qa.ishumei.com/static/" + reportname
    record = Result(task_id=db_task.task_id, case_run_way=case_run_way, operate_by=operate_by, result=report_link)
    try:
        db.session.add(record)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"code": 300, "message": str(e)})
    subject = "接口自动化测试报告"
    body = "Hi,附件是本次接口自动化测试报告。\nBy beacon"
    # send_to = CaseTask.query.filter_by(task_id=task_id).first().email
    if db_task.email is not None:
        send_to = []
        send_to.append(db_task.email)
        try:
            # 激活上下文
            with app.app_context():
                send_mail(subject=subject, sender=send_by, recipients=send_to, body=body, file=report)
        except Exception as e:
            return jsonify({"code": 300, "message": str(e)})
