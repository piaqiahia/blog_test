import json
from flask import current_app
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

class SendMsg():
    def __init__(self, ak:str = '', secret:str = '',sign_name:str = '', template_code:str = '') -> None:
        self.ak = current_app.config['ALIYUN_ACCESSKEY_ID'] if ak == '' else ak
        self.secret = current_app.config['ALIYUN_ACCESSKEY_SECRET'] if secret == '' else secret
        self.sign_name = current_app.config['ALIYUN_SEND_MSG_SIGN_NAME'] if sign_name == '' else sign_name
        self.template_code = current_app.config['ALIYUN_SEND_MSG_TEMPLATE_CODE'] if template_code == '' else template_code
        self.client = AcsClient(self.ak, self.secret, 'cn-hangzhou')

    def send_code(self,phoneNumbers, code) -> bool:
        m = {'code': code}
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https') # https | http
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')

        request.add_query_param('PhoneNumbers', phoneNumbers)
        request.add_query_param('SignName', self.sign_name)
        request.add_query_param('TemplateCode', self.template_code)
        request.add_query_param('TemplateParam', json.dumps(m))

        response = self.client.do_action(request)
        ret = json.loads(str(response, encoding = 'utf-8'))
        if ret and ret['Code'] == 'OK':
            return True
        else:
            print(ret)
        return False


if __name__ == '__main__':
    sm = SendMsg('llskdfjkskfskdjf','ksjdkfksdjfkskdfjksdf','测试', 'SMS_218710028')
    ret = sm.send_code('13888888888', '123456')
    print(ret)