# coding:utf-8
from flask import request, jsonify, g, current_app
from app.model import Client, Manager, Form, Comment
from .. import db, redis
import uuid

from . import api
from .decorators import login_check, admin_check, superadmin_check, allow_cross_domain

@api.route('/comments/<int:id>', methods=['GET'])
@allow_cross_domain
@login_check
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    if not g.current_manager and g.current_client.id != comment.client_id: 
        return jsonify({'code': 0, 'message': 'No Permission'}), 401
    return jsonify({'code': 1, 'comment': comment.to_json()})
    

@api.route('/comments', methods=['GET'])
@allow_cross_domain
def get_comments():
    comments = Comment.query.all()
    return jsonify({'code': 1, 'comments': [comment.to_json() for comment in comments]})
