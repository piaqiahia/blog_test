from unicodedata import name
import uuid
from flask.helpers import url_for
from flask import Blueprint, current_app, flash, redirect, request, session, g
from flask.templating import render_template
from flask_login.utils import current_user, login_required
from sqlalchemy import true

from app.model.common import PayLog
from app.util.ali_face_pay import AliFacePay

from .. import main as main_bp
from app.util import build_template_path, allowed_file, R, request_form_auto_fill, build_mcode, upload
from app.util.ali_send_msg import SendMsg
import os
from datetime import datetime
from app.ext import db
from app.model import User

def flash_success(msg):
    flash({'success':msg})

def flash_error(msg):
    flash({'error':msg})

bp = Blueprint('tool', __name__)
main_bp.register_blueprint(bp, url_prefix='/tool')

"""
用户个人信息设置
"""

tpl_profix = '/tool/'

@bp.get('/')
def index():
    return render_template(build_template_path(tpl_profix + 'index.html'))

@bp.get('/markdown-editor')
def markdown_editor():
    return render_template(build_template_path(tpl_profix + 'markdown_editor.html'))


@bp.get('/cron')
def cron():
    return render_template(build_template_path(tpl_profix + 'cron.html'))
