from flask import request,current_app, abort, Response, url_for
from flask_login import current_user, AnonymousUserMixin
from functools import wraps
from app.model import OptLog
from app.ext import db, cache
from .ip_util import get_real_ip, get_ip_city
from .perms_cache import get_perms_cache
import json

def admin_perm(model_name, opt, permission='',admin_required = True):
    def _admin_required(func):
        """ 检查管理员权限 """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                f_name = f.__name__
                if admin_required: #需要管理身份验证
                    if not current_user or (not current_user.is_admin() if hasattr(current_user, 'is_admin') else True):
                        abort(403)
                if not _verify(permission):
                    abort(403)
                result = f(*args, **kwargs)
                opt_log(model_name,opt,permission,f_name, result)
                return result
            return decorated_function
        return decorator(func)
    return _admin_required


def _verify(permission)->bool :
    """验证权限"""
    if permission == '':
        return True
    if current_user.username == 'admin':
        return True
    perms = get_perms_cache(current_user)
    if perms and permission in perms:
        return True
    return False


def opt_log(model_name, opt, permission, f_name, result):
    """操作日志"""
    ip = get_real_ip()

    # 统一构建公共字段
    log_data = dict(
        title=model_name,
        method=f_name,
        opt_name=opt,
        oper_url=request.path,
        request_method=request.method,
        oper_param=json.dumps(request.values.to_dict(), ensure_ascii=False),
        oper_name=current_user.username if not isinstance(current_user, AnonymousUserMixin) else '',
        ipaddr=ip,
        login_location=get_ip_city(ip),
        browser=request.user_agent.browser,
        ossystem=request.user_agent.platform,
        state=200,
    )

    if isinstance(result, Response) and result.is_json:
        # JSON 响应：记录结构化数据
        try:
            json_result = json.dumps(result.get_json(force=True), ensure_ascii=False)
        except Exception:
            json_result = result.get_data(as_text=True)  # 兜底
        log_data.update(
            json_result=json_result,
            is_json_result=True
        )
    else:
        # 非 JSON 响应（redirect / render_template / str 等）
        # 👇 关键修复：json_result 设为 None，不存 Response 对象
        log_data.update(
            json_result=None,  # ✅ 安全！
            is_json_result=False
        )

    opt_log_entry = OptLog(**log_data)
    db.session.add(opt_log_entry)