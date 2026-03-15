from typing import Any
from flask import render_template, request, redirect, url_for, flash, current_app, jsonify, \
    send_from_directory,make_response, session, Blueprint
from flask_login.utils import login_required, current_user

from app.util.common import admin_required
from app.util import R, request_form_auto_fill
from app.util.model import query_model
from app.ext import db

from app.admin import admin
from app.model import Menu, Role, User, Article, Category, FriendlyLink, Tag
from app.util import Row
from app.ext import cache
import json
from sqlalchemy import func

def reMenus(db_menus, parent_id):
    list = []
    for m in db_menus:
        if m.parent_id == parent_id and m.menu_type != 'F' and m.visible == 0:
            menu = Row()
            menu.id = m.id
            menu.parent_id = None
            menu.perms = m.perms
            menu.target = m.target
            menu.menu_type = m.menu_type
            menu.url = m.url
            menu.visible = m.visible
            menu.icon = m.icon
            menu.is_refresh = m.is_refresh
            menu.order_num = m.order_num
            menu.name = m.name
            menu.children = reMenus(db_menus, menu.id)
            list.append(menu)
    return list

def get_menus(user):
    """获取菜单"""
    cache_key = f"MENUS_USER_{user.id}"
    menus = cache.get(cache_key)
    if menus:
        return json.loads(menus)
    else:
        cache.delete(cache_key)
        if user.username == 'admin':
            list = Menu.query.order_by(Menu.order_num.asc()).all()
            menus = reMenus(list, None)
        elif user.role is not None:
            list = user.role.menus.order_by(Menu.order_num.asc()).all()
            menus = reMenus(list, None)
        else:
            menus = [{}]
        if current_app.config.get('SYS_DEBUG_STATE','true').lower() != 'true':
            cache.set(cache_key, json.dumps(menus))
    return menus

@admin.route('/', methods=['GET', 'POST'])
@login_required
@admin_required
def index():
    current_user.ping()
    user = current_user
    user.ping()
    menus = get_menus(user)
    main_url = url_for('admin.dashboard')
    menu_style = request.cookies.get('nav-style', current_app.config.get('SYS_NAV_STYLE','default'))
    web_page = 'admin/index-topnav.html' if menu_style == 'topnav' else 'admin/index.html' 
    return render_template(web_page, menus = menus, main_url = main_url)

@admin.get('/switch_skin')
@login_required
@admin_required
def switch_skin():
    return render_template('admin/switch_skin.html')


@admin.get('/menu_style/<style>')
@login_required
@admin_required
def menu_style(style):
    response = make_response("success")
    response.set_cookie('nav-style', style)
    return response

@admin.get('/lockscreen')
@admin_required
def lockscreen():
    """锁屏"""
    return render_template('admin/lock.html')

@admin.post('/unlockscreen')
def unlockscreen():
    """解锁屏幕"""
    password = request.form.get('password','').strip()
    if current_user is None or not current_user.is_authenticated:
        return R.error(msg = '服务器超时，请重新登录')
    if current_user.verify_password(password):
        return R.success()

    return R.error(msg='密码不正确请重新输入')

@admin.get('/dashboard')
@login_required
@admin_required
def dashboard():
    """管理后台首页面板"""
    # 基础统计数据
    user_count = User.query.count()
    role_count = Role.query.count()
    menu_count = Menu.query.count()
    
    # CMS统计数据
    article_count = Article.query.count()
    category_count = Category.query.count()
    link_count = FriendlyLink.query.count()
    tag_count = Tag.query.count()
    vip_count = User.query.filter(User.user_type=='vip').count()
    
    # 获取最近文章统计
    recent_articles = Article.query.order_by(Article.ctime.desc()).limit(5).all()
    
    # 获取文章分类统计
    category_stats = db.session.query(
        Category.name,
        func.count(Article.id).label('count')
    ).outerjoin(Article, Category.id == Article.category_id).group_by(Category.id, Category.name).all()
    
    # 获取标签云数据
    tag_stats = db.session.query(
        Tag.name,
        func.count(Article.id).label('count')
    ).join(Article.tags).group_by(Tag.id, Tag.name).all()
    
    # 获取系统信息
    import platform
    import sys
    system_info = {
        'os_name': platform.system(),
        'os_version': platform.version(),
        'python_version': sys.version.split()[0],
        'hostname': platform.node()
    }
    
    return render_template('admin/dashbord.html',
                         stats={
                             'user_count': user_count,
                             'role_count': role_count,
                             'menu_count': menu_count,
                             'article_count': article_count,
                             'category_count': category_count,
                             'link_count': link_count,
                             'tag_count': tag_count,
                             'vip_count': vip_count
                         },
                         recent_articles=recent_articles,
                         category_stats=category_stats,
                         tag_stats=tag_stats,
                         system_info=system_info)