from datetime import datetime
import os
from typing import Any
from flask import render_template, request, redirect, url_for, flash, current_app, jsonify, \
    send_from_directory,make_response, session, Blueprint
from flask_login.utils import login_required, current_user
from werkzeug.utils import secure_filename

from app.util.common import admin_required, allowed_file, upload
from app.util.permission import admin_perm
from app.util import R, request_form_auto_fill
from app.util.model import query_model
from app.ext import db

from app.admin.views.sys import sys_bp
from app.model import Role, User,Org

bp = Blueprint('user', __name__)
sys_bp.register_blueprint(bp, url_prefix='/user')
tpl_prefix = 'admin/sys/user/'
model_name = '用户管理'

@bp.get('/')
@login_required
@admin_perm(model_name, '列表', permission='sys:user:view')
def users():
    """
    用户
    """
    return render_template(tpl_prefix + 'list.html')

@bp.get('/select_list')
@login_required
@admin_perm(model_name, '打开选中用户')
def select_list():
    """
    打开选中用户
    """
    return render_template(tpl_prefix + 'select_list.html')

@bp.route('/list',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '列表数据', permission='sys:user:view')
def list():
    """
    获取列表
    """
    list = query_model(User, search_query, need_scope=True)
    return jsonify(list)

def search_query(query):
    query = query.filter(User.deleted == 0)
    value = request.form.get('name','')
    if value.strip() != '':
        query = query.filter(User.name.like('%%%s%%' % value))
    value = request.form.get('user_type','')
    if value.strip() != '':
        query = query.filter(User.user_type == value)
    value = request.form.get('username','')
    if value.strip() != '':
        query = query.filter(User.username.like('%%%s%%' % value))

    value = request.form.get('mobile', '')
    if value.strip() != '':
        query = query.filter(User.mobile.like('%%%s%' % value))
    value = request.form.get('status', '')
    if value != '':
        query = query.filter(User.status == value)
    value = request.form.get('org_id', '')
    if value != '':
        query = query.filter(User.org_id == value)
        # org = Org.query.get(value)
        # query = query.filter(User.org_id.in_(org._children_ids()))
    stime = request.form.get('stime','')
    etime = request.form.get('etime','')
    if stime.strip() != '':
        query = query.filter(User.ctime >= stime)
    if etime.strip() != '':
        query = query.filter(User.ctime <= etime)
    query = query.order_by(User.id.desc())
    return query

@bp.route('/add',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '添加', permission='sys:user:add')
def add():
    """
    菜单添加
    """
    if request.method == 'POST': # 添加
        user = User()
        request_form_auto_fill(user)
        user.password = request.form.get('password', '123456')
        user.org_id = current_user.org_id
        db.session.add(user)
        db.session.commit()
        return R.success(msg='成功')
    roles = []
    if current_user.username == 'admin':
        roles = query_model(Role, lambda query: query.filter(Role.status == 0).order_by(Role.sort.asc()), is_page=False)
    else:
        roles = query_model(Role, lambda query: query.filter(Role.status == 0) \
            .filter((Role.id == current_user.role.id) | (Role.org_id == current_user.org.id)) \
            .order_by(Role.sort.asc()), is_page=False)
    return render_template(tpl_prefix + 'add.html', roles = roles)

@bp.route('/edit',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '修改', permission='sys:user:edit')
def edit():
    """
    编辑修改
    """
    if request.method == 'POST': 
        id = request.form.get('id', 0, type=int)
        user = User.query.get(id)
        request_form_auto_fill(user)
        db.session.commit()
        return R.success()

    id = request.args.get('id', 0, type=int)
    user = User.query.get(id)
    roles = []
    if current_user.username == 'admin':
        roles = query_model(Role, lambda query: query.filter(Role.status == 0).order_by(Role.sort.asc()), is_page=False)
    else:
        roles = query_model(Role, lambda query: query.filter(Role.status == 0) \
            .filter((Role.id == current_user.role.id) | (Role.org_id == current_user.org.id)) \
            .order_by(Role.sort.asc()), is_page=False)
    return render_template(tpl_prefix + 'edit.html', d = user, roles = roles)

@bp.route('/remove',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '删除', permission='sys:user:remove')
def remove():
    """
    根据id删除
    """
    id = request.args.get('id',0, type= int)
    user = User.query.get(id)
    if user.username == 'admin':
        return R.error(msg='禁止删除admin账号')
    # db.session.delete(user)
    User.query.filter(User.id == id).update({'deleted': 1})
    db.session.commit()
    return R.success()


@bp.post('/change_status')
@login_required
@admin_perm(model_name, '修改用户状态')
def change_status():
    """
    修改用户状态
    """
    user_id = request.form.get('id', 0, type=int)
    status = request.form.get('status', '', type=int)
    user = User.query.filter(User.id == user_id).first()
    if user:
        user.status = status
        db.session.commit()
        return R.success(msg='设置成功')
    return R.error(msg='设置失败')

@bp.post('/check_username_unique')
@login_required
@admin_required
def check_username_unique():
    """
    查看账号是否存在
    """
    user_id = request.form.get('user_id')
    username = request.form.get('username', '')
    q = User.query.filter(User.username == username)
    if user_id:
        q = q.filter(User.id != user_id)
    user = q.first()
    if user :
        return '1'
    return '0'

@bp.post('/check_mobile_unique')
@login_required
@admin_required
def check_mobile_unique():
    """
    查看手机号是否存在
    """
    user_id = request.form.get('user_id')
    mobile = request.form.get('mobile', '')
    q = User.query.filter(User.mobile == mobile)
    if user_id:
        q = q.filter(User.id != user_id)
    user = q.first()
    if user :
        return '1'
    return '0'

@bp.route('/reset_pwd',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '重置密码', permission='sys:user:reset_pwd')
def reset_pwd():
    """
    重置密码
    """
    if request.method == 'POST': # 添加
        username = request.form.get('username', '')
        password = request.form.get('password','').strip()
        user = User.query.filter(User.username == username).one()
        if not user:
            return R.success(msg = '查无此用户!')
        user.password = password
        db.session.commit()
        return R.success(msg='成功')
    id = request.args.get('id',type = int)
    user = User.query.get(id)
    return render_template(tpl_prefix + 'reset_pwd.html', user = user)


@bp.route('/profile',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '查看个人资料')
def profile():
    """
    个人资料
    """
    return render_template(tpl_prefix + 'profile.html', user = current_user)

@bp.route('/profile/check_pwd',methods=['GET','POST'])
@login_required
@admin_required
def check_pwd():
    """
    查看当前用户密码是否正确
    """
    password = request.args.get('password','')
    user = current_user
    if user.verify_password(password):
        return 'true'
    return 'false'

@bp.route('/profile/reset_pwd',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '重置密码')
def profile_reset_pwd():
    """
    修改当前用户密码
    """
    if request.method == 'POST':
        password = request.form.get('newPassword','123456')
        current_user.password = password
        db.session.commit()
        return R.success(msg='修改密码成功')
    return render_template(tpl_prefix + 'profile_reset_pwd.html')


@bp.get('/profile/avatar')
@login_required
@admin_required
def profile_avatar():
    return render_template(tpl_prefix + 'profile_avatar.html')

@bp.post('/profile/update_avatar')
@login_required
@admin_perm(model_name, '修改头像')
def profile_update_avatar():
    """更新用户头像"""
    file=request.files.get('avatarfile')
    if not allowed_file(file.filename):
        return R.error(msg='不支持的图片格式')
    else:
        url_path = ''
        upload_type = current_app.config.get('H3BLOG_UPLOAD_TYPE')
        ex=os.path.splitext(file.filename)[1]
        filename=datetime.now().strftime('%Y%m%d%H%M%S')+ex
        # filename= secure_filename(file.filename)
        if upload_type is None or upload_type == '' or upload_type == 'local':
            file.save(os.path.join(current_app.config['H3BLOG_UPLOAD_PATH'],filename))
            url_path = url_for('admin.uploaded_file',filename=filename)
        #返回
        user = current_user
        user.avatar = url_path
        db.session.add(user)
    return R.success(msg='上传成功')

@bp.get('/profile/regions')
@login_required
@admin_required
def profile_regions():
    """获取当前用户机构授权区域"""
    if current_user.org is None:
        return jsonify([])
    regions = []
    for region in current_user.org.regions.all():
        d = {
            'id': region.id,
            'name': region.name,
            'pId' : region.parent_id,
            'title': region.name
        }
        regions.append(d)
    return jsonify(regions)


@bp.get('/profile/coursetypes')
@login_required
@admin_required
def profile_coursetypes():
    """获取当前用户机构授权课程类型"""
    if current_user.org is None:
        return jsonify([])
    coursetypes = []
    for c in current_user.org.coursetypes.all():
        d = {
            'id': c.id,
            'name': c.name,
            'pId' : c.parent_id,
            'title': c.name
        }
        coursetypes.append(d)
    return jsonify(coursetypes)



@bp.route('/profile/sys_set',methods=['GET','POST'])
@login_required
def profile_sys_set():
    """
    修改系统设置
    """
    if request.method == 'POST':
        org = current_user.org
        logo_file = request.files.get('logo_file')
        if logo_file:
            img_url = upload('logo_file', 'logo')
            org.logo = img_url
        request_form_auto_fill(org)
        db.session.commit()
        current_user.org = org
        return R.success(msg='保存成功')
    return render_template(tpl_prefix + 'profile_reset_pwd.html')