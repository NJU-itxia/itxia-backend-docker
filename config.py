import os
class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = 'saduhsuaihfe332r32rfo43rtn3noiYUG9jijoNF23'
    QINIU_ACCESS_KEY = '2SDKEG3KlbfHAHhT_Ajj5UyZY_mgNo1HZS-2yiJM'
    QINIU_SECRET_KEY = 'sewuf9u7Gq_s8GvBpZld0x_y5VDZwzHp4awJxSS9'
    BUCKET_NAME = 'itxia'
    FLASKY_POSTS_PER_PAGE = 20


class DevelopmentConfig(Config):
    DEBUG = True

    REDIS_URL = "redis://:@redis:6379/0"
    SQLALCHEMY_DATABASE_URI = "mysql://" + os.environ('MYSQL_USERNAME') + ":" + os.environ('MYSQL_PASSWORD')+ "@db:3306/apidb?charset=utf8"


class ProductionConfig(Config):
    DEBUG = False
    
    REDIS_URL = "redis://:secret_password@localhost:6379/0"
    SQLALCHEMY_DATABASE_URI = "mysql://itxiadb:secret_password@localhost/apidb?charset=utf8"


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
