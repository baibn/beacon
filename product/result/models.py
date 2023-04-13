from product import db
from datetime import datetime


class Result(db.Model):
    __tablename__ = 'result'
    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, nullable=True, unique=False, comment='执行的用例集id')
    task_id = db.Column(db.String(50), nullable=True, unique=False, comment='执行的任务id')
    operate_by = db.Column(db.String(30), nullable=False, comment='执行人人')
    operate_at = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='执行时间')
    case_run_way = db.Column(db.SmallInteger, nullable=False, default=1, comment='关联用例的执行方式,0-定时执行,1-单次执行')
    result = db.Column(db.String(500), nullable=False, comment="报告链接")

    def __repr__(self):
        return '<Result %s>' % self.record_id
