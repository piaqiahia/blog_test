from typing import Any

from sqlalchemy.orm import backref, defaultload, relationship,aliased
from sqlalchemy import func,Column, ForeignKey, Integer, String, DateTime, select, Boolean, TypeDecorator
from sqlalchemy.dialects  import sqlite
from sqlalchemy.sql.expression import false
from app.ext import db
from flask_login import UserMixin, AnonymousUserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import current_user
from flask import url_for

from app.util.common import to_datetime

class UniversalDateTime(TypeDecorator):
    impl = DateTime  # 默认使用DateTime类型

    def load_dialect_impl(self, dialect):
        # 对SQLite使用DATETIME类型（存储为字符串）
        if dialect.name  == 'sqlite':
            return dialect.type_descriptor(sqlite.DATETIME()) 
        else:
            return dialect.type_descriptor(self.impl) 
    def process_bind_param(self, value, dialect):
        # 将 Python datetime 对象转换为数据库可接受的格式
        if value is not None:
            if dialect.name == 'sqlite':
                # sqlite 不支持字符串格式日期，要转化成datetime对象
                if isinstance(value, str):
                    return to_datetime(value)
                return value
            else:
                # 其他数据库通常不需要特别格式化
                return value
        return value

def default_create_by():
    if current_user and not isinstance(current_user, AnonymousUserMixin):
        return current_user.id
    return None

def default_create_org():
    if current_user and not isinstance(current_user, AnonymousUserMixin):
        if current_user.org:
            return current_user.org.id
    return None

class BaseUser(db.Model, UserMixin):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    mobile = db.Column(db.String(32), comment='手机号')
    username = db.Column(db.String(64), unique=True, index=True, comment='账号')
    password_hash = db.Column(db.String(256), comment='密码')
    nickname = db.Column(db.String(100), nullable=False, default='', comment = '别名')
    avatar = db.Column(db.String(120),default='', comment='头像')
    last_seen = db.Column(UniversalDateTime, default=datetime.utcnow, comment='最后登陆时间')

    ctime = db.Column(UniversalDateTime, default=datetime.now, comment = '创建时间')
    create_by = db.Column(db.Integer, default = default_create_by, comment = '创建者')
    utime = db.Column(UniversalDateTime, default=datetime.now, comment = '修改时间')
    update_by = db.Column(db.String(64), default = '', comment = '修改者')
    deleted = db.Column(db.Integer, nullable=False, default=0, comment='删除标记') # 0=未删除 1= 删除

    @property
    def password(self):
        raise ArithmeticError('非明文密码，不可读。')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password=password)
    
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

def on_update_by():
    if current_user and not isinstance(current_user, AnonymousUserMixin):
        return current_user.mobile
    return ''

class BaseModel(db.Model, UserMixin):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ctime = db.Column(UniversalDateTime, default=datetime.now, comment = '创建时间')
    create_by = db.Column(db.Integer, default = default_create_by, comment = '创建者')
    utime = db.Column(UniversalDateTime, default=datetime.now, comment = '修改时间', onupdate=func.now())
    update_by = db.Column(db.String(64), default = '', comment = '修改者', onupdate= lambda: current_user.mobile if current_user and not isinstance(current_user, AnonymousUserMixin) else '')
    deleted = db.Column(db.Integer, nullable=False, default=0, comment='删除标记') # 0=未删除 1= 删除
    remark = db.Column(db.String(200), default='', comment='备注')
    org_id = db.Column(db.Integer, default = default_create_org, comment='机构id')


class User(BaseUser):
    __tablename__ = 'user'
    email = db.Column(db.String(64),unique=True, index=True, default='', comment='电子邮箱')
    name = db.Column(db.String(64),nullable=False, default='', comment='姓名')
    sex = db.Column(db.String(2), nullable=False, default='', comment='性别')
    member_since = db.Column(UniversalDateTime, default=datetime.utcnow)
    status = db.Column(db.Integer, nullable=False, default=0, comment = '0正常 1停用')
    user_type = db.Column(db.String(64),default='admin', comment='admin=后台管理员')
    role_id = db.Column(db.Integer, db.ForeignKey('sys_role.id'))
    role = relationship('Role')
    remark = db.Column(db.String(200), default='')
    org_id = db.Column(db.Integer, db.ForeignKey('org.id'))
    org = relationship('Org')
    vip_deadline = db.Column(db.DateTime, default=datetime.now, comment = '期限时间')

    def get_id(self):
        if self.user_type == 'admin':
            return 'admin.' + str(self.id)
        else:
            return 'member.' + str(self.id)

    def is_admin(self):
        return True

    def __repr__(self):
        return '<User %r>' % self.username

    def to_dict(self):
        d = {i.name: getattr(self, i.name) for i in self.__table__.columns}
        d['org'] = self.org
        return d
    
    def user_type_name(self):
        """用户类型名称"""
        if self.user_type == 'admin':
            return '管理员'
        elif self.user_type == 'member':
            return '普通会员'
        elif self.user_type == 'vip':
            return 'VIP会员'
        else:
            return '未知'
    
    def avatar_img(self):
        avatar = self.avatar
        if avatar is None or avatar == '':
            avatar = url_for('static', filename='img/avatar.webp')
        return avatar

class AnonymousUser(AnonymousUserMixin):
    id = None
    role = None
    def is_admin(self):
        return False



role_menu = db.Table('sys_role_menu',
                       db.Column('role_id',db.Integer,db.ForeignKey('sys_role.id', ondelete='CASCADE'),primary_key=True),
                       db.Column('menu_id',db.Integer,db.ForeignKey('sys_menu.id', ondelete='CASCADE'),primary_key=True))


class Menu(BaseModel):
    """菜单"""
    __tablename__ = 'sys_menu'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, default = '', comment='菜单名称')
    parent_id = db.Column(db.Integer, db.ForeignKey('sys_menu.id'), default=None, comment='父菜单ID')
    order_num = db.Column(db.Integer, default=0, comment='显示排序')
    url = db.Column(db.String(200), default='#', comment='请求地址')
    target = db.Column(db.String(20), default='', comment='打开方式(menuItem页签 menuBlank新窗口)')
    menu_type = db.Column(db.String(5), default='', comment='菜单类型（M目录 C菜单 F按钮）')
    visible = db.Column(db.Integer, default='0', comment='菜单状态（0显示 1隐藏）')
    perms = db.Column(db.String(100), default=None, comment='权限标识')
    icon = db.Column(db.String(100), default='#', comment = '菜单图标')
    is_refresh = db.Column(db.Integer, default=1, comment='是否刷新（0刷新 1不刷新）')
    children = relationship("Menu",backref = backref("parent", remote_side=[id]), order_by=order_num.asc())

class Role(BaseModel):
    """角色"""
    __tablename__ = 'sys_role'
    name = db.Column(db.String(64), nullable=False, default = '', comment='角色名称')
    key = db.Column(db.String(64), nullable=False, default = '', comment='角色权限字符串')
    sort = db.Column(db.Integer, default = 0, comment='显示顺序')
    scope = db.Column(db.Integer, default = 2, comment = '数据范围（1：超管权限 2：机构管理员权限 3: 代理权限）')
    status = db.Column(db.Integer, default = 0, comment = '角色状态(0正常 1停用')
    menus = relationship('Menu',secondary=role_menu,lazy='dynamic', order_by=Menu.order_num.asc())
    org_id = db.Column(db.Integer, db.ForeignKey('org.id'))

    def scopes(self):
        if self.scope == 1 or current_user.username == 'admin':
            return [
                {'id': 1, 'name': '超管权限'},
                {'id': 2, 'name': '本部门及子部门权限'},
                {'id': 3, 'name': '本部门权限'},
                {'id': 4, 'name': '个人权限'}
            ]
        elif self.scope == 2:
            return [
                {'id': 2, 'name': '本部门及子部门权限'},
                {'id': 3, 'name': '本部门权限'},
                {'id': 4, 'name': '个人权限'}
            ]
        elif self.scope == 3:
            return [
                {'id': 3, 'name': '本部门权限'},
                {'id': 4, 'name': '个人权限'}
            ]
        else:
            return [{'id': 3, 'name': '个人权限'}]



class DictType(BaseModel):
    """字典类型"""
    __tablename__ = 'sys_dict_type'
    name = db.Column(db.String(100), nullable=False, default = '', comment='字典名称')
    dict_type = db.Column(db.String(100), nullable=False, default = '', comment = '字典类型')
    status = db.Column(db.Integer, default = 0, comment = '状态(0正常 1停用')

class DictData(BaseModel):
    """字典数据"""
    __tablename__ = 'sys_dict_data'
    sort = db.Column(db.Integer, default = 0, comment='字典顺序')
    label = db.Column(db.String(100), nullable=False, default='', comment = '字典标签')
    value = db.Column(db.String(100), nullable=False, default='', comment='字典键值')
    dict_type = db.Column(db.String(100), nullable=False, default='', comment = '字典类型')
    css_class = db.Column(db.String(100), nullable=False, default='', comment = '样式属性（其他样式扩展）')
    list_class = db.Column(db.String(100), nullable=False, default='', comment = '表格回显样式')
    is_default = db.Column(db.String(1), default='N', comment='是否默认（Y是 N否）')
    status = db.Column(db.Integer, default = 0, comment = '状态(0正常 1停用')


class LoginLog(db.Model):
    """登录日志"""
    __tablename__ = 'sys_login_log'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login_name = db.Column(db.String(100), nullable=False, default='', comment='登录账号')
    ipaddr = db.Column(db.String(64), nullable=False, default='', comment='登录ip')
    login_location = db.Column(db.String(200), nullable=False, default='', comment='登录地点')
    browser = db.Column(db.String(200), nullable=False, default='', comment='浏览器类型')
    ossystem = db.Column(db.String(200), nullable=False, default='', comment='操作系统')
    state = db.Column(db.Integer, nullable=False, default=1, comment='登录状态')
    msg = db.Column(db.String(200), nullable=False, default='', comment='提示消息')
    login_time = db.Column(db.DateTime, default=datetime.now, comment = '访问时间')
    deleted = db.Column(db.Integer, nullable=False, default=0, comment='删除标记') # 0=未删除 1= 删除


class OptLog(db.Model):
    """登录日志"""
    __tablename__ = 'sys_opt_log'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, default='', comment='模块标题')
    opt_name = db.Column(db.String(100), nullable=False, default='', comment='操作')
    method = db.Column(db.String(50), nullable=False, default='', comment='方法名称')
    oper_url = db.Column(db.String(400), nullable=False, default='', comment='请求URL')
    request_method = db.Column(db.String(50), nullable=False, default='', comment='请求方式')
    is_json_result = db.Column(db.Boolean, nullable=False, default=True, comment='是否是json结果')
    oper_param = db.Column(db.Text, comment='请求参数')
    json_result = db.Column(db.Text, comment='返回参数')
    oper_name = db.Column(db.String(100), nullable=False, default='', comment='操作人员')
    ipaddr = db.Column(db.String(64), nullable=False, default='', comment='主机地址')
    login_location = db.Column(db.String(200), nullable=False, default='', comment='操作地点')
    browser = db.Column(db.String(200), nullable=False, default='', comment='浏览器类型')
    ossystem = db.Column(db.String(200), nullable=False, default='', comment='操作系统')
    state = db.Column(db.Integer, nullable=False, default=1, comment='操作状态')
    msg = db.Column(db.String(200), nullable=False, default='', comment='提示消息')
    oper_time = db.Column(db.DateTime, default=datetime.now, comment = '访问时间')
    deleted = db.Column(db.Integer, nullable=False, default=0, comment='删除标记') # 0=未删除 1= 删除

class Member(BaseUser):
    __tablename__ = 'member'
    status = db.Column(db.Integer, nullable=False, default=0, comment = '0正常 1停用')
    name = db.Column(db.String(64), nullable=False, default='', comment='姓名')
    org_id = db.Column(db.Integer, db.ForeignKey('org.id'))
    org = relationship('Org')

    def get_id(self):
        return 'member.' + str(self.id)

    def is_admin(self):
        return False

    def to_dict(self):
        d = {i.name: getattr(self, i.name) for i in self.__table__.columns}
        d['org'] = self.org
        return d


class Org(db.Model):
    """机构"""
    __tablename__ = 'org'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, default = '', comment='名称')
    parent_id = Column(Integer, ForeignKey('org.id'), default=None, comment='父ID')
    order_num = Column(Integer, default=0, comment='排序')
    children = relationship("Org",backref = backref("parent", remote_side=[id]), order_by=order_num.asc())
    deleted = db.Column(db.Integer, nullable=False, default=0, comment='删除标记') # 0=未删除 1= 删除

    def _children_ids(self,id = None):
        if id is None:
            id = self.id

        q = """
            select t4.id from
            (
                select @ids _ids, (select @ids := group_concat(id) from org where find_in_set(parent_id, @ids)) 
                from org t1, (select @ids := :id) t2
                where @ids is not null
            ) t3, org t4
            where find_in_set(t4.id, t3._ids);
        """
        try:
            results =  db.session.execute(q,{'id': id}).fetchall()
        except Exception as e:
            q = """
                WITH RECURSIVE subcategories AS (
                    SELECT id, parent_id
                    FROM org
                    WHERE parent_id = {} 

                    UNION ALL

                    SELECT c.id, c.parent_id
                    FROM org c
                    INNER JOIN subcategories s ON c.parent_id = s.id
                )
                SELECT id FROM subcategories
            """.format(id)
            results =  db.session.execute(q,{'id': id}).fetchall()
        ids = []
        for row in results:
            ids.append(row['id'])
        return ids

        


class GenModel(BaseModel):
    '''代码生成'''
    __tablename__ = 'gen_model'
    name = db.Column(db.String(200), nullable=False, default='', comment='名称')
    model = db.Column(db.String(64), nullable=False, default='', comment='模块')
    model_name = db.Column(db.String(64), nullable=False, default='', comment='模块名称')
    tpl_path = db.Column(db.String(120), nullable=False, default='', comment='模板路径')
    view_path = db.Column(db.String(120), nullable=False, default='', comment='view路径')
    tpl_category = db.Column(db.String(120), nullable=False, default='', comment='模板类型')
    tree_code = db.Column(db.String(64), nullable=False, default='', comment='树字段编码')
    tree_parent_code = db.Column(db.String(64), nullable=False, default='', comment='树父字段编码')
    tree_name = db.Column(db.String(64), nullable=False, default='', comment = '树名称字段')
    tree_order = db.Column(db.String(64), nullable=False, default='', comment = '排序字段')
    parent_menu_id = db.Column(db.Integer, comment= '父菜单id')
    parent_menu_name = db.Column(db.String(64), nullable=False, default='', comment='父菜单名称')

    def has_html_type(self,html_type)->bool:
        for c in self.columns:
            if html_type in c.html_type:
                return True
        return False
    
    def get_dict_columns(self):
        '''获取需要字段渲染的字段列表'''
        cols = []
        for c in self.columns:
            if len(c.dict_type) > 0:
                cols.append(c)
        
        return cols


class GenColumn(BaseModel):
    '''代码生成字段'''
    __tablename__ = 'gen_column'
    gen_model_id = db.Column(db.Integer, db.ForeignKey('gen_model.id', ondelete='CASCADE'), comment='gen_model_id')
    gen_model = relationship('GenModel',backref=backref('columns'))
    col_name = db.Column(db.String(200), nullable=False, default='', comment='列名称')
    col_comment = db.Column(db.String(200), nullable=False, default='', comment='列描述')
    col_type = db.Column(db.String(200), nullable=False, default='', comment='列类型')
    is_required = db.Column(db.Integer, nullable=False, default=1, comment='是否必填')
    is_insert = db.Column(db.Integer, nullable=False, default=1, comment='是否插入字段')
    is_edit = db.Column(db.Integer, nullable=False, default=1, comment='是否编辑字段')
    is_list = db.Column(db.Integer, nullable=False, default=1, comment='是否列表字段')
    is_query = db.Column(db.Integer, nullable=False, default=1, comment='是否查询字段')
    query_type = db.Column(db.String(200), nullable=False, default='', comment='查询方式（等于、不等于、大于、小于、范围）')
    html_type = db.Column(db.String(200), nullable=False, default='', comment='显示类型（文本框、文本域、下拉框、复选框、单选框、日期控件）')
    order_num = db.Column(db.Integer, nullable=False, default=0, comment = '排序')
    dict_type = db.Column(db.String(200), nullable=False, default='', comment='字典类型')


class Setting(BaseModel):
    '''
    系统配置信息
    '''
    __tablename__ = 'setting'
    id = db.Column(db.Integer, primary_key=True)
    sname = db.Column(db.String(128), nullable=False, default='', comment='参数名称')
    skey = db.Column(db.String(64),index=True,unique=True, comment='参数键名')
    svalue = db.Column(db.Text,nullable=False, default='', comment='参数键值')
    stype = db.Column(db.String(2), nullable=False, default='', comment='系统内置')
    col_type = db.Column(db.String(64), nullable=False, default='text', comment='输入类型')

class PayLog(BaseModel):
    """支付记录"""
    __tablename__ = 'pay_log'
    pay_type = db.Column(db.String(100), nullable=False, default='', comment='支付类型')
    action_type = db.Column(db.String(100), nullable=False, default='', comment='动作类型')
    order_no = db.Column(db.String(128), nullable=False,unique=True, index=True, default='', comment='订单号')
    subject = db.Column(db.String(300), nullable=False, default='', comment='商品描述')
    trade_no = db.Column(db.String(300), nullable=False, default='', comment='交易订单号')
    total_fee = db.Column(db.DECIMAL(10,2), default=0.00, comment='支付金额')
    state = db.Column(db.Integer, nullable=False, default=0, comment='支付状态')
    return_code = db.Column(db.String(300), nullable=False, default='', comment='支付回调信息返回码')
    return_data = db.Column(db.String(5000), nullable=False, default='', comment='返回信息')
    return_time = db.Column(db.DateTime, comment = '回调时间')
    create_by = db.Column(db.Integer, db.ForeignKey('user.id'),default = default_create_by, comment = '创建者')
    user = relationship('User')
    ref_id = db.Column(db.Integer,comment='关联id')

    def to_dict(self):
        d = {i.name: getattr(self, i.name) for i in self.__table__.columns}
        d['user'] = self.user
        return d