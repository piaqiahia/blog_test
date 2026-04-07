from flask import render_template, request, jsonify, Blueprint,current_app, make_response
from flask_login.utils import login_required, current_user

from app.util.common import admin_required
from app.util.common import time_now_name, upload, get_download_file_path
from app.util import R, request_form_auto_fill
from app.util.model import query_model
from app.util.dict_data import get_dict_data, get_label_by_value
from app.ext import db

from openpyxl import Workbook

from app.admin.views.sys import sys_bp
from app.model import Setting
from app.util.permission import admin_perm

bp = Blueprint('setting', __name__)
sys_bp.register_blueprint(bp, url_prefix='/setting')
tpl_prefix = 'admin/sys/setting/'
model_name = '系统参数'

@bp.route('/',methods=['GET'])
@login_required
@admin_perm(model_name, '列表', permission='sys:setting:view')
def index():
    """
    列表
    """
    return render_template( tpl_prefix + 'list.html')

@bp.route('/list',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '列表数据', permission='sys:setting:view')
def list():
    """
    获取列表
    """
    list = query_model(Setting, search_query)
    return jsonify(list)

def search_query(query):
    value = request.values.get('name','')
    if value.strip() != '':
        query = query.filter(Setting.sname.like('%%%s%%' % value))

    query = query.order_by(Setting.id.desc())
    return query


@bp.route('/export',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '添加', permission='sys:setting:export')
def export():
    query  = search_query(Setting.query)
    list = query.all()
    
    title = ["参数名称","参数键名","参数键值"]
    stype_datas = get_dict_data('sys_setting_stype')
    wb = Workbook()
    sheet_names = wb.sheetnames
    ws = wb[sheet_names[0]]
    ws.append(title)
    for row in list:
        data = []
        data.append(row.sname)
        data.append(row.skey)
        data.append(row.svalue)
        ws.append(data)
    
    abs_filepath, filepath = get_download_file_path("{}.xlsx".format(time_now_name()))
    wb.save(abs_filepath)
    return R.success(msg=filepath)
    

@bp.route('/add',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '添加', permission='sys:setting:add')
def add():
    """
    添加
    """
    if request.method == 'POST': # 添加
        o = Setting()
        request_form_auto_fill(o)

        if o.col_type == 'file':
            svalue = request.files.get('svalue')
            if svalue:
                file_path = upload('svalue', 'img')
                o.svalue = file_path

        db.session.add(o)
        db.session.commit()

        current_app.config[o.skey.upper()] = o.svalue

        return R.success(msg='成功')

    return render_template( tpl_prefix + 'add.html')

@bp.route('/edit',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '修改', permission='sys:setting:edit')
def edit():
    """
    编辑修改
    """
    if request.method == 'POST': 
        id = request.form.get('id', 0, type=int)
        o = Setting.query.get(id)
        request_form_auto_fill(o)

        if o.col_type == 'file':
            svalue = request.files.get('svalue')
            if svalue:
                file_path = upload('svalue', 'img')
                o.svalue = file_path

        db.session.commit()

        current_app.config[o.skey.upper()] = o.svalue
        return R.success()

    id = request.args.get('id', 0, type=int)
    o = Setting.query.get(id)
    return render_template(tpl_prefix + 'edit.html', d = o)

@bp.route('/remove',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '删除', permission='sys:setting:remove')
def remove():
    """
    根据id删除
    """
    ids = request.values.get('ids', type=str)
    ids = [int(i) for i in ids.split(',')]
    Setting.query.filter(Setting.id.in_(ids)).delete(synchronize_session=False)
    return R.success()


