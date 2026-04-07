from flask import request, jsonify, Blueprint,current_app, render_template
from flask.globals import session
from flask_login.utils import login_required, current_user, login_user
from . import api
from app.util import R, build_mcode
import markdown
from app.settings import basedir
import os

@api.get('/api_doc')
def api_doc():
    exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite','markdown.extensions.tables','markdown.extensions.toc']
    mdcontent = ""
    path = os.path.join(basedir,'app','api','api.md')
    with open(path,'r',encoding='utf-8') as f:
        mdcontent = f.read()
    html = markdown.markdown(mdcontent,extensions=exts)
    # print(html)
    return render_template('api/api_doc.html', content = html)