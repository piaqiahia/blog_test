from typing import Any
from flask import render_template, request, redirect, url_for, flash, current_app, jsonify, \
    send_from_directory,make_response, session, Blueprint
from flask_login import current_user
from flask_login.utils import login_required

from app.util.common import admin_required
from app.util import R, request_form_auto_fill
from app.util.model import query_model
from app.ext import db

from app.admin.views.sys import sys_bp
from app.model import Menu, Role, User
from app.util.permission import admin_perm
from app.util.perms_cache import delete_perms_cache

bp = Blueprint('role', __name__)
sys_bp.register_blueprint(bp, url_prefix='/role')
tpl_prefix = 'admin/sys/role/'
model_name = '角色管理'

@bp.route('/',methods=['GET'])
@login_required
@admin_perm(model_name, '列表', permission='sys:role:view')
def roles():
    """
    角色
    """
    return render_template( tpl_prefix + 'list.html')

@bp.route('/list',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '列表数据', permission='sys:role:view')
def list():
    """
    菜单获取列表
    """
    list = query_model(Role, search_query,need_scope=True)
    return jsonify(list)

def search_query(query):
    query = query.filter(Role.deleted == 0)
    if current_user.username == 'admin':
        query = query.filter_by(create_by = current_user.id)
    value = request.form.get('name','')
    if value.strip() != '':
        query = query.filter(Role.name.like('%%%s%%' % value))

    value = request.form.get('status', '')
    if value != '':
        query = query.filter(Role.status == value)
    query = query.order_by(Role.sort.asc())
    return query

@bp.route('/add',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '添加', permission='sys:role:add')
def add():
    """
    菜单角色
    """
    if request.method == 'POST': # 添加
        role = Role()
        request_form_auto_fill(role)
        menuIds = request.form.get('menuIds', '')
        for m_id in menuIds.split(','):
            if m_id == '':
                continue
            menu = Menu.query.get(m_id)
            role.menus.append(menu)
        role.org_id = current_user.org_id
        db.session.add(role)
        db.session.commit()
        return R.success(msg='成功')

    return render_template( tpl_prefix + 'add.html')

@bp.route('/edit',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '修改', permission='sys:role:edit')
def edit():
    """
    编辑修改
    """
    if request.method == 'POST': 
        id = int(request.form.get('id', 0))
        role = Role.query.get(id)
        request_form_auto_fill(role)
        menuIds = request.form.get('menuIds', '')
        role.menus = [] #清空menus关联表数据
        for m_id in menuIds.split(','):
            if m_id == '':
                continue
            menu = Menu.query.get(m_id)
            role.menus.append(menu)
        db.session.commit()
        #清理相关用户权限缓存
        users = User.query.filter(User.role == role).all()
        for user in users:
            delete_perms_cache(user)
        return R.success()

    id = int(request.args.get('id', 0))
    role = Role.query.get(id)
    return render_template(tpl_prefix + 'edit.html', d = role)

@bp.route('/remove',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '删除', permission='sys:role:remove')
def remove():
    """
    根据id删除
    """
    id = request.args.get('id',0, type= int)
    Role.query.filter(Role.id == id).update({'deleted': 1})
    db.session.commit()
    return R.success()