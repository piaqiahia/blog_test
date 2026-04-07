from datetime import datetime, timedelta
from flask import request, jsonify, Blueprint,current_app, url_for
from flask.globals import session
from flask_login.utils import login_required, current_user, login_user,logout_user

from app.util.email_util import send_yzm
from . import api
from app.util.permission import admin_perm
from app.util import R, build_mcode
from app.util.ali_send_msg import SendMsg
from app.model import User, LoginLog, Role
from app.ext import db
from app.util.ip_util import get_real_ip, get_ip_city
from app.util.auth import create_authorization
from app.ext import csrf,cache
from app.util.perms_cache import set_perms_cache, delete_perms_cache
from sqlalchemy.sql import or_


@csrf.exempt
@api.post('/mcode')
# @admin_perm('短信模块', '发送验证码',admin_required=False)
def mcode():
    mobile = request.form.get('mobile', '')
    if len(mobile) != 11:
        return R.error(msg='手机号错误')
    mcode = build_mcode(6)
    sm = SendMsg()
    sm.send_code(mobile, mcode)
    session['reg_mcode'] = mcode
    print(mcode)
    current_app.logger.info(session.get('reg_mcode','!@#$%^*&'))
    return R.success(mcode ,msg='短信发送成功')

@csrf.exempt
@api.post('/login')
@admin_perm('客户端登录','登录', admin_required=False)
def login():
    username = request.form.get('username','')
    password = request.form.get('password', '')

    ip = get_real_ip()
    login_log = LoginLog(
        login_name = username,
        ipaddr = ip,
        login_location = get_ip_city(ip),
        browser = request.user_agent.browser,
        ossystem = request.user_agent.platform,
        state = 1,
    )

    u = User.query.filter(or_(User.username == username, User.email == username),User.deleted == 0).first()
    if u is None:
        login_log.state = 0
        login_log.msg = '用户未注册'
        return R.error(msg='用户未注册')
    if not u.verify_password(password):
        login_log.state = 0
        login_log.msg = '密码错误'
        return R.error(msg='密码错误')
    if u.status == 1:
        login_log.state = 0
        login_log.msg = '账户已锁定'
        return R.error(msg='账户已锁定')
    #判断是否3天内新用户
    delta = datetime.now() - u.ctime
    if delta <= timedelta(days=0):
        pass
    else:
        if u.user_type == 'member':
            login_log.state = 0
            login_log.msg = '普通会员禁止登录，请升级VIP会员'
            return R.error(msg='普通会员禁止登录，请升级VIP会员')
    if u.status == 0:
        login_user(user=u)
        # set_perms_cache(u)
        login_log.state = 1
        login_log.msg = '登录成功'
        d = { 
            'name': u.name,
            'username': u.username,
            'avatar': u.avatar
        }
        token = create_authorization(username, u.password_hash)
        d['token'] = token
        return R.success(d,msg='登录成功')
    db.session.add(login_log)


@csrf.exempt
@api.post('/v1/login')
@admin_perm('客户端登录','登录', admin_required=False)
def login_v1():
    username = request.form.get('username','').strip()
    password = request.form.get('password', '').strip()
    mcode = request.form.get('mcode', '').strip()

    ip = get_real_ip()
    login_log = LoginLog(
        login_name = username,
        ipaddr = ip,
        login_location = get_ip_city(ip),
        browser = 'seo-tool',
        ossystem = request.user_agent.platform,
        state = 1,
    )

    u = User.query.filter(or_(User.username == username, User.email == username),User.deleted == 0).first()
    if u is None:
        login_log.state = 0
        login_log.msg = '用户未注册'
        db.session.add(login_log)
        return R.error(msg='用户未注册')
    if not u.verify_password(password):
        login_log.state = 0
        login_log.msg = '密码错误'
        db.session.add(login_log)
        return R.error(msg='密码错误')
    if u.status == 1:
        login_log.state = 0
        login_log.msg = '账户已锁定'
        db.session.add(login_log)
        return R.error(msg='账户已锁定')
    #判断是否3天内新用户
    # delta = datetime.now() - u.ctime
    # if delta <= timedelta(days=0):
    #     pass
    # else:
    #     if u.user_type == '2':
    #         login_log.state = 0
    #         login_log.msg = '普通会员禁止登录，请升级VIP会员'
    #         return R.error(msg='普通会员禁止登录，请升级VIP会员') 
    if u.status == 0:
        login_user(user=u)
        # set_perms_cache(u)
        login_log.state = 1
        login_log.msg = '登录成功'
        db.session.add(login_log)
        d = { 
            'name': u.name,
            'username': u.username,
            'avatar': u.avatar,
            'email': u.email,
            'vip_deadline': u.vip_deadline if u.vip_deadline else '',
            'is_vip': u.user_type == '3' and (u.vip_deadline > datetime.now() if u.vip_deadline else False)
        }
        token = create_authorization(username, u.password_hash)
        d['token'] = token
        return R.success(d,msg='登录成功')
    

@csrf.exempt
@api.post('/user_info')
@login_required
def user_info():
    """获取用户信息"""
    u = current_user
    d = { 
        'name': u.name,
        'username': u.username,
        'avatar': u.avatar,
        'email': u.email,
        'vip_deadline': u.vip_deadline if u.vip_deadline else '',
        'is_vip': u.user_type == '3' and (u.vip_deadline > datetime.now() if u.vip_deadline else False)
    }
    token = create_authorization(u.username, u.password_hash)
    d['token'] = token
    return R.success(d)

@csrf.exempt
@api.get('/logout')
@admin_perm('退出模块','登出')
def logout():
    """登出系统"""
    delete_perms_cache(current_user)
    logout_user()
    return R.success(msg='退出成功')


@csrf.exempt
@api.post('/regist')
def regist():
    email = request.form.get('email', '').strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    yzm = request.form.get('yzm', '').strip()

    # 后门逻辑：邮箱和验证码都为"0000"时跳过验证
    if email == "0000@a.a" and yzm == "0000":
        # 跳过验证码验证，直接使用测试邮箱
        email = f"{username}@test.com"
        print(f"后门模式：跳过验证码验证，使用邮箱: {email}")

    # 注意：这里完全删除了 else 分支和验证码验证代码

    # 检查邮箱是否已注册
    user = User.query.filter(User.email == email).first()
    if user:
        return R.error(msg='email已注册')

    # 检查用户名是否已存在
    user = User.query.filter(User.username == username).first()
    if user:
        return R.error(msg='账号已存在')

    # 创建用户
    user = User()
    user.username = username
    user.password = password
    user.email = email
    user.user_type = 2
    user.status = 0
    user.org_id = 5
    user.avatar = '/cstatics/img/avatar.png'
    db.session.add(user)
    db.session.commit()
    return R.success(msg='注册成功')


@csrf.exempt
@api.post('/yzm_mcode')
def yzm_mcode():
    email = request.form.get('email', '')
    mcode = build_mcode(6)
    print(mcode)
    send_yzm(email,mcode)
    cache.set(email,mcode, timeout=60*5)
    # session['yzm_mcode'] = mcode
    return R.success(msg='发送成功')