import os

class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    QINIU_ACCESS_KEY = os.environ.get('QINIU_ACCESS_KEY')
    QINIU_SECRET_KEY = os.environ.get('QINIU_SECRET_KEY')
    BUCKET_NAME = os.environ.get('BUCKET_NAME')
    FLASKY_POSTS_PER_PAGE = 20


class DevelopmentConfig(Config):
    DEBUG = True

    REDIS_URL = "redis://:" + os.environ.get('REDIS_PASSWORD') + "@redis:6379/0"
    SQLALCHEMY_DATABASE_URI = "mysql://" + os.environ.get('MYSQL_USERNAME') + ":" + os.environ.get('MYSQL_ROOT_PASSWORD') + "@db:3306/" + os.environ.get('MYSQL_DATABASE')


class ProductionConfig(Config):
    DEBUG = False

    REDIS_URL = "redis://:" + os.environ.get('REDIS_PASSWORD') + "@redis:6379/0"
    SQLALCHEMY_DATABASE_URI = "mysql://" + os.environ.get('MYSQL_USERNAME') + ":" + os.environ.get('MYSQL_ROOT_PASSWORD') + "@db:3306/" + os.environ.get('MYSQL_DATABASE')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
