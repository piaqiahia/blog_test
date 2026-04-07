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
from app.model import Category
import pathlib, os

bp = Blueprint('category', __name__)
cms_bp.register_blueprint(bp, url_prefix='/category')
tpl_prefix = 'admin/cms/category/'
model_name = '栏目管理'

@bp.route('/',methods=['GET'])
@login_required
@admin_perm(model_name, '查看列表', permission='cms:category:view')
def index():
    """
    列表
    """
    return render_template( tpl_prefix + 'list.html')

@bp.route('/list',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '获取列表数据', permission='cms:category:view')
def list():
    """
    获取列表
    """
    list = query_model(Category, search_query, is_page=False, need_scope=True)
    return jsonify(list)

def search_query(query):
    query = query.filter(Category.deleted == 0)
    value = request.values.get('title','').strip()
    if value != '':
        query = query.filter(Category.title == value)
    value = request.values.get('name','').strip()
    if value != '':
        query = query.filter(Category.name == value)
    value = request.values.get('visible','').strip()
    if value != '':
        query = query.filter(Category.visible == value)
    

    query = query.order_by(Category.order_num.asc())
    value = request.values.get('ids','').strip()
    if value != '':
        ids = value.split(',')
        query = query.filter(Category.id.in_(ids))
    return query


@bp.route('/export',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '导出excel', permission='cms:category:export')
def export():
    list = query_model(Category, search_query, is_page=False, need_scope=True)
    
    title = ["备注","机构id","栏目标题","父ID","编码","描述","列表模板","单页/详情模板","模板类型 list,single_page","可以录入信息内容","seo标题","seo描述","seo关键词","排序","是否隐藏",""]
    tpl_mold_datas = get_dict_data('cms_category_tpl_mold')
    visible_datas = get_dict_data('cms_visible')
    wb = Workbook()
    sheet_names = wb.sheetnames
    ws = wb[sheet_names[0]]
    ws.append(title)
    for row in list:
        data = []
        data.append(row.remark)
        data.append(row.org_id)
        data.append(row.title)
        data.append(row.parent_id)
        data.append(row.name)
        data.append(row.desp)
        data.append(get_label_by_value(tpl_list_datas, row.tpl_list))
        data.append(get_label_by_value(tpl_page_datas, row.tpl_page))
        data.append(get_label_by_value(tpl_mold_datas, row.tpl_mold))
        data.append(row.content)
        data.append(row.seo_title)
        data.append(row.seo_description)
        data.append(row.seo_keywords)
        data.append(row.order_num)
        data.append(get_label_by_value(visible_datas, row.visible))
        data.append(row.icon)
        ws.append(data)
    
    abs_filepath, filepath = get_download_file_path("{}.xlsx".format(time_now_name()))
    wb.save(abs_filepath)
    return R.success(msg=filepath)
    

@bp.route('/add',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '添加', permission='cms:category:add')
def add():
    """
    添加
    """
    if request.method == 'POST': # 添加
        o = Category()
        request_form_auto_fill(o)
        if o.parent_id == 'None' or o.parent_id == '':
            o.parent_id = None

        c = Category.query.filter(Category.deleted == 0, Category.name == o.name).first()
        if c:
            return R.error(msg=f"栏目编码[{o.name}] 已经存在，请勿重复设置")
        db.session.add(o)
        db.session.commit()
        return R.success(msg='成功')

    parent_id = request.args.get('parent_id', 0, type = int)
    d = Category()
    if parent_id == 0 :
        d.id = None
        d.name = '无'
    else:
        d = Category.query.get(parent_id)
    tpls = get_tpl_list()
    tpl_list_select = tpls
    tpl_single_select = tpls
    return render_template( tpl_prefix + 'add.html', d = d, tpl_list_select = tpl_list_select, tpl_single_select = tpl_single_select)

def get_tpl_list():
    path = pathlib.Path().cwd() / 'app' / 'main' / 'themes' / current_app.config.get('H3BLOG_TEMPLATE', 'tend')
    tpls = [ t.name for t in path.glob('*.html') if t.is_file()] 
    return tpls

@bp.route('/edit',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '修改', permission='cms:category:edit')
def edit():
    """
    编辑修改
    """
    if request.method == 'POST': 
        id = request.form.get('id', 0, type=int)
        o = Category.query.get(id)
        request_form_auto_fill(o)

        if o.parent_id == 'None' or o.parent_id == '':
            o.parent_id = None
        db.session.commit()
        return R.success()

    id = request.args.get('id', 0, type=int)
    o = Category.query.get(id)
    tpls = get_tpl_list()
    tpl_list_select = tpls
    tpl_single_select = tpls
    return render_template(tpl_prefix + 'edit.html', d = o, tpl_list_select = tpl_list_select, tpl_single_select = tpl_single_select)

@bp.route('/remove',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '删除', permission='cms:category:remove')
def remove():
    """
    根据id删除
    """
    ids = request.values.get('ids', type=str)
    ids = [int(i) for i in ids.split(',')]
    Category.query.filter(Category.id.in_(ids)).update({'deleted': 1})
    return R.success()


@bp.route('/select_tree',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '选择上级')
def select_tree():
    id = request.args.get('id', 0, type=int)
    d = Category.query.get(id)
    return render_template(tpl_prefix + 'select_tree.html', d = d)

@bp.route('/tree_data',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '获取树形数据')
def tree_data():
    """
    获取tree数据json
    """
    list = Category.query.order_by(Category.id.asc()).all()
    return jsonify(list)


@bp.route('/select_category_tree',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '选择上级')
def select_category_tree():
    id = request.args.get('id', 0, type=int)
    d = Category.query.get(id)
    return render_template(tpl_prefix + 'select_category_tree.html', d = d)

@bp.route('/category_tree_data',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '获取树形数据')
def category_tree_data():
    """
    获取tree数据json
    """
    list = Category.query.filter(Category.deleted == 0).order_by(Category.order_num.asc(), Category.id.asc()).all()
    return jsonify(list)

