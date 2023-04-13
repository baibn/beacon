from product import db
from datetime import datetime


class CaseGroup(db.Model):
    __tablename__ = 'case_group'
    group_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_name = db.Column(db.String(50), nullable=False, unique=True, comment='用例集名称')
    group_code = db.Column(db.String(200), nullable=False, unique=True, comment='用例集code，用来生成关联用例的用例编号')
    proj_type = db.Column(db.String(50), unique=False, nullable=False, comment='需要特殊处理的用例集类型')
    encode_type = db.Column(db.String(50), unique=False, nullable=False, comment='接口参数需要加密处理的类型')
    service = db.Column(db.String(50), unique=False, nullable=False, comment='用例集所属服务：天网，音视频，文本，图片，web')
    ext = db.Column(db.String(50), nullable=True, comment="额外信息")
    create_by = db.Column(db.String(30), nullable=False, comment='创建人')
    update_by = db.Column(db.String(30), nullable=False, comment='更新人')
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    status = db.Column(db.SmallInteger, nullable=False, default=1, comment='启用状态，1-启用，0-禁用')
    is_del = db.Column(db.SmallInteger, nullable=False, default=0, comment='是否删除')

    def __repr__(self):
        return '<CaseGroup %s>' % self.group_id


# 用例和计划关系表
case_task_relation = db.Table(
    'case_task_relation',
    db.Column('cp_task_id', db.Integer, db.ForeignKey('case_task.task_id'), primary_key=True),
    db.Column('cp_case_id', db.Integer, db.ForeignKey('case_manage.case_id'), primary_key=True),
)


class CaseManage(db.Model):
    __tablename__ = "case_manage"
    case_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    case_name = db.Column(db.String(100), unique=True, comment='用例名称')
    case_sign = db.Column(db.String(200), unique=True, comment='用例编号')
    description = db.Column(db.Text(65535), unique=False, comment='描述信息')
    method = db.Column(db.String(20), unique=False, comment='http请求方法')
    url = db.Column(db.Text(4294967295), unique=False, comment='请求的url')
    port = db.Column(db.String(50), unique=False, nullable=False, comment='请求的端口号')
    params = db.Column(db.Text(4294967295), unique=False, comment='参数')
    headers = db.Column(db.String(500), unique=False, comment='http请求头信息')
    set_up = db.Column(db.String(500), unique=False, comment='sql标识，多个用","分割')
    expect_res = db.Column(db.Text(4294967295), unique=False, comment='预期结果')
    expect_keys = db.Column(db.String(500), nullable=False, unique=False, comment='请求结果中预期存在的keys')
    unexpect_keys = db.Column(db.String(500), nullable=False, unique=False, comment='请求结果中预期不存在的keys')
    delay_time = db.Column(db.Integer(), nullable=False, unique=False, comment='每条用例执行完后的等待时间,单位：秒')
    history_check = db.Column(db.Text(4294967295), unique=False, nullable=True, comment='历史记录校验')
    create_by = db.Column(db.String(30), nullable=False, comment='创建人')
    update_by = db.Column(db.String(30), nullable=False, comment='更新人')
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    status = db.Column(db.SmallInteger, nullable=False, default=1, comment='可执行状态，1-启用，0-禁用')

    group_id = db.Column('group_id', db.Integer, db.ForeignKey('case_group.group_id'))
    case_group = db.relationship('CaseGroup', backref='casemanage', single_parent=True)

    def __repr__(self):
        return '<Case %s>' % self.case_id


class CaseTask(db.Model):
    __tablename__ = 'case_task'
    task_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    task_name = db.Column(db.String(50), nullable=False, unique=True, comment='任务名称')
    task_group = db.Column(db.String(50), nullable=False, default=-1, comment='关联的用例集，默认-1为没设置')
    isDel = db.Column(db.SmallInteger, nullable=False, default=0, comment='是否删除')
    create_by = db.Column(db.String(30), nullable=False, comment='创建人')
    update_by = db.Column(db.String(30), nullable=False, comment='更新人')
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    case_run_way = db.Column(db.SmallInteger, nullable=False, default=1, comment='关联用例的执行方式,0-定时执行,1-单次执行')
    case_run_way_0 = db.Column(db.String(30), nullable=False, default='0 24 * * *', comment='定时任务表达式，默认每天晚上12点执行')
    status = db.Column(db.SmallInteger, nullable=False, default=1, comment='计划执行状态，1-启用，0-禁用')
    is_del = db.Column(db.SmallInteger, nullable=False, default=0, comment='是否删除')
    email = db.Column(db.String(50), nullable=True, unique=False, comment='邮件')

    cases = db.relationship('CaseManage', secondary=case_task_relation, backref='casetask')  # 反向引用

    def __repr__(self):
        return '<CaseTask %s>' % self.task_id
