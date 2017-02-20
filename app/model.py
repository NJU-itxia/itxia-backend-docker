from datetime import datetime
from . import db
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method, hybrid_method
from flask import url_for
import random

class Manager(db.Model):
    __tablename__ = 'manager'

    id = db.Column('id', db.Integer, primary_key=True)
    role = db.Column('role', db.String(30), nullable=False, default='itxia')
    password = db.Column('password', db.String(30), nullable=False)
    username = db.Column('username', db.String(30), index=True, unique=True, nullable=False)
    email = db.Column('email', db.String(64), index=True, unique=True, nullable = False)
    campus = db.Column('campus', db.String(10), index=True, nullable=False)
    avatar_picture = db.Column('avatar_picture', db.String(120), default='')
    register_time = db.Column('register_time', db.DateTime, index=True, default=datetime.now)
    handle_forms = db.relationship('Form', backref='handle_manager', lazy='dynamic', uselist=True)
    comments = db.relationship('Comment', backref='comment_manager', lazy='dynamic', uselist=True)
    
    
    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        
        seed()
        for i in range(count):
            m = Manager(email=forgery_py.internet.email_address(),
                     password=forgery_py.lorem_ipsum.word(),
                     campus=['gulou', 'xianlin'][random.randint(0,1)],
                     username=forgery_py.lorem_ipsum.word(),
                     register_time=forgery_py.date.date(True))
            db.session.add(m)
            try:
                db.session.commit()
                db.session.remove()
            except IntegrityError:
                db.session.rollback()
                
 
    def to_json(self):
        json_post = {
            'username': self.username,
            'password': self.password
        }
        return json_post

class Form(db.Model):
    __tablename__ = 'form'

    id = db.Column('id', db.Integer, primary_key=True)
    post_time = db.Column('post_time', db.DateTime, default=datetime.now)
    campus = db.Column('campus', db.String(10), index=True, nullable=False)
    status = db.Column('status', db.String(10), index=True, default='waiting', nullable=False)
    machine_model = db.Column('machine_model', db.String(64), nullable=False)
    OS = db.Column('OS', db.String(64), nullable = False)
    description = db.Column('description', db.String(240), nullable=False)
    picture_content = db.Column('picture_content', db.String(900))
    handle_manager_id = db.Column('handle_manager_id', db.Integer, db.ForeignKey('manager.id'))
    post_client_id = db.Column('post_client_id', db.Integer, db.ForeignKey('client.id'))
    comments = db.relationship('Comment', backref='form_to_comment', lazy='dynamic', uselist=True)
    
    
    @hybrid_property
    def pictures(self):
        if not self.picture_content:
            return []
        return self.picture_content.split(', ')


    @pictures.setter
    def pictures(self, urls):
        self.picture_content = ', '.join(urls)
    
    
    @hybrid_property
    def state(self):
        if not self.handle_manager:
            return 'waiting'
        return self.status


    @state.setter
    def state(self, managing):
        self.status = managing
    
    
    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        client_count = Client.query.count()
        for i in range(count):
            c = Client.query.offset(randint(0, client_count - 1)).first()
            m = Manager.query.offset(randint(0, client_count - 1)).first()
            f = Form(description=forgery_py.lorem_ipsum.words(10),
                     post_time=forgery_py.date.date(True),
                     campus=['gulou', 'xianlin'][random.randint(0,1)],
                     machine_model=forgery_py.lorem_ipsum.word(),
                     OS=forgery_py.lorem_ipsum.word(),
                     post_client=c,
                     handle_manager=m)
            f.state = ['working', 'done'][random.randint(0,1)]
            db.session.add(f)
            try:
                db.session.commit()
                db.session.remove()
            except IntegrityError:
                db.session.rollback()

        
    def to_json(self):
        handle_manager_username = None
        post_client_phone_number = None
        comments_of_post = None
        if self.post_client:
            post_client_phone_number = self.post_client.phone_number
        if self.handle_manager:
            handle_manager_username = self.handle_manager.username
        if self.comments:
            comments_of_post = [comment.to_json() for comment in self.comments]
            
        json_post = {
            'url': url_for('api1_1.get_form', id=self.id, _external=True),
            'comments': comments_of_post,
            'post_client_phone_number': post_client_phone_number,
            'handle_manager_username': handle_manager_username,
            'campus': self.campus,
            'machine_model': self.machine_model,
            'OS': self.OS,
            'description': self.description,
            'picture_content': self.picture_content,
            'status': self.status,
            'timestamp': self.post_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        return json_post


class Client(db.Model):
    __tablename__ = 'client'

    id = db.Column('id', db.Integer, primary_key=True)
    password = db.Column('password', db.String(30), nullable=False)
    phone_number = db.Column('phone_number', db.String(15), index=True, unique=True, nullable=False)
    email = db.Column('email', db.String(64), index=True, unique=True)
    avatar_picture = db.Column('avatar_picture', db.String(120), default='')
    register_time = db.Column('register_time', db.DateTime, index=True, default=datetime.now)
    post_forms = db.relationship('Form', backref='post_client', lazy='dynamic', uselist=True)
    comments = db.relationship('Comment', backref='comment_client', lazy='dynamic', uselist=True)
    
    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        
        seed()
        for i in range(count):
            c = Client(email=forgery_py.internet.email_address(),
                     password=forgery_py.lorem_ipsum.word(),
                     phone_number=forgery_py.address.phone(),
                     register_time=forgery_py.date.date(True))
            db.session.add(c)
            try:
                db.session.commit()
                db.session.remove()
            except IntegrityError:
                db.session.rollback() 
    
    
    @staticmethod
    def get_item(id):
        return Client.query.get(id)

class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column('id', db.Integer, primary_key=True)
    comment_time = db.Column('comment_time', db.DateTime, default=datetime.now)
    content = db.Column('content', db.String(500), nullable=False)
    manager_id = db.Column('manager_id', db.Integer, db.ForeignKey('manager.id'))
    client_id = db.Column('client_id', db.Integer, db.ForeignKey('client.id'))
    form_id = db.Column('form_id', db.Integer, db.ForeignKey('form.id'))
    comment_to_reply = db.Column('comment_to_reply', db.Integer, index=True)
    
    @hybrid_property
    def reply(self):
        if not self.comment_to_reply:
            return None
        return self.comment_to_reply
    
    @reply.setter
    def reply(self, comment):
        self.comment_to_reply = comment.id
        
    @hybrid_property
    def commentator(self):
        if self.client_id:
            return {'client': self.comment_client.phone_number}
        elif self.manager_id:
            return {'manager': self.comment_manager.username}
            
    @commentator.setter
    def commentator(self, people):
        if people.__class__ == Client:
            self.comment_client = people
        if people.__class__ == Manager:
            self.comment_manager = people
            
    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        client_count = Client.query.count()
        manager_count = Manager.query.count()
        form_count = Form.query.count()
        for i in range(count):
            c = Client.query.offset(randint(0, client_count - 1)).first()
            m = Manager.query.offset(randint(0, manager_count - 1)).first()
            f = Form.query.offset(randint(0, form_count - 1)).first()
            comment = Comment(content=forgery_py.lorem_ipsum.words(10),
                     comment_time=forgery_py.date.date(True),
                     form_to_comment=f)
            comment.commentator = [c, m][random.randint(0,1)]
            db.session.add(comment) 
            try:
                db.session.commit()
                db.session.remove()
            except IntegrityError:
                db.session.rollback() 
        
        comment_count = comment.query.count()
        for i in range(count):
            reply = comment.query.offset(randint(0, comment_count - 1)).first()
            c = Client.query.offset(randint(0, client_count - 1)).first()
            m = Manager.query.offset(randint(0, manager_count - 1)).first()
            f = Form.query.offset(randint(0, form_count - 1)).first()
            comment = Comment(content=forgery_py.lorem_ipsum.words(10),
                     comment_time=forgery_py.date.date(True),
                     form_to_comment=f)
            comment.reply = reply
            db.session.add(comment) 
            try:
                db.session.commit()
                db.session.remove()
            except IntegrityError:
                db.session.rollback() 
            
    def to_json(self):
        reply = None
        if self.reply:
            reply = url_for('api1_1.get_comment', id=self.reply, _external=True)
        json_comment = {
            'url': url_for('api1_1.get_comment', id=self.id, _external=True),
            'reply': reply,
            'content': self.content,
            'comment_time': self.comment_time.strftime('%Y-%m-%d %H:%M:%S'),
            'commentator': self.commentator
            }
            
        return json_comment
