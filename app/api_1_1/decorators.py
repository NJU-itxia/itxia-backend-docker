# coding:utf-8
from flask import request, jsonify, current_app, make_response, g
from .. import redis
from functools import wraps

def allow_cross_domain(fun):
    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        rst = make_response(fun(*args, **kwargs))
        rst.headers['Access-Control-Allow-Origin'] = '*'
        rst.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE'
        allow_headers = "Referer, Accept, Origin, User-Agent, Token, Role"
        rst.headers['Access-Control-Allow-Headers'] = allow_headers
        return rst
    return wrapper_fun

def login_check(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not g.token:
            return jsonify({'code': 0, 'message': 'Validation Needed'}), 401
        
        if g.role.has_key('manager'):
            username = redis.get('token:%s' % g.token)
            if not username or token != redis.hget('manager:%s' % username, 'token'):
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
