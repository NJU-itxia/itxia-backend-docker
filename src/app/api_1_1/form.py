# coding:utf-8
from flask import request, jsonify, g, current_app
from app.model import Client, Manager, Form
from .. import db, redis

from . import api
from .decorators import login_check

@api.route('/forms', methods=['GET'])
def get_forms():
    forms = Form.query.all()
    return jsonify({'code': 1, 'forms': [form.to_json() for form in forms]})
    
@api.route('/forms/<int:id>', methods=['GET'])
@login_check
def get_form(id):
    form = Form.query.get_or_404(id)
    if not g.current_manager and g.current_client.id != form.post_client_id: 
        return jsonify({'code': 0, 'message': 'No Permission'}), 401
    return jsonify({'code': 1, 'forms': form.to_json()})
    
@api.route('/forms/<int:id>', methods=['PUT'])
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
