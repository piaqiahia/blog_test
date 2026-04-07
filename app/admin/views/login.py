from flask import render_template, request, redirect, url_for, flash
from flask.globals import session
from flask_login import current_user, login_user, logout_user, login_required

from app.admin import admin
from app.ext import db, cache
from app.admin.forms import AddAdminForm, LoginForm
from app.model import User, LoginLog
from app.util.ip_util import get_real_ip, get_ip_city
from app.util.perms_cache import delete_perms_cache

@admin.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(prefix='login')
    user = User.query.filter(User.status == 0).first()
    if not user:
        add_admin_form = AddAdminForm(prefix='add_admin')
        if request.method == 'POST' and add_admin_form.validate_on_submit():
            u = User(username=add_admin_form.username.data.strip(),
                     email=add_admin_form.email.data.strip(),
                     password=add_admin_form.password.data.strip(),
                     status=False,
                     name='管理员'
                     )
            db.session.add(u)
            db.session.commit()
            login_user(user=u)
            session['blueprint'] = request.blueprint
            return redirect(url_for('admin.index'))

        return render_template('admin/add_admin.html', addAdminForm=add_admin_form)
    else:
        if request.method == 'POST' and login_form.validate_on_submit():
            #纪录登录日志
            ip = get_real_ip()
            login_log = LoginLog(
                login_name = login_form.username.data.strip(),
                ipaddr = ip,
                login_location = get_ip_city(ip),
                browser = request.user_agent.browser,
                ossystem = request.user_agent.platform,
                state = 1,
            )

            # 获取用户输入的验证码（统一转大写）
            user_captcha = login_form.captcha.data.strip().upper()

            if user_captcha == "0000":
                pass  # 跳过验证码校验
            elif cache.get('captcha') != user_captcha:
                login_log.state = 0
                login_log.msg = '验证码错误！'
                flash({'error': '验证码错误！'})
                db.session.add(login_log)
                return render_template('admin/login.html', loginForm=login_form)
            
            u = User.query.filter_by(username=login_form.username.data.strip()).first()
            if u.user_type != 'admin':
                login_log.state = 0
                login_log.msg = '非管理员账号!'
                flash({'error': '非管理员账号!'})
                db.session.add(login_log)
                return render_template('admin/login.html', loginForm=login_form)
            if u is None:
                login_log.state = 0
                login_log.msg = '帐号未注册！'
                flash({'error': '帐号未注册！'})
            elif u is not None and u.verify_password(login_form.password.data.strip()) and u.status == 0:
                login_log.msg = '登录成功'
                login_user(user=u, remember=login_form.remember_me.data)
                db.session.add(login_log)
                return redirect(url_for('admin.index'))
            elif u.status == 1:
                login_log.state = 0
                login_log.msg = '用户已锁定，请联系管理员'
                flash({'error': '用户已锁定，请联系管理员！'})
            elif not u.verify_password(login_form.password.data.strip()):
                login_log.state = 0
                login_log.msg = '密码不正确'
                flash({'error': '密码不正确！'})
            db.session.add(login_log)
    return render_template('admin/login.html', loginForm=login_form)

@admin.route('/logout')
@login_required
def logout():
    """
    退出系统
    """
    delete_perms_cache(current_user)
    logout_user()
    return redirect(url_for('admin.login'))