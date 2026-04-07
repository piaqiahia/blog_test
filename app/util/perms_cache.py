from app.ext import cache
from app.model import User, Menu


def set_perms_cache(user: User):
    """设置用户权限缓存"""
    if not isinstance(user, User):
        return None
    if user.role is not None:
        list = user.role.menus.order_by(Menu.order_num.asc()).all()
        d = dict()
        for m in list:
            perms = m.perms.strip()
            if perms != '':
                d[perms] = m.name
        cache.set('PERMS_{}'.format(user.id), d)
        return d
    return None

def get_perms_cache(user: User):
    """获取权限缓存"""
    perms = cache.get('PERMS_{}'.format(user.id))
    if perms:
        return perms
    else: # 如果为None 重新获取下，有可能是过期了
        cache.delete('PERMS_{}'.format(user.id))
        perms = set_perms_cache(user)
    return perms

def delete_perms_cache(user: User):
    """清除权限缓存"""
    cache.delete('PERMS_{}'.format(user.id))