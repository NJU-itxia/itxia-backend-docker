# coding:utf-8
from flask import request, jsonify, current_app, make_response, g
from .. import redis
from functools import wraps


def login_check(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not g.token:
            return jsonify({'code': 0, 'message': 'Validation Needed'}), 401
        
        if not g.role:
            return jsonify({'code': 0, 'message': 'Token Expire'}), 401

        if g.role.has_key('manager'):
            username = redis.hget('token:%s' % token, 'id')
            if not username or g.token != redis.hget('manager:%s' % username, 'token'):
                return jsonify({'code': 2, 'message': 'Wrong Validation'}), 401
        elif g.role.has_key('client'):
            phone_number = redis.hget('token:%s' % token, 'id')
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
        if not g.role.has_key('manager') or g.role['manager'].role != 'admin':
            return jsonify({'code': 0, 'message': 'No Permission'}), 401

        return f(*args, **kwargs)
    return decorator
    
def superadmin_check(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not g.role.has_key('manager') or g.role['manager'].role != 'superadmin':
            return jsonify({'code': 0, 'message': 'No Permission'}), 401
        return f(*args, **kwargs)
    return decorator
