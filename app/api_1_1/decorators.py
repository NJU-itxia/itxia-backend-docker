# coding:utf-8
from flask import request, jsonify, current_app
from .. import redis
from functools import wraps


def login_check(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get('token')
        role = request.headers.get('role')
        if not token:
            return jsonify({'code': 0, 'message': 'Validation Needed'})
        
        if role == 'manager':
            username = redis.get('token:%s' % token)
            if not username or token != redis.hget('manager:%s' % username, 'token'):
                return jsonify({'code': 2, 'message': 'Wrong Validation for manager'})
        else:
            phone_number = redis.get('token:%s' % token)
            if not phone_number or token != redis.hget('client:%s' % phone_number, 'token'):
                return jsonify({'code': 2, 'message': 'Wrong Validation'})

        return f(*args, **kwargs)
    return decorator
    
def manager_check(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        role = request.headers.get('role')
        if role != 'manager':
            return jsonify({'code': 0, 'message': 'No Permission'})
        return f(*args, **kwargs)
    return decorator
