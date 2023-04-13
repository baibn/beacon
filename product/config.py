# -*- coding: utf-8 -*-
import os


class Config(object):
    DEBUG = True
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    TOOL_PATH = os.path.join(BASE_DIR, "library_fp/fp-enc-tool.jar")
    PROFILE_TOOL_PATH = os.path.join(BASE_DIR, "library_fp/deploy_write_profile")
    KEY_PATH = os.path.join(BASE_DIR, "library_fp/")
    TEMP_PATH = os.path.join(BASE_DIR, "library_fp/temp.txt")
    ORGANIZATION = "GLOBAL"
    AINFOKEY = "smsdkshumeiorganizationflag"
    JSON_AS_ASCII = False
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///'+ os.path.join(BASE_DIR,'data.db')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root123@localhost:3306/beacon?charset=utf8mb4'
    # 数据改变后自动提交
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # 数据变化的自动警告关闭
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = "qwertyuioplkjhgfds"
    JWT_SECRET = "qwertyuioplkjhgfds"
    REPORT_PATH = os.path.join(BASE_DIR, 'record')
    LOG_NAME = os.path.join(BASE_DIR, 'logs', 'beacon.log')
    # 数据类型配置
    type_dict = {"int": int, "float": float, "string": str, "bool": bool, "list": list, "json": str}
    # 用户所属服务配置
    service_list = [{'天网': 'tianwang'}, {'音视频': 'audio_video'}, {'图片': 'image'}, {'文本': 'text'}, {'WEB': 'web'},
                    {'天象': 'tianxiang'}]
    # 专项类型
    proj_type = ['Videostream_V2', 'Videostream_V4', 'Audiostream_V2', 'Audiostream_V4', 'Android_v3', 'iOS_v3',
                 'web_v3', 'weapp_V3', 'android_v4', 'iOS_v4', 'quickapp_v4']
    # 加密类型
    encode_type = {
        'Android_v3': ['Android_v3_0', 'Android_v3_1', 'Android_v3_3', 'Android_v3_5', 'Android_v3_7', 'Android_v3_9',
                       'Android_v3_11'],
        'iOS_v3': ['iOS_v3_0', 'iOS_v3_2', 'iOS_v3_4', 'iOS_v3_6', 'iOS_v3_8', 'iOS_v3_10'],
        'web_v3': ['web_v3'], 'weapp_V3': ['weapp_V3'],
        'android_v4': ['android_v4_2048'], 'iOS_v4': ['iOS_v4_1024'],
        'quickapp_v4': ['quickapp_v4_1024', 'quickapp_v4_2048']}
    # 模版所属服务配置
    obj_name_list = [{'天网': 'tianwang'}, {'音频文件': 'audio'}, {'音频流': 'audioStream'}, {'视频文件': 'video'},
                     {'视频流': 'videoStream'}, {'图片': 'image'}, {'文本': 'text'}, {'WEB': 'web'}, {'天象': 'tianxiang'}]
    # 服务器ssh配置
    ssh_conf_dict = {
        "test11": {
            "Host": "10.141.48.108",
            "Port": 22,
            "User": "work",
            "Pwd": "shumeitest2019"
        },
        "test12": {
            "Host": "10.141.56.227",
            "Port": 22,
            "User": "work",
            "Pwd": "shumeitest2019"
        },
        "test13": {
            "Host": "10.141.16.179",
            "Port": 22,
            "User": "work",
            "Pwd": "shumeitest2019"
        },
        "test14": {
            "Host": "10.141.16.120",
            "Port": 22,
            "User": "work",
            "Pwd": "shumeitest2019"
        },
        "test-re1": {
            "Host": "10.0.64.89",
            "Port": 22,
            "User": "work",
            "Pwd": "shumeitest2019"
        },
        "devtest2": {
            "Host": "10.141.0.234",
            "Port": 22,
            "User": "work",
            "Pwd": "shumeitest2019"
        }
    }
    category_list = ["NORMAL", "SQL", "CASE"]
    p_key_path = os.path.join(BASE_DIR, "sql_config/id_rsa_mysql")
    sql_conf_path = os.path.join(BASE_DIR, "sql_config/config.json")
    # 邮件相关配置
    MAIL_SERVER = "smtp.ishumei.com"
    MAIL_PORT = 25
    MAIL_USERNAME = "luolingling@ishumei.com"
    MAIL_PASSWORD = "SM@yixuan1129"
    MAIL_CHARSET = "utf-8"
    MAIL_SMTPAUTH = True

    @classmethod
    def init_app(cls, app):
        pass
