from flask import render_template, request, redirect, url_for, flash
from flask.globals import session
from flask_login import login_user, logout_user, login_required

from app.admin import admin
from app.ext import db
from app.admin.forms import AddAdminForm, LoginForm
from app.model import User, Org
import random
from app.util import R, request_form_auto_fill, build_mcode
from app.util.ali_send_msg import SendMsg
import random
import string

def build_org_code() -> str:
    while True:
     code = ''.join(random.sample(string.ascii_letters + string.digits, 4))
     code = code.lower()
     org = Org.query.filter(Org.code == code).first()
     if org is None:
         return code

@admin.route('/reg_mcode', methods=['GET', 'POST'])
def reg_mcode():
    if request.method == 'POST':
        captcha = request.form.get('captcha','')
        if session.get('captcha','.@#%&*') != captcha.upper():
            return R.error(msg='验证码不正确', code=501)

        mobile = request.form.get('mobile', '')
        user = User.query.filter(User.username == mobile).first()
        if user:
            return R.error(msg = '手机号已注册', code = 502)
        mcode = build_mcode(6)
        sm = SendMsg()
        sm.send_code(mobile, mcode)
        session['reg_mcode'] = mcode
        return R.success(msg='短信发送成功')

@admin.route('/regist', methods=['GET', 'POST'])
def regist():
    """机构注册"""
    if request.method == 'POST':
        org = Org()
        request_form_auto_fill(org)
        user_name = request.form.get('user_name', '')
        user_mobile = request.form.get('user_mobile','')
        user = User.query.filter(User.username == user_mobile).first()
        if user :
            return R.error(msg='手机账号已经存在')
        mcode = request.form.get('mcode','')
        print(session.get('reg_mcode','!@#$%^*&'))
        if session.get('reg_mcode','!@#$%^*&') != mcode:
            return R.error(msg='短信验证码不正确')
        password = request.form.get('password', '')
        repassword = request.form.get('repassword','')
        if password != repassword:
            return R.error(msg='密码不一致')
        org.contact = user_name
        org.mobile = user_mobile
        org.code = build_org_code()
        org.is_read = '是'

        db.session.add(org)

        user = User()
        user.username = user_mobile
        user.name = user_name
        user.mobile = user_mobile
        user.password = password
        user.status = 1
        user.org = org
        user.nickname = user_name
        user.user_type = 'qiye'
        
        db.session.add(user)

        return R.success(msg='注册成功')

    return render_template('admin/regist.html')


@admin.get('/regist/agreement')
def regist_agreement():
    return render_template('admin/regist_agreement.html')