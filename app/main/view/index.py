from datetime import datetime, timedelta
import json
from flask import render_template, current_app, redirect,g, request,abort
from flask.helpers import url_for
from flask_login import current_user, login_required
from app.ext import sitemap
from app.model.common import PayLog, User
from app.model import VipPrice
from app.util.ajax_result import R
from app.util.ali_face_pay import AliFacePay
from app.util.common import get_bing_img_url

from .. import main as main_bp
from app.util import build_template_path
from app.ext import db,csrf
from app.model import Article,Category,Tag
from sqlalchemy import or_

def build_template_path(tpl: str) -> str:
    """ 获取模板路径 """
    return '{}/{}'.format(current_app.config['H3BLOG_TEMPLATE'], tpl)


@main_bp.before_request
def before_request():
    if request.endpoint == 'main.static':
    # if '/css/' in request.path or '/js/' in request.path or '/img/' in request.path:
        return

@main_bp.route('/favicon.ico')
def favicon():
    return main_bp.send_static_file('img/favicon.ico')

@main_bp.route('/', methods=['GET'])
def index():
    return render_template(build_template_path('index.html'))

@main_bp.route('/category/<c>/', methods=['GET', 'POST'])
def category(c):
    """
    文章分类
    """
    cty = Category.query.filter_by(name=c).first()
    if cty is None :
        return abort(404)
    tpl_name = cty.tpl_list
    if cty.tpl_mold == 'single_page':
        tpl_name = cty.tpl_page
    return render_template(build_template_path(tpl_name), category=cty)

@main_bp.route('/article/<name>/', methods=['GET', 'POST'])
def article(name):
    article = Article.query.filter(Article.name==name,Article.deleted==0).first()
    if article is None:
        abort(404)
    if article.state != 1:
        if request.args.get('preview','no') == 'no':
            abort(404)
    else:
        article.vc = article.vc + 1
    db.session.commit()
    category = article.category
    tpl_name = category.tpl_page
    return render_template(build_template_path(tpl_name), article=article, category=category)



@main_bp.route('/search', methods=['GET', 'POST'])
def search():
    kw = request.values.get('q','')
    page = request.args.get('page', 1, type=int)
    pagelist = Article.query.filter(or_(Article.content_html.like('%%%s%%' % kw), Article.title.like('%%%s%%' % kw)), Article.state == 1, Article.deleted == 0).order_by(Article.publish_time.desc()). \
        paginate(page=page, per_page=current_app.config['H3BLOG_POST_PER_PAGE'], error_out=False)
    return render_template(build_template_path('search_result.html'), pagelist=pagelist)


@main_bp.route('/tag/<t>/', methods=['GET'])
def tag(t):
    page = request.args.get('page', 1, type=int)
    tag = Tag.query.filter(Tag.code == t).first()
    if tag is None:
        return abort(404)
    articles = tag.articles.filter(Article.state == 1, Article.deleted==0).\
        order_by(Article.sn.desc(),Article.publish_time.desc()). \
        paginate(page=page, per_page=current_app.config['H3BLOG_POST_PER_PAGE'], error_out=False)
    return render_template(build_template_path('tag.html'), articles=articles, tag=tag,orderby='time')


@main_bp.route('/subject', methods=['GET'])
def subject():
    categorys = Category.query.filter(Category.deleted == 0, Category.visible == 1, Category.parent_id == None).order_by(Category.order_num.asc())
    return render_template(build_template_path('subject.html'), categorys = categorys)

@sitemap.register_generator
def site_map():
    """
    sitemap生成
    """
    articles = Article.query.filter(Article.state == 1, Article.deleted == 0).all()
    categories = Category.query.all()
    import datetime
    now = datetime.datetime.now()
    #首页
    yield 'main.index',{},now.strftime('%Y-%m-%dT%H:%M:%S'),'always',1.0

    #分类
    for category in categories:
        yield 'main.category',{'c':category.name},now.strftime('%Y-%m-%dT%H:%M:%S'),'always',0.9

    #文章
    for a in articles:
        #posts.post是文章视图的endpoint,后面是其参数
        yield 'main.article',{'name':a.name}


@main_bp.route('/robots.txt')
def robots():
    return current_app.config['H3BLOG_ROBOTS']

@main_bp.post('/article/pay/')
@login_required
def vip_pay():
    """
    文章付费
    """
    pay_amount = request.form.get("price",type=float)
    print(pay_amount)
    article_id = request.form.get("article_id", type=int)
    article = Article.query.get(article_id)
    out_trade_no = AliFacePay.gen_trade_no(pre_string='atc' +  str(current_user.id))
    log = PayLog()
    log.pay_type = '支付宝当面付'
    log.action_type = '文章付费'
    log.order_no = out_trade_no
    log.subject = article.title
    log.total_fee = pay_amount
    log.ref_id = article_id
    log.state = 0

    db.session.add(log)
    db.session.commit()
    sendbox_debug = current_app.config.get('ALIPAY_SENDBOX_DEBUG','FALSE').upper() == 'TRUE'
    pay = AliFacePay(
        app_id=current_app.config.get('ALIPAY_APPID'),
        app_private_key= current_app.config.get('ALIPAY_PRIVATE_KEY'),
        alipay_public_key= current_app.config.get('ALIPAY_PUBLIC_KEY'),
        notify_url= current_app.config.get('ALIPAY_NOTIFY_URL'),
        sandbox_debug=sendbox_debug,
    )
    qrcode_url = pay.precreate(out_trade_no, pay_amount,'文章付费')
    result = {
        'out_trade_no': out_trade_no,
        'qrcode_url': qrcode_url,
    }
    return R.success(result)

@main_bp.post('/is_pay/')
@login_required
def is_pay():
    """
    查看是否支付成功
    """
    order_no = request.form.get('order_no','')
    log = PayLog.query.filter(PayLog.order_no == order_no).first()
    if log and log.state == 1:
        return R.success(True,msg='支付成功')
    return R.error(False,msg='未支付')

@main_bp.route('/alipay_nofity', methods=['POST'])
@csrf.exempt
def alipay_nofity():
    data = request.form.to_dict()
    print(data)
    sendbox_debug = current_app.config.get('ALIPAY_SENDBOX_DEBUG','FALSE').upper() == 'TRUE'
    pay = AliFacePay(
        app_id=current_app.config.get('ALIPAY_APPID'),
        app_private_key= current_app.config.get('ALIPAY_PRIVATE_KEY'),
        alipay_public_key= current_app.config.get('ALIPAY_PUBLIC_KEY'),
        notify_url= current_app.config.get('ALIPAY_NOTIFY_URL'),
        sandbox_debug=sendbox_debug,
    )
    if pay.verify_params_sign(data):
        trade_status = data['trade_status']
        if trade_status == 'TRADE_SUCCESS':
            order_no = data['out_trade_no']
            log = PayLog.query.filter(PayLog.order_no == order_no).first()
            if log:
                log.state = 1
                log.return_code = trade_status
                log.return_data = json.dumps(data)
                log.return_time = datetime.now()
                log.trade_no = data['trade_no']

                if log.action_type == '开通VIP':
                    vipprice = VipPrice.query.get(log.ref_id)
                    days = int(vipprice.days)
                    user = User.query.get(log.create_by)
                    if user.user_type == 'vip':
                        if user.vip_deadline > datetime.now():
                            user.vip_deadline = user.vip_deadline + timedelta(days=days)
                        else:
                            user.vip_deadline = datetime.now() + timedelta(days=days)
                    else:
                        user.user_type = 'vip' 
                        current_date = datetime.now()
                        next_year = current_date + timedelta(days=days)
                        user.vip_deadline =  next_year
            pass
        return 'success'

    print('验证签名失败')
    return '404'




@main_bp.route('/bing_bg')
def bing_bg():
    '''
    获取背景地址
    '''
    return redirect(get_bing_img_url())