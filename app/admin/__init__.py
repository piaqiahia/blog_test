
from flask import Blueprint

admin = Blueprint('admin', __name__, template_folder="templates", static_folder='static', static_url_path='/astatics',)

# 在末尾导入相关模块，是为了避免循环导入依赖，因为在下面的模块中还要导入蓝本main
from . import errors
from .views import login, regist, captcha, common
from .views.sys import *
from .views.cms import *
