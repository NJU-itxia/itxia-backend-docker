# coding:utf-8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
from flask_cors import CORS, cross_origin
from config import config
from qiniu import Auth


db = SQLAlchemy()
redis = FlaskRedis()

def create_app(config_name='default'):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config[config_name])
    app.q = Auth(access_key=app.config['QINIU_ACCESS_KEY'], secret_key=app.config['QINIU_SECRET_KEY'])
    app.bucket_name = app.config['BUCKET_NAME']

    app.debug = app.config['DEBUG']

    db.init_app(app)
    redis.init_app(app)

    from .api_1_1 import api as api_1_1_blueprint
    app.register_blueprint(api_1_1_blueprint, url_prefix='/api/v1_1')

    return app
