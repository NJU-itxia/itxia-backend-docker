# coding:utf-8
from flask import request, jsonify, g, url_for, current_app, json
from app.model import Client, Form
from .. import db, redis
import hashlib
import time
import random
from app.util import message_validate
from .decorators import login_check
from sqlalchemy import func
from . import api


@api.route('/client/login', methods=['POST'])
def login():
    phone_number = request.get_json().get('phone_number')
    encryption_str = request.get_json().get('encryption_str')
    random_str = request.get_json().get('random_str')
    time_stamp = request.get_json().get('time_stamp')
    client = Client.query.filter_by(phone_number=phone_number).first()

    if not client:
        return jsonify({'code': 0, 'message': '没有此用户'})

    password_in_sql = client.password

    s = hashlib.sha256()
    s.update(password_in_sql)
    s.update(random_str)
    s.update(time_stamp)
    server_encryption_str = s.hexdigest()

    if server_encryption_str != encryption_str:
        return jsonify({'code': 0, 'message': '密码错误'})

    m = hashlib.md5()
    m.update(phone_number)
    m.update(client.password)
    m.update(str(int(time.time())))
    token = m.hexdigest()

    pipeline = redis.pipeline()
    pipeline.hmset('client:%s' % client.phone_number, {'token': token, 'email': client.email, 'app_online': 1})
    pipeline.set('token:%s' % token, client.phone_number)
    pipeline.expire('token:%s' % token, 3600*24*30)
    pipeline.execute()

    return jsonify({'code': 1, 'message': '成功登录', 'email': client.email, 'token': token})


@api.route('/client')
@login_check
def client():
    client = g.current_client
    email = redis.hget('client:%s' % client.phone_number, 'email')
    return jsonify({'code': 1, 'email': email, 'phone_number': client.phone_number})


@api.route('/client/logout')
@login_check
def logout():
    client = g.current_client

    pipeline = redis.pipeline()
    pipeline.delete('token:%s' % g.token)
    pipeline.hmset('client:%s' % client.phone_number, {'app_online': 0})
    pipeline.execute()
    return jsonify({'code': 1, 'message': '成功注销'})


@api.route('/client/set-head-picture', methods=['POST'])
@login_check
def set_head_picture():
    avatar_picture = request.get_json().get('avatar_picture')
    client = g.current_client
    client.avatar_picture = avatar_picture
    try:
        db.session.commit()
    except Exception as e:
        print e
        db.session.rollback()
        return jsonify({'code': 0, 'message': '未能成功上传'})
    redis.hset('client:%s' % client.phone_number, 'avatar_picture', avatar_picture)
    return jsonify({'code': 1, 'message': '成功上传'})
    

@api.route('/client/register-step-1', methods=['POST'])
def register_step_1():
    """
    接受phone_number,发送短信
    """
    phone_number = request.get_json().get('phone_number')
    client = Client.query.filter_by(phone_number=phone_number).first()

    if client:
        return jsonify({'code': 0, 'message': '该用户已经存在,注册失败'})
    validate_number = str(random.randint(100000, 1000000))
    result, err_message = message_validate(phone_number, validate_number)

    if not result:
        return jsonify({'code': 0, 'message': err_message})

    pipeline = redis.pipeline()
    pipeline.set('validate:%s' % phone_number, validate_number)
    pipeline.expire('validate:%s' % phone_number, 60)
    pipeline.execute()

    return jsonify({'code': 1, 'message': '发送成功'})


@api.route('/client/register-step-2', methods=['POST'])
def register_step_2():
    """
    验证短信接口
    """
    phone_number = request.get_json().get('phone_number')
    validate_number = request.get_json().get('validate_number')
    validate_number_in_redis = redis.get('validate:%s' % phone_number)

    if validate_number != validate_number_in_redis:
        return jsonify({'code': 0, 'message': '验证没有通过'})

    pipe_line = redis.pipeline()
    pipe_line.set('is_validate:%s' % phone_number, '1')
    pipe_line.expire('is_validate:%s' % phone_number, 120)
    pipe_line.execute()

    return jsonify({'code': 1, 'message': '短信验证通过'})


@api.route('/client/register-step-3', methods=['POST'])
def register_step_3():
    """
    密码提交
    """
    phone_number = request.get_json().get('phone_number')
    password = request.get_json().get('password')
    password_confirm = request.get_json().get('password_confirm')

    if len(password) < 7 or len(password) > 30:
        # 这边可以自己拓展条件
        return jsonify({'code': 0, 'message': '密码长度不符合要求'})

    if password != password_confirm:
        return jsonify({'code': 0, 'message': '密码和密码确认不一致'})

    is_validate = redis.get('is_validate:%s' % phone_number)

    if is_validate != '1':
        return jsonify({'code': 0, 'message': '验证码没有通过'})

    pipeline = redis.pipeline()
    pipeline.hset('register:%s' % phone_number, 'password', password)
    pipeline.expire('register:%s' % phone_number, 120)
    pipeline.execute()

    return jsonify({'code': 1, 'message': '提交密码成功'})


@api.route('/client/register-step-4', methods=['POST'])
def register_step_4():
    """
    基本资料提交
    """
    phone_number = request.get_json().get('phone_number')
    email = request.get_json().get('email')

    is_validate = redis.get('is_validate:%s' % phone_number)

    if is_validate != '1':
        return jsonify({'code': 0, 'message': '验证码没有通过'})

    password = redis.hget('register:%s' % phone_number, 'password')

    new_client = Client(phone_number=phone_number, password=password, email=email)
    db.session.add(new_client)

    try:
        db.session.commit()
    except Exception as e:
        print e
        db.session.rollback()
        return jsonify({'code': 0, 'message': '注册失败, 邮箱已注册'})
    finally:
        redis.delete('is_validate:%s' % phone_number)
        redis.delete('register:%s' % phone_number)

    return jsonify({'code': 1, 'message': '注册成功'})
    

@api.route('/client/forms/post', methods=['POST'])
@login_check
def form_post():
    client = g.current_client
    campus = request.get_json().get('campus')
    machine_model = request.get_json().get('machine_model')
    OS = request.get_json().get('OS')
    description = request.get_json().get('description')
    pictures = request.get_json().get('pictures')
    
    new_form = Form(campus=campus,
                        machine_model=machine_model,
                        OS=OS,
                        description=description)
    new_form.pictures = pictures
    client.post_forms = [new_form]
    db.session.add(client)
    try:
        db.session.commit()
    except Exception as e:
        print e
        db.session.rollback()
        return jsonify({'code': 0, 'message': '提交不成功'})
    return jsonify({'code': 1, 'message': '提交成功'})
    

@api.route('/client/forms', methods=['GET'])
@login_check
def get_forms():
    client = g.current_client
    page = request.args.get('page', 1, type=int)
    pagination = Form.query.filter_by(post_client_id=client.id).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    forms = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_forms', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_forms', page=page+1, _external=True)
        
    status_tuple = db.session.query(Form.status, func.count(Form.status)).filter(Form.post_client_id == client.id).group_by(Form.status).all()
    status_json = json.dumps(dict(status_tuple))
    return jsonify({
        'code': 1,
        'forms': [form.to_json() for form in forms],
        'prev': prev,
        'next': next,
        'count': status_json
        })
        

@api.route('/client/forms/<int:id>', methods=['GET'])
@login_check
def get_form(id):
    form = Form.query.get_or_404(id)
    if g.current_client.id != form.post_client_id: 
        return jsonify({'code': 0, 'message': '沒有权限'})
    return jsonify({'code': 1, 'forms': form.to_json()})
    

@api.route('/client/forms/<int:id>/edit', methods=['PUT'])
@login_check
def edit_form(id):
    form = Form.query.get_or_404(id)
    if g.current_client.id != form.post_client_id: 
        return jsonify({'code': 0, 'message': '沒有权限'})
    form.campus = request.get_json().get('campus')
    form.machine_model = request.get_json().get('machine_model')
    form.OS = request.get_json().get('OS')
    form.description = request.get_json().get('description')
    form.pictures = request.get_json().get('pictures')
    db.session.add(form)
    db.session.commit(form)
    return jsonify({'code': 1, 'message': '修改成功'})    
