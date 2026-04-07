from typing import Any, List
from flask import request, current_app
from flask_login import current_user, AnonymousUserMixin
import re


class Row(dict):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __setattr__(self, name, val):
        self[name] = val
    def __getattr__(self,name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

def get_obj_fields(obj):
    """获取模型对象的表字段, obj或model均可"""
    if obj is None:
        return []
    return [column.name for column in obj.__table__.columns]


def request_form_auto_fill(model, data_dict = None) -> None:
    data = request.form.to_dict() if data_dict is None else data_dict
    if data is not None:
        data = {key: value for key, value in data.items()
                if key in get_obj_fields(model)}
        # [setattr(model, key, value) for key, value in data.items()]
        
        # 获取模型字段类型信息
        model_fields = {column.name: column.type for column in model.__table__.columns}
        
        for key, value in data.items():
            if key in model_fields:
                field_type = model_fields[key]
                # 处理DateTime字段
                if isinstance(value, str) and value.strip():
                    try:
                        from datetime import datetime
                        # 检查字段类型是否为DateTime类型
                        is_datetime_field = False
                        
                        # 检查是否是UniversalDateTime类型
                        if hasattr(field_type, 'impl') and hasattr(field_type.impl, '__name__'):
                            if field_type.impl.__name__ == 'DateTime':
                                is_datetime_field = True
                        
                        # 检查是否是普通的db.DateTime类型
                        elif hasattr(field_type, '__class__') and hasattr(field_type.__class__, '__name__'):
                            if field_type.__class__.__name__ == 'DateTime':
                                is_datetime_field = True
                        
                        # 如果是DateTime类型，尝试转换为datetime对象
                        if is_datetime_field:
                            # 尝试解析常见日期时间格式
                            if ' ' in value:
                                # 格式：YYYY-MM-DD HH:MM:SS
                                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                            elif 'T' in value:
                                # 格式：YYYY-MM-DDTHH:MM:SS
                                value = datetime.strptime(value.replace('T', ' '), '%Y-%m-%d %H:%M:%S')
                            else:
                                # 格式：YYYY-MM-DD
                                value = datetime.strptime(value, '%Y-%m-%d')
                    except (ValueError, TypeError):
                        # 如果转换失败，保持原值
                        pass
                
                setattr(model, key, value)

def get_request_valid_data(obj):
    data = request.get_json()
    if data is not None:
        data = {key: value for key, value in request.get_json().items()
                if key in get_obj_fields(obj)}
    return data

def parse_form_subs(sub_prefix='sub', model=None, check=lambda x: True)->List[Any]:
    """解析子表单提交"""
    if not sub_prefix.endswith('['):
        sub_prefix = sub_prefix + '['
    data = request.form.to_dict()
    hive = {}
    for key, value in data.items():
        if key.startswith(sub_prefix):
            nums = re.findall(r'[\[](.*?)[\]]',key)
            index = 0
            if len(nums) > 0 :
                index = int(nums[0])
            names = key.split('.')
            if names[0] in hive:
                obj = hive[names[0]]
                obj[names[1]] = value
                hive[names[0]] = obj
            else:
                hive[names[0]] = {
                    names[1]: value,
                    '_index' : index
                }
    
    subs = [ Row(v) for k, v in hive.items() if check(v)]
    subs.sort(key= lambda sub: sub['_index'])
    if model:
        objs = []
        for sub in subs:
            o = model()
            request_form_auto_fill(o,sub)
            objs.append(o)
        return objs
    return subs


def query_model(model, search_func, is_page = True, page_name = 'pageNum', per_page_name = 'pageSize', per = 10, need_scope = False, need_delete=True) -> Any:
    """
    根据model查询
    """
    query = model.query
    if need_delete:
        query = query.filter(model.deleted == 0)
    if search_func is not None:
        query = search_func(model.query)
    if need_scope:
        if current_user and not isinstance(current_user, AnonymousUserMixin) and current_user.role is not None and current_user.username != 'admin':
            scope = current_user.role.scope
            if scope is None or scope == 0:
                scope = 2
            if scope == 1: #超管权限
                pass
            if scope == 2: # 本部门及子部门权限
                query = query.filter(model.org_id.in_(current_user.org._children_ids()))
            elif scope == 3: # 本部门权限
                # 判断org_id是否存在如果不存在，通过create_by 获取所有机构数据
                query = query.filter_by(org_id = current_user.org_id)
            else: # scope == 4
                #个人数据 通过create_by 字段获取
                query = query.filter_by(create_by = current_user.id)
    if is_page :
        page = request.values.get(page_name, 1, type = int)
        per_page = request.values.get(per_page_name, per, type = int)
        return query.paginate(page=page, per_page=per_page, error_out=False)
    return query.all()
