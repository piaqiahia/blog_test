import uuid
from flask_login import login_user
from sqlalchemy.sql import or_
from flask.helpers import url_for
from flask import Blueprint, current_app, flash, redirect, request, session, g
from flask.templating import render_template
from flask_login.utils import current_user, login_required
from sqlalchemy import true

from app.model.common import PayLog
from app.model import VipPrice
from app.util.ali_face_pay import AliFacePay
from app.util.auth import auth_decode

from .. import main as main_bp
from app.util import build_template_path, allowed_file, R, request_form_auto_fill, build_mcode, upload
from app.util.ali_send_msg import SendMsg
from datetime import datetime, timedelta
from app.ext import db,cache,csrf
from app.model import User

def flash_success(msg):
    flash({'success':msg})

def flash_error(msg):
    flash({'error':msg})

account_bp = Blueprint('account', __name__)
main_bp.register_blueprint(account_bp, url_prefix='/account')

"""
用户个人信息设置
"""

tpl_profix = '/account/'

@account_bp.get('/')
@login_required
def index():
    return render_template(build_template_path(tpl_profix + 'index.html'))

@account_bp.route('/user_info', methods=['GET', 'POST'])
@login_required
def user_info():
    if request.method == 'POST':
        name = request.form.get('name','')
        avatar = request.form.get('avatar')
        user = current_user
        user.avatar = avatar
        user.name = name
        user.mobile = request.form.get('mobile')
        flash_success('保存成功')
        return redirect(url_for('main.account.user_info'))
    return render_template(build_template_path(tpl_profix + 'user_info.html'))

@account_bp.route('/repassword' , methods=['GET', 'POST'])
@login_required
def repassword():
    """修改密码"""
    if request.method == 'POST':
        oldpassword = request.form.get('oldpassword','')
        password = request.form.get('password','')
        password2 = request.form.get('password2','')
        user = current_user
        if not user.verify_password(oldpassword):
            flash_error('原密码错误')
            return render_template(build_template_path(tpl_profix + 'repassword.html'))
        if password != password2:
            flash_error('新密码两次不一致')
            return render_template(build_template_path(tpl_profix + 'repassword.html'))
        if len(password) < 6:
            flash_error('密码长度最少6位')
            return render_template(build_template_path(tpl_profix + 'repassword.html'))
        flash_success('密码修改成功')
        user.password = password
        return redirect(url_for('main.account.repassword'))
    return render_template(build_template_path(tpl_profix + 'repassword.html'))


@account_bp.route('/email_verify', methods=['GET', 'POST'])
@login_required
def email_verify():
    if request.method == 'POST':
        email = request.form.get('email','').strip()
        if email == '':
            flash_error('邮件不能为空')
            return redirect(url_for('main.account.email_verify'))
        yzm = request.form.get('yzm','').strip()
        if cache.get(email) != yzm.upper():
            flash_error('验证码不正确')
            return redirect(url_for('main.account.email_verify'))
        u = User.query.filter(User.email == email).first()
        user = current_user
        if u.id != user.id:
            flash_error('邮箱已存在，如账号忘记密码，请在登录界面找回密码')
            return redirect(url_for('main.account.email_verify'))
        user.email = email
        flash_success('邮箱修改成功')
        return redirect(url_for('main.account.email_verify'))
    return render_template(build_template_path(tpl_profix + 'email_verify.html'))


@csrf.exempt
@account_bp.route('/auto_vip_pay/', methods=['GET', 'POST'])
def auto_vip_apy():
    """解析token"""
    if request.method == 'POST':
        if not current_user.is_authenticated:
            token = request.values.get('token','').strip()
            # BasicaGNxIzojcGJrZGYyOnNoYTI1NjoyNjAwMDAkNDkzSUxOZkVOWElSemVUbyQxODFlYTI1ODI2MjY0MmQzODg4ZjAwMDU5ZThiZWUyOTBiY2E0ZjM0YTQxMjJkODNmODljZjM4YjQ2NjJkOGU0
            user_info = auth_decode(token)
            print(user_info)
            u = User.query.filter(or_(User.username == user_info[0], User.email == user_info[0]),User.deleted == 0).first()
            if u and u.password_hash == user_info[1]:
                print('执行登录')
                login_user(user=u)
        return redirect(url_for('.vip_pay'))
        
    return render_template(build_template_path(tpl_profix + 'auto_vip_pay.html'))


@account_bp.route('/vip_pay/', methods=['GET', 'POST'])
@login_required
def vip_pay():
    """
    开通vip支付功能
    """
    if request.method == 'POST':
        item_id = request.form.get('item_id',type=int)
        vipprice = VipPrice.query.get(item_id)
        if vipprice is None:
            return R.error(msg='参数错误')
        
        pay_amount = str(vipprice.price)
        out_trade_no = AliFacePay.gen_trade_no(pre_string='vip' +  str(current_user.id))
        log = PayLog()
        log.pay_type = '支付宝当面付'
        log.action_type = '开通VIP'
        log.order_no = out_trade_no
        log.subject = f"{vipprice.name}"
        log.total_fee = pay_amount
        log.state = 0
        log.ref_id = vipprice.id

        db.session.add(log)
        db.session.commit()
        sendbox_debug = current_app.config.get('ALIPAY_SENDBOX_DEBUG','FALSE').upper() == 'TRUE'
        pay = AliFacePay(
            app_id=current_app.config.get('ALIPAY_APPID'),
            app_private_key= current_app.config.get('ALIPAY_PRIVATE_KEY'),
            alipay_public_key= current_app.config.get('ALIPAY_PUBLIC_KEY'),
            notify_url= current_app.config.get('ALIPAY_NOTIFY_URL'),
            sandbox_debug=sendbox_debug,
        )
        qrcode_url = pay.precreate(out_trade_no, pay_amount,log.subject)
        result = {
            'out_trade_no': out_trade_no,
            'qrcode_url': qrcode_url,
        }
        return R.success(result)
    prices = VipPrice.query.all()
    return render_template(build_template_path(tpl_profix + 'vip_pay.html'), prices = prices)



@account_bp.route('/pay_logs', methods=['GET', 'POST'])
@login_required
def pay_logs():
    page = request.args.get('page', 1, type=int)
    now = datetime.now()
    logs = PayLog.query.filter(PayLog.create_by == current_user.id, PayLog.state == 1, PayLog.ctime >= now - timedelta(days=30)).order_by(PayLog.id.desc()). \
        paginate(page=page, per_page=current_app.config['H3BLOG_POST_PER_PAGE'], error_out=False)
    return render_template(build_template_path(tpl_profix + 'pay_logs.html'), pagelist = logs)


@account_bp.route('/password/reset' , methods=['GET', 'POST'])
def password_reset():
    """密码重置"""
    if request.method == 'POST':
        email = request.form.get('email','')
        password = request.form.get('password','')
        yzm = request.form.get('yzm','')
        user = User.query.filter(User.email == email,User.deleted == 0).first()
        if cache.get(email) != yzm:
            flash_error('验证码错误')
            return render_template(build_template_path(tpl_profix + 'password_reset.html'))
        if user is None:
            flash_error('账号不存在请先注册')
            return render_template(build_template_path(tpl_profix + 'password_reset.html'))
        if len(password) < 6:
            flash_error('密码长度最少6位')
            return render_template(build_template_path(tpl_profix + 'password_reset.html'))
        flash_success('密码修改成功')
        user.password = password
        return redirect(url_for('main.login'))
    return render_template(build_template_path(tpl_profix + 'password_reset.html'))