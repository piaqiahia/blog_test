from typing import Any
from flask import render_template, request, redirect, url_for, flash, current_app, jsonify, \
    send_from_directory,make_response, session, Blueprint
from flask_login.utils import login_required, current_user

from app.util.common import admin_required
from app.util import R, request_form_auto_fill
from app.util.model import query_model
from app.ext import db

from app.admin.views.sys import sys_bp
from app.model import DictType,DictData
from app.util.permission import admin_perm

bp = Blueprint('dict_data', __name__)
sys_bp.register_blueprint(bp, url_prefix='/dict_data')

tpl_prefix = 'admin/sys/dict_data/'
model_name = '字典数据'


@bp.get('/')
@login_required
@admin_perm(model_name, '列表')
def dict_datas():
    """
    字典数据
    """
    dict_type_id = request.args.get('id',0, type=int)
    dict_types = DictType.query.filter(DictType.status==0).order_by(DictType.id.asc()).all()
    return render_template(tpl_prefix + 'list.html', dict_types = dict_types,dict_type_id = dict_type_id)

@bp.route('/list',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '列表数据')
def list():
    """
    菜单获取列表
    """
    list = query_model(DictData, search_query)
    return jsonify(list)

def search_query(query):
    value = request.form.get('name','')
    if value.strip() != '':
        query = query.filter(DictData.name.like('%%%s%%' % value))
    
    value = request.form.get('dict_type', '')
    if value.strip() !='':
        query = query.filter(DictData.dict_type==value)

    value = request.form.get('status', '')
    if value != '':
        query = query.filter(DictData.status == value)
    query = query.order_by(DictData.id.desc())
    return query

@bp.route('/add',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '添加')
def add():
    """
    添加
    """
    if request.method == 'POST': # 添加
        dt = DictData()
        request_form_auto_fill(dt)
        db.session.add(dt)
        db.session.commit()
        return R.success(msg='成功')
    return render_template(tpl_prefix + 'add.html', dict_type=request.args.get('dict_type',''))

@bp.route('/edit',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '修改')
def edit():
    """
    编辑修改
    """
    if request.method == 'POST': 
        id = request.form.get('id', 0, type=int)
        dt = DictData.query.get(id)
        request_form_auto_fill(dt)
        db.session.commit()
        return R.success()

    id = request.args.get('id', 0, type=int)
    dt = DictData.query.get(id)
    return render_template(tpl_prefix + 'edit.html', d = dt)

@bp.route('/remove',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '删除')
def remove():
    """
    根据id删除
    """
    id = request.args.get('id',0, type= int)
    dt = DictData.query.get(id)
    db.session.delete(dt)
    db.session.commit()
    return R.success()