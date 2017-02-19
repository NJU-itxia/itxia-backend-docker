# coding:utf-8
from flask import request, jsonify, g, current_app
from app.model import Client, Manager, Form
from .. import db, redis
import uuid

from . import api
from .decorators import login_check, admin_check, superadmin_check, allow_cross_domain

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

@api.route('/forms', methods=['GET'])
@allow_cross_domain
def get_forms():
    forms = Form.query.all()
    return jsonify({'code': 1, 'forms': [form.to_json() for form in forms]})

@api.route('/managers', methods=['GET'])
@allow_cross_domain
def get_all_managers():
    managers = Manager.query.all()
    return jsonify({'code': 1, 'managers': [manager.to_json() for manager in managers]})
    
@api.route('/forms/<int:id>', methods=['GET'])
@allow_cross_domain
@login_check
def get_form(id):
    form = Form.query.get_or_404(id)
    if not g.current_manager and g.current_client.id != form.post_client_id: 
        return jsonify({'code': 0, 'message': 'No Permission'}), 401
    return jsonify({'code': 1, 'forms': form.to_json()})
    

@api.route('/forms/<int:id>', methods=['PUT'])
@allow_cross_domain
@login_check
def edit_form(id):
    form = Form.query.get_or_404(id)
    if not g.current_manager and g.current_client.id != form.post_client_id: 
        return jsonify({'code': 0, 'message': 'No Permission'})
    edit_map = request.get_json().get('edit')
    for key in edit_map:
        if key == 'managing':
            if not g.current_manager:
                return jsonify({'code': 0, 'message': 'You are not itxia'}), 401
            elif not form.handle_manager or g.current_manager == form.handle_manager:
                form.state = edit_map['managing']
                form.handle_manager = g.current_manager
            else:
                return jsonify({'code': 0, 'message': 'A itxia had been working on the form'}), 403
        else:
            try:
                form.__dict__[key] = edit_map[key]
            except Exception as e:
                print e
                return jsonify({'code': 0, 'message': 'Requst Format Wrong'}), 403
        
    db.session.add(form)
    db.session.commit()
    return jsonify({'code': 1, 'message': 'Modified Successfully'})
    
@api.route('/admin/add_manager', methods=['POST'])
@allow_cross_domain
@login_check
@admin_check
def add_manager():
    username = request.get_json().get('username') or ''
    password = request.get_json().get('password') or ''
    email = request.get_json().get('email') or ''
    campus = request.get_json().get('campus') or ''
    
    new_manager = Manager(username=username, password=password, email=email, campus=campus)
    db.session.add(new_manager)
    print username, password
    try:
        db.session.commit()
    except Exception as e:
        print e
        db.session.rollback()
        return jsonify({'code': 0, 'message': 'Nickname had been registered'}), 403
    
    return jsonify({'code': 1, 'message': 'Register Successfully'})

@api.route('/admin/uplevel_manager', methods=['PUT'])
@allow_cross_domain
@login_check
@admin_check
def uplevel_manager():
    username = request.get_json().get('username')
    manager = Manager.query.filter_by(username=username).first()
    if manager:
        manager.role = 'admin'
    else:
        return jsonify({'code': 0, 'message': 'No such manager'})
    
    return jsonify({'code': 1, 'message': 'Uplevel Successfully'}) 

@api.route('/superadmin/modify_manager', methods=['PUT'])
@allow_cross_domain
@login_check
@superadmin_check
def modify_manager():
    username = request.get_json().get('username') or ''
    manager = Manager.query.filter_by(username=username).first()
    if manager:
        edit_map = request.get_json().get('edit')
        for key in edit_map:
            try:
                form.__dict__[key] = edit_map[key]
            except Exception as e:
                print e
                return jsonify({'code': 0, 'message': 'Requst Format Wrong'}), 403
    else:
        return jsonify({'code': 0, 'message': 'No such manager'})
    
    return jsonify({'code': 1, 'message': 'Modified Successfully'})    

   
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

