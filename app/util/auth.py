import base64
from datetime import datetime

def create_authorization(username,password)->str:
    """创建认证"""
    user_info_str = username + '#:#' + password
    user_info = base64.b64encode(user_info_str.encode())
    return 'Basic' + user_info.decode()

def auth_decode(authorization:str):
    """根据认证获取用户信息"""
    authorization = authorization.replace('Basic', '', 1)
    try:
        data = base64.b64decode(authorization.encode())
        user_info = data.decode().split("#:#")
    except:
        return tuple()
    return tuple(user_info)


def need_token(func):
    def wrapper(*args,**kwargs):
        return func(*args,**kwargs)
    return wrapper