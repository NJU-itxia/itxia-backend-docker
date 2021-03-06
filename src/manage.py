# coding:utf-8
from app import create_app, db
from app.model import Form, Manager, Client, Comment
from flask_script import Shell, Command, Manager as M
from flask_migrate import Migrate, MigrateCommand

app = create_app('default')
manager = M(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, Manager=Manager, Client=Client, Comment = Comment, Form=Form)

@manager.command
def testdb():
    Client.generate_fake(10) 
    Manager.generate_fake(10) 
    Form.generate_fake(10) 
    Comment.generate_fake(10)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':

    manager.run()
