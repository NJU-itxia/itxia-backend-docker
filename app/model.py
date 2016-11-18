from datetime import datetime
from . import db
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from flask import url_for
import random

class Server(db.Model):
    __tablename__ = 'server'

    id = db.Column('id', db.Integer, primary_key=True)
    password = db.Column('password', db.String(30), nullable=False)
    username = db.Column('username', db.String(30), index=True, unique=True, nullable=False)
    email = db.Column('email', db.String(64), index=True, unique=True, nullable = False)
    campus = db.Column('campus', db.String(10), index=True, nullable=False)
    avatar_picture = db.Column('avatar_picture', db.String(120), default='')
    register_time = db.Column('register_time', db.DateTime, index=True, default=datetime.now)
    handle_forms = db.relationship('Form', backref='handle_server', lazy='dynamic', uselist=True)
    
    
    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        
        seed()
        for i in range(count):
            s = Server(email=forgery_py.internet.email_address(),
                     password=forgery_py.lorem_ipsum.word(),
                     campus=['gulou', 'xianlin'][random.randint(0,1)],
                     username=forgery_py.lorem_ipsum.word(),
                     register_time=forgery_py.date.date(True))
            db.session.add(s)
            try:
                db.session.commit()
                db.session.remove()
            except IntegrityError:
                db.session.rollback() 
    

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
    handle_server_id = db.Column('handle_server_id', db.Integer, db.ForeignKey('server.id'))
    post_client_id = db.Column('post_client_id', db.Integer, db.ForeignKey('client.id'))
    
    
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
        if not self.handle_server:
            return 'waiting'
        return self.status


    @state.setter
    def state(self, working_done):
        self.status = working_done
    
    
    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        client_count = Client.query.count()
        for i in range(count):
            c = Client.query.offset(randint(0, client_count - 1)).first()
            s = Server.query.offset(randint(0, client_count - 1)).first()
            f = Form(description=forgery_py.lorem_ipsum.words(10),
                     post_time=forgery_py.date.date(True),
                     campus=['gulou', 'xianlin'][random.randint(0,1)],
                     machine_model=forgery_py.lorem_ipsum.word(),
                     OS=forgery_py.lorem_ipsum.word(),
                     post_client=c,
                     handle_server=s)
            f.state = ['working', 'done'][random.randint(0,1)],
            db.session.add(f)
            db.session.commit()  

        
    def to_json(self):
        handle_server_username = None
        post_client_phone_number = None
        if self.post_client:
            post_client_phone_number = self.post_client.phone_number
        if self.handle_server:
            handle_server_username = self.handle_server.username
            
        json_post = {
            'url': url_for('api1_1.get_form', id=self.id, _external=True),
            'post_client_phone_number': post_client_phone_number,
            'handle_server_username': handle_server_username,
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
    
