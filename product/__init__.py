from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from product.config import Config
from flask_mail import Mail
from flask_apscheduler.scheduler import APScheduler

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
mail = Mail(app)
scheduler = APScheduler()

# 实现csrf保护
csrf = CSRFProtect()


def create_app():
    Config.init_app(app)
    from product.api.users import login
    from product.api.users import user
    from product.api.case import case
    from product.api.case_group import case_group
    from product.api.case_task import case_task
    from product.api.global_data import global_data
    from product.api.run_group import run_group
    from product.api.run_task import run_task
    from product.api.record import record
    from product.api.schema import schema_data
    from product.api.sql import sql_manage

    app.register_blueprint(login, url_prefix='/api/login')
    app.register_blueprint(user, url_prefix='/api/user')
    app.register_blueprint(case, url_prefix='/api/case')
    app.register_blueprint(case_group, url_prefix='/api/casegroup')
    app.register_blueprint(case_task, url_prefix='/api/casetask')
    app.register_blueprint(global_data, url_prefix='/api/globaldata')
    app.register_blueprint(run_group, url_prefix='/api/rungroup')
    app.register_blueprint(run_task, url_prefix='/api/runtask')
    app.register_blueprint(record, url_prefix='/api/record')
    app.register_blueprint(schema_data, url_prefix='/api/schema')
    app.register_blueprint(sql_manage, url_prefix='/api/sqlmanage')
    db.init_app(app)
    app.db = db
    scheduler.init_app(app)
    with app.app_context():
        scheduler.start()
    app.scheduler = scheduler
    app.mail = mail

    return app
