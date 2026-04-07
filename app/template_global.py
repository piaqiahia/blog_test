from datetime import datetime
import re
from typing import Any, List
from flask.app import Flask
from flask_login import current_user
from flask import url_for, request, g
from sqlalchemy.orm import query 
from app.model import DictData
from app.model.cms import FriendlyLink
from app.util.perms_cache import get_perms_cache
from app import util
from app.model import Article,Category, Tag, Banner

def register_template_filter(app: Flask):
    '''注册模板过滤器'''

    @app.template_filter()
    def seconds_hms(sconds: int) -> str:
        millis = sconds * 1000
        seconds, milliseconds = divmod(millis, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return ("%d:%d:%d" % (hours, minutes, seconds))
        # return time.strftime('%H:%M:%S', time.gmtime(sconds))

    @app.template_filter('request_page_params')
    def request_page_params(d, *args):
        if d.get('page',None):
            del d['page']
        for a in args:
            if d.get(a, None):
                del d[a]
        return d
    
    @app.template_filter("pretty_date")
    def pretty_date(time):
        return util.pretty_date(time)
    
    @app.template_filter('hidden_content')
    def hidden_content(content):
        if current_user.is_authenticated:
            return content.replace('[h3_hidden]','').replace('[/h3_hidden]','')
        else:
            login_url = url_for('main.login') + '?next=' + request.path
            repl = '''
            <p class="border border-warning p-2 text-center">
            本文隐藏内容 <a href="{}">登陆</a> 后才可以浏览
            </p>
            '''.format(login_url)
            return re.sub('\[h3_hidden\].*?\[/h3_hidden\]',repl,content,flags=re.DOTALL)

def register_template_global(app: Flask):
    """
    注册模板全局函数
    """
    @app.template_global()
    def now():
        """当前时间"""
        return datetime.now()
    
    @app.template_global()
    def strptime(t,format='%Y-%m-%d'):
        """字符串转日期"""
        return datetime.strptime(t, format)
    
    @app.template_global()
    def get_website_run_time(start_time_str):
        """网站运行时间"""
        start_time = start_time_str or '2020-02-20'
        start_time = start_time_str if len(start_time_str.strip())>0 else '2020-02-20'
        print(start_time)
        delta = (datetime.now() - datetime.strptime(start_time, '%Y-%m-%d'))
        seconds = delta.days * 24 * 60 * 60 + delta.seconds
        years, secs = divmod(seconds ,(365 * 24 * 60 * 60))
        days = int(secs / (24 * 60 * 60))
        return f'{years}年 {days}天'
    @app.template_global()
    def get_dict_data(dict_type):
        """根据字典类型获取字典数据"""
        list = DictData.query.filter(DictData.dict_type == dict_type, DictData.status == 0).\
            order_by(DictData.sort.asc()).all()
        return list
    
    @app.template_global()
    def has_perms(perm)->bool:
        """判断权限是否存在"""
        perms = get_perms_cache(current_user)
        if perms and perm in perms:
            return True
        return False

    @app.template_global()
    def check_perms(perm)->str:
        """判断权限是否存在"""
        if current_user.username == 'admin':
            return ''
        perms = get_perms_cache(current_user)
        if perms and perm in perms:
            return ''
        return 'hidden'

    @app.template_global()
    def get_dict_data_label_by_value(dict_type,value):
        """根据字典类型和值或去标签名称"""
        o = DictData.query.filter(DictData.dict_type == dict_type, DictData.status == 0, DictData.value == value).first()
        return o.label


    @app.template_global()
    def any_in(list, stra):
        """判断列表中任何一个在字符串sta中则返回True"""
        return any(x in stra for x in list)
    
    @app.template_global()
    def get_article_by_id(id:int):
        """根据id获取文章"""
        return Article.query.get(id)
    
    @app.template_global()
    def get_articles(
            categorys:str = None, #文章分类，分类标识逗号分割比如"python,flask,django"
            tags:str = None, # 文章标签，文章标签逗号分割比如"python,安全,何三笔记"
            is_hot:bool = False, # 是否热门文章,根据浏览量进行获取
            hot_num:int = 0, # 热门文章值，比如 hot_num = 5 是获取文章浏览量大于等于5的数据
            orderby:str = '', # 排序 按照发布时间 asc=升序 desc= 降序
            is_page:bool = False, # 是否分页，如果is_page=True即开启分页,如果开启分页返回数据将是Paginate类型
            page:int = 1,  # 分页页数
            per_page:int = 10 # 每页条数
        ) -> Any:
        """
        根据条件获取已发布的文章
        """
        query = Article.query.filter(Article.state == 1, Article.deleted ==0)
        if categorys and len(categorys) > 0:
            cs = Category.query.filter(Category.deleted ==0 ,Category.name.in_(categorys.split(','))).all()
            c_ids = []
            for c in cs:
                c_ids.extend(c._children_ids())
            query = query.filter(Article.category_id.in_(c_ids))
            # query = query.filter(Article.category.has(Category.name.in_(categorys.split(','))))
        if tags and len(tags) > 0:
            query = query.filter(Article.tags.any(Tag.name.in_(tags.split(','))))
        if is_hot:
            query = query.filter(Article.vc >= hot_num)
            query = query.order_by(Article.vc.desc())
        if orderby.lower() == 'asc':
            query = query.order_by(Article.publish_time.asc())
        elif orderby.lower() == 'desc':
            query = query.order_by(Article.publish_time.desc())
        else:
            query = query.order_by(Article.publish_time.desc())
        
        if type(page) != int:
            try:
                page = int(page)
            except:
                page = 1
        pg = query.paginate(page=page, per_page=per_page, error_out=False)
        if is_page:
            return pg
        else:
            return pg.items

    @app.template_global()
    def get_categorys(names:str = None, visible = 1) -> List[Category] :
        """
        获取文章分类
        """
        query = Category.query.filter(Category.deleted == 0)
        if names and len(names) > 0:
            query = query.filter(Category.name.in_(names.split(',')))
        if visible:
            query = query.filter(Category.visible == visible)
        query = query.order_by(Category.order_num.asc())
        return query.all()
    
    @app.template_global()
    def get_category_by_name(name:str = None) -> Category:
        """获取分类文章"""
        return Category.query.filter(Category.name == name).first()

    @app.template_global()
    def get_categorys_by_parent(parent_id = None, visible = 1) -> List[Category] :
        """
        获取文章分类
        """
        query = Category.query.filter(Category.parent_id ==parent_id, Category.deleted == 0)
        if visible:
            query = query.filter(Category.visible == visible)
        query = query.order_by(Category.order_num.asc())
        return query.all()
    
    @app.template_global()
    def get_categorys_by_parent_name(parent_name = None, visible = 1) -> List[Category] :
        """
        获取文章分类
        """
        parent_id = Category.query.filter(Category.name == parent_name).first().id
        query = Category.query.filter(Category.parent_id ==parent_id, Category.deleted == 0)
        if visible:
            query = query.filter(Category.visible == visible)
        query = query.order_by(Category.order_num.asc())
        return query.all()

    @app.template_global()
    def get_tags(tags:str = None, rtype='obj') -> List[Tag] :
        """
        获取系统标签
        """
        query = Tag.query.filter(Tag.visible == True, Tag.deleted == 0)
        if tags and len(tags) > 0:
            query = query.filter(Tag.name.in_(tags.split(',')))
        datas = query.all()
        if rtype == 'name':
            return [t.name for t in datas]
        return datas

    @app.template_global()
    def get_banners(mtype:str = None) -> List[Banner]:
        """
        根据类型获取banner
        """
        query = Banner.query.filter(Banner.deleted == 0)
        if mtype and len(mtype)>0:
            query = query.filter(Banner.mtype == mtype)
        query = query.order_by(Banner.order_num.asc())
        return query.all()
    
    @app.template_global()
    def get_friendlylinks() -> List[FriendlyLink]:
        """获取友情链接"""
        return FriendlyLink.query.filter(FriendlyLink.state == True).all()
    
    @app.template_global()
    def admin_login_background() -> str:
        """获取后台登录背景图"""
        background = app.config.get('SYS_LOGIN_BACKGROUND', '')
        if background or background.strip() == '':
            return url_for('main.bing_bg')
        return background


if __name__ == '__main__':
    pass