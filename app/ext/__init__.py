from flask import current_app
from flask.app import Flask
from flask_login import LoginManager
from flask_sitemap import Sitemap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache

from app.util.auth import auth_decode

class AppHelper(object):
    def init_app(self, app: Flask, db=None, directory=None, **kwargs):
        self.app = app
        self.config_update()
    def config_update(self):
        with self.app.app_context():
            from app.model import Setting
            settings = Setting.query.all()
            for o in settings:
                if o.skey:
                    if o.skey in ['h3blog_comment','h3blog_register_invitecode']:
                        v = True if o.svalue == '1' else False
                        self.app.config[o.skey.upper()] = v
                    else:
                        self.app.config[o.skey.upper()] = o.svalue
            from app.model import Theme
            theme = Theme.query.filter(Theme.is_active == True).first()
            if theme:
                self.app.config['H3BLOG_TEMPLATE'] = theme.code

class DBConfig(object):
    def init_app(self, app, db=None):
        try:
            with db.get_engine(app=app).connect() as conn:
                objs = conn.execute("select * from setting")
                for o in objs:
                    if o.skey:
                        if o.skey in ['h3blog_comment','h3blog_register_invitecode']:
                            v = True if o.svalue == '1' else False
                            app.config[o.skey.upper()] = v
                        else:
                            app.config[o.skey.upper()] = o.svalue
        except:
            # print('连接数据库失败或setting表不存在')
            pass
        
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
app_helper = AppHelper()
csrf = CSRFProtect()
db_config = DBConfig()
cache = Cache()
sitemap = Sitemap()


@login_manager.user_loader
def load_user(user_id):
    from flask import request
    from app.model import User, Member
    temp = user_id.split('.')
    try:
        uid = temp[1]
        # return User.query.get(int(uid))
        if temp[0] == 'admin' and request.blueprint.startswith('admin'):
            return User.query.filter(User.id==int(uid),User.user_type=='admin').first()
        elif temp[0] == 'member' and request.blueprint.startswith('mobile'):
            return User.query.filter(User.id==int(uid),User.user_type !='admin').first()
        elif request.blueprint.startswith('main'):
            return User.query.get(int(uid))
        else:
            return None
    except:
        return None
    

@login_manager.request_loader
def request_loader(request):
    from app.model import User # type: ignore
    token = request.headers.get(current_app.config.get('H3BLOG_AUTHORIZATION_HEADER'))
    if token:
        user_info = auth_decode(token)
        if len(user_info) == 2:
            return User.query.filter(User.username == user_info[0], User.password_hash == user_info[1]).first()
    return None

login_manager.session_protection = 'strong'
login_manager.login_view = 'admin.login'
if 1 == 1:
    from app.model import AnonymousUser
    login_manager.anonymous_user = AnonymousUser
#在主__init__.py -》 register_blueprints() 方法中已经设置
# login_manager.blueprint_login_views = {
#         'main' : 'main.login',
#         'main.profile' : 'main.login',
#         'main.study' : 'main.login',
#     }
login_manager.login_message = ''
login_manager.login_message_category = 'warning'
