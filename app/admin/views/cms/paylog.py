from flask import render_template, request, jsonify, Blueprint,current_app, make_response
from flask_login.utils import login_required, current_user

from app.util.common import time_now_name, upload, get_download_file_path
from app.util.permission import admin_perm
from app.util import R, request_form_auto_fill
from app.util.model import query_model
from app.util.dict_data import get_dict_data, get_label_by_value
from app.ext import db

from openpyxl import Workbook

from app.admin.views.cms import cms_bp
from app.model import PayLog
import os

bp = Blueprint('paylog', __name__)
cms_bp.register_blueprint(bp, url_prefix='/paylog')
tpl_prefix = 'admin/cms/paylog/'
model_name = '支付日志'

@bp.route('/',methods=['GET'])
@login_required
@admin_perm(model_name, '查看列表', permission='cms:paylog:view')
def index():
    """
    列表
    """
    return render_template( tpl_prefix + 'list.html')

@bp.route('/list',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '获取列表数据', permission='cms:paylog:view')
def list():
    """
    获取列表
    """
    list = query_model(PayLog, search_query, need_scope=True)
    return jsonify(list)

def search_query(query):
    query = query.filter(PayLog.deleted == 0)
    value = request.values.get('pay_type','').strip()
    if value != '':
        query = query.filter(PayLog.pay_type.like('%%%s%%' % value))
    value = request.values.get('action_type','').strip()
    if value != '':
        query = query.filter(PayLog.action_type.like('%%%s%%' % value))
    value = request.values.get('order_no','').strip()
    if value != '':
        query = query.filter(PayLog.order_no.like('%%%s%%' % value))
    value = request.values.get('subject','').strip()
    if value != '':
        query = query.filter(PayLog.subject.like('%%%s%%' % value))
    value = request.values.get('trade_no','').strip()
    if value != '':
        query = query.filter(PayLog.trade_no.like('%%%s%%' % value))
    value = request.values.get('total_fee','').strip()
    if value != '':
        query = query.filter(PayLog.total_fee == value)
    value = request.values.get('state','').strip()
    if value != '':
        query = query.filter(PayLog.state == value)
    value = request.values.get('return_code','').strip()
    if value != '':
        query = query.filter(PayLog.return_code == value)
    

    query = query.order_by(PayLog.id.desc())
    value = request.values.get('ids','').strip()
    if value != '':
        ids = value.split(',')
        query = query.filter(PayLog.id.in_(ids))
    return query


@bp.route('/export',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '导出excel', permission='cms:paylog:export')
def export():
    list = query_model(PayLog, search_query, is_page=False, need_scope=True)
    
    title = ["备注","机构id","支付类型","动作类型","订单号","商品描述","交易订单号","支付金额","支付状态","支付回调信息返回码","返回信息","回调时间"]
    state_datas = get_dict_data('paylog_state')
    wb = Workbook()
    sheet_names = wb.sheetnames
    ws = wb[sheet_names[0]]
    ws.append(title)
    for row in list:
        data = []
        data.append(row.remark)
        data.append(row.org_id)
        data.append(row.pay_type)
        data.append(row.action_type)
        data.append(row.order_no)
        data.append(row.subject)
        data.append(row.trade_no)
        data.append(row.total_fee)
        data.append(get_label_by_value(state_datas, row.state))
        data.append(row.return_code)
        data.append(row.return_data)
        data.append(row.return_time)
        ws.append(data)
    
    abs_filepath, filepath = get_download_file_path("{}.xlsx".format(time_now_name()))
    wb.save(abs_filepath)
    return R.success(msg=filepath)
    

@bp.route('/add',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '添加', permission='cms:paylog:add')
def add():
    """
    添加
    """
    if request.method == 'POST': # 添加
        o = PayLog()
        request_form_auto_fill(o)

        db.session.add(o)
        db.session.commit()
        return R.success(msg='成功')

    return render_template( tpl_prefix + 'add.html')

@bp.route('/edit',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '修改', permission='cms:paylog:edit')
def edit():
    """
    编辑修改
    """
    if request.method == 'POST': 
        id = request.form.get('id', 0, type=int)
        o = PayLog.query.get(id)
        request_form_auto_fill(o)

        db.session.commit()
        return R.success()

    id = request.args.get('id', 0, type=int)
    o = PayLog.query.get(id)
    return render_template(tpl_prefix + 'edit.html', d = o)

@bp.route('/remove',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '删除', permission='cms:paylog:remove')
def remove():
    """
    根据id删除
    """
    ids = request.values.get('ids', type=str)
    ids = [int(i) for i in ids.split(',')]
    PayLog.query.filter(PayLog.id.in_(ids)).update({'deleted': 1})
    return R.success()


