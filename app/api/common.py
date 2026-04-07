from flask import request, jsonify, Blueprint
from . import api
from app.util.permission import admin_perm
from app.util import R
from app.model import DictData
from app.ext import csrf

bp = Blueprint('common', __name__)
api.register_blueprint(bp, url_prefix='/common')
model_name = '通用模块'

@csrf.exempt
@bp.get('/dict_data')
@admin_perm(model_name, '获取字典数据',admin_required=False)
def mcode():
    dict_type = request.args.get('dict_type', '')
    list = DictData.query.filter(DictData.dict_type == dict_type, DictData.status == 0).\
            order_by(DictData.sort.asc()).all()
    return R.success(list, msg='获取数据成功')