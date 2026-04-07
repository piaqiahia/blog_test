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
from app.model import VipPrice
import os

bp = Blueprint('vipprice', __name__)
cms_bp.register_blueprint(bp, url_prefix='/vipprice')
tpl_prefix = 'admin/cms/vipprice/'
model_name = 'vip价格'

@bp.route('/',methods=['GET'])
@login_required
@admin_perm(model_name, '查看列表', permission='cms:vipprice:view')
def index():
    """
    列表
    """
    return render_template( tpl_prefix + 'list.html')

@bp.route('/list',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '获取列表数据', permission='cms:vipprice:view')
def list():
    """
    获取列表
    """
    list = query_model(VipPrice, search_query, need_scope=True)
    return jsonify(list)

def search_query(query):
    query = query.filter(VipPrice.deleted == 0)
    value = request.values.get('name','').strip()
    if value != '':
        query = query.filter(VipPrice.name == value)
    value = request.values.get('price','').strip()
    if value != '':
        query = query.filter(VipPrice.price == value)
    value = request.values.get('days','').strip()
    if value != '':
        query = query.filter(VipPrice.days == value)
    

    query = query.order_by(VipPrice.sn.asc(),VipPrice.id.asc())
    value = request.values.get('ids','').strip()
    if value != '':
        ids = value.split(',')
        query = query.filter(VipPrice.id.in_(ids))
    return query


@bp.route('/export',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '导出excel', permission='cms:vipprice:export')
def export():
    list = query_model(VipPrice, search_query, is_page=False, need_scope=True)
    
    title = ["备注","机构id","名称","支付金额","天数","描述"]
    wb = Workbook()
    sheet_names = wb.sheetnames
    ws = wb[sheet_names[0]]
    ws.append(title)
    for row in list:
        data = []
        data.append(row.remark)
        data.append(row.org_id)
        data.append(row.name)
        data.append(row.price)
        data.append(row.days)
        data.append(row.desp)
        ws.append(data)
    
    abs_filepath, filepath = get_download_file_path("{}.xlsx".format(time_now_name()))
    wb.save(abs_filepath)
    return R.success(msg=filepath)
    

@bp.route('/add',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '添加', permission='cms:vipprice:add')
def add():
    """
    添加
    """
    if request.method == 'POST': # 添加
        o = VipPrice()
        request_form_auto_fill(o)

        db.session.add(o)
        db.session.commit()
        return R.success(msg='成功')

    return render_template( tpl_prefix + 'add.html')

@bp.route('/edit',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '修改', permission='cms:vipprice:edit')
def edit():
    """
    编辑修改
    """
    if request.method == 'POST': 
        id = request.form.get('id', 0, type=int)
        o = VipPrice.query.get(id)
        request_form_auto_fill(o)

        db.session.commit()
        return R.success()

    id = request.args.get('id', 0, type=int)
    o = VipPrice.query.get(id)
    return render_template(tpl_prefix + 'edit.html', d = o)

@bp.route('/remove',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '删除', permission='cms:vipprice:remove')
def remove():
    """
    根据id删除
    """
    ids = request.values.get('ids', type=str)
    ids = [int(i) for i in ids.split(',')]
    VipPrice.query.filter(VipPrice.id.in_(ids)).update({'deleted': 1})
    return R.success()


