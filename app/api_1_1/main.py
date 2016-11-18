# coding:utf-8
from flask import request, jsonify, g, current_app
from app.model import Client, Server, Form
from .. import db, redis
import uuid

from . import api
from .decorators import login_check

@api.before_request
def before_request():
    token = request.headers.get('token')
    role = request.headers.get('role')
    print request.endpoint
    if role == 'server':
        username = redis.get('token:%s' % token)
        if username:
            g.current_server = Server.query.filter_by(username=username).first()
            g.token = token
    else:
        phone_number = redis.get('token:%s' % token)
        if phone_number:
            g.current_client = Client.query.filter_by(phone_number=phone_number).first()
            g.token = token
    return
    
    
@api.teardown_request
def handle_teardown_request(exception):
    db.session.remove()

@api.route('/')
def index():
    return 'hello'

@api.route('/forms', methods=['GET'])
def get_all_forms():
    forms = Form.query.all()
    return jsonify({'code': 1, 'forms': [form.to_json() for form in forms]})
        
@api.route('/get-multi-qiniu-token')
@login_check
def get_multi_qiniu_token():
    count = int(request.args.get('count'))

    if not 0 < count < 10:
        return jsonify({'code': 0, 'message': '一次只能获取1到9个'})

    key_token_s = []
    for i in range(count):
        key = uuid.uuid1()
        token = current_app.q.upload_token(current_app.bucket_name, key, 3600)
        key_token_s.append({'key': key, 'token': token})
    return jsonify({'code': 1, 'key_token_s': key_token_s})
 
    
@api.route('/get-qiniu-token')
def get_qiniu_token():
    key = uuid.uuid4()
    token = current_app.q.upload_token(current_app.bucket_name, key, 3600)
    return jsonify({'code': 1, 'key': key, 'token': token})
