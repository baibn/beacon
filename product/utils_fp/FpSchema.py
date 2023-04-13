# -*- coding: UTF-8 -*-
import json
from jsonschema import validate

'''
设备指纹jsonschema校验1100返回模板
'''
schema_1100 = {
    "definitions": {},
    "$schema": "http://json-schema.org/draft-06/schema#",
    "$id": "http://example.com/example.json",
    "title": "code:1100的模板",
    "type": "object",
    "properties": {
        "code": {
            "$id": "/properties/code",
            "description": "请求返回状态码",
            "type": "integer",
            "enum": [1100]
        },
        "detail": {
            "$id": "/properties/detail",
            "description": "请求返回detail字段",
            "type": "object",
            "minProperties": 1,
            "properties": {
                "deviceId": {
                    "$id": "/properties/detail/properties/deviceId",
                    "description": "detail字段中的deviceId",
                    "type": "string"
                },
                "sid": {
                    "$id": "/properties/detail/properties/sid",
                    "description": "detail字段中的sid",
                    "type": "string"
                }
            },
            "required": []
        },
        "requestId": {
            "$id": "/properties/requestId",
            "description": "请求返回的唯一请求id",
            "type": "string"
        }
    },
    "required": ["code", "detail", "requestId"],
    "additionalProperties": True
}

'''
设备指纹jsonschema校验1902返回模板
'''
schema_1902 = {
    "definitions": {},
    "$schema": "http://json-schema.org/draft-06/schema#",
    "$id": "http://example.com/example.json",
    "title": "code:1902的模板",
    "type": "object",
    "properties": {
        "code": {
            "$id": "/properties/code",
            "description": "请求返回状态码",
            "type": "integer",
            "enum": [1902]
        },
        "message": {
            "$id": "/properties/message",
            "description": "错误1902时的描述信息字段",
            "type": "string"
        },
        "requestId": {
            "$id": "/properties/requestId",
            "description": "请求返回的唯一请求id",
            "type": "string"
        }
    },
    "required": ["code", "requestId"],
    "additionalProperties": True
}

'''
设备指纹jsonschema校验1903返回模板
'''
schema_1903 = {
    "definitions": {},
    "$schema": "http://json-schema.org/draft-06/schema#",
    "$id": "http://example.com/example.json",
    "title": "code:1903的模板",
    "type": "object",
    "properties": {
        "code": {
            "$id": "/properties/code",
            "description": "请求返回状态码",
            "type": "integer",
            "enum": [1903]
        },
        "message": {
            "$id": "/properties/message",
            "description": "错误1903时的描述信息字段",
            "type": "string"
        },
        "requestId": {
            "$id": "/properties/requestId",
            "description": "请求返回的唯一请求id",
            "type": "string"
        }
    },
    "required": ["code", "message", "requestId"],
    "additionalProperties": True

}

'''
设备指纹jsonschema校验9101返回模板
'''
schema_9101 = {
    "definitions": {},
    "$schema": "http://json-schema.org/draft-06/schema#",
    "$id": "http://example.com/example.json",
    "title": "code:9101的模板",
    "type": "object",
    "properties": {
        "code": {
            "$id": "/properties/code",
            "description": "请求返回状态码",
            "type": "integer",
            "enum": [9101]
        },
        "message": {
            "$id": "/properties/message",
            "description": "错误9101时的描述信息字段",
            "type": "string"
        },
        "requestId": {
            "$id": "/properties/requestId",
            "description": "请求返回的唯一请求id",
            "type": "string"
        }
    },
    "required": ["code", "message", "requestId"],
    "additionalProperties": True
}

'''
设备指纹jsonschema校验1905返回模板
'''
schema_1905 = {
    "definitions": {},
    "$schema": "http://json-schema.org/draft-06/schema#",
    "$id": "http://example.com/example.json",
    "title": "code:1905的模板",
    "type": "object",
    "properties": {
        "code": {
            "$id": "/properties/code",
            "description": "请求返回状态码",
            "type": "integer",
            "enum": [1905]
        },
        "message": {
            "$id": "/properties/message",
            "description": "错误1905时的描述信息字段",
            "type": "string"
        },
        "requestId": {
            "$id": "/properties/requestId",
            "description": "请求返回的唯一请求id",
            "type": "string"
        }
    },
    "required": ["code", "requestId"],
    "additionalProperties": True
}


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
        elif a == -1 or b == -1:#没有查找到"（""）"时，直接返回content
            return content
        else:
            result_info = content[a + 1:b]
            return result_info
    except:
        return content


def check_json_schema(response, code):
    '''
        jsonschema校验函数
    Args:
        response:接口的返回结果
        code:预期校验的jsonschema状态码
    Returns:
        jsonschema校验结果

    '''
    response = json.loads(str(response))
    # code = str(response['code'])
    try:
        if code == 1100:
            validate(response, schema=schema_1100)
            return 'True'
        elif code == 1902:
            validate(response, schema=schema_1902)
            return 'True'
        elif code == 1903:
            validate(response, schema=schema_1903)
            return 'True'
        elif code == 1905:
            validate(response, schema=schema_1905)
            return 'True'
        else:
            validate(response, schema=schema_9101)
            return 'True'
    except:
        return 'False'


def check_jsonp_schema(response, code):
    '''
        jsonschema校验函数
    Args:
        response:接口的返回结果
        code:预期校验的jsonschema状态码
    Returns:
        jsonschema校验结果

    '''
    response = release_jsonp(response)
    response = json.loads(str(response))
    # code = str(response['code'])
    try:
        if code == 1100:
            validate(response, schema=schema_1100)
            return 'True'
        elif code == 1902:
            validate(response, schema=schema_1902)
            return 'True'
        elif code == 1903:
            validate(response, schema=schema_1903)
            return 'True'
        elif code == 1905:
            validate(response, schema=schema_1905)
            return 'True'
        else:
            validate(response, schema=schema_9101)
            return 'True'
    except:
        return 'False'
