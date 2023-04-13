from product import db


class User(db.Model):
    __tablename__ = "user_info"
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    user = db.Column(db.String(30), unique=True)
    pwd = db.Column(db.String(30), unique=False)
    role = db.Column(db.String(20), unique=False)

    @staticmethod
    def set_default_users():
        superman = User(user='superman', pwd='ishumei123', role='admin')
        db.session.add(superman)
        db.session.commit()

    def __repr__(self):
        return '<User %s>' % self.id
