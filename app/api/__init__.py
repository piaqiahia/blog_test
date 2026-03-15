from flask import Blueprint

api = Blueprint('api', __name__, template_folder="templates")

# 在末尾导入相关模块，是为了避免循环导入依赖，因为在下面的模块中还要导入蓝本main
from . import errors,login,vip