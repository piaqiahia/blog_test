from flask import render_template, request, redirect, url_for, flash, current_app, jsonify, \
    send_from_directory,make_response, session, Blueprint
from flask_login.utils import login_required, current_user

from app.util.common import admin_required
from app.util import R, request_form_auto_fill
from app.ext import db

from app.admin.views.sys import sys_bp
from app.model import Menu, Role
from app.util.permission import admin_perm


bp = Blueprint('menu', __name__)
sys_bp.register_blueprint(bp, url_prefix='/menu')
tpl_prefix = 'admin/sys/menu/'
model_name = '菜单管理'

@bp.route('/',methods=['GET'])
@login_required
@admin_perm(model_name, '列表', permission='sys:menu:view')
def menus():
    """
    菜单获取
    """
    return render_template(tpl_prefix +  'list.html')

@bp.route('/list',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '列表数据', permission='sys:menu:view')
def list():
    """
    菜单获取列表
    """
    query = search_query(Menu.query)
    list = query.all()
    return jsonify(list)

def search_query(query):
    value = request.form.get('name','')
    if value.strip() != '':
        query = query.filter(Menu.name.like('%%%s%%' % value))

    value = request.form.get('visible', '')
    if value != '':
        query = query.filter(Menu.visible == value)
        
    query = query.order_by(Menu.order_num.asc())
    return query

@bp.route('/add',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '添加', permission='sys:menu:add')
def add():
    """
    菜单添加
    """
    if request.method == 'POST': # 添加
        menu = Menu()
        request_form_auto_fill(menu)
        if menu.parent_id == 'None' :
            menu.parent_id = None
        db.session.add(menu)
        db.session.commit()
        return R.success(msg='成功')

    parent_id = request.args.get('parent_id', 0, type = int)
    menu = Menu()
    if parent_id == 0 :
        menu.id = None
        menu.name = '主目录'
    else:
        menu = Menu.query.get(parent_id)
    return render_template(tpl_prefix + 'add.html', menu = menu)

@bp.route('/edit',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '修改', permission='sys:menu:edit')
def edit():
    """
    编辑修改
    """
    if request.method == 'POST': 
        id = request.form.get('id', 0, type=int)
        menu = Menu.query.get(id)
        request_form_auto_fill(menu)
        if menu.parent_id == 'None':
            menu.parent_id = None
        db.session.commit()
        return R.success()

    id = request.args.get('id', 0, type = int)
    menu = Menu.query.get(id)
    return render_template(tpl_prefix + 'edit.html', d = menu)

@bp.route('/select_menu_tree',methods=['GET','POST'])
@login_required
@admin_required
def select_menu_tree():
    id = request.args.get('id', 0, type=int)
    menu = Menu.query.get(id)
    return render_template(tpl_prefix + 'select_menu_tree.html', d = menu)

@bp.route('/tree_data',methods=['GET','POST'])
@login_required
@admin_required
def tree_data():
    """
    获取菜单数据json
    """
    list = Menu.query.order_by(Menu.id.asc(), Menu.order_num.asc()).all()
    return jsonify(list)

@bp.route('/remove',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '删除', permission='sys:menu:remove')
def remove():
    """
    根据id删除
    """
    id = request.args.get('id',0, type= int)
    menu = Menu.query.get(id)
    db.session.delete(menu)
    db.session.commit()
    return R.success()


@bp.route('/role_tree_data',methods=['GET'])
@login_required
@admin_required
def role_tree_data():
    """
    根据role id 获取菜单格式内容
    """
    id = request.args.get('id', 0, type= int)
    if current_user.username == 'admin':
        list = Menu.query.all()
    else:
        list = current_user.role.menus.all()
    datas = []
    select_menus = []
    if id != 0:
        role = Role.query.get(id)
        select_menus = role.menus.all()

    def is_exist(menu, list):
        for o in list:
            if menu.id == o.id:
                return True
        return False   
    for m in list:
        d = {
            'id': m.id,
            'name': m.name,
            'pId' : m.parent_id,
            'title': m.name,
            'checked': is_exist(m, select_menus)
        }
        datas.append(d)

    return jsonify(datas)