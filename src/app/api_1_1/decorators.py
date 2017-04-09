# coding:utf-8
from flask import request, jsonify, current_app, make_response, g
from .. import redis
from functools import wraps


def login_check(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not g.token:
            return jsonify({'code': 0, 'message': 'Validation Needed'}), 401
        
        if g.role.has_key('manager'):
            username = redis.get('token:%s' % g.token)
            if not username or g.token != redis.hget('manager:%s' % username, 'token'):
                return jsonify({'code': 2, 'message': 'Wrong Validation'}), 401
        else:
            phone_number = redis.get('token:%s' % g.token)
            if not phone_number or g.token != redis.hget('client:%s' % phone_number, 'token'):
                return jsonify({'code': 2, 'message': 'Wrong Validation'}), 401

        return f(*args, **kwargs)
    return decorator
    
def manager_check(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not g.role.has_key('manager'):
            return jsonify({'code': 0, 'message': 'No Permission'}), 401
        return f(*args, **kwargs)
    return decorator
    
def admin_check(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if g.role['manager'] != 'admin':
            return jsonify({'code': 0, 'message': 'No Permission'}), 401
        return f(*args, **kwargs)
    return decorator
    
def superadmin_check(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if g.role['manager'] != 'superadmin':
            return jsonify({'code': 0, 'message': 'No Permission'}), 401
        return f(*args, **kwargs)
    return decorator
