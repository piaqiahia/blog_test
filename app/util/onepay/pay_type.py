from .ali import AliPay
from .wx import WxPay

__all__ = ('ali_pay', 'wx_pay')


def ali_pay(config):
    return AliPay(config)


def wx_pay(config):
    return WxPay(config)
