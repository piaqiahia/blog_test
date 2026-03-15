from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text,DECIMAL
from sqlalchemy.orm import backref, relationship
from sqlalchemy import func, text
from flask_login import UserMixin, AnonymousUserMixin

from app.util.common import CustomHtmlFormatter, slugify
from .common import BaseModel, PayLog,User, default_create_by
from datetime import datetime
import hashlib
from flask_login import current_user
from flask import url_for, request
import markdown
from markdown.extensions.toc import TocExtension  # 锚点的拓展
from markdown.extensions.codehilite import CodeHiliteExtension
from typing import Any
from app.util import get_short_id
from app.ext import db


class Category(BaseModel):
    """栏目"""
    __tablename__ = 'cms_category'
    id = db.Column(db.Integer, primary_key=True)
    title = Column(String(64),index=True, comment='栏目标题')
    parent_id = db.Column(db.Integer, db.ForeignKey('cms_category.id'), default=None, comment='父ID')
    name = Column(String(64), index=True, comment='编码')
    desp = Column(String(300), comment='描述')
    tpl_list = Column(String(300), comment='列表模板') #列表模板
    tpl_page = Column(String(300), comment='单页/详情模板') #单页/详情模板
    tpl_mold = Column(String(20), comment='模板类型 list,single_page') #模板类型 list,single_page
    content = Column(Text,comment='可以录入信息内容') # 如果是单页，可以录入信息内容
    seo_title = Column(String(100), comment='seo标题')
    seo_description = Column(String(300), comment='seo描述')
    seo_keywords = Column(String(300), comment='seo关键词')
    order_num = Column(Integer, default=0, comment='排序')
    visible = Column(Integer, default=1, comment='是否隐藏') #是否隐藏
    icon = Column(String(128), default='')
    img = Column(String(300), comment='栏目图片')
    desp = Column(Text, comment='栏目描述')
    h_role = Column(Integer, default=0, comment='0=无,1=管理员,2=会员,3=vip, 4=付费') #那个角色可以看见隐藏的内容
    price = Column(DECIMAL(10,2), default=0.00, comment='单价') 
    children = relationship("Category",backref = backref("parent", remote_side=[id]), order_by=order_num.asc())

    def to_dict(self):
        d = {i.name: getattr(self, i.name) for i in self.__table__.columns}
        d['articles_count'] = self.articles_count()
        return d

    def __repr__(self):
        return '<Name %r>' % self.name

    def children_names(self):
        ids = self._children_ids()
        cs = Category.query.filter(Category.id.in_(ids), Category.deleted == 0).all()
        names = []
        for c in cs:
            names.append(c.name)
        return names
    def _children_ids(self,id = None):
        if id is None:
            id = self.id

        q = text("""
            select t4.id from
            (
                select @ids _ids, (select @ids := group_concat(id) from cms_category where find_in_set(parent_id, @ids) and deleted = 0) 
                from cms_category t1, (select @ids := :id) t2
                where @ids is not null
            ) t3, cms_category t4
            where find_in_set(t4.id, t3._ids);
        """)
        try:
            results =  db.session.execute(q,{'id': id}).fetchall()
        except Exception as e:
            q = text("""
                WITH RECURSIVE subcategories AS (
                    SELECT id, parent_id
                    FROM cms_category
                    WHERE parent_id = {} 

                    UNION ALL

                    SELECT c.id, c.parent_id
                    FROM cms_category c
                    INNER JOIN subcategories s ON c.parent_id = s.id
                )
                SELECT id FROM subcategories
            """.format(id))
            results =  db.session.execute(q,{'id': id}).fetchall()
        ids = []
        for row in results:
            ids.append(row[0])  # 使用整数索引访问元组中的第一个字段(id)
        return ids

    def articles(self,
            tags:str = None, # 文章标签，文章标签逗号分割比如"python,安全,何三笔记"
            is_hot:bool = False, # 是否热门文章,根据浏览量进行获取
            hot_num:int = 0, # 热门文章值，比如 hot_num = 5 是获取文章浏览量大于等于5的数据
            has_children_category = False, # 是否包含子栏目文章数据
            orderby:str = '', # 排序 按照发布时间 asc=升序 desc= 降序
            is_page:bool = False, # 是否分页，如果is_page=True即开启分页,如果开启分页返回数据将是Paginate类型
            page:int = 1,  # 分页页数
            per_page:int = 10 # 每页条数
        ):
        """获取全部的文章"""
        query = Article.query.filter(Article.state == 1, Article.deleted ==0)
        if has_children_category:
            query = query.filter(Article.category_id.in_(self._children_ids()))
        else:
            query = query.filter(Article.category_id == self.id)
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
            query = query.order_by(Article.sn.desc(),Article.publish_time.desc())
        if is_page:
            if type(page) != int:
                try:
                    page = int(page)
                except:
                    page = 1
            return query.paginate(page=page, per_page = per_page, error_out = False)
        else:
            return query.all()
        
    def articles_count(self,
            tags:str = None, # 文章标签，文章标签逗号分割比如"python,安全,何三笔记"
            is_hot:bool = False, # 是否热门文章,根据浏览量进行获取
            hot_num:int = 0, # 热门文章值，比如 hot_num = 5 是获取文章浏览量大于等于5的数据
        ):
        """获取的文章数量"""
        query = Article.query.filter(Article.state == 1, Article.deleted ==0)
        query = query.filter(Article.category_id.in_(self._children_ids()))
        if tags and len(tags) > 0:
            query = query.filter(Article.tags.any(Tag.name.in_(tags.split(','))))
        if is_hot:
            query = query.filter(Article.vc >= hot_num)
        return query.count()
        
    
    @property
    def url(self) ->str:
        return url_for('main.category', c=self.name)
    
    def crumbs(self):
        def _crumbs(cs,c):
            cs.append(c)
            if c.parent:
                _crumbs(cs,c.parent)
        cs = []
        _crumbs(cs,self)
        return cs[::-1]
    
    #获取顶部栏目
    def top_category(self):
        def _top(c):
            if c.parent_id is None:
                return c
            return _top(c.parent)
        return _top(self)

article_tag = db.Table('cms_article_tag',
                       db.Column('article_id',Integer,ForeignKey('cms_article.id', ondelete='CASCADE'),primary_key=True),
                       db.Column('tag_id',Integer,ForeignKey('cms_tag.id', ondelete='CASCADE'),primary_key=True))


class Tag(BaseModel):
    __tablename__ = 'cms_tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64),nullable=False, unique=True, index=True, comment='名称')
    code = Column(String(64), nullable=False, unique=True, index = True, comment='编码')
    visible = Column(Integer, default=1, comment='是否可见') #是否隐藏

    def to_dict(self):
        d = {i.name: getattr(self, i.name) for i in self.__table__.columns}
        d['article_count'] = self.articles.count()
        return d

    @classmethod
    def add(self,name :str) -> Any:
        """添加标签"""
        name = name.strip()
        tag = Tag.query.filter(Tag.name == name).first()
        if tag is not None:
            return tag
        code = get_short_id()
        while db.session.query(Tag.query.filter(Tag.code == code).exists()).scalar():
            code = get_short_id()
        tag = Tag(name = name,code = code, visible = True)
        db.session.add(tag)
        db.session.commit()
        return tag

    def __repr__(self):
        return '<Name %r>' % self.name
    
def time_stamp():
    """当前时间戳"""
    return datetime.now().timestamp()

class Article(BaseModel):
    """文章"""
    __tablename__ = 'cms_article'
    id = Column(Integer, primary_key=True)
    title = Column(String(120), index=True, comment='标题')
    name = Column(String(64),index=True,unique=True, comment='编码')
    editor = Column(String(10),nullable=False, default='', comment='编辑器')
    content = Column(Text, comment='md内容')
    content_html = Column(Text, comment='内容')
    summary = Column(String(300), comment='简述')
    thumbnail = Column(String(200), comment='缩略图')
    state = Column(Integer,default=0, comment='状态')
    vc = Column(Integer,default=0, comment='访问统计')
    toc = Column(Text, comment='目录')
    comment_num = Column(Integer,nullable=False, default=0)
    publish_time = Column(DateTime, index=True, comment='发布时间')
    author = Column(String(64),nullable=False, default='', comment='作者')
    create_by = db.Column(db.Integer, default = default_create_by, comment = '创建者')
    category_id = Column(Integer, ForeignKey('cms_category.id'))
    category = relationship('Category')
    tags = relationship('Tag',secondary=article_tag,backref=backref('articles',lazy='dynamic'),lazy='dynamic')
    h_content = Column(Text, nullable=False, default = '') #隐藏内容
    h_role = Column(Integer, default=0, comment='0=无,1=管理员,2=会员,3=vip, 4=付费') #那个角色可以看见隐藏的内容
    price = Column(DECIMAL(10,2), default=0.00, comment='单价') 
    sn = Column(Integer,nullable=False,default=time_stamp, comment='排序')
    is_crawl = Column(Integer, default = 0, comment = '是否抓取内容')
    origin_url = Column(String(200), default = '', comment = '抓取内容的原始url')
    origin_author = Column(String(100), default = '', comment = '原作者')
    

    def to_dict(self):
        d = {i.name: getattr(self, i.name) for i in self.__table__.columns}
        d['category'] = self.category
        return d

    def content_to_html(self):
        return markdown.markdown(self.content, extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            ])
    def md_convert(self):
        md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown_checklist.extension',
                CodeHiliteExtension(pygments_formatter=CustomHtmlFormatter),
                TocExtension(slugify=slugify),
            ])
        html = md.convert(self.content)
        return (html, md.toc)

    @property
    def user(self):
        """返回作者对象"""
        return User.query.get(self.create_by)

    @property
    def category(self):
        """返回文章分类对象"""
        return Category.query.get(self.category_id)

    @property
    def category_name(self):
        """返回文章分类名称，主要是为了使用 flask-wtf 的 obj 返回对象的功能"""
        return Category.query.get(self.category_id).name

    @property
    def previous(self):
        """用于分页显示的上一页"""
        a = self.query.filter(Article.state==1, Article.deleted==0,Article.id < self.id). \
            order_by(Article.timestamp.desc()).first()
        return a

    @property
    def next(self):
        """用于分页显示的下一页"""
        a = self.query.filter(Article.state==1,Article.deleted==0,Article.id > self.id). \
            order_by(Article.timestamp.asc()).first()
        return a

    @property
    def tag_names(self):
        """返回文章的标签的字符串，用英文‘, ’分隔，主要用于修改文章功能"""
        tags = []
        for tag in self.tags:
            tags.append(tag.name)
        return ', '.join(tags)

    @property
    def thread_key(self): # 用于评论插件
        return hashlib.new(name='md5', string=str(self.id)).hexdigest()

    @property
    def show_h_content(self) -> str:
        if self.h_role == 0: #隐藏
            return ''
        # 如果是角色查看内容判断是否当前用户角色是否可以查看
        if self.h_role == 4: #文章为单独付费文章，判断是否支付过
            log = PayLog.query.filter(PayLog.action_type == '文章付费', PayLog.ref_id == self.id, PayLog.state == 1, PayLog.create_by == current_user.id).first()
            if log:
                return self.h_content
            # url = url_for('main.login') + '?next=' + request.path
            repl = '''
            <p class="border border-warning p-2 text-center">
                本文隐藏内容需单独 <a href="" class="pay_article" data-articleid="{}" data-price="{}" style="color: rgb(48, 83, 241);">购买({}元)</a> 后才可以浏览
            </p>
            '''.format(self.id, self.price, self.price)
            return repl
        elif self.h_role == 3: #如果设置VIP用户可查看
            if current_user.is_authenticated and current_user.user_type == 'vip':
                return self.h_content
            url = url_for('main.account.vip_pay') + '?next=' + request.path
            repl = '''
            <p class="border border-warning p-2 text-center">
                本文隐藏内容 <a href="{}" style="color: rgb(48, 83, 241);">VIP会员</a> 才可以浏览
            </p>
            '''.format(url)
            return repl
        elif self.h_role == 2: #会员查看
            if current_user.is_authenticated and current_user.user_type in ['member','vip']:
                return self.h_content
            url = url_for('main.login') + '?next=' + request.path
            repl = '''
            <p class="border border-warning p-2 text-center">
                本文隐藏内容 <a href="{}" style="color: rgb(48, 83, 241);">登录</a> 后才可以浏览
            </p>
            '''.format(url)
            return repl
        else:
            return ''
    @property
    def url(self) ->str:
        return url_for('main.article', id=self.id)

    def __repr__(self):
        return '<Title %r>' % self.title

    def crumbs(self):
        def _crumbs(cs,c):
            cs.append(c)
            if c.parent:
                _crumbs(cs,c.parent)
        cs = []
        _crumbs(cs,self.category)
        return cs[::-1]
    
    def thumbnail_img(self):
        thumbnail = self.thumbnail
        if self.thumbnail is None or self.thumbnail == '':
            thumbnail = self.category.img
        if thumbnail is None or thumbnail == '':
            thumbnail = url_for('static', filename='img/thumbnail.jpg')
        return thumbnail
    

class Comment(db.Model):
    '''
    评论
    '''
    __tablename__ = 'cms_comment'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, default=0)
    user = db.relationship('User',backref=db.backref('comments',lazy='dynamic'), lazy=True)
    article_id = db.Column(db.Integer, db.ForeignKey('cms_article.id'), nullable=False, default=0, comment='关联的文章id')
    article = db.relationship('Article',backref=db.backref('comments',lazy='dynamic',order_by=id.desc()), lazy=True)
    content = db.Column(db.String(1024))
    reply_id = db.Column(db.Integer, db.ForeignKey('cms_comment.id'), default=None, comment='回复对应的评论id')
    replies = db.relationship('Comment', back_populates='comment')
    comment = db.relationship('Comment', back_populates='replies', remote_side=[id])
    timestamp = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<user_id: %r, article_id: %r,reply_id: %r, content: %r>' % (self.user_id,self.article_id,self.reply_id,self.content)

class InvitationCode(db.Model):
    '''
    邀请码
    '''
    __tablename__ = 'invitation_code'
    id = db.Column(db.Integer, primary_key = True)
    code = db.Column(db.String(64),unique = True, nullable=False)
    user = db.Column(db.String(64))
    state = db.Column(db.Boolean, default=True)

class OnlineTool(db.Model):
    '''
    在线工具
    '''
    __tablename__ = 'cms_online_tool'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    desp = db.Column(db.String(120))
    img = db.Column(db.String(200))
    url = db.Column(db.String(200))
    sn = db.Column(db.Integer,default=0)
    state = db.Column(db.Integer, default=1)
    timestamp = db.Column(db.DateTime, default=datetime.now)

class Material(BaseModel):
    """素材管理"""
    __tablename__ = 'cms_material'
    name = Column(String(64), default='', comment='名称')
    mtype = Column(String(32), default='pic', comment='类型')
    url = Column(String(120), comment='文件')
    remark = Column(String(32), comment='备注')

class Banner(BaseModel):
    """横幅"""
    __tablename__ = 'cms_baaner'
    name = Column(String(64), nullable=False,default='', comment='名称')
    mtype = Column(String(32), nullable=False,default='', comment='类型')
    img = Column(String(220), nullable=False ,default='',comment='图片')
    video = Column(String(500), nullable=False, default='', comment='视频地址')
    url = Column(String(300), nullable=False ,default='', comment='链接')
    remark = Column(String(300), nullable=False,comment='备注')
    order_num = Column(Integer, default=0, comment='排序')

    
class FriendlyLink(BaseModel):
    """友情连接"""
    __tablename__ = 'cms_friendly_link'
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(200), nullable=False, default = '', comment='连接')
    name = db.Column(db.String(200), nullable=False, default='', comment='名称')
    state = db.Column(db.Integer, default=1, comment='状态')
    ctime = db.Column(db.DateTime, default=datetime.now, comment='时间')

class VipPrice(BaseModel):
    """vip价格表"""
    __tablename__ = 'vip_price'
    name = Column(String(128), nullable=False, default='', comment='名称')
    price = Column(DECIMAL(10,2), default=0.00, comment='支付金额')
    days = Column(Integer, nullable=False, default=30, comment='天数')
    desp = Column(Text,nullable=False, default='', comment='描述')
    sn = Column(Integer, nullable=False, default=0, comment='排序')
    def to_dict(self):
        d = {i.name: getattr(self, i.name) for i in self.__table__.columns}
        # d['member'] = self.member
        return d


class Theme(BaseModel):
    """网站主题模板"""
    __tablename__ = 'cms_theme'
    name = Column(String(64), nullable=False, default='', comment='主题名称')
    code = Column(String(64), nullable=False, unique=True, index=True, comment='主题代码')
    description = Column(String(300), nullable=False, default='', comment='主题描述')
    preview_img = Column(String(200), nullable=False, default='', comment='预览图片')
    author = Column(String(64), nullable=False, default='', comment='作者')
    version = Column(String(20), nullable=False, default='1.0.0', comment='版本号')
    is_active = Column(Integer, nullable=False, default=0, comment='是否激活(0=否,1=是)')
    sn = Column(Integer, nullable=False, default=0, comment='排序')
    
    def to_dict(self):
        d = {i.name: getattr(self, i.name) for i in self.__table__.columns}
        return d
    
    def __repr__(self):
        return '<Theme %r>' % self.name