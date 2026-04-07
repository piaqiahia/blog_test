from flask import current_app
from wechatpayv3 import WeChatPay,WeChatPayType

def pay_config(pay_type:str = 'wx_pay'):
    if pay_type in ('ali_pay','alipay', 'ali-pay'):
        return {
            'pay_type': 'ali_pay', # 必填 区分支付类型
            'app_id': current_app.config.get('ALIPAY_APPID',''), #必填 应用id
            'private_key': current_app.config.get('ALIPAY_PRIVATE_KEY', ''), #必填 私钥
            'public_key': current_app.config.get('ALIPAY_PUBLIC_KEY', ''),#必填 公钥
            'notify_url': current_app.config.get('ALIPAY_NOTIFY_URL',''),# 异步回调地址
            'sign_type': current_app.config.get('ALIPAY_SIGNTYPE', 'RSA2'),  # 签名算法 RSA 或者 RSA2
            'debug': current_app.config.get('ALIPAY_DEBUG',False), # 是否是沙箱模式
        }

    return {
        'pay_type': 'wx_pay', # 必填 区分支付类型
        'app_id': current_app.config.get('WECHAT_APPID'),  # 必填,应用id
        'app_secret': current_app.config.get('WECHAT_APP_SECRET',''), # 应用密钥
        'mch_key': current_app.config.get('WECHAT_MCH_KEY',''),  # 必填,商户平台密钥
        'mch_id': current_app.config.get('WECHAT_MCH_ID', ''),  # 必填,微信支付分配的商户号
        'notify_url': current_app.config.get('WECHAT_NOTIFY_URL',''),# 异步回调地址
        'api_cert_path': current_app.config.get('WECHAT_API_CERT_PATH',''), # API证书
        'api_key_path': current_app.config.get('WECHAT_API_KEY_PATH', '') # API证书 key
    }


def get_wechatpay() -> WeChatPay:
    return WeChatPay(
        wechatpay_type=WeChatPayType.NATIVE,
        mchid=current_app.config.get('WECHAT_MCH_ID', ''),
        private_key=current_app.config.get('WECHAT_API_KEY', ''),
        cert_serial_no=current_app.config.get('WECHAT_CERT_SERIAL_NO', ''),
        apiv3_key=current_app.config.get('WECHAT_APIV3_KEY'),
        appid=current_app.config.get('WECHAT_APPID'),
        notify_url=current_app.config.get('WECHAT_NOTIFY_URL'),
        cert_dir=current_app.config.get('WECHAT_CERT_DIR'),
        logger=current_app.logger,
        partner_mode=current_app.config.get('WECHAT_PARTNER_MODE'),
        proxy=None)