# coding:utf-8
from flask import request, jsonify, g, url_for, current_app, json
from app.model import Client, Manager, Form
from .. import db, redis
import hashlib
import time
import random
from app.util import message_validate
from .decorators import login_check, manager_check, allow_cross_domain
from sqlalchemy import func
from . import api
    

@api.route('/managers', methods=['GET'])
@allow_cross_domain
def get_all_managers():
    managers = Manager.query.all()
    return jsonify({'code': 1, 'managers': [manager.to_json() for manager in managers]})
    
     
@api.route('/manager/login', methods=['POST'])
@allow_cross_domain
def manager_login():
    username = request.get_json().get('username') or ''
    encryption_str = request.get_json().get('encryption_str') or ''
    random_str = request.get_json().get('random_str') or ''
    time_stamp = request.get_json().get('time_stamp') or ''
    manager = Manager.query.filter_by(username=username).first() 

    if not username:
        return jsonify({'code': 0, 'message': 'No Manager Exist'}), 401

    password_in_sql = manager.password

    s = hashlib.sha256()
    s.update(password_in_sql)
    s.update(random_str)
    s.update(time_stamp)
    server_encryption_str = s.hexdigest()

    if server_encryption_str != encryption_str:
        return jsonify({'code': 0, 'message': 'Wrong Password'}), 401

    m = hashlib.md5()
    m.update(username)
    m.update(manager.password)
    m.update(str(int(time.time())))
    token = m.hexdigest()

    pipeline = redis.pipeline()
    pipeline.hmset('manager:%s' % manager.username, {'token': token, 'email': manager.email, 'app_online': 1})
    pipeline.set('token:%s' % token, manager.username)
    pipeline.expire('token:%s' % token, 3600*24*30)
    pipeline.execute()

    return jsonify({'code': 1, 'message': 'Successful Log In', 'email': manager.email, 'token': token})
    
@api.route('/manager')
@allow_cross_domain
@login_check
@manager_check
def manager():
    manager = g.current_manager
    email = redis.hget('manager:%s' % manager.username, 'email')
    return jsonify({'code': 1, 'email': email, 'username': manager.username})


@api.route('/manager/logout')
@allow_cross_domain
@login_check
@manager_check
def manager_logout():
    manager = g.current_manager

    pipeline = redis.pipeline()
    pipeline.delete('token:%s' % g.token)
    pipeline.hmset('manager:%s' % manager.username, {'app_online': 0})
    pipeline.execute()
    return jsonify({'code': 1, 'message': 'Successful Log Out'})


@api.route('/manager/set-head-picture', methods=['POST'])
@allow_cross_domain
@login_check
@manager_check
def manager_set_head_picture():
    avatar_picture = request.get_json().get('avatar_picture')
    manager = g.current_manager
    manager.avatar_picture = avatar_picture
    try:
        db.session.commit()
    except Exception as e:
        print e
        db.session.rollback()
        return jsonify({'code': 0, 'message': '未能成功上传'})
    redis.hset('manager:%s' % manager.username, 'avatar_picture', avatar_picture)
    return jsonify({'code': 1, 'message': '成功上传'})
    
@api.route('/manager/waiting_forms', methods=['GET'])
@allow_cross_domain
@login_check
@manager_check
def get_waiting_forms():
    page = request.args.get('page', 1, type=int)
    pagination = Form.query.filter_by(status='waiting').paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    forms = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_waiting_forms', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_waiting_forms', page=page+1, _external=True)
    
    status_tuple = db.session.query(Form.status, func.count(Form.status)).group_by(Form.status).all()
    status_json = json.dumps(dict(status_tuple))
    return jsonify({
        'code': 1,
        'status': 'waiting',
        'forms': [form.to_json() for form in forms],
        'prev': prev,
        'next': next,
        'count': status_json,
        })
        
        
@api.route('/manager/working_forms', methods=['GET'])
@allow_cross_domain
@login_check
@manager_check
def get_working_forms():
    page = request.args.get('page', 1, type=int)
    pagination = Form.query.filter_by(status='working').paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    forms = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_working_forms', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_working_forms', page=page+1, _external=True)
    
    status_tuple = db.session.query(Form.status, func.count(Form.status)).group_by(Form.status).all()
    status_json = json.dumps(dict(status_tuple))
    return jsonify({
        'code': 1,
        'status': 'working',
        'forms': [form.to_json() for form in forms],
        'prev': prev,
        'next': next,
        'count': status_json,
        })
    
@api.route('/manager/done_forms', methods=['GET'])
@allow_cross_domain
@login_check
@manager_check
def get_done_forms():
    page = request.args.get('page', 1, type=int)
    pagination = Form.query.filter_by(status='done').paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    forms = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_done_forms', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_done_forms', page=page+1, _external=True)

    status_tuple = db.session.query(Form.status, func.count(Form.status)).group_by(Form.status).all()
    status_json = json.dumps(dict(status_tuple))
    return jsonify({
        'code': 1,
        'status': 'done',
        'forms': [form.to_json() for form in forms],
        'prev': prev,
        'next': next,
        'count': status_json,
        })
        
@api.route('/manager/all_forms', methods=['GET'])
@allow_cross_domain
@login_check
@manager_check
def get_all_forms():
    forms = Form.query.all()
    return jsonify({'code': 1, 'forms': [form.to_json() for form in forms]})
    

