# -*- encoding: utf-8 -*-
# !/usr/bin/python
import sys
import os
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from product import create_app, db
from product.users.models import User

# init时不需要启动后台监控程序
if 'init' in sys.argv:
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'
app = create_app()
# 创建数据库表
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

@manager.command
def init():
    db.drop_all()
    db.create_all()
    User.set_default_users()

# python manager.py runserver -h 0.0.0.0 -p 8989
if __name__ == '__main__':
    manager.run()
