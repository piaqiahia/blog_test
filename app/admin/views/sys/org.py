from flask import render_template, request, jsonify, Blueprint,current_app, make_response
from flask_login.utils import login_required, current_user

from app.util.common import time_now_name, upload, get_download_file_path
from app.util.permission import admin_perm
from app.util import R, request_form_auto_fill
from app.util.model import query_model
from app.util.dict_data import get_dict_data, get_label_by_value
from app.ext import db

from openpyxl import Workbook

from app.admin.views.sys import sys_bp
from app.model import Org
import os

bp = Blueprint('org', __name__)
sys_bp.register_blueprint(bp, url_prefix='/org')
tpl_prefix = 'admin/sys/org/'
model_name = '部门管理'

@bp.route('/',methods=['GET'])
@login_required
@admin_perm(model_name, '查看列表', permission='sys:org:view')
def index():
    """
    列表
    """
    return render_template( tpl_prefix + 'list.html')

@bp.route('/list',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '获取列表数据', permission='sys:org:view')
def list():
    """
    获取列表
    """
    query = search_query(Org.query)
    list = query.all()
    return jsonify(list)

def search_query(query):
    query = query.filter(Org.deleted == 0)
    value = request.values.get('name','').strip()
    if value != '':
        query = query.filter(Org.name == value)
    value = request.values.get('parent_id','').strip()
    if value != '':
        query = query.filter(Org.parent_id == value)
    value = request.values.get('order_num','').strip()
    if value != '':
        query = query.filter(Org.order_num == value)
    

    query = query.order_by(Org.order_num.asc())
    return query


@bp.route('/export',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '导出excel', permission='sys:org:export')
def export():
    query  = search_query(Org.query)
    list = query.all()
    
    title = ["名称","父ID","排序"]
    wb = Workbook()
    sheet_names = wb.sheetnames
    ws = wb[sheet_names[0]]
    ws.append(title)
    for row in list:
        data = []
        data.append(row.name)
        data.append(row.parent_id)
        data.append(row.order_num)
        ws.append(data)
    
    abs_filepath, filepath = get_download_file_path("{}.xlsx".format(time_now_name()))
    wb.save(abs_filepath)
    return R.success(msg=filepath)
    

@bp.route('/add',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '添加', permission='sys:org:add')
def add():
    """
    添加
    """
    if request.method == 'POST': # 添加
        o = Org()
        request_form_auto_fill(o)
        if o.parent_id == 'None' or o.parent_id == '':
            o.parent_id = None

        db.session.add(o)
        db.session.commit()
        return R.success(msg='成功')

    parent_id = request.args.get('parent_id', 0, type = int)
    d = Org()
    if parent_id == 0 :
        d.id = None
        d.name = '无'
    else:
        d = Org.query.get(parent_id)
    return render_template( tpl_prefix + 'add.html', d = d)

@bp.route('/edit',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '修改', permission='sys:org:edit')
def edit():
    """
    编辑修改
    """
    if request.method == 'POST': 
        id = request.form.get('id', 0, type=int)
        o = Org.query.get(id)
        request_form_auto_fill(o)

        if o.parent_id == 'None' or o.parent_id == '':
            o.parent_id = None
        db.session.commit()
        return R.success()

    id = request.args.get('id', 0, type=int)
    o = Org.query.get(id)
    return render_template(tpl_prefix + 'edit.html', d = o)

@bp.route('/remove',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '删除', permission='sys:org:remove')
def remove():
    """
    根据id删除
    """
    ids = request.values.get('ids', type=str)
    ids = [int(i) for i in ids.split(',')]
    Org.query.filter(Org.id.in_(ids)).update({'deleted': 1})
    return R.success()


@bp.route('/select_tree',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '选择上级')
def select_tree():
    id = request.args.get('id', 0, type=int)
    d = Org.query.get(id)
    return render_template(tpl_prefix + 'select_tree.html', d = d)

@bp.route('/tree_data',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '获取树形数据')
def tree_data():
    """
    获取tree数据json
    """
    list = Org.query.filter(Org.deleted == 0).order_by(Org.id.asc()).all()
    return jsonify(list)


@bp.route('/user_tree_data',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '获取用户树形数据')
def user_tree_data():
    """
    获取tree数据json
    """
    query = Org.query
    if current_user.username == 'admin':
        pass
    elif current_user.role and current_user.role.scope:
        scope = current_user.role.scope
        if scope is None or scope == 0:
            scope = 2
        if scope == 1: #超管权限
            pass
        if scope == 2: # 本部门及子部门权限
            query = query.filter(Org.id.in_(current_user.org._children_ids()))
        elif scope == 3: # 本部门权限
            # 判断org_id是否存在如果不存在，通过create_by 获取所有机构数据
            query = query.filter(Org.id == current_user.org_id)
        else: # scope == 4
            #个人数据 通过create_by 字段获取
            query = query.filter_by(create_by = current_user.id)
    else:
        query = query.filter_by(create_by = current_user.id)
    list = query.filter(Org.deleted == 0).order_by(Org.id.asc()).all()
    return jsonify(list)

