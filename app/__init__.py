import code
import os
import logging
from unicodedata import name
import click
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, url_for, g, abort
from flask_sqlalchemy.record_queries import get_recorded_queries
from flask_wtf.csrf import CSRFError
from app.ext import db, login_manager, csrf, migrate,app_helper, db_config, cache, sitemap
from app.ext.json_provider import CustomJSONProvider
from app.settings import config
from app.template_global import register_template_filter, register_template_global
from app.model import Org

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_app(config_name=None):
    """使用工厂函数初始化程序实例

    Args:
        config_name (str): 配置名称，默认为 FLASK_CONFIG 环境变量或 'development'

    Returns:
        Flask: 应用实例
    """
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    """ 使用工厂函数初始化程序实例"""
    app = Flask(__name__)
    app.config['CONFIG_NAME'] = config_name
    app.config.from_object(config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_AS_ASCII'] = False
    app.json_provider_class = CustomJSONProvider
    app.json = CustomJSONProvider(app)

    if 'DATABASE_URL' in os.environ:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

    # 判断数据库是否是sqlite，如果是需要将连接池去掉
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
        app.config['SQLALCHEMY_POOL_SIZE'] = None
        app.config['SQLALCHEMY_POOL_TIMEOUT'] = None
        app.config['SQLALCHEMY_MAX_OVERFLOW'] = None

    register_logging(app)
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    register_errors(app)
    register_shell_context(app)
    register_request_handlers(app)
    register_template_filter(app)
    register_template_global(app)

    return app


def register_logging(app):
    class RequestFormatter(logging.Formatter):

        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    request_formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(os.path.join(basedir, 'logs/h3blog.log'),
                                       maxBytes=10 * 1024 * 1024, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    if not app.debug:
        app.logger.addHandler(file_handler)


def register_extensions(app: Flask):
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app,db=db)
    app_helper.init_app(app)
    db_config.init_app(app, db=db)
    cache.init_app(app)
    sitemap.init_app(app)


    


def register_blueprints(app: Flask):
    # 注册蓝本 main
    from app.main import main as main_blueprint, change_static_folder
    change_static_folder(main_blueprint, app.config['H3BLOG_TEMPLATE'])
    app.register_blueprint(main_blueprint)

    # 注册蓝本 admin
    from app.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    #设置main 蓝图下所有蓝图登陆入口地址
    blueprint_login_views = {}
    main_login_view = 'main.login'
    for name in app.blueprints:
        if name.startswith('main'):
            blueprint_login_views[name] = main_login_view

    login_manager.blueprint_login_views = blueprint_login_views

def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        from app.model import User, Setting
        return dict(db=db, User=User,Setting = Setting)


def register_errors(app):
    pass

def register_request_handlers(app: Flask):
    from flask_login import current_user

    @app.context_processor
    def context_processor():
        '''
        上下文处理器, 返回的字典可以在全部模板中使用
        '''
        return {'current_user': current_user}

    # @app.before_request
    def before_app_request():
        h3blog_domain = app.config['H3BLOG_DOMAIN']
        host = request.host
        if host.endswith(h3blog_domain) and len(host) > len(h3blog_domain):
            codes = host.split('.')
            if len(codes) > 4:
                abort(404)
            code = codes[0]
            org = Org.query.filter(Org.code == code).first()
            if org :
                g.org = org
            else:
                abort(404)
        else:
            org = Org.query.filter(Org.id == 0).first()
            g.org = org

    @app.after_request
    def query_profiler(response):
        for q in get_recorded_queries():
            if q.duration >= app.config['H3BLOG_SLOW_QUERY_THRESHOLD']:
                app.logger.warning(
                    'Slow query: Duration: %fs\n Location: %s\nQuery: %s\n '
                    % (q.duration, q.location, q.statement)
                )
        return response

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if exception:
            db.session.rollback()
        db.session.commit()


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    @click.option('--force', is_flag=True, help='Force drop without confirmation', default=False)
    def initdb(drop, force):
        """Initialize the database."""
        if drop:
            # 如果在 Docker 中运行（通过环境变量判断），或者强制执行
            if not force and not os.getenv('DOCKER_MODE') and not click.confirm('确认要删除所有表及记录吗？',
                                                                                default=False):
                click.echo('已取消')
                return

            db.drop_all()
            click.echo('已删除所有表')

        db.create_all()
        try:
            from app.initdb import init_database_data
            init_database_data(db)
            click.echo('初始数据已加载')
        except Exception as e:
            click.echo(f'加载初始数据失败: {e}')

        click.echo('数据库初始化完成')