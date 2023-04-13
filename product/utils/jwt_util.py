# -*- coding: utf-8 -*-

from flask import g
from functools import wraps
import jwt
from flask import request, current_app
from datetime import datetime, timedelta


def generate_jwt(payload, expiry, secret=None):
    """
    生成jwt
    :param payload: dict 载荷
    :param expiry: datetime 有效期
    :param secret: 盐
    :return: token
    """
    _payload = {
        'exp': expiry
    }
    _payload.update(payload)

    if not secret:
        secret = current_app.config['JWT_SECRET']

    token = jwt.encode(_payload, secret, algorithm='HS256')

    return token


def verify_jwt(token, secret=None):
    """
    校验jwt
    :param token: token值
    :param secret: 盐
    :return: payload 载荷
    """
    if not secret:
        secret = current_app.config['JWT_SECRET']
    try:
        payload = jwt.decode(token, secret, algorithms='HS256')
    except:
        payload = None
    return payload


# 每次请求前进行校验authentication
def jwt_authentication():
    g.user_id = None
    g.is_refresh = False
    # 获取请求头中的token
    token = request.headers.get('Authorization')
    if token is not None and token.startswith('JWT '):
        token = token[4:]
        # 验证token
        payload = verify_jwt(token)
        if payload is not None:
            # 保存到g对象中
            g.user_id = payload.get('user_id')
            g.is_refresh = payload.get('is_refresh', False)


def generate_token(user_id, refresh=True):
    """
    token方案(暂时不用这个方案，用tools里的)：
    比如说Token的有效期是7天，当服务器接受到一个Token后，如果它已经过期，但是已过期的时间在xx天内，比如说30天，我们就返回一个新的Token，但是如果过期时间不超过30天就可以用旧的Token换取一个新的Token，如果超过了30天那就需要重新登录。
    生成token
    :param user_id:
    :return:
    """
    # 获取盐
    secret = current_app.config.get('JWT_SECRET')
    # 定义过期时间
    expiry = datetime.utcnow() + timedelta(hours=2)
    # 生成Token
    token = 'JWT ' + generate_jwt({'user_id': user_id}, expiry, secret)
    if refresh:
        expiry = datetime.utcnow() + timedelta(days=15)
        # is_refresh作为更新token的信号
        refresh_token = 'JWT ' + generate_jwt({'user_id': user_id, 'is_refresh': True}, expiry, secret)
    else:
        refresh_token = None
    return token, refresh_token


# 强制登录
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if g.user_id is not None:
            return func(*args, **kwargs)
        else:
            return {'message': 'Invalid token'}, 401

    return wrapper
