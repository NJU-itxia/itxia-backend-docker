# coding:utf-8
from flask import request, jsonify, g, current_app
from app.model import Client, Manager, Form
from .. import db, redis

from . import api
from .decorators import login_check, admin_check, superadmin_check, allow_cross_domain

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

@api.route('/admin/modify_manager', methods=['PUT'])
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
