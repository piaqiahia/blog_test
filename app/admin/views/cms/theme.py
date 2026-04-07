from flask import render_template, request, jsonify, Blueprint,current_app, make_response
from flask_login.utils import login_required, current_user

from app.util.common import time_now_name, upload, get_download_file_path
from app.util.permission import admin_perm
from app.util import R, request_form_auto_fill
from app.util.model import query_model
from app.util.dict_data import get_dict_data, get_label_by_value
from app.ext import db

from openpyxl import Workbook
from app.util.template_manager import template_manager

from app.admin.views.cms import cms_bp
from app.model import Theme
import os

bp = Blueprint('theme', __name__)
cms_bp.register_blueprint(bp, url_prefix='/theme')
tpl_prefix = 'admin/cms/theme/'
model_name = '网站主题'

@bp.route('/',methods=['GET'])
@login_required
@admin_perm(model_name, '查看列表', permission='cms:theme:view')
def index():
    """
    列表
    """
    return render_template( tpl_prefix + 'list.html')

@bp.route('/list',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '获取列表数据', permission='cms:theme:view')
def list():
    """
    获取列表
    """
    list = query_model(Theme, search_query, need_scope=True)
    return jsonify(list)

def search_query(query):
    query = query.filter(Theme.deleted == 0)
    value = request.values.get('name','').strip()
    if value != '':
        query = query.filter(Theme.name == value)
    value = request.values.get('code','').strip()
    if value != '':
        query = query.filter(Theme.code == value)
    

    query = query.order_by(Theme.id.desc())
    value = request.values.get('ids','').strip()
    if value != '':
        ids = value.split(',')
        query = query.filter(Theme.id.in_(ids))
    return query


@bp.route('/export',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '导出excel', permission='cms:theme:export')
def export():
    list = query_model(Theme, search_query, is_page=False, need_scope=True)
    
    title = ["主题名称","主题代码","主题描述","预览图片","作者","版本号","是否激活","排序","备注","机构id"]
    is_active_datas = get_dict_data('theme_is_active')
    wb = Workbook()
    sheet_names = wb.sheetnames
    ws = wb[sheet_names[0]]
    ws.append(title)
    for row in list:
        data = []
        data.append(row.name)
        data.append(row.code)
        data.append(row.description)
        data.append(row.preview_img)
        data.append(row.author)
        data.append(row.version)
        data.append(get_label_by_value(is_active_datas, row.is_active))
        data.append(row.sn)
        data.append(row.remark)
        data.append(row.org_id)
        ws.append(data)
    
    abs_filepath, filepath = get_download_file_path("{}.xlsx".format(time_now_name()))
    wb.save(abs_filepath)
    return R.success(msg=filepath)
    

@bp.route('/add',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '添加', permission='cms:theme:add')
def add():
    """
    添加
    """
    if request.method == 'POST': # 添加
        o = Theme()
        request_form_auto_fill(o)
        preview_img = request.files.get('preview_img')
        if preview_img:
            img_url = upload('preview_img', 'img')
            o.preview_img = img_url

        db.session.add(o)
        db.session.commit()
        return R.success(msg='成功')

    return render_template( tpl_prefix + 'add.html')

@bp.route('/edit',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '修改', permission='cms:theme:edit')
def edit():
    """
    编辑修改
    """
    if request.method == 'POST': 
        id = request.form.get('id', 0, type=int)
        o = Theme.query.get(id)
        request_form_auto_fill(o)
        preview_img = request.files.get('preview_img')
        if preview_img:
            img_url = upload('preview_img', 'img')
            o.preview_img = img_url

        db.session.commit()
        return R.success()

    id = request.args.get('id', 0, type=int)
    o = Theme.query.get(id)
    return render_template(tpl_prefix + 'edit.html', d = o)

@bp.route('/remove',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '删除', permission='cms:theme:remove')
def remove():
    """
    根据id删除
    """
    ids = request.values.get('ids', type=str)
    ids = [int(i) for i in ids.split(',')]
    Theme.query.filter(Theme.id.in_(ids)).delete()
    db.session.commit()
    return R.success()



@bp.route('/scan', methods=['POST'])
@login_required
@admin_perm(model_name, '扫描', permission='cms:theme:scan')
def scan():
    """扫描主题目录"""
    # 使用模板管理器扫描主题
    added_count, message = template_manager.scan_themes()
    return R.success()


@bp.route('/activate', methods=['GET'])
@login_required
@admin_perm(model_name, opt='激活', permission='cms:theme:activate')
def activate():
    """激活主题"""
    theme_id = request.args.get('id', type=int)
    if not theme_id:
        return R.error(msg='参数错误')
    
    theme = Theme.query.get_or_404(theme_id)
    
    # 使用模板管理器激活主题
    success, message = template_manager.activate_theme(theme.code)
    
    if success:
        return R.success(msg=message)
    else:
        return R.error(msg=message)