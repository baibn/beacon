from product import db
from datetime import datetime


class SqlManage(db.Model):
    __tablename__ = "sql_manage"
    sql_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    sql_name = db.Column(db.String(100), nullable=False, unique=True, comment='sql标识')
    type = db.Column(db.String(100), nullable=False, unique=False, comment='sql类型[select,delete,update,insert]')
    database = db.Column(db.String(100), nullable=False, unique=False, comment='数据库库名称，多个用","分割')
    databases = db.Column(db.String(100), nullable=False, unique=False, comment='数据源,默认default')
    value = db.Column(db.String(1024), nullable=False, unique=False, comment='sql语句')
    create_by = db.Column(db.String(30), nullable=False, comment='创建人')
    update_by = db.Column(db.String(30), nullable=False, comment='更新人')
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')


    def __repr__(self):
        return '<SqlManage %s>' % self.sql_id
