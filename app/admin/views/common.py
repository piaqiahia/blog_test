from flask import jsonify, current_app, send_from_directory, request,abort
from flask_login import login_user
import app.util as util
from app.ext import db

from app.admin import admin
from app.util.onepay import PayOrder, Pay
from app.util.payutil import pay_config
from app.util.ajax_result import R
from app.model import PayLog
import os
from app.ext import csrf
from datetime import datetime
import json
import pathlib

@admin.route('/upload', methods=['GET', 'POST'])
def upload():
    """上传图片"""
    folder = request.values.get('folder','')
    url = util.upload('file',folder)
    return util.R.success(data=url)

@admin.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['H3BLOG_UPLOAD_PATH'], filename)

@admin.get('/download')
def download():
    fileName = request.values.get('fileName','')
    file_path = os.path.join(current_app.config['H3BLOG_UPLOAD_PATH'], fileName)
    file_handle = open(file_path, 'rb')

    name = 'download'
    ext = ''
    if fileName and len(fileName)>0:
        name = pathlib.Path(fileName).name
        ext = pathlib.Path(fileName).suffix

    mime_types = {
        '.doc'    :    ' application/msword',
        '.dot'    :    ' application/msword',
        '.docx'	 :    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.dotx'	 :    'application/vnd.openxmlformats-officedocument.wordprocessingml.template',
        '.docm'	 :    'application/vnd.ms-word.document.macroEnabled.12',
        '.dotm'	 :    'application/vnd.ms-word.template.macroEnabled.12',
        '.xls'    :    ' application/vnd.ms-excel',
        '.xlt'    :    ' application/vnd.ms-excel',
        '.xla'    :    ' application/vnd.ms-excel',
        '.xlsx'	 :    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.xltx'	 :    'application/vnd.openxmlformats-officedocument.spreadsheetml.template',
        '.xlsm'	 :    'application/vnd.ms-excel.sheet.macroEnabled.12',
        '.xltm'	 :    'application/vnd.ms-excel.template.macroEnabled.12',
        '.xlam'	 :    'application/vnd.ms-excel.addin.macroEnabled.12',
        '.xlsb'	 :    'application/vnd.ms-excel.sheet.binary.macroEnabled.12',
        '.ppt'    :    ' application/vnd.ms-powerpoint',
        '.pot'    :    ' application/vnd.ms-powerpoint',
        '.pps'    :    ' application/vnd.ms-powerpoint',
        '.ppa'    :    ' application/vnd.ms-powerpoint',
        '.pptx'	 :    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.potx'	 :    'application/vnd.openxmlformats-officedocument.presentationml.template',
        '.ppsx'	 :    'application/vnd.openxmlformats-officedocument.presentationml.slideshow',
        '.ppam'	 :    'application/vnd.ms-powerpoint.addin.macroEnabled.12',
        '.pptm'	 :    'application/vnd.ms-powerpoint.presentation.macroEnabled.12',
        '.potm'	 :    'application/vnd.ms-powerpoint.presentation.macroEnabled.12',
        '.ppsm'	 :    'application/vnd.ms-powerpoint.slideshow.macroEnabled.12',
        '.zip'    :    ' application/zip',
        '.tar'    :    ' application/x-tar',
    }
    
    mimetype = mime_types.get(ext,'')

    # windows下有问题
    # @after_this_request
    # def remove_file(response):
    #     try:
    #         os.remove(file_path)
    #         file_handle.close()
    #     except Exception as error:
    #         current_app.logger.error("Error removing or closing downloaded file handle", error)
    #     return response
    # return send_file(file_handle)

    # This *replaces* the `remove_file` + @after_this_request code above
    def stream_and_remove_file():
        yield from file_handle
        file_handle.close()
        os.remove(file_path)

    

    return current_app.response_class(
        stream_and_remove_file(),
        headers={'Content-Disposition': f'attachment; filename={name}', 'filename': f'{name}', 'Content-Type': f'{mimetype}'}
    )


@csrf.exempt
@admin.route('/pay_notify/wx', methods=['POST'])
def pay_notify_wx():
    pay = Pay(pay_config(pay_type='wx_pay'))
    # 传入对应支付方式返回的原始数据，校验成功会返回解析成json数据
    req_xml = request.data
    print('返回的数据：', req_xml)
    result = pay.parse_and_verify_result(req_xml)
    print('解析结果:', result)
    #写入数据库
    out_trade_no = result['out_trade_no']
    trade_no = result['transaction_id']
    paylog = PayLog.query.filter(PayLog.order_no == out_trade_no, PayLog.state == 0).first()
    if paylog:
        paylog.trade_no = trade_no
        paylog.state = 1
        paylog.return_code = result['result_code']
        paylog.return_data = json.dumps(result)
        paylog.return_time = datetime.now()
        db.session.add(paylog)
        #处理业务逻辑
        db.session.commit()
        return "<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>"
    return abort(500)

@csrf.exempt
@admin.route('/pay_notify/ali', methods=['POST'])
def pay_notify_ali():
    pay = Pay(pay_config(pay_type='ali_pay'))
    # 传入对应支付方式返回的原始数据，校验成功会返回解析成json数据
    data = request.form.to_dict()
    print('返回的数据：', data)
    result = pay.parse_and_verify_result(data)
    print('解析结果:', result)
    #写入数据库
    out_trade_no = result['out_trade_no']
    trade_no = result['trade_no']
    paylog = PayLog.query.filter(PayLog.order_no == out_trade_no, PayLog.state == 0).first()
    if paylog:
        paylog.trade_no = trade_no
        paylog.state = 1
        paylog.return_code = result['trade_status']
        paylog.return_data = json.dumps(result)
        paylog.return_time = datetime.now()
        db.session.add(paylog)

        #处理业务逻辑
        db.session.commit()
        return R.success()
    return abort(500)
    

