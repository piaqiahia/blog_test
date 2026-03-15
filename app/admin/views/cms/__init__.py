from flask import Blueprint
from app.admin import admin

cms_bp = Blueprint('cms', __name__)
admin.register_blueprint(cms_bp, url_prefix='/cms')

# 在末尾导入相关模块，是为了避免循环导入依赖，因为在下面的模块中还要导入蓝本main
from . import category, material, article, banner, tag, paylog,friendlylink,vipprice,theme