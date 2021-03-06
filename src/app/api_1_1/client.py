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
def client_login():
    """
    user login
    :request:    phone number of user identity, random string, timestamp
                 and encrypted string of password adding random string and timestamo by sha256 method
                 {'phone_number': ,'random_str': ,'time_stamp': ,'encryption_str': }
    :response:   state code and message of problem information, if successful, a token
                 for further request will be appended
                 {'code': , 'message': } or {'code': , 'message': ,'token': ,}

    """
    # Check the requst format. If the body in request is nothing or is
    # not in json, the back server will return wrong.
    if not request or not request.get_json():
        return jsonify({'code': 0, 'message': 'Wrong Request Format'}), 400

    phone_number = request.get_json().get('phone_number') or ''
    encryption_str = request.get_json().get('encryption_str') or ''
    random_str = request.get_json().get('random_str') or ''
    time_stamp = request.get_json().get('time_stamp') or ''

    client = Client.query.filter_by(phone_number=phone_number).first()

    # Check the client is really exist.
    if not client:
        return jsonify({'code': 0, 'message': 'No Client Exist'})

    password_in_sql = client.password

    # Recompute the encryption string at the backen to check the password
    s = hashlib.sha256()
    s.update(password_in_sql)
    s.update(random_str)
    s.update(time_stamp)
    server_encryption_str = s.hexdigest()

    if server_encryption_str != encryption_str:
        return jsonify({'code': 0, 'message': 'Wrong Password'})

    # Compute the token to response
    m = hashlib.md5()
    m.update(phone_number)
    m.update(client.password)
    m.update(str(int(time.time())))
    token = m.hexdigest()

    # Store the client login state in redis
    pipeline = redis.pipeline()
    pipeline.hmset('client:%s' % client.phone_number, {
        'token': token, 'app_online': 1})
    pipeline.hmset('token:%s' % token, {'role': 'client', 'id': client.phone_number})
    pipeline.expire('token:%s' % token, 3600 * 24 * 30)
    pipeline.execute()

    return jsonify({
        'code': 1, 'message': 'Log in Successfully', 'token': token})


@api.route('/client')
@login_check
def get_client():
    """
    get the information of user
    :request:    in @login_check warpp function, it will check the token added in 
                 the requst header 'Token' get by api.before_request in main.py
    :response:   the information of user
    """
    client = g.current_client

    email = redis.hget('client:%s' % client.phone_number, 'email')
    return jsonify({
        'code': 1, 'info': client.to_json()})


@api.route('/clients', methods=['GET'])
def get_clients():
    clients = Client.query.all()
    return jsonify({'code': 1, 'clients': [client.to_json() for client in clients]})


@api.route('/client/logout')
@login_check
def client_logout():
    client = g.current_client

    pipeline = redis.pipeline()
    pipeline.delete('token:%s' % g.token)
    pipeline.hmset('client:%s' % client.phone_number, {'app_online': 0})
    pipeline.execute()
    return jsonify({'code': 1, 'message': 'Log Out Successfully'})


@api.route('/client/set-head-picture', methods=['POST'])
@login_check
def client_set_head_picture():
    avatar_picture = request.get_json().get('avatar_picture')
    client = g.current_client
    client.avatar_picture = avatar_picture
    try:
        db.session.commit()
    except Exception as e:
        print e
        db.session.rollback()
        return jsonify({'code': 0, 'message': 'Upload Unsuccessfully'})
    redis.hset('client:%s' % client.phone_number,
               'avatar_picture', avatar_picture)
    return jsonify({'code': 1, 'message': 'Upload Successfully'})


@api.route('/client/register-step-1', methods=['POST'])
def register_step_1():
    if not request or not request.get_json():
        return jsonify({'code': 0, 'message': 'Wrong Request Format'}), 400
    phone_number = request.get_json().get('phone_number') or ''
    client = Client.query.filter_by(phone_number=phone_number).first()

    if client:
        return jsonify({'code': 0, 'message': 'The Client Has Been Exist, Please Log In'})
    validate_number = str(random.randint(100000, 1000000))
    result, err_message = message_validate(phone_number, validate_number)

    if not result:
        return jsonify({'code': 0, 'message': err_message})

    pipeline = redis.pipeline()
    pipeline.set('validate:%s' % phone_number, validate_number)
    pipeline.expire('validate:%s' % phone_number, 60)
    pipeline.execute()

    return jsonify({'code': 1, 'message': 'Send Successfully'})


@api.route('/client/register-step-2', methods=['POST'])
def register_step_2():
    if not request or not request.get_json():
        return jsonify({'code': 0, 'message': 'Wrong Request Format'}), 400
    phone_number = request.get_json().get('phone_number') or ''
    validate_number = request.get_json().get('validate_number') or ''
    validate_number_in_redis = redis.get('validate:%s' % phone_number)

    if validate_number != validate_number_in_redis:
        return jsonify({'code': 0, 'message': 'Wrong Validate number'})

    pipe_line = redis.pipeline()
    pipe_line.set('is_validate:%s' % phone_number, '1')
    pipe_line.expire('is_validate:%s' % phone_number, 120)
    pipe_line.execute()

    return jsonify({'code': 1, 'message': 'Validate Successfully'})


@api.route('/client/register-step-3', methods=['POST'])
def register_step_3():
    if not request or not request.get_json():
        return jsonify({'code': 0, 'message': 'Wrong Request Format'}), 400
    phone_number = request.get_json().get('phone_number') or ''
    password = request.get_json().get('password') or ''
    password_confirm = request.get_json().get('password_confirm') or ''

    if len(password) < 7 or len(password) > 30:
        # 这边可以自己拓展条件
        return jsonify({'code': 0, 'message': 'Password Too Short Or Too Long'})

    if password != password_confirm:
        return jsonify({'code': 0, 'message': 'Wrong Password confirm'})

    is_validate = redis.get('is_validate:%s' % phone_number)

    if is_validate != '1':
        return jsonify({'code': 0, 'message': 'Wrong Validate number'})

    pipeline = redis.pipeline()
    pipeline.hset('register:%s' % phone_number, 'password', password)
    pipeline.expire('register:%s' % phone_number, 120)
    pipeline.execute()

    return jsonify({'code': 1, 'message': 'Submit Password Successfully'})


@api.route('/client/register-step-4', methods=['POST'])
def register_step_4():
    if not request or not request.get_json():
        return jsonify({'code': 0, 'message': 'Wrong Request Format'}), 400
    phone_number = request.get_json().get('phone_number') or ''
    email = request.get_json().get('email') or ''

    is_validate = redis.get('is_validate:%s' % phone_number)

    if is_validate != '1':
        return jsonify({'code': 0, 'message': 'Wrong Validate number'})

    password = redis.hget('register:%s' % phone_number, 'password')
    if not password:
        return jsonify({'code': 0, 'message': 'Password is not set'})

    new_client = Client(phone_number=phone_number,
                        password=password, email=email)
    db.session.add(new_client)

    try:
        db.session.commit()
    except Exception as e:
        print e
        db.session.rollback()
        return jsonify({'code': 0, 'message': 'The Mail Has Been Registered'})
    finally:
        redis.delete('is_validate:%s' % phone_number)
        redis.delete('register:%s' % phone_number)

    return jsonify({'code': 1, 'message': 'Register Successfully'})

@api.route('/client/register', methods=['POST'])
def register():
    if not request or not request.get_json():
        return jsonify({'code': 0, 'message': 'Wrong Request Format'}), 400
    phone_number = request.get_json().get('phone_number') or ''
    client = Client.query.filter_by(phone_number=phone_number).first()

    if client:
        return jsonify({'code': 0, 'message': 'The Client Has Been Exist, Please Log In'})

    password = request.get_json().get('password') or ''
    password_confirm = request.get_json().get('password_confirm') or ''
    email = request.get_json().get('email') or ''

    if password != password_confirm:
        return jsonify({'code': 0, 'message': 'Wrong Password confirm'})
    new_client = Client(phone_number=phone_number,
                        password=password, email=email)
    db.session.add(new_client)
    try:
        db.session.commit()
    except Exception as e:
        print e
        db.session.rollback()
        return jsonify({'code': 0, 'message': 'The Mail Has Been Registered'})

    return jsonify({'code': 1, 'message': 'Register Successfully'})     


@api.route('/client/forms', methods=['POST'])
@login_check
def form_post():
    if not request or not request.get_json():
        return jsonify({'code': 0, 'message': 'Wrong Request Format'}), 400
    client = g.current_client
    campus = request.get_json().get('campus') or ''
    machine_model = request.get_json().get('machine_model') or ''
    OS = request.get_json().get('OS') or ''
    description = request.get_json().get('description') or ''
    pictures = request.get_json().get('pictures') or ''

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
        return jsonify({'code': 0, 'message': 'Submit Unsuccessfully'})
    return jsonify({'code': 1, 'message': 'Submit Successfully'})


@api.route('/client/forms', methods=['GET'])
@login_check
def client_forms():
    client = g.current_client
    if not client:
        return jsonify({'code': 1, 'message': 'Wrong request'})
    page = request.args.get('page', 1, type=int)
    pagination = Form.query.filter_by(post_client_id=client.id).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    forms = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_forms', page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_forms', page=page + 1, _external=True)

    status_tuple = db.session.query(Form.status, func.count(Form.status)).filter(
        Form.post_client_id == client.id).group_by(Form.status).all()
    status_json = json.dumps(dict(status_tuple))
    return jsonify({
        'code': 1,
        'forms': [form.to_json() for form in forms],
        'prev': prev,
        'next': next,
        'count': status_json
    })
