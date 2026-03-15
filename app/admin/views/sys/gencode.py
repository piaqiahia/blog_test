import os
import re
from flask import render_template, request, jsonify, Blueprint
from flask_login.utils import login_required
from app import model

from app.util.common import admin_required
from app.util import R, request_form_auto_fill
from app.util.model import query_model
from app.ext import db

from app.admin.views.sys import sys_bp
from app.model import GenColumn, GenModel, DictType, Menu
from app.settings import basedir

bp = Blueprint('gencode', __name__)
sys_bp.register_blueprint(bp, url_prefix='/gencode')
tpl_prefix = 'admin/sys/gencode/'

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
    菜单获取列表
    """
    list = query_model(GenModel, search_query)
    return jsonify(list)

def search_query(query):
    value = request.form.get('name','')
    if value.strip() != '':
        query = query.filter(GenModel.name.like('%%%s%%' % value))

    query = query.order_by(GenModel.id.desc())
    return query


def get_html_type_by_col_type(col_type:str) ->str:
    '''根据类型获取html类型'''
    html_type = 'input'
    if 'DATETIME' == col_type:
        html_type = 'datetime'
    elif 'TEXT' == col_type:
        html_type = 'summernote'
    else:
        html_type = 'input'
    return html_type

# 找出模块里所有的类名
def get_classes(arg):
    import inspect
    classes = []
    clsmembers = inspect.getmembers(arg, inspect.isclass)
    for (name, _) in clsmembers:
        classes.append(name)
    return classes

@bp.route('/add',methods=['GET','POST'])
@login_required
@admin_required
def add():
    """
    菜单添加
    """
    if request.method == 'POST': # 添加
        gm = GenModel()
        request_form_auto_fill(gm)
        gm.model_name = str(gm.model).lower()
        gm.tpl_path = 'cms.'+gm.model_name
        gm.view_path = 'cms'
        db.session.add(gm)

        _model = getattr(model, gm.model)
        m = _model()
        for col in m.__table__.columns:
            print(col.name, col.type)
            if col.name in ['id', 'ctime', 'create_by', 'utime', 'update_by', 'deleted']:
                continue
            gcol = GenColumn(
                gen_model = gm,
                col_name = col.name,
                col_comment = col.comment,
                col_type = str(col.type),
                html_type = get_html_type_by_col_type(str(col.type))
            )
            db.session.add(gcol)
        # cols = {i.name: getattr(m, i.name) for i in m.__table__.columns}
        # print(cols)
        db.session.commit()
        return R.success(msg='成功')
    classes = get_classes(model)
    gms = GenModel.query.all()
    has_names = [gm.model for gm in gms]
    classes = [name for name in classes if name not in has_names]
    return render_template( tpl_prefix + 'add.html', models = classes)


@bp.route('/edit',methods=['GET','POST'])
@login_required
@admin_required
def edit():
    """
    编辑修改
    """
    if request.method == 'POST': 
        id = int(request.form.get('id', 0))
        gm = GenModel.query.get(id)
        request_form_auto_fill(gm)

        param = 'columns'
        columns = {}
        for k,v in request.form.to_dict().items():
            if param in k:
                #print(k, v)
                i = k[7:k.index('.')]
                if i in columns:
                    o = columns.get(i)
                else:
                    o = {}
                    columns[i] = o
                p = k[k.index('.') + 1:]
                o[p] = v

        # print(columns)

        for v in columns.values():
            id = v.get('id')
            gc =GenColumn.query.get(id)
            request_form_auto_fill(gc, data_dict=v)
            gc.is_required = v.get('is_required') if v.get('is_required') else 0
            gc.is_insert = v.get('is_insert') if v.get('is_insert') else 0
            gc.is_edit = v.get('is_edit') if v.get('is_edit') else 0
            gc.is_list = v.get('is_list') if v.get('is_list') else 0
            gc.is_query = v.get('is_query') if v.get('is_query') else 0
            db.session.add(gc)


        db.session.commit()
        return R.success()

    id = int(request.args.get('id', 0))
    gm = GenModel.query.get(id)
    _model = getattr(model, gm.model)
    m = _model()
    return render_template(tpl_prefix + 'edit.html', d = gm, columns =  m.__table__.columns)


@bp.post('/columns')
def columns():
    """获取字段列表"""
    id = request.form.get('id',0, type=int)
    def _q(query):
        query = query.filter(GenColumn.gen_model_id == id).order_by(GenColumn.order_num.asc())
        return query
    list = query_model(GenColumn, _q, per=100)
    return jsonify(list)

@bp.route('/remove',methods=['GET','POST'])
@login_required
@admin_required
def remove():
    """
    根据id删除
    """
    id = request.args.get('id',0, type= int)
    role = GenModel.query.get(id)
    db.session.delete(role)
    db.session.commit()
    return R.success()

@bp.route('/preview',methods=['GET','POST'])
@login_required
@admin_required
def preview():
    """预览代码"""
    id = request.args.get('id', type=int)
    gm = GenModel.query.get(id)
    list = gen_preview(gm)
    return R.success(list)


@bp.route('/gencode',methods=['GET','POST'])
@login_required
@admin_required
def gencode():
    """代码生成"""
    id = request.args.get("id", type= int)
    gm = GenModel.query.get(id)
    list = gen_preview(gm)

    if gm.tpl_category == 'api':
        py_path = os.path.join(basedir,'app', 'api', '{}.py'.format(gm.model_name))
        for t in list:
            name = t['name']
            content = t['content']
            ext = name[name.rfind('.')+1:]
            if ext == 'py':
                with open(py_path, 'w', encoding='utf-8', newline='') as f:
                    f.write(content)
            break
        return R.success(msg='生成成功')
        
    
    py_path = os.path.join(basedir, 'app','admin','views',gm.view_path)
    if not os.path.exists(py_path):
        os.makedirs(py_path)
    html_path = os.path.join(basedir, 'app', 'admin', 'templates', 'admin', *(gm.tpl_path.split('.')))
    if not os.path.exists(html_path):
        os.makedirs(html_path)
    for t in list:
        name = t['name']
        content = t['content']
        ext = name[name.rfind('.')+1:]
        if ext == 'html':
            file_path = os.path.join(html_path, name)
            with open(file_path, 'w', encoding="utf-8", newline='') as f:
                f.write(content)
        elif ext == 'py':
            file_path = os.path.join(py_path, '{}.py'.format(gm.model_name))
            with open(file_path, 'w', encoding="utf-8", newline='') as f:
                f.write(content)
    #插入菜单
    if gm.parent_menu_id != '':
        perm_prefix = ":".join(gm.tpl_path.split("."))
        menu = Menu.query.filter(Menu.menu_type == 'C', Menu.perms == perm_prefix + ':view').first()
        if menu is None:
            menu = Menu(
                name = gm.name,
                parent_id = gm.parent_menu_id,
                order_num = 1,
                url = '/admin/{}/'.format("/".join(gm.tpl_path.split("."))),
                target = 'menuItem',
                menu_type = 'C',
                perms = perm_prefix + ':view',
            )
            db.session.add(menu)
            db.session.commit()
        addBtn = Menu.query.filter(Menu.menu_type == 'F', Menu.perms == perm_prefix + ':add').first()
        if addBtn is None:
            addBtn = Menu(name = '添加',parent_id = menu.id,order_num = 1,menu_type = 'F',perms = perm_prefix + ':add')
            db.session.add(addBtn)
        editBtn = Menu.query.filter(Menu.menu_type == 'F', Menu.perms == perm_prefix + ':edit').first()
        if editBtn is None:
            editBtn = Menu(name = '修改',parent_id = menu.id,order_num = 2,menu_type = 'F',perms = perm_prefix + ':edit')
            db.session.add(editBtn)
        removeBtn = Menu.query.filter(Menu.menu_type == 'F', Menu.perms == perm_prefix + ':remove').first()
        if removeBtn is None:
            removeBtn = Menu(name = '删除',parent_id = menu.id,order_num = 3,menu_type = 'F',perms = perm_prefix + ':remove')
            db.session.add(removeBtn)
        exportBtn = Menu.query.filter(Menu.menu_type == 'F', Menu.perms == perm_prefix + ':export').first()
        if exportBtn is None:
            exportBtn = Menu(name = '导出',parent_id = menu.id,order_num = 4,menu_type = 'F',perms = perm_prefix + ':export')
            db.session.add(exportBtn)
        
        db.session.commit()
        
    return R.success(msg='生成成功')


def gen_preview(genModel: GenModel):
    from mako.template import Template
    tpls = [
        'add.html',
        'edit.html',
        'list.html',
        'view.py'
    ]
    if genModel.tpl_category == 'tree':
        tpls.append('select_tree.html')
    
    if genModel.tpl_category == 'crud_html':
        tpls = [
            'add.html',
            'edit.html',
            'list_html.html',
            'view.py'
        ]
    if genModel.tpl_category == 'api':
        tpls = ['api.py']
    base_path = os.path.join(basedir,'app','admin','templates','admin','sys','gencode','vm')
    files = []
    for tpl in tpls:
        tpl_path = os.path.join(base_path, tpl)
        t = Template(filename=tpl_path)
        content = t.render(m = genModel)
        f = {}
        f['name'] = tpl
        f['content'] = content
        files.append(f)
    return files


@bp.route('/select_dict_tree',methods=['GET','POST'])
@login_required
@admin_required
def select_dict_tree():
    """字典选择界面"""
    id = request.args.get('id', 0, type=int)
    dict_type = request.args.get('dict_type','')
    d = DictType.query.filter(DictType.dict_type == dict_type).first()
    return render_template(tpl_prefix + 'select_dict_tree.html', id = id, d = d)

@bp.route('/tree_data',methods=['GET','POST'])
@login_required
@admin_required
def tree_data():
    """字典类型数据"""
    list = DictType.query.filter(DictType.status == 0).all()
    return jsonify(list)