import pathlib
import unicodedata
from flask import request,current_app, abort, Response, url_for
from flask_login import current_user
from functools import wraps
import geoip2
import requests
import json
import logging
import re
import uuid
import random
import os
import time
from datetime import datetime
import oss2
from typing import Any
from pygments.formatters.html import HtmlFormatter
from bs4 import BeautifulSoup
from html2text import HTML2Text
from urllib import parse

class Row(dict):
    """通用字典，并且可以使用点号.访问"""
    def __getattr__(self,name:str, default: Any = ''):
        try:
            return self[name]
        except KeyError:
            return default
    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value

def admin_required(func):
    """ 检查管理员权限 """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_admin():
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator(func)

def isAjax() -> bool :
    '''
    判断是否是ajax请求
    '''
    ajax_header = request.headers.get('X-Requested-With')
    if ajax_header and ajax_header == 'XMLHttpRequest':
        return True
    return False

def build_mcode(n) -> str:
    """产生验证码"""
    code = ''
    for i in range(n):
        add = random.randint(0, 9)
        code += str(add)
    return code.lower()

def build_template_path(tpl: str) -> str:
    """ 获取模板路径 """
    from app.util.template_manager import template_manager
    return template_manager.build_template_path(tpl)

def upload_file_qiniu(inputdata,filename=None):
    from qiniu import Auth, put_data, etag
    access_key = current_app.config.get('QINIU_ACCESS_KEY')
    secret_key = current_app.config.get('QINIU_SECRET_KEY')
    '''
    :param inputdata: bytes类型的数据
    :return: 文件在七牛的上传名字
    '''
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    #要上传的空间
    bucket_name = 'h3blog'

    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name)
    #如果需要对上传的图片命名，就把第二个参数改为需要的名字
    ret1,ret2=put_data(token,filename,data=inputdata)
    print('ret1:',ret1)
    print('ret2:',ret2)

    #判断是否上传成功
    if ret2.status_code!=200:
        raise Exception('文件上传失败')

    return ret1.get('key')

def file_list_qiniu():
    from qiniu import Auth, BucketManager
    access_key = current_app.config.get('QINIU_ACCESS_KEY')
    secret_key = current_app.config.get('QINIU_SECRET_KEY')
    cdn = current_app.config.get('QINIU_CDN_URL')
    q = Auth(access_key, secret_key)
    bucket = BucketManager(q)
    bucket_name = 'h3blog'
    # 前缀
    prefix = None
    # 列举条目
    limit = 100
    # 列举出除'/'的所有文件以及以'/'为分隔的所有前缀
    delimiter = None
    # 标记
    marker = None
    ret, eof, info = bucket.list(bucket_name, prefix, marker, limit, delimiter)
    # print(info)
    # assert len(ret.get('items')) is not None
    items = ret.get('items')
    return [ {'key':item['key'],'url': cdn + item['key']} for item in items]

def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(int(second_diff / 60)) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(int(second_diff / 3600)) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(int(day_diff / 7)) + " weeks ago"
    if day_diff < 365:
        return str(int(day_diff / 30)) + " months ago"
    return str(int(day_diff / 365)) + " years ago"



import re 
from datetime import datetime 
 
def to_datetime(date_str, default=None):
    """
    将常见日期时间字符串转换为datetime对象 
    支持格式包括：
    - ISO 8601（含时区）
    - 年-月-日 时:分:秒[.毫秒]
    - 月/日/年 时:分:秒 [AM/PM]
    - 紧凑格式（YYYYMMDDHHMMSS）
    - Unix时间戳（秒/毫秒）
 
    参数：
    - date_str: 输入的日期时间字符串 
    - default: 默认日期时间（datetime对象或字符串），如果未提供，默认为当前时间 
 
    返回：
    - datetime对象，如果无法解析则返回默认日期时间 
    """
    if default is None:
        default = datetime.now()   # 默认使用当前时间 
    elif isinstance(default, str):
        default = to_datetime(default)  # 递归解析默认日期时间 
 
    date_str = str(date_str).strip()
    if not date_str:  # 如果输入为空，直接返回默认值 
        return default 
 
    # 预处理时区格式（将+08:00转换为+0800）
    date_str = re.sub(r'([+-]\d{2}):(\d{2})$',  r'\1\2', date_str)
 
    date_formats = [
        # 带时区格式 
        "%Y-%m-%dT%H:%M:%S.%f%z",  # ISO 8601带微秒和时区 
        "%Y-%m-%d %H:%M:%S.%f%z",  # 带微秒和时区 
        "%Y-%m-%dT%H:%M:%S%z",     # ISO 8601带时区 
        "%Y-%m-%d %H:%M:%S%z",     # 带时区 
        
        # 标准日期时间格式 
        "%Y-%m-%d %H:%M:%S.%f",    # 带微秒 
        "%Y-%m-%d %H:%M:%S",       # 标准格式 
        "%Y/%m/%d %H:%M:%S",       # 斜杠分隔 
        "%m/%d/%Y %I:%M:%S %p",    # 12小时制带AM/PM 
        "%d-%m-%Y %H:%M:%S",       # 日月年格式 
        "%Y%m%d%H%M%S",            # 紧凑格式 
        
        # 纯日期格式 
        "%Y-%m-%d",                # ISO日期 
        "%d/%m/%Y",                # 日月年 
        "%b %d %Y %H:%M:%S",       # 月份缩写（Oct 05 2023）
    ]
    
    # 尝试匹配预定义格式 
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str,  fmt)
        except ValueError:
            continue 
    
    # 尝试解析为时间戳（支持秒和毫秒）
    try:
        ts = float(date_str)
        if ts > 1e10:  # 处理毫秒级时间戳 
            ts = ts / 1000.0 
        return datetime.fromtimestamp(ts) 
    except:
        pass 
    
    # 如果所有尝试都失败，返回默认日期时间 
    return default 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['H3BLOG_ALLOWED_IMAGE_EXTENSIONS']


def get_download_file_path(filename:str, folder:str = 'export')->str:
    """获取导出文件地址"""
    file_folder = current_app.config['H3BLOG_UPLOAD_PATH']
    file_folder = os.path.join(file_folder, folder)
    if not os.path.exists(file_folder):
        os.makedirs(file_folder)
    return (os.path.join(file_folder, filename), os.path.join(folder, filename))

def time_now_name():
    """当前时间名称"""
    return datetime.now().strftime('%Y%m%d%H%M%S')

def upload(form_name:str, folder:str = '', rename=True, upload_type='') -> str:
    file = request.files.get(form_name)
    print(file.filename)
    if not allowed_file(file.filename):
        from .ajax_result import R
        abort(R.error(msg='不支持的格式'))
    else:
        url_path = ''
        upload_type = upload_type if upload_type else current_app.config.get('H3BLOG_UPLOAD_TYPE')
        filename = file.filename
        if rename:
            ex=os.path.splitext(file.filename)[1]
            # filename=datetime.now().strftime('%Y%m%d%H%M%S')+ex
            filename= str(uuid.uuid1())+ex
        url_fileanme = filename
        # filename= secure_filename(file.filename)
        if upload_type is None or upload_type == '' or upload_type == 'local':
            file_folder = current_app.config['H3BLOG_UPLOAD_PATH']
            if folder != '':
                file_folder = os.path.join(file_folder, folder)
                if not os.path.exists(file_folder):
                    os.makedirs(file_folder)
                url_fileanme = folder + '/' + filename
            file.save(os.path.join(file_folder,filename))
            url_path = url_for('admin.uploaded_file',filename= url_fileanme)
        elif upload_type == 'aliyun-oss':
            auth = oss2.Auth(current_app.config['ALIYUN_ACCESSKEY_ID'], current_app.config['ALIYUN_ACCESSKEY_SECRET'])
            bucket = oss2.Bucket(auth, current_app.config['ALIYUN_STATIC_ENDPOINT'], current_app.config['ALIYUN_STATIC_BUCKET_NAME'])
            f_path = 'static/{}{}'.format(folder + '/' if folder != '' else '',filename)
            bucket.put_object(f_path, file)
            url_path = current_app.config['ALIYUN_BUCKET_DOMAIN'] + f_path
            pass
        elif upload_type == 'qiniu':
            qiniu_cdn_url = current_app.config.get('QINIU_CDN_URL')
            url_path = qiniu_cdn_url + upload_file_qiniu(file.read(),filename)
        return url_path

def baidu_push_urls(domain,urls):
    """
    主动推送给百度
    """
    headers = {'Content-Type':'text/plain'}
    url = 'http://data.zz.baidu.com/urls?site={}&token={}'. \
        format(domain,current_app.config.get('BAIDU_PUSH_TOKEN'))
    try:
        ret = requests.post(url, headers = headers, data = urls, timeout = 3).text
        return json.loads(ret)
    except Exception as e :
        logging.error(e)
        return {'success':0,'msg':'超时错误'}

def strip_tags(string, allowed_tags=''):
    """
    去除html标签
    """
    if allowed_tags != '':
        # Get a list of all allowed tag names.
        allowed_tags = allowed_tags.split(',')
        allowed_tags_pattern = ['</?'+allowed_tag+'[^>]*>' for allowed_tag in allowed_tags]
        all_tags = re.findall(r'<[^>]+>', string, re.I)
        not_allowed_tags = []
        tmp = 0
        for tag in all_tags:
            for pattern in allowed_tags_pattern:
                rs = re.match(pattern,tag)
                if rs:
                    tmp += 1
                else:
                    tmp += 0
            if not tmp:
                not_allowed_tags.append(tag)
            tmp = 0
        for not_allowed_tag in not_allowed_tags:
            string = re.sub(re.escape(not_allowed_tag), '',string)
        print(not_allowed_tags)
    else:
        # If no allowed tags, remove all.
        string = re.sub(r'<[^>]*?>', '', string)
  
    return string

def gen_invit_code(count,long):
    '''
    生成邀请码
    count 数量
    long 长度
    '''
    import string, random
    r = []
    base_string = string.digits+string.ascii_letters
    for i in range(count):
        card_code = ''
        for j in range(long):
            card_code += random.choice(base_string)
        r.append(card_code)
    return r


def get_bing_img_url(format='js',idx=0):
    '''
    获取bing每日壁纸url
    '''
    url = 'https://cn.bing.com/HPImageArchive.aspx?format={}&idx={}&n=1'.format(format,idx)
    resp = requests.get(url,timeout=5).text
    data = json.loads(resp)
    return 'https://cn.bing.com{}'.format(data['images'][0]['url'])



def get_short_id() -> str:
    array = [ "0", "1", "2", "3", "4", "5","6", "7", "8", "9",
          "a", "b", "c", "d", "e", "f","g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s","t", "u", "v", "w", "x", "y", "z",
          "A", "B", "C", "D", "E", "F", "G", "H", "I","J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V","W", "X", "Y", "Z"
          ] 
    id = str(uuid.uuid4()).replace("-", '') # 注意这里需要用uuid4
    buffer = []
    for i in range(0, 8):
        start = i *  4
        end = i * 4 + 4
        val = int(id[start:end], 16)
        buffer.append(array[val % 62]) 
    return "".join(buffer)


def gen_order_sn()-> str:
    """
    订单号，随机生成
    规则：当前时间+userid+随机数
    """
    random_ins = random.Random()
    userid = current_user.id if current_user and current_user.id else ''
    return f"{time.strftime('%Y%m%d%H%M%S')}{userid}{random_ins.randint(10,99)}"

class CustomHtmlFormatter(HtmlFormatter):
    def __init__(self, lang_str='', **options):
        super().__init__(**options)
        # lang_str has the value {lang_prefix}{lang}
        # specified by the CodeHilite's options
        self.lang_str = lang_str

    def _wrap_code(self, source):
        yield 0, f'<code class="{self.lang_str}">'
        yield from source
        yield 0, '</code>'

def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)



def strdecode(text):
    if not isinstance(text, str):
        try:
            text = text.decode('utf-8')
        except UnicodeDecodeError:
            text = text.decode('gbk', 'ignore')
        return text
    return text


def open_url(url):
    header = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.2; rv:16.0) Gecko/20100101 Firefox/16.0',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Connection':'keep-alive'
    }
    
    # request = urllib.request(url, headers=header)
    # request.add_header('Accept-encoding', 'gzip')
    # response = urllib.urlopen(request)
    # html = response.read()
    # html = check_gzip(response, html)
    html = requests.get(url, headers = header).text
    return html

def full_url(url, src):
    src_parse = parse.urlparse(src)
    if not src_parse.netloc and not src_parse.scheme:
        if not src.startswith("/"):
            end_index = url.rfind("/")
            url = url[:end_index]
            src = u"{0}/{1}".format(url, src)
        else:
            url = parse.urlparse(url)
            src = u"{0}://{1}{2}".format(url.scheme, url.netloc, src)
    elif not src_parse.scheme:
        url = parse.urlparse(url)
        src = u"{0}:{1}".format(url.scheme, src)
    return src

def download_file(url, filename):
    url_path = ''
    try:
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 6.2; rv:16.0) Gecko/20100101 Firefox/16.0',
            'Connection':'keep-alive'
        }
        req = requests.get(url, headers=headers ,stream = True, timeout = 3)
    except:
        return False
    if req.status_code == 200:
        upload_type = current_app.config.get('H3BLOG_UPLOAD_TYPE')
        if upload_type is None or upload_type == '' or upload_type == 'local':
            upload_path = pathlib.Path(current_app.config['H3BLOG_UPLOAD_PATH'])
            upload_file_path = upload_path.joinpath(filename)
            with open(upload_file_path,mode='wb') as f:
                f.write(req.content)
            url_path = url_for('admin.uploaded_file',filename=filename)
        elif upload_type == 'qiniu':
            try:
                qiniu_cdn_url = current_app.config.get('QINIU_CDN_URL')
                req.raw.decode_content = True
                url_path = qiniu_cdn_url + upload_file_qiniu(req.raw,filename)
            except Exception as e:
                print(e)
                return ''
    return url_path

def download_html_image(url, html, path):
    """ 下载html中的图片 """
    soup = BeautifulSoup(html, "html.parser")
    imgs = soup.select("img")
    for img in imgs:
        if not img.has_attr("src"):
            continue
        src = img['src'] if not url else full_url(url, img["src"])
        _, ext = os.path.splitext(src)
        filename=datetime.now().strftime('%Y%m%d%H%M%S')+ext
        img_new_url = download_file(src, filename)
        if img_new_url != '':
            img['src'] = img_new_url
        time.sleep(1.5)
    return str(soup)


def html_remove_all_a(html)-> str:
    """去掉html中所有的a连接"""
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all('a'):
        if a.string:
            a.replace_with(a.string)
    return str(soup)

def html2markdown(html, url, download, path):
    html = html_remove_all_a(html)
    if not download:
        h = HTML2Text(baseurl = url, bodywidth = 0)
    else:
        html = download_html_image(url, html, path)
        h = HTML2Text(bodywidth = 0)
    md = h.handle(html)
    return md


if __name__ == "__main__":
    # codes = gen_invit_code(1000,15)
    # print(codes)
    ip_city = '未知'
    geoip2_path = 'D:\tools\GeoLite2-City_20211019\GeoLite2-City.mmdb'
    with geoip2.database.Reader('D:\\tools\\GeoLite2-City_20211019\\GeoLite2-City.mmdb') as reader:
        response = reader.city('110.249.252.222')
        country = response.country.names.get('zh-CN',response.country.names.get('en'))
        province = response.subdivisions.most_specific.names['zh-CN']
        province = response.subdivisions.most_specific.names.get('zh-CN', response.subdivisions.most_specific.names.get('en'))
        city = response.city.names.get('zh-CN', response.city.names.get('en'))
        ip_city = '{} {} {}'.format(country,province,city)
    print(ip_city)
