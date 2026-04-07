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
from app.model import Banner
import os

bp = Blueprint('banner', __name__)
cms_bp.register_blueprint(bp, url_prefix='/banner')
tpl_prefix = 'admin/cms/banner/'
model_name = '横幅管理'

@bp.route('/',methods=['GET'])
@login_required
@admin_perm(model_name, '查看列表', permission='cms:banner:view')
def index():
    """
    列表
    """
    return render_template( tpl_prefix + 'list.html')

@bp.route('/list',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '获取列表数据', permission='cms:banner:view')
def list():
    """
    获取列表
    """
    list = query_model(Banner, search_query, need_scope=True)
    return jsonify(list)

def search_query(query):
    query = query.filter(Banner.deleted == 0)
    value = request.values.get('name','').strip()
    if value != '':
        query = query.filter(Banner.name == value)
    value = request.values.get('mtype','').strip()
    if value != '':
        query = query.filter(Banner.mtype.like('%%%s%%' % value))
    

    query = query.order_by(Banner.id.desc())
    value = request.values.get('ids','').strip()
    if value != '':
        ids = value.split(',')
        query = query.filter(Banner.id.in_(ids))
    query = query.order_by(Banner.mtype.asc(),Banner.order_num.asc())
    return query


@bp.route('/export',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '导出excel', permission='cms:banner:export')
def export():
    list = query_model(Banner, search_query, is_page=False, need_scope=True)
    
    title = ["机构id","名称","类型","图片","链接","备注"]
    wb = Workbook()
    sheet_names = wb.sheetnames
    ws = wb[sheet_names[0]]
    ws.append(title)
    for row in list:
        data = []
        data.append(row.org_id)
        data.append(row.name)
        data.append(row.mtype)
        data.append(row.img)
        data.append(row.url)
        data.append(row.remark)
        ws.append(data)
    
    abs_filepath, filepath = get_download_file_path("{}.xlsx".format(time_now_name()))
    wb.save(abs_filepath)
    return R.success(msg=filepath)
    

@bp.route('/add',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '添加', permission='cms:banner:add')
def add():
    """
    添加
    """
    if request.method == 'POST': # 添加
        o = Banner()
        request_form_auto_fill(o)
        img = request.files.get('img')
        if img:
            img_url = upload('img', 'img')
            o.img = img_url

        db.session.add(o)
        db.session.commit()
        return R.success(msg='成功')

    return render_template( tpl_prefix + 'add.html')

@bp.route('/edit',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '修改', permission='cms:banner:edit')
def edit():
    """
    编辑修改
    """
    if request.method == 'POST': 
        id = request.form.get('id', 0, type=int)
        o = Banner.query.get(id)
        request_form_auto_fill(o)
        img = request.files.get('img')
        if img:
            img_url = upload('img', 'img')
            o.img = img_url

        db.session.commit()
        return R.success()

    id = request.args.get('id', 0, type=int)
    o = Banner.query.get(id)
    return render_template(tpl_prefix + 'edit.html', d = o)

@bp.route('/remove',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '删除', permission='cms:banner:remove')
def remove():
    """
    根据id删除
    """
    ids = request.values.get('ids', type=str)
    ids = [int(i) for i in ids.split(',')]
    Banner.query.filter(Banner.id.in_(ids)).update({'deleted': 1})
    return R.success()


