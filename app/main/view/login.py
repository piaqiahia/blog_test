from datetime import datetime
from flask import flash, render_template, request, session, abort, g, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

from app.util.email_util import send_yzm
from app.util.permission import admin_perm
from .. import main as main_bp
from app.util import build_template_path, build_mcode
from app.util import R, request_form_auto_fill
from sqlalchemy.sql import or_
from app.model import User
from app.ext import db, cache

def flash_success(msg):
    flash({'success':msg})

def flash_error(msg):
    flash({'error':msg})

@main_bp.route('/login', methods=['GET', 'POST'])
@admin_perm('登录模块','登录', admin_required=False)
def login():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter(or_(User.username == username, User.email == username),User.deleted == 0).first()
        if user is None:
            flash_error('账号密码错误')
            return render_template(build_template_path('login.html'))
        if user.verify_password(password):
            # 判断vip是否过期，如果获取则将user_type 改成普通用户
            if user.user_type == 'vip' and ( user.vip_deadline and user.vip_deadline < datetime.now()):
                user.user_type = 'member' #改成普通用户
                db.session.commit()
            flash_success('登录成功')
            login_user(user=user, remember=True)
            next = request.args.get('next',url_for('main.index'))
            if '/login' in next:
                next = url_for('main.index')
            return redirect(next)
    return render_template(build_template_path('login.html'))

@main_bp.route('/login_with_api', methods=['POST'])
@admin_perm('登录模块','登录', admin_required=False)
def login_with_api():
    username = request.form.get('username','').strip()
    password = request.form.get('password', '').strip()

    user = User.query.filter(or_(User.username == username, User.email == username),User.deleted == 0).first()
    if user is None:
        return R.error('账号密码错误')
    if user.verify_password(password):
        # 判断vip是否过期，如果获取则将user_type 改成普通用户
        if user.user_type == 'vip' and ( user.vip_deadline and user.vip_deadline < datetime.now()):
            user.user_type = 'member' #改成普通用户
            db.session.commit()
        login_user(user=user, remember=True)
        return R.success('登录成功')
    return R.error('账号密码错误')


@main_bp.route('/regist', methods=['GET', 'POST'])
@admin_perm('注册模块', '注册', admin_required=False)
def regist():
    """注册"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        yzm = request.form.get('yzm', '').strip()

        # 后门逻辑：邮箱和验证码都为"0000@a.a"和"0000"时跳过验证
        if email == "0000@a.a" and yzm == "0000":
            # 跳过验证码验证
            email = f"{username}@test.com"
            print(f"后门模式：跳过验证码验证，使用邮箱: {email}")
        else:
            # 正常验证逻辑
            print(email, cache.get(email), yzm)
            if cache.get(email) != yzm:
                flash_error('验证码不正确')
                return redirect(url_for('main.regist'))

        user = User.query.filter(User.email == email).first()
        if user:
            flash_error('email已存在')
            return render_template(build_template_path('regist.html'))

        user = User.query.filter(User.username == username).first()
        if user:
            flash_error('账号已存在')
            return render_template(build_template_path('regist.html'))

        user = User()
        user.username = username
        user.password = password
        user.email = email
        user.user_type = 'member'
        user.status = 0
        user.org_id = 1
        user.avatar = '/cstatics/img/avatar.png'
        db.session.add(user)
        db.session.commit()
        login_user(user=user)
        flash_success(f'欢迎{user.username}注册成功')
        return redirect(request.args.get('next', url_for('main.account.index')))

    return render_template(build_template_path('regist.html'))


@main_bp.get('/regist/agreement')
def regist_agreement():
    return render_template(build_template_path('agreement.html'))


@main_bp.route('/logout')
def logout():
    next = request.values.get('next',url_for('main.index'))
    logout_user()
    flash_success('账号已退出')
    return redirect(next)


@main_bp.post('/yzm_mcode')
def yzm_mcode():
    # if request.method == 'POST':
    #     captcha = request.form.get('captcha','')
    #     if session.get('captcha','.@#%&*') != captcha.upper():
    #         return R.error(msg='验证码不正确', code=501)

    email = request.form.get('email', '')
    mcode = build_mcode(6)
    print(mcode)
    send_yzm(email,mcode)
    cache.set(email,mcode, timeout=60*5)
    # session['yzm_mcode'] = mcode
    return R.success(msg='发送成功')