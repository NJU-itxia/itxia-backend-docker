# coding:utf-8
from flask import request, jsonify, g, current_app
from app.model import Client, Manager, Form
from .. import db, redis
import uuid

from . import api
from .decorators import login_check, admin_check, superadmin_check, allow_cross_domain

@api.before_request
def before_request():
    token = request.headers.get('Token') 
    role = request.headers.get('Role')
    g.current_manager = None
    g.current_client = None
    print request.endpoint
    if role == 'manager':
        username = redis.get('token:%s' % token)
        if username:
            g.current_manager = Manager.query.filter_by(username=username).first()
            g.token = token
            g.role = {'manager': g.current_manager.role}
    else:
        phone_number = redis.get('token:%s' % token)
        if phone_number:
            g.current_client = Client.query.filter_by(phone_number=phone_number).first()
            g.token = token
            g.role = {'client': 'client'}
    return
    
    
@api.teardown_request
def handle_teardown_request(exception):
    db.session.remove()

@api.route('/')
@allow_cross_domain
def index():
    return 'hello'

@api.route('/get-multi-qiniu-token')
@allow_cross_domain
@login_check
def get_multi_qiniu_token():
    count = int(request.args.get('count'))

    if not 0 < count < 10:
        return jsonify({'code': 0, 'message': 'The count limits between 1 and 9'}), 403

    key_token_s = []
    for i in range(count):
        key = uuid.uuid1()
        token = current_app.q.upload_token(current_app.bucket_name, key, 3600)
        key_token_s.append({'key': key, 'token': token})
    return jsonify({'code': 1, 'key_token_s': key_token_s})
 
    
@api.route('/get-qiniu-token')
@allow_cross_domain
@login_check
def get_qiniu_token():
    key = uuid.uuid4()
    token = current_app.q.upload_token(current_app.bucket_name, key, 3600)
    return jsonify({'code': 1, 'key': key, 'token': token})

