# coding:utf-8
from app import create_app, db
from app.model import Form, Server, Client
from flask_script import Manager, Shell, Command
from flask_migrate import Migrate, MigrateCommand

app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, Server=Server, Client=Client, Form=Form)
    
@manager.command    
def testdb():
    Client.generate_fake(10) #构造虚拟用户
    Server.generate_fake(10) #构造虚拟itxia
    Form.generate_fake(10) #构造虚拟订单

    
                   
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':

    manager.run()
