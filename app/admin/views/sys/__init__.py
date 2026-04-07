from flask import Blueprint
from app.admin import admin

sys_bp = Blueprint('sys', __name__)
admin.register_blueprint(sys_bp, url_prefix='/sys')

# 在末尾导入相关模块，是为了避免循环导入依赖，因为在下面的模块中还要导入蓝本main
from . import index, menu,role,user,dict_type,dict_data,gencode, loginlog, optlog,setting,org