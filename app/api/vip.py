from datetime import datetime
from flask import render_template, request, jsonify, Blueprint,current_app, make_response
from flask_login.utils import login_required, current_user

from app.model.common import PayLog
from app.util.ali_face_pay import AliFacePay
from app.util.common import time_now_name, upload, get_download_file_path
from app.util.permission import admin_perm
from app.util import R, request_form_auto_fill
from app.util.model import query_model
from app.util.dict_data import get_dict_data, get_label_by_value
from app.ext import db

from app.model import VipPrice

from . import api
from app.ext import csrf

bp = Blueprint('vip', __name__)
api.register_blueprint(bp, url_prefix='/vip')
model_name = '开通vip接口'

@csrf.exempt
@bp.get('/prices')
def prices():
    """
    价格列表
    """
    list = VipPrice.query.all()
    return R.success(data=list)

@csrf.exempt
@bp.post('/vip_pay_qrcode')
@login_required
def vip_pay_qrcode():
    """
    开通vip支付功能
    """
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
    log.subject = f"seo-tool-{vipprice.name}"
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

@csrf.exempt
@bp.post('/is_pay/')
# @login_required
def is_pay():
    """
    查看是否支付成功
    """
    order_no = request.form.get('order_no','')
    log = PayLog.query.filter(PayLog.order_no == order_no).first()
    if log and log.state == 1:
        return R.success(True,msg='支付成功')
    return R.error(False,msg='未支付')