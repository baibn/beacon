import psutil
from collections import Iterable
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
import functools
from flask import current_app, jsonify, request
import json
import hashlib
from product.users.models import User
from flask_mail import Message
from product import mail, app
import uuid
import re
from jsonschema import Draft7Validator
import time
from product.utils.excute import Execute, FindPath
from product.case.models import CaseGroup, CaseManage
from product.global_data.models import GlobalData
from product.sql.models import SqlManage
from product.utils.DB_lib import DbLibrary
import requests
from product.utils_fp.FpEncoder import FpEncoder
from product.utils_fp.FpDataDealer import FpDataDealer
from product.config import Config
from jsonpath import jsonpath


def string_to_md5(string):
    """
    str 取MD5
    :param string
    :return:
    """
    md5_val = hashlib.md5(string.encode('utf8')).hexdigest()
    return md5_val


def create_token(api_user):
    """
    生成token
    :param api_user:用户
    :return: token
    """
    s = Serializer(current_app.config["SECRET_KEY"], expires_in=86400)
    # 接收用户id转换与编码
    token = s.dumps({"user": api_user}).decode("ascii")
    return token


def verify_token(token):
    """
    校验token
    :param token:
    :return: 用户信息 or None
    """

    # 参数为私有秘钥，跟上面方法的秘钥保持一致
    s = Serializer(current_app.config["SECRET_KEY"])
    try:
        # 转换为字典
        data = s.loads(token)
    except Exception as e:
        print(e)
        return None
    return data['user']


def get_user(token):
    s = Serializer(current_app.config["SECRET_KEY"])
    try:
        data = s.loads(token)
        user_id = data['user']
    except Exception as e:
        print(e)
        return jsonify({"code": 200, "message": "超时或用户不存在"})
    user_data = User.query.filter_by(id=user_id).first()
    if user_data is not None:
        return user_data.user
    else:
        return jsonify({"code": 200, "message": "超时或用户不存在"})


def login_required(func):
    @functools.wraps(func)
    def verify_token(*args, **kwargs):
        try:
            # 在请求头上拿到token
            token = request.headers["token"]
        except Exception:
            # 没接收的到token,给前端抛出错误
            # 这里的code暂时随便定义。
            return jsonify(code=4103, msg='缺少参数token')
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            s.loads(token)
            user = User.query.filter_by(id=s.loads(token)['user']).first()
            assert user is not None
        except Exception:
            return jsonify(code=4101, msg="登录已过期,或用户不存在!")
        return func(*args, **kwargs)

    return verify_token


def model_to_dict(result):
    # 转换完成后，删除  '_sa_instance_state' 特殊属性
    try:
        if isinstance(result, Iterable):
            tmp = [dict(zip(res.__dict__.keys(), res.__dict__.values())) for res in result]
            for t in tmp:
                t.pop('_sa_instance_state')
        else:
            tmp = dict(zip(result.__dict__.keys(), result.__dict__.values()))
            tmp.pop('_sa_instance_state')
        return tmp
    except BaseException as e:
        print(e.args)
        raise TypeError('Type error of parameter')


def get_cpu_syl(interval=1):
    """CPU使用率"""
    total_cpu = psutil.cpu_times().user + psutil.cpu_times().idle
    user_cpu = psutil.cpu_times().user
    cpu_syl = '%.3f' % (user_cpu / total_cpu * 100)
    # return (str(psutil.cpu_percent(interval)))
    return cpu_syl


def get_mem_syl():
    """内存使用率"""
    # 使用psutil.virtual_memory方法获取内存完整信息
    mem = psutil.virtual_memory()
    mem_total = mem.total
    mem_used = mem.used
    mem_syl = '%.3f' % (mem_used / float(mem_total) * 100)
    return mem_syl


def get_dis_syl():
    """硬盘使用率"""
    dis_syl = '%.3f' % (psutil.disk_usage('/').used / float(psutil.disk_usage('/').total) * 100)
    return dis_syl


def to_json(inst, cls):
    d = dict()
    '''
    获取表里面的列并存到字典里面
    '''
    for c in cls.__table__.columns:
        v = getattr(inst, c.name)
        d[c.name] = v
    return json.dumps(d)


def send_mail(subject, sender, recipients, body, file):
    message = Message(
        subject=subject, sender=sender, recipients=recipients)
    message.body = body
    # 加载附件
    with app.open_resource(file) as fp:
        message.attach(file, "text/html", fp.read())
    try:
        mail.send(message)
    except Exception as e:
        return jsonify({"code": 300, "message": str(e)})


# 生成唯一标识(btid)
def generate_btid():
    btid = uuid.uuid1().hex
    return btid


# 生成唯一标识列表(btid)
def generate_btid_list(num):
    btid_list = []
    for i in range(1, num):
        btid = uuid.uuid4().hex
        btid_list.append(btid)
    return btid_list


def time_yyyyy_MM_dd():
    return time.strftime('%Y-%m-%d', time.localtime())


def time_YMDHMS():
    return time.strftime('%Y%m%d-%H%M%S', time.localtime())


def local_time():
    return int(time.time())


def local_time_13():
    return int(time.time() * 1000)


# Jsonp中提取Json数据
def release_jsonp(content):
    try:
        a = content.find('(')
        b = content.find(')')
        c = b
        c = content.find(')', c + 1)
        if c != -1:
            while c != -1:
                c = content.find(')', c + 1)
                result_info = content[a + 1:c]
                return result_info
        else:
            result_info = content[a + 1:b]
            return result_info
    except:
        return content


# 从内容中提取参数字典中要删除的键值对的key,格式为#{key},返回key的list
def extract_delete_key(content):
    variable_regexp = r"\#\{(.+?)\}"
    if not isinstance(content, str):
        content = str(content)
    try:
        return re.findall(variable_regexp, content)
    except TypeError:
        return []


class JsonCompare:

    def compare(self, exp, act):
        ans = []
        self._compare(exp, act, ans, '')
        return ans

    def _compare(self, a, b, ans, path):
        a = self._to_json(a)
        b = self._to_json(b)
        if type(a) != type(b):
            ans.append(f"{path} 类型不一致, 分别为{type(a)} {type(b)}")
            return
        if isinstance(a, dict):
            keys = []
            for key in a.keys():
                pt = path + "/" + key
                if key in b.keys():
                    self._compare(a[key], b[key], ans, pt)
                    keys.append(key)
                else:
                    ans.append(f"{pt} 在后者中不存在")
            for key in b.keys():
                if key not in keys:
                    pt = path + "/" + key
                    ans.append(f"{pt} 在后者中多出")
        elif isinstance(a, list):
            i = j = 0
            while i < len(a):
                pt = path + "/" + str(i)
                if j >= len(b):
                    ans.append(f"{pt} 在后者中不存在")
                    i += 1
                    j += 1
                    continue
                self._compare(a[i], b[j], ans, pt)
                i += 1
                j += 1
            while j < len(b):
                pt = path + "/" + str(j)
                ans.append(f"{pt} 在前者中不存在")
                j += 1
        else:
            if a != b:
                ans.append(
                    f"{path} 数据不一致: {a} "
                    f"!= {b}" if path != "" else
                    f"数据不一致: {a} != {b}")

    def _color(self, text, _type=0):
        if _type == 0:
            # 说明是绿色
            return """<span style="color: #13CE66">{}</span>""".format(text)
        return """<span style="color: #FF4949">{}</span>""".format(text)

    def _weight(self, text):
        return """<span style="font-weight: 700">{}</span>""".format(text)

    def _to_json(self, string):
        try:
            float(string)
            return string
        except:
            try:
                if isinstance(string, str):
                    return json.loads(string)
                return string
            except:
                return string

    def check_json_format(self, raw_msg):
        """
        用于判断一个字符串是否符合Json格式
        :param self:
        :return:
        """
        if isinstance(raw_msg, str):  # 首先判断变量是否为字符串
            try:
                json.loads(raw_msg, encoding='utf-8')
            except ValueError:
                return False
            return True
        else:
            return False


class SchemaDiff(object):
    def diff_data(self, data, schema):
        """
        input str or dict

        schema: json模版

        return str
        """
        if isinstance(data, str):
            json_data = json.loads(data)
        elif isinstance(data, dict):
            json_data = data
        else:
            raise Exception("输入不是字符串和字典")
        validator = Draft7Validator(schema)
        errors = validator.iter_errors(json_data)
        error_is_empty = True
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
            if suberror_is_empty:
                if 'False schema does not allow' in e.message:
                    e.message = '此参数不应该出现'
                print("json数据不符合schema规定：\n出错字段：{}\n提示信息：{}".format(" --> ".join(['%s' % i for i in e.absolute_path]),
                                                                    e.message))
        if error_is_empty:
            return "PASS"
        else:
            print("失败的模板校验data:{0},schema:{1}".format(data, schema))
            return "FAIL"

    def batch_diff_data(self, datas, schema):
        """
        input list

        schema: json模版

        """
        if isinstance(datas, list):
            if len(datas) == 0:
                raise Exception("输入列表为空")
        else:
            raise Exception("输入不是列表")
        result_list = []
        for data in datas:
            result = self.diff_data(data, schema)
            result_list.append(result)
        # if "FAIL" in result_list:
        #     raise Exception("数据与{0}预期不符".format(schema_name))
        # else:
        #     print("验证成功！")
        return result_list


def refer_case_response(request_data):
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
    return response


if __name__ == "__main__":
    # 预期结果
    a = """
    {
     "name": "lixiaoyao",
     "age": 19,
     "wife": ["linyueru", "zhaolinger"],
     "job": {
      "yuhang": "混混",
      "suzhou": "林家堡姑爷",
      "suoyaota": "仙剑派弟子"
     }
    }
    """

    # 实际结果
    b = """
    {
     "name": "lixiaoyao",
     "age": 23,
     "wife": ["anu", "zhaolinger"],
     "job": {
      "yuhang": "混混",
      "suzhou": "林家堡姑爷",
      "suoyaota": "仙剑派子弟"
     }
    }
    """
    obj = JsonCompare()
    ans = obj.compare(a, b)
    print(ans)
