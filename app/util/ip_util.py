from flask import request, current_app
import geoip2.database

def get_real_ip():
    """获取真实ip"""
    headers = request.headers
    if headers.get('X-Forwarded-For'):
        ip = headers.get('X-Forwarded-For')
    elif headers.get('X-Real-IP'):
        ip = headers.get('X-Real-IP')
    else:
        ip = request.remote_addr
    return ip


def get_ip_city(ip):
    """根据IP判断所属城市"""
    #下载地址 https://www.maxmind.com/en/accounts/626047/geoip/downloads
    #账号：466867714@qq.com
    ip_city = '未知'
    geoip2_path = current_app.config.get('GEOIP2_PATH','')
    if geoip2 == '':
        return ip_city
    try:
        with geoip2.database.Reader(geoip2_path) as reader:
            response = reader.city(ip)
            country = response.country.names.get('zh-CN',response.country.names.get('en'))
            province = response.subdivisions.most_specific.names['zh-CN']
            province = response.subdivisions.most_specific.names.get('zh-CN', response.subdivisions.most_specific.names.get('en'))
            city = response.city.names.get('zh-CN', response.city.names.get('en'))
            ip_city = '{} {} {}'.format(country,province,city)
    except:
        pass
    return ip_city