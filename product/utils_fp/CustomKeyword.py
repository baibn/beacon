#!usr/bin/env python
# encoding=utf-8
'''this file is creat for diy keyword'''

import json
import os
import base64
import binascii
import hashlib
import redis
import urllib.request, urllib.parse, urllib.error
import time
import linecache
from xlrd import open_workbook
from xlutils.copy import copy
from Crypto.Cipher import AES


def Write_Excel(filename, sheetname, row, column, content):
    print(filename)
    file = open_workbook(filename, 'w')
    wb = copy(file)
    sheetindex = file.sheet_names().index(sheetname)
    wb.get_sheet(int(sheetindex)).write(int(row), int(column), content)
    wb.save(filename)


'''
#获取测试工程绝对路径
def GetPwd():
    pwd = os.getcwd()#获取启动路径
    print pwd
    if 'testcase' in pwd: 	
    	pwd_fin = pwd.rstrip('testcase/')#通过启动路径获取上一级路径
    	return pwd_fin
    return pwd

#路径分隔符处理
def StrReplace(str):
    new_str = str.replace("\\","/")#将windows路径中的'\'符号替换成'/'
    return new_str
'''


# 打开文件操作
def OpenTxt(filename):
    filename = str(filename)  # 将路径强转成字符串格式
    f = open(filename, 'r+')  # 以只读方式打开测试数据文件
    return f  # 返回文件句柄


# 获取测试数据文件行数
def GetRowCountdiy(f):
    number = f.readlines()  # 读取文件内容
    lines = len(number)  # 获取内容长度
    f.close()  # 关闭文件
    return lines


# 通过指定行与列获取数据
def ReadCellDataByCoordinatesdiy(filename, row, column):
    row = int(row)
    column = int(column)
    result = linecache.getline(filename, column)  # 引用linecache库，获取指定行内容
    result_fin = result.split("\t")[row].rstrip('\n')  # 对获取到的行内容进行列筛选，并过滤换行符
    result_fin = result_fin.decode('gbk')  # 返回结果解码
    return result_fin


# unicode类型转换dict类型
def UnicodeToDict(input):
    result = str(input)
    result_dict = json.loads(result)
    return result_dict


def CheckType(str):
    print((type(str)))


def jsonToDict(DictStr):
    try:
        return json.loads(DictStr)
    except:
        return 'this string not a dictionary string'


# Jsonp中提取Json数据
def ReleaseJsonp(content):
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


# 字符串或字典转为json
def ContentToJson(content):
    try:
        if isinstance(content, str):
            data = json.loads(content)
            data = json.JSONEncoder().encode(data)
            return data
        if isinstance(content, dict):
            data = json.JSONEncoder().encode(content)
            return data
    except:
        return content


def JsonDecode(content):
    try:
        data = json.loads(content)
        value = list(data.keys())
        # print value
        str = '{'
        for key in value:
            if data[key]:
                mdict = '"' + key + '":"' + data[key] + '",',
            else:
                mdict = '"' + key + '":"null"',
        sjson = str + mdict + '}'
        return sjson
    except:
        return content


# 计算图片的base64(base64中包含\n)
def Base64FunStr(filepath):
    f = open(filepath, 'rb')
    # imgBase64=base64.b64encode(f.read())
    imgBase64 = base64.encodestring(f.read())
    f.close()
    return imgBase64


# 计算图片的base64(base64中不包含\n)
def Base64Fun(filepath):
    f = open(filepath, 'rb')
    imgBase64 = base64.b64encode(f.read())
    # imgBase64=base64.encodestring(f.read())
    f.close()
    return imgBase64


def CRC32(filepath):
    try:
        fp = open(filepath, 'rb')
        crc = binascii.crc32(fp.read())
        if crc > 0:
            fp.close()
            # crc32=str(crc)
            crc32 = crc
        else:
            crc32 = ~crc ^ 0xffffffff
        # return int(crc32)
        return int('%d' % crc32)
    except:
        return ""


# AES加密解密算法
def pkcs5padding(data):
    N = AES.block_size
    K = len(data)
    print((N, K))
    return data + (N - K % N) * chr(N - K % N)


# Android
def enc_dec_test(fname, org1):
    org, iv = org1, "0102030405060708"
    key = hashlib.md5("smsdk" + org).hexdigest()

    src_data = open(fname).read()

    # sef string replace
    cur_timestamp_str = str(int(time.time()) * 1000);
    src_data = src_data.replace('${BOOT}', cur_timestamp_str);

    plain = pkcs5padding(src_data)
    # plain = pkcs5padding(fname)

    enc = AES.new(key, AES.MODE_CBC, iv)
    encrypted = base64.b64encode(enc.encrypt(plain))
    print(("encrypted is %s" % (encrypted)))
    return encrypted

    # dec = AES.new(key, AES.MODE_CBC, iv)
    # print dec.decrypt(base64.b64decode(encrypted))


# wrapper mobile data to http post body str
def Wrapper(filename, organization):
    return WrapperMobile(filename, organization)


def Wrapper(filename, organization, platform):
    if "mobile" == platform:
        return WrapperMobile(filename, organization)
    elif "web" == platform:
        return WrapperWeb(filename, organization)
    else:
        return None


def WrapperSDKData(filename):
    return open(filename).read().strip('\n')


def WrapperMobile(filename, organization):
    fingerprint_str = enc_dec_test(filename, organization)
    middle_dict = {}
    middle_dict['fpEncode'] = 3
    middle_dict['fingerprint'] = fingerprint_str
    middle_dict['sessionId'] = 'fingerprint'
    final_dict = {}
    final_dict['organization'] = organization
    final_dict['data'] = middle_dict
    print(("middle_dict is %s" % (json.dumps(final_dict))))
    return json.dumps(final_dict)


def WrapperWeb(filename, organization):
    smdata = open(filename).read()
    smdata = smdata.strip('\n')
    middle_dict = {}
    middle_dict['callback'] = 'smCB_15170'
    middle_dict['organization'] = organization
    middle_dict['smdata'] = smdata
    middle_dict['os'] = 'web'
    middle_dict['version'] = '2.0.0'
    return urllib.parse.urlencode(middle_dict)


def WrapperProxy(filename, organization, os):
    header = {"ua": "do not change any more"}
    d = {}
    d["type"] = 1
    d["os"] = os
    d["smdata"] = open(filename).read().strip('\n')
    d["header"] = json.dumps(header)
    d_str = json.dumps(d)
    d_base64_str = base64.b64encode(d_str)

    middle_d = {}
    middle_d["fingerprint"] = d_base64_str
    middle_d["fpEncode"] = 1
    middle_d["sessionId"] = "1"
    middle_d["ip"] = "192.168.0.1"

    final_d = {}
    final_d["organization"] = organization
    final_d["data"] = middle_d
    return json.dumps(final_d)


def WrapperDR(access_key, id):
    middle_d = {}
    middle_d["deviceId"] = id

    final_d = {}
    final_d["accessKey"] = access_key
    final_d["data"] = middle_d
    return json.dumps(final_d)


def ParseWebResult(str):
    # smCB_15170()
    elements = str.split('(')
    if 2 != len(elements):
        return None
    elements = elements[1].split(')')
    if 2 != len(elements):
        return None
    return json.loads(elements[0])


# IOS
def enc_dec_ios(fname, org1):
    org, iv = org1, "0102030405060708"
    key = hashlib.md5("smsdk" + org).hexdigest()

    plain = pkcs5padding(open(fname).read())
    # plain = pkcs5padding(fname)

    enc = AES.new(key, AES.MODE_ECB)
    encrypted = base64.b64encode(enc.encrypt(plain))
    # print encrypted
    return encrypted


# 线上Android
def online_andr(fname, org1):
    org, iv = org1, "0102030405060708"
    key = hashlib.md5("smsdk" + org).hexdigest()

    plain = pkcs5padding(open(fname).read())
    # plain = pkcs5padding(fname)

    enc = AES.new(key, AES.MODE_CBC, iv)
    encrypted = base64.b64encode(enc.encrypt(plain))
    return encrypted

    # dec = AES.new(key, AES.MODE_CBC, iv)
    # print dec.decrypt(base64.b64decode(encrypted))


# 线上IOS
def online_ios(fname, org1):
    org, iv = org1, "0102030405060708"
    key = hashlib.md5("smsdk" + org).hexdigest()

    plain = pkcs5padding(open(fname).read())
    # plain = pkcs5padding(fname)

    enc = AES.new(key, AES.MODE_ECB)
    encrypted = base64.b64encode(enc.encrypt(plain))
    # print encrypted
    return encrypted


def equalset(left, right):
    return left == right


# redis
def ParseRedisConf(str):
    elements = str.split(',')
    if len(elements) != 3:
        return None, None, None
    return elements[0], elements[1], elements[2]


def rsmembersfirst(keys, redis1, redis2):
    ip1, port1, passwd1 = ParseRedisConf(redis1)
    ip2, port2, passwd2 = ParseRedisConf(redis2)
    pool1 = redis.ConnectionPool(host=ip1, port=port1, password=passwd1)
    pool2 = redis.ConnectionPool(host=ip2, port=port2, password=passwd2)
    conn1 = redis.Redis(connection_pool=pool1)
    conn2 = redis.Redis(connection_pool=pool2)
    print(keys)
    s1 = conn1.get(keys)
    s2 = conn2.get(keys)
    print((type(s1), type(s2)))
    if str(s1) == 'None':
        print('There are no data in redis1')
        if str(s2) == 'None':
            return 'None'
        else:
            print('Data in redis2')
            return s2
    else:
        print('Data in redis1')
        return s1


def rhgetall(keys, ip='10.66.228.123', port='6379', passwd='crs-170dbkmq:shumeitest2018'):
    pool = redis.ConnectionPool(host=ip, port=port, password=passwd)
    conn = redis.Redis(connection_pool=pool)
    return conn.hgetall(keys)


def rsmembers(keys, ip='10.66.228.123', port='6379', password='crs-170dbkmq:shumeitest2018'):
    pool = redis.ConnectionPool(host=ip, port=port, password=password)
    conn = redis.Redis(connection_pool=pool)
    return conn.smembers(keys)


def rdel(keys, ip='10.66.228.123', port='6379', password='crs-170dbkmq:shumeitest2018'):
    pool = redis.ConnectionPool(host=ip, port=port, password=password)
    conn = redis.Redis(connection_pool=pool)
    return conn.delete(keys)


def rttl(keys, ip='10.66.228.123', port='6379', password='crs-170dbkmq:shumeitest2018'):
    pool = redis.ConnectionPool(host=ip, port=port, password='crs-170dbkmq:shumeitest2018')
    conn = redis.Redis(connection_pool=pool)
    return rttl(keys)
