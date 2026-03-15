from typing import Any
from flask import render_template, request, redirect, url_for, flash, current_app, jsonify, \
    send_from_directory,make_response, session, Blueprint
from flask_login.utils import login_required, current_user

from app.util.common import admin_required
from app.util import R, request_form_auto_fill
from app.util.model import query_model
from app.ext import db

from app.admin.views.sys import sys_bp
from app.model import DictType
from app.util.permission import admin_perm

bp = Blueprint('dict_type', __name__)
sys_bp.register_blueprint(bp, url_prefix='/dict_type')

tpl_prefix = 'admin/sys/dict_type/'
model_name = '字典类型'

@bp.get('/')
@login_required
@admin_perm(model_name, '列表', permission='sys:dict_type:view')
def dict_types():
    """
    字典类型
    """
    return render_template(tpl_prefix + 'list.html')

@bp.route('/list',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '列表数据', permission='sys:dict_type:view')
def list():
    """
    菜单获取列表
    """
    list = query_model(DictType, search_query)
    return jsonify(list)

def search_query(query):
    value = request.form.get('name','')
    if value.strip() != '':
        query = query.filter(DictType.name.like('%%%s%%' % value))

    value = request.form.get('status', '')
    if value != '':
        query = query.filter(DictType.status == value)
    query = query.order_by(DictType.id.desc())
    return query

@bp.route('/add',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '添加', permission='sys:dict_type:add')
def add():
    """
    添加
    """
    if request.method == 'POST': # 添加
        dt = DictType()
        request_form_auto_fill(dt)
        db.session.add(dt)
        db.session.commit()
        return R.success(msg='成功')
    return render_template(tpl_prefix + 'add.html')

@bp.route('/edit',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '修改', permission='sys:dict_type:edit')
def edit():
    """
    编辑修改
    """
    if request.method == 'POST': 
        id = request.form.get('id', 0, type=int)
        dt = DictType.query.get(id)
        request_form_auto_fill(dt)
        db.session.commit()
        return R.success()

    id = request.args.get('id', 0, type=int)
    dt = DictType.query.get(id)
    return render_template(tpl_prefix + 'edit.html', d = dt)

@bp.route('/remove',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '删除', permission='sys:dict_type:remove')
def remove():
    """
    根据id删除
    """
    id = request.args.get('id',0, type= int)
    dt = DictType.query.get(id)
    db.session.delete(dt)
    db.session.commit()
    return R.success()


@bp.post('/check_dict_type_unique')
@login_required
@admin_required
def check_dict_type_unique():
    """
    查看账号是否存在
    """
    id = request.form.get('id')
    dict_type = request.form.get('dict_type', '')
    q = DictType.query.filter(DictType.dict_type == dict_type)
    if id:
        q = q.filter(DictType.id != id)
    user = q.first()
    if user :
        return '1'
    return '0'