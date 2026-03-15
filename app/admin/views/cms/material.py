import io
from flask import render_template, request, jsonify, Blueprint,current_app, make_response, send_file
from flask_login.utils import login_required, current_user

from app import util
from app.util.common import time_now_name, upload, get_download_file_path
from app.util.permission import admin_perm
from app.util import R, request_form_auto_fill
from app.util.model import query_model
from app.util.dict_data import get_dict_data, get_label_by_value
from app.ext import db

from openpyxl import Workbook

from app.admin.views.cms import cms_bp
from app.admin import admin as admin_bp
from app.model import Material
import os

bp = Blueprint('material', __name__)
cms_bp.register_blueprint(bp, url_prefix='/material')
tpl_prefix = 'admin/cms/material/'
model_name = '素材管理'

@bp.route('/',methods=['GET'])
@login_required
@admin_perm(model_name, '查看列表', permission='cms:material:view')
def index():
    """
    列表
    """
    return render_template( tpl_prefix + 'list.html')

@bp.route('/list',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '获取列表数据', permission='cms:material:view')
def list():
    """
    获取列表
    """
    list = query_model(Material, search_query, need_scope=True)
    return jsonify(list)

def search_query(query):
    query = query.filter(Material.deleted == 0)
    value = request.values.get('name','').strip()
    if value != '':
        query = query.filter(Material.name.like('%%%s%%' % value))
    value = request.values.get('mtype','').strip()
    if value != '':
        query = query.filter(Material.mtype == value)
    value = request.values.get('url','').strip()
    if value != '':
        query = query.filter(Material.url == value)
    

    query = query.order_by(Material.id.desc())
    value = request.values.get('ids','').strip()
    if value != '':
        ids = value.split(',')
        query = query.filter(Material.id.in_(ids))
    return query


@bp.route('/export',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '导出excel', permission='cms:material:export')
def export():
    list = query_model(Material, search_query, is_page=False, need_scope=True)
    
    title = ["机构id","名称","类型","文件","备注"]
    mtype_datas = get_dict_data('cms_material_type')
    wb = Workbook()
    sheet_names = wb.sheetnames
    ws = wb[sheet_names[0]]
    ws.append(title)
    for row in list:
        data = []
        data.append(row.org_id)
        data.append(row.name)
        data.append(get_label_by_value(mtype_datas, row.mtype))
        data.append(row.url)
        data.append(row.remark)
        ws.append(data)
    
    abs_filepath, filepath = get_download_file_path("{}.xlsx".format(time_now_name()))
    wb.save(abs_filepath)
    return R.success(msg=filepath)
    

@bp.route('/add',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '添加', permission='cms:material:add')
def add():
    """
    添加
    """
    if request.method == 'POST': # 添加
        o = Material()
        request_form_auto_fill(o)
        url = request.files.get('url')
        if url:
            img_url = upload('url', 'img')
            o.url = img_url

        db.session.add(o)
        db.session.commit()
        return R.success(msg='成功')

    return render_template( tpl_prefix + 'add.html')

@bp.route('/edit',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '修改', permission='cms:material:edit')
def edit():
    """
    编辑修改
    """
    if request.method == 'POST': 
        id = request.form.get('id', 0, type=int)
        o = Material.query.get(id)
        request_form_auto_fill(o)
        url = request.files.get('url')
        if url:
            img_url = upload('url', 'img')
            o.url = img_url

        db.session.commit()
        return R.success()

    id = request.args.get('id', 0, type=int)
    o = Material.query.get(id)
    return render_template(tpl_prefix + 'edit.html', d = o)

@bp.route('/remove',methods=['GET','POST'])
@login_required
@admin_perm(model_name, '删除', permission='cms:material:remove')
def remove():
    """
    根据id删除
    """
    ids = request.values.get('ids', type=str)
    ids = [int(i) for i in ids.split(',')]
    Material.query.filter(Material.id.in_(ids)).update({'deleted': 1})
    return R.success()


@bp.route('/imagehosting')
@login_required
def image_hosting():
    """
    图床
    """
    # from app.util import file_list_qiniu
    # imgs = file_list_qiniu()
    page = request.args.get('page',1, type=int)
    imgs = Material.query.order_by(Material.id.desc()). \
        paginate(page=page, per_page=20, error_out=False)
    return render_template( tpl_prefix + 'image_hosting.html',imgs = imgs)


@bp.route('/draw_preview', methods=['GET'])
@login_required
def draw_preview():
    width = request.args.get('width',type=int,default = 800)
    height = request.args.get('height',type=int, default= 400)
    background_color = request.args.get('background_color', '#424155')
    title = request.args.get('title','何三笔记')
    title_color = request.args.get('title_color','#ff0000')
    print(title_color)
    title_size = request.args.get('title_size',type=int, default= 60)
    font_path = os.path.join(admin_bp.static_folder,'fonts','站酷庆科黄油体.ttf')
    d_config = {
        'width': width,
        'height': height,
        'background_img': '',
        'background_color': background_color,

        'layers': [
            {
                'layer_type': 'text',
                'color': title_color,
                'font': {
                    'font': font_path,
                    'size': title_size,
                },
                'position': '0,0',
                'align': 'center',
                'text': title
            }
        ]
    }
    d = util.H3blogDrow()
    d.parse_config(d_config)
    img = d.draw()
    bytesIO = io.BytesIO()
    img.save(bytesIO, 'PNG')
    bytesIO.seek(0)
    return send_file(bytesIO, mimetype='image/png')