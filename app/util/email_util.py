import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from flask import current_app

def send_yzm(receiver:str,yzm:str,smtp_server=None, smtp_user=None, smtp_pwd_auth=None,smtp_sender=None):
    """发送验证码"""

    smtp_server = smtp_server or current_app.config.get('MAIL_SERVER') # 服务地址
    smtp_user = smtp_user or current_app.config.get('MAIL_USERNAME') # 用户名
    smtp_pwd_auth = smtp_pwd_auth or current_app.config.get('MAIL_PASSWORD') # 密码/授权码
    smtp_sender = smtp_sender or current_app.config.get('MAIL_DEFAULT_SENDER', smtp_user) # 发送人

    
    msgRoot = MIMEMultipart('related')
    msgRoot['From'] = smtp_sender
    msgRoot['To'] =  receiver
    subject = '邮件验证码'
    msgRoot['Subject'] = Header(subject, 'utf-8')
    
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)
    
    
    mail_msg = """
    <p></p>
    <p>该邮件由<a href='https://www.h3blog.com'>何三笔记</a>发送，如下为网站验证码,请尽快验证，以免失效！</p>
    <p>验证码：<b>{}</b></p>
    <p></p>
    """.format(yzm)
    msgAlternative.attach(MIMEText(mail_msg, 'html', 'utf-8'))
    
    try:
        smtpObj = smtplib.SMTP_SSL('smtp.163.com')
        smtpObj.login(smtp_user, smtp_pwd_auth)
        smtpObj.sendmail(smtp_sender, receiver, msgRoot.as_string())
        print ("邮件发送成功")
    except smtplib.SMTPException as e:
        print(e)
        print ("Error: 无法发送邮件")
        raise(e)

    pass

if __name__ == '__main__':
    send_yzm('466867714@qq.com','abc123')