# coding:utf-8
from flask import request, jsonify, g, current_app
from app.model import Client, Manager, Form
from .. import db, redis
import uuid

from . import api
from .decorators import login_check

@api.before_request
def before_request():
    token = request.headers.get('token')
    role = request.headers.get('role')
    g.current_manager = None
    g.current_client = None
    print request.endpoint
    if role == 'manager':
        username = redis.get('token:%s' % token)
        if username:
            g.current_manager = Manager.query.filter_by(username=username).first()
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
    
@api.route('/forms/<int:id>', methods=['GET'])
@login_check
def get_form(id):
    form = Form.query.get_or_404(id)
    if not g.current_manager and g.current_client.id != form.post_client_id: 
        return jsonify({'code': 0, 'message': '沒有权限'})
    return jsonify({'code': 1, 'forms': form.to_json()})
    

@api.route('/forms/<int:id>', methods=['PUT'])
@login_check
def edit_form(id):
    form = Form.query.get_or_404(id)
    if not g.current_manager and g.current_client.id != form.post_client_id: 
        return jsonify({'code': 0, 'message': '沒有权限'})
    edit_map = request.get_json().get('edit')
    for key in edit_map:
        if key != 'managing':
            form.__dict__[key] = edit_map[key]
    if g.current_manager:
        form.status = request.get_json().get('managing')
    db.session.add(form)
    db.session.commit()
    return jsonify({'code': 1, 'message': '修改成功'})
    
@api.route('/admin/add_manager', methods=['POST'])
#@login_check
def add_manager():
    username = request.get_json().get('username')
    password = request.get_json().get('password')
    email = request.get_json().get('email')
    campus = request.get_json().get('campus')
    
    new_manager = Manager(username=username, password=password, email=email, campus=campus)
    db.session.add(new_manager)
    print username, password
    try:
        db.session.commit()
    except Exception as e:
        print e
        db.session.rollback()
        return jsonify({'code': 0, 'message': '昵称已注册'})
    
    return jsonify({'code': 1, 'message': '注册成功'})
    
    
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
