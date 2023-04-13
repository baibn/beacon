from product import db
from datetime import datetime


class SchemaData(db.Model):
    __tablename__ = "schema_data"
    schema_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    obj_name = db.Column(db.String(100), nullable=False, unique=False, comment='所属专项')
    name = db.Column(db.String(100), nullable=False, unique=True, comment='模版名称')
    value = db.Column(db.Text(4294967295), nullable=False, unique=False, comment='模版内容')
    create_by = db.Column(db.String(30), nullable=False, comment='创建人')
    update_by = db.Column(db.String(30), nullable=False, comment='更新人')
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def __repr__(self):
        return '<SchemaData %s>' % self.schema_id