from flask import render_template, request, jsonify, current_app
from . import api
from app.util.ajax_result import R
import traceback


@api.errorhandler(Exception)
def error_500(error):
    current_app.logger.error(traceback.format_exc())
    return R.error(msg=error.__str__())

@api.errorhandler(403)
def forbidden(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    return render_template('admin/errors/403.html'), 403


@api.errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('admin/errors/404.html'), 404


@api.errorhandler(500)
def internal_server_error(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return render_template('admin/errors/500.html'), 500
