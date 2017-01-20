# coding:utf-8
from app import create_app, db
from app.model import Form, Manager, Client
from flask_script import Shell, Command, Manager as M
from flask_migrate import Migrate, MigrateCommand

app = create_app('default')
manager = M(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, Manager=Manager, Client=Client, Form=Form)
    
@manager.command    
def testdb():
    Client.generate_fake(10) #构造虚拟用户
    Manager.generate_fake(10) #构造虚拟itxia
    Form.generate_fake(10) #构造虚拟订单

    
                   
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':

    manager.run()
