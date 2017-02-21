# coding:utf-8
from flask import request, jsonify, g, current_app
from app.model import Client, Manager, Form, Comment
from .. import db, redis
import uuid

from . import api
from .decorators import login_check, admin_check, superadmin_check, allow_cross_domain

@api.route('/comments/<int:id>', methods=['GET'])
@login_check
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    if not g.current_manager and g.current_client.id != comment.client_id: 
        return jsonify({'code': 0, 'message': 'No Permission'}), 401
    return jsonify({'code': 1, 'comment': comment.to_json()})

@api.route('/comments', methods=['POST'])
@login_check
def edit_comment(id):
    comment = Comment.query.get_or_404(id)
    if not g.current_manager and g.current_client.id != comment.client_id: 
        return jsonify({'code': 0, 'message': 'No Permission'})
        
    if not request or not request.get_json():
        return jsonify({'code': 0, 'message': 'Wrong Request Format'}), 400   
    content = request.get_json().get('content') or ''
    form_url = request.get_json().get('form_url') or ''
    reply_url = request.get_json().get('reply') or ''
    
    form_id = form_url.split('/')[-1]
    reply_id = comment_url.split('/')[-1]
    f = Form.query.filter_by(id=form_id).first()
    comment = Comment(content=content,
                     form_to_comment=f)
    comment.reply = reply_id
    if g.current_manager:
        comment.commentator = g.current_manager
    if g.current_client:
        comment.commentator = g.current_client
    
    db.session.add(comment)   
    try:
        db.session.commit()
    except Exception as e:
        print e
        db.session.rollback()
        return jsonify({'code': 0, 'message': 'Comment Unsuccessfully'})
    return jsonify({'code': 1, 'message': 'Comment Successfully'})
        

@api.route('/comments', methods=['GET'])
def get_comments():
    comments = Comment.query.all()
    return jsonify({'code': 1, 'comments': [comment.to_json() for comment in comments]})
