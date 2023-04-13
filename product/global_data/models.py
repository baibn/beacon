from product import db
from datetime import datetime


class GlobalData(db.Model):
    __tablename__ = "global_data"
    data_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True, comment='变量名称')
    category = db.Column(db.String(50), unique=False, default='global',
                         comment="'normal' | 'sql' | 'case' ,'mormal'为普通变量,'sql'为sql变量,'case'case变量(用例依赖),")
    value = db.Column(db.Text(4294967295), nullable=False, unique=False, comment='变量值')
    type = db.Column(db.String(20), nullable=False, unique=False, comment='变量类型')
    scope = db.Column(db.String(20), unique=False, default='global',
                      comment="'global' | 'group' ，'global'为全局变量， 'group'作用范围是用例集'")
    create_by = db.Column(db.String(30), nullable=False, comment='创建人')
    update_by = db.Column(db.String(30), nullable=False, comment='更新人')
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    group_id = db.Column(db.String(30), default="0", comment="默认0,全局变量")

    def __repr__(self):
        return '<GlobalData %s>' % self.data_id
