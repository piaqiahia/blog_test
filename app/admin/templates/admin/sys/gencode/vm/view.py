from flask import render_template, request, jsonify, Blueprint,current_app, make_response
from flask_login.utils import login_required, current_user

from app.util.common import time_now_name, upload, get_download_file_path
from app.util.permission import admin_perm
from app.util import R, request_form_auto_fill
from app.util.model import query_model
from app.util.dict_data import get_dict_data, get_label_by_value
from app.ext import db

from openpyxl import Workbook
from tempfile import NamedTemporaryFile

from app.admin.views.${m.view_path} import ${m.view_path}_bp
from app.model import ${m.model}
import os

bp = Blueprint('${m.model_name}', __name__)
${m.view_path}_bp.register_blueprint(bp, url_prefix='/${m.model_name}')
tpl_prefix = 'admin/${"/".join(m.tpl_path.split("."))}/'
model_name = '${m.name}'

@bp.route('/',methods=['GET'])
@login_required
@admin_perm(model_name, '查看列表', permission='${m.view_path}:${m.model_name}:view')
def index():
    """
    列表
    """
    % if m.tpl_category == 'crud_html':
    list_page = query_model(${m.model}, search_query, is_page=True, page_name='page')
    return render_template( tpl_prefix + 'list.html', list_page = list_page)
    % else:
    return render_template( tpl_prefix + 'list.html')
    % endif

@bp.route('/list',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '获取列表数据', permission='${m.view_path}:${m.model_name}:view')
def list():
    """
    获取列表
    """
    % if m.tpl_category == 'tree':
    list = query_model(${m.model}, search_query, is_page=False, need_scope=True)
    % else:
    list = query_model(${m.model}, search_query, need_scope=True)
    % endif
    return jsonify(list)

def search_query(query):
    query = query.filter(${m.model}.deleted == 0)
    % for c in m.columns:
    % if c.is_query == 1 and c.query_type == 'BETWEEN':
    start = request.values.get('${c.col_name}_start','').strip()
    end = request.values.get('${c.col_name}_end', '').strip()
    if start != '' and end != '':
        query = query.filter(${m.model}.${c.col_name}.between(start, end))
    elif start == '' and end != '':
        query = query.filter(${m.model}.${c.col_name} < end)
    elif start != '' and end == '':
        query = query.filter(${m.model}.${c.col_name} > start)
    % elif c.is_query == 1 and c.query_type == 'EQ':
    value = request.values.get('${c.col_name}','').strip()
    if value != '':
        query = query.filter(${m.model}.${c.col_name} == value)
    % elif c.is_query == 1 and c.query_type == 'NE':
    value = request.values.get('${c.col_name}','').strip()
    if value != '':
        query = query.filter(${m.model}.${c.col_name} != value)
    % elif c.is_query == 1 and c.query_type == 'GT':
    value = request.values.get('${c.col_name}','').strip()
    if value != '':
        query = query.filter(${m.model}.${c.col_name} > value)
    % elif c.is_query == 1 and c.query_type == 'GTE':
    value = request.values.get('${c.col_name}','').strip()
    if value != '':
        query = query.filter(${m.model}.${c.col_name} >= value)
    % elif c.is_query == 1 and c.query_type == 'LT':
    value = request.values.get('${c.col_name}','').strip()
    if value != '':
        query = query.filter(${m.model}.${c.col_name} < value)
    % elif c.is_query == 1 and c.query_type == 'LTE':
    value = request.values.get('${c.col_name}','').strip()
    if value != '':
        query = query.filter(${m.model}.${c.col_name} <= value)
    % elif c.is_query == 1 and c.query_type == 'LIKE':
    value = request.values.get('${c.col_name}','').strip()
    if value != '':
        query = query.filter(${m.model}.${c.col_name}.like('%%%s%%' % value))
    % endif
    % endfor
    

    % if m.tpl_category == 'tree':
    query = query.order_by(${m.model}.${m.tree_order}.asc())
    % else:
    query = query.order_by(${m.model}.id.desc())
    % endif
    value = request.values.get('ids','').strip()
    if value != '':
        ids = value.split(',')
        query = query.filter(${m.model}.id.in_(ids))
    return query


@bp.route('/export',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '导出excel', permission='${m.view_path}:${m.model_name}:export')
def export():
    list = query_model(${m.model}, search_query, is_page=False, need_scope=True)
    <%  
        _title = []
        for c in m.columns:
            _title.append(c.col_comment)
    %>
    title = [${ ','.join('"{0}"'.format(x) for x in _title)}]
    % for col in m.get_dict_columns():
    ${col.col_name}_datas = get_dict_data('${col.dict_type}')
    % endfor
    wb = Workbook()
    sheet_names = wb.sheetnames
    ws = wb[sheet_names[0]]
    ws.append(title)
    for row in list:
        data = []
        % for c in m.columns:
        % if c.html_type == 'select' or c.html_type == 'radio':
        data.append(get_label_by_value(${c.col_name}_datas, row.${c.col_name}))
        % else:
        data.append(row.${c.col_name})
        % endif
        % endfor
        ws.append(data)
    
    % if m.tpl_category == 'crud_html':
    with NamedTemporaryFile(delete=False) as tmp:
        wb.save(tmp.name)
        tmp.seek(0)
        content = tmp.read()
    resp = make_response(content)
    resp.headers["Content-Disposition"] = 'attachment; filename=download.xlsx'
    resp.headers['Content-Type'] = 'application/x-xlsx'
    return resp
    % else:
    abs_filepath, filepath = get_download_file_path("{}.xlsx".format(time_now_name()))
    wb.save(abs_filepath)
    return R.success(msg=filepath)
    % endif
    

@bp.route('/add',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '添加', permission='${m.view_path}:${m.model_name}:add')
def add():
    """
    添加
    """
    if request.method == 'POST': # 添加
        o = ${m.model}()
        request_form_auto_fill(o)
        % for c in m.columns:
        % if 'upload' in c.html_type:
        ${c.col_name} = request.files.get('${c.col_name}')
        if ${c.col_name}:
            img_url = upload('${c.col_name}', 'img')
            o.${c.col_name} = img_url
        % endif
        % endfor
        % if m.tpl_category == 'tree':
        if o.${m.tree_parent_code} == 'None' or o.${m.tree_parent_code} == '':
            o.${m.tree_parent_code} = None
        % endif

        db.session.add(o)
        db.session.commit()
        return R.success(msg='成功')

    % if m.tpl_category == 'tree':
    parent_id = request.args.get('parent_id', 0, type = int)
    d = ${m.model}()
    if parent_id == 0 :
        d.id = None
        d.name = '无'
    else:
        d = ${m.model}.query.get(parent_id)
    return render_template( tpl_prefix + 'add.html', d = d)
    % else:
    return render_template( tpl_prefix + 'add.html')
    % endif

@bp.route('/edit',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '修改', permission='${m.view_path}:${m.model_name}:edit')
def edit():
    """
    编辑修改
    """
    if request.method == 'POST': 
        id = request.form.get('id', 0, type=int)
        o = ${m.model}.query.get(id)
        request_form_auto_fill(o)
        % for c in m.columns:
        % if 'upload' in c.html_type:
        ${c.col_name} = request.files.get('${c.col_name}')
        if ${c.col_name}:
            img_url = upload('${c.col_name}', 'img')
            o.${c.col_name} = img_url
        % endif
        % endfor

        % if m.tpl_category == 'tree':
        if o.${m.tree_parent_code} == 'None' or o.${m.tree_parent_code} == '':
            o.${m.tree_parent_code} = None
        % endif
        db.session.commit()
        return R.success()

    id = request.args.get('id', 0, type=int)
    o = ${m.model}.query.get(id)
    return render_template(tpl_prefix + 'edit.html', d = o)

@bp.route('/remove',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '删除', permission='${m.view_path}:${m.model_name}:remove')
def remove():
    """
    根据id删除
    """
    ids = request.values.get('ids', type=str)
    ids = [int(i) for i in ids.split(',')]
    ${m.model}.query.filter(${m.model}.id.in_(ids)).update({'deleted': 1})
    return R.success()


% if m.tpl_category == 'tree':
@bp.route('/select_tree',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '选择上级')
def select_tree():
    id = request.args.get('id', 0, type=int)
    d = ${m.model}.query.get(id)
    return render_template(tpl_prefix + 'select_tree.html', d = d)

@bp.route('/tree_data',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '获取树形数据')
def tree_data():
    """
    获取tree数据json
    """
    list = ${m.model}.query.order_by(${m.model}.id.asc()).all()
    return jsonify(list)

% endif