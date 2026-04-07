from flask import render_template, request, jsonify, Blueprint,current_app, make_response
from flask_login.utils import login_required, current_user
from app.util import model

from app.util.common import admin_required, time_now_name, upload, get_download_file_path
from app.util import R, request_form_auto_fill
from app.util.model import query_model
from app.util.dict_data import get_dict_data, get_label_by_value
from app.ext import db

from openpyxl import Workbook

from app.admin.views.sys import sys_bp
from app.model import OptLog
import os

bp = Blueprint('optlog', __name__)
sys_bp.register_blueprint(bp, url_prefix='/optlog')
tpl_prefix = 'admin/sys/optlog/'

@bp.route('/',methods=['GET'])
@login_required
@admin_required
def index():
    """
    列表
    """
    return render_template( tpl_prefix + 'list.html')

@bp.route('/list',methods=['GET','POST'])
@login_required
@admin_required
def list():
    """
    获取列表
    """
    list = query_model(OptLog, search_query)
    return jsonify(list)

def search_query(query):
    value = request.values.get('oper_name','')
    if value.strip() != '':
        query = query.filter(OptLog.oper_name.like('%%%s%%' % value))

    query = query.order_by(OptLog.id.desc())
    return query


@bp.route('/export',methods=['GET','POST'])
@login_required
@admin_required
def export():
    query  = search_query(OptLog.query)
    list = query.all()
    
    title = ["模块标题","方法名称","请求URL","请求方式","请求参数","返回参数","操作人员","主机地址","操作地点","浏览器类型","操作系统","操作状态","提示消息","访问时间"]
    state_datas = get_dict_data('sys_optlog_state')
    wb = Workbook()
    sheet_names = wb.sheetnames
    ws = wb[sheet_names[0]]
    ws.append(title)
    for row in list:
        data = []
        data.append(row.title)
        data.append(row.method)
        data.append(row.oper_url)
        data.append(row.request_method)
        data.append(row.oper_param)
        data.append(row.json_result)
        data.append(row.oper_name)
        data.append(row.ipaddr)
        data.append(row.login_location)
        data.append(row.browser)
        data.append(row.ossystem)
        data.append(get_label_by_value(state_datas, row.state))
        data.append(row.msg)
        data.append(row.oper_time)
        ws.append(data)
    
    abs_filepath, filepath = get_download_file_path("{}.xlsx".format(time_now_name()))
    wb.save(abs_filepath)
    return R.success(msg=filepath)
    

@bp.route('/add',methods=['GET','POST'])
@login_required
@admin_required
def add():
    """
    添加
    """
    if request.method == 'POST': # 添加
        o = OptLog()
        request_form_auto_fill(o)

        db.session.add(o)
        db.session.commit()
        return R.success(msg='成功')

    return render_template( tpl_prefix + 'add.html')

@bp.route('/edit',methods=['GET','POST'])
@login_required
@admin_required
def edit():
    """
    编辑修改
    """
    if request.method == 'POST': 
        id = request.form.get('id', 0, type=int)
        o = OptLog.query.get(id)
        request_form_auto_fill(o)

        db.session.commit()
        return R.success()

    id = request.args.get('id', 0, type=int)
    o = OptLog.query.get(id)
    return render_template(tpl_prefix + 'edit.html', d = o)

@bp.route('/remove',methods=['GET','POST'])
@login_required
@admin_required
def remove():
    """
    根据id删除
    """
    ids = request.values.get('ids', type=str)
    ids = [int(i) for i in ids.split(',')]
    OptLog.query.filter(OptLog.id.in_(ids)).delete(synchronize_session=False)
    return R.success()

@bp.route('/clean',methods=['GET','POST'])
@login_required
@admin_required
def clean():
    """
    清空操作日志
    """
    OptLog.query.filter(1==1).delete(synchronize_session=False)
    return R.success()


@bp.route('/detail',methods=['GET','POST'])
@login_required
@admin_required
def detail():
    """
    详情
    """
    id = request.args.get('id', 0, type=int)
    o = OptLog.query.get(id)
    return render_template(tpl_prefix + 'detail.html', d = o)


