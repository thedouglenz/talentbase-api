from passlib.apps import custom_app_context as pwd_context

from . import db

class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    deleted = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"User(name = {self.name}, email = {self.email})"

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)
