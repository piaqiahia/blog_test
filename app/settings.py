# -*- coding: utf-8 -*-
import os
import sys
import hashlib
from flask import current_app, render_template
from flask.app import Flask
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY') or hashlib.new('md5', b'x21h3blog5x').hexdigest()
    WTF_CSRF_ENABLED = False # 全局关闭csrf
    WTF_CSRF_TIME_LIMIT = 36000

    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=15)

    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_POOL_RECYCLE = int(os.getenv('SQLALCHEMY_POOL_RECYCLE',10)) #多少秒后自动回收连接
    SQLALCHEMY_POOL_SIZE = int(os.getenv('SQLALCHEMY_POOL_SIZE',30)) # 数据库连接池的大小。默认是引擎默认值5
    SQLALCHEMY_POOL_TIMEOUT = int(os.getenv('SQLALCHEMY_POOL_TIMEOUT', 10)) #设定连接池的连接超时时间。默认是10 
    SQLALCHEMY_MAX_OVERFLOW = int(os.getenv('SQLALCHEMY_MAX_OVERFLOW', 10)) # 控制在连接池达到最大值后可以创建的连接数。当这些额外的 连接回收到连接池后将会被断开和抛弃
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ECHO = False

    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'king233666888@163.com'
    MAIL_PASSWORD = 'THiD4zj7mvbbbrAd'
    MAIL_DEFAULT_SENDER = 'king233666888@163.com'

    H3BLOG_AUTHORIZATION_HEADER = 'Authorization' # app认证头部标识
    H3BLOG_TITLE = os.getenv('H3BLOG_TITLE','何三笔记')
    H3BLOG_DOMAIN = os.getenv('H3BLOG_DOMAIN','www.h3blog.com')
    H3BLOG_KEYWORDS = os.getenv('H3BLOG_KEYWORDS','何三笔记')
    H3BLOG_DESCRIPTION = os.getenv('H3BLOG_DESCRIPTION','何三笔记')
    H3BLOG_EMAIL = os.getenv('H3BLOG_EMAIL','')
    H3BLOG_POST_PER_PAGE = 10
    H3BLOG_MANAGE_POST_PER_PAGE = 15
    H3BLOG_COMMENT_PER_PAGE = 15
    H3BLOG_SLOW_QUERY_THRESHOLD = 1
    H3BLOG_REGISTER_INVITECODE = os.getenv('H3BLOG_REGISTER_INVITECODE',False)   # 是否开启邀请码注册
    H3BLOG_COMMENT = os.getenv("H3BLOG_COMMENT", False) # 是否开发评论，默认不开启
    H3BLOG_EDITOR = os.getenv('H3BLOG_EDITOR', 'markdown') # 默认编辑器
    H3BLOG_TEMPLATE = os.getenv('H3BLOG_TEMPLATE', 'tend') # 前端模板

    H3BLOG_UPLOAD_TYPE = os.getenv('H3BLOG_UPLOAD_TYPE','') # 默认本地上传
    H3BLOG_UPLOAD_PATH = os.path.join(basedir, 'uploads')
    H3BLOG_ALLOWED_IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'webp','doc','docx','xls','xlsx','ppt','pptx', 'pdf','mp3', 'mp4']
    H3BLOG_TONGJI_SCRIPT = os.getenv('H3BLOG_TONGJI_SCRIPT','') #统计代码
    H3BLOG_EXTEND_META = os.getenv('H3BLOG_EXTEND_META', '') # 扩展META
    H3BLOG_ROBOTS = os.getenv('H3BLOG_ROBOTS', 'User-agent: *\nAllow: /') # 网站robots定义
    # 网站备案信息
    H3BLOG_START_TIME = os.getenv('H3BLOG_START_TIME', '2020-02-20') # 网站开始运行时间
    H3BLOG_GWAB = os.getenv('H3BLOG_GWAB', '') # 公安备案号
    H3BLOG_ICP = os.getenv('H3BLOG_ICP', '') # ICP备案号
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024 # 支持最大100M上传

    QINIU_CDN_URL = os.getenv('QINIU_CDN_URL','http://cdn.h3blog.com/')
    QINIU_BUCKET_NAME = os.getenv('QINIU_BUCKET_NAME','h3blog')
    QINIU_ACCESS_KEY = os.getenv('QINIU_ACCESS_KEY','key123')
    QINIU_SECRET_KEY = os.getenv('QINIU_SECRET_KEY','secret456')

    BAIDU_PUSH_TOKEN = os.getenv('BAIDU_PUSH_TOKEN') #主动推送给百度链接，token是在搜索资源平台申请的推送用的准入密钥

    SITEMAP_URL_SCHEME = os.getenv('SITEMAP_URL_SCHEME','http')
    SITEMAP_MAX_URL_COUNT = os.getenv('SITEMAP_MAX_URL_COUNT',100000)

    # 阿里云支付配置
    ALIPAY_APPID= os.getenv('ALIPAY_APPID', '123123') # 设置签约的appid
    ALIPAY_PUBLIC_KEY = os.getenv('ALIPAY_PUBLIC_KEY', '123') # 支付宝公钥
    ALIPAY_PRIVATE_KEY =os.getenv('ALIPAY_PRIVATE_KEY', '123') # 私钥
    ALIPAY_DEBUG = os.getenv('ALIPAY_DEBUG', False)
    ALIPAY_NOTIFY_URL = os.getenv('ALIPAY_NOTIFY_URL', 'http://pay.xxx.com/admin/pay_notify/ali')
    ALIPAY_SIGNTYPE = os.getenv('ALIPAY_SIGNTYPE', 'RSA2')

    #微信支付配置
    WECHAT_APPID = os.getenv('WECHAT_APPID', '123123')
    WECHAT_APP_SECRET = os.getenv('WECHAT_APP_SECRET', '123123')
    WECHAT_MCH_KEY = os.getenv('WECHAT_MCH_KEY', '12313')
    WECHAT_MCH_ID = os.getenv('WECHAT_MCH_ID', '123123')
    WECHAT_NOTIFY_URL = os.getenv('WECHAT_NOTIFY_URL', 'http://pay.xxx.com/admin/pay_notify/wx')
    WECHAT_API_CERT_PATH = os.getenv('WECHAT_API_CERT_PATH','')
    WECHAT_API_KEY_PATH = os.getenv('WECHAT_API_KEY_PATH','')


 
    ALIYUN_ACCESSKEY_ID = os.getenv('ALIYUN_ACCESSKEY_ID', '') # 阿里云AccessKey ID
    ALIYUN_ACCESSKEY_SECRET = os.getenv('ALIYUN_ACCESSKEY_SECRET', '') # 阿里云AccessKey Secret
    ALIYUN_SEND_MSG_SIGN_NAME = os.getenv('ALIYUN_SEND_MSG_SIGN_NAME', '') # 阿里云短信签名
    ALIYUN_SEND_MSG_TEMPLATE_CODE = os.getenv('ALIYUN_SEND_MSG_TEMPLATE_CODE', '') # 阿里云短信模板
    
    ALIYUN_VIDEO_REGION_ID = os.getenv('ALIYUN_VIDEO_REGION_ID', '') #阿里云视频存储节点
    ALIYUN_TEMPLATEGROUPID = os.getenv('ALIYUN_TEMPLATEGROUPID', 'VOD_NO_TRANSCODE') #阿里云转码模版组id 

    ALIYUN_SFX_APPCODE = os.getenv('ALIYUN_SFX_APPCODE','123123') #阿里云身份证验证

    ALIYUN_DOC_API = os.getenv('ALIYUN_DOC_API', 'http://doc-h3blog.oss-cn-beijing.aliyuncs.com/') # 阿里云访问文档api地址

    ALIYUN_STATIC_ENDPOINT = os.getenv('ALIYUN_STATIC_ENDPOINT', 'http://oss-cn-beijing.aliyuncs.com')
    ALIYUN_STATIC_BUCKET_NAME = os.getenv('ALIYUN_STATIC_BUCKET_NAME', '123123')
    ALIYUN_BUCKET_DOMAIN = os.getenv('ALIYUN_BUCKET_DOMAIN', 'http://abc.oss-cn-beijing.aliyuncs.com/')

    GEOIP2_PATH = os.getenv('GEOIP2_PATH', 'D:\\tools\\GeoLite2-City_20211019\\GeoLite2-City.mmdb') # 根据ip定位城市数据库位置GeoLite2-City.mmdb

    # CACHE_TYPE = os.getenv('CACHE_TYPE', "SimpleCache") #RedisCache
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.getenv('CACHE_REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = 300 # 缓存时间
    APP_DEBUG = os.getenv('APP_DEBUG', 'False') == 'True'



    

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(basedir, 'data-dev.db'))
    DEFAULT_MYSQL_URI = 'mysql+pymysql://root:1511054331@127.0.0.1:3306/h3blog'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', DEFAULT_MYSQL_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # in-memory database

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    pass

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

if __name__ == "__main__":
    pass