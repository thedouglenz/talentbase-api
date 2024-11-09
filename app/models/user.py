from datetime import datetime

from itsdangerous import (URLSafeTimedSerializer as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Boolean, func

from . import db

class UserModel(db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now())
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[datetime] = mapped_column(DateTime)
    last_login: Mapped[datetime] = mapped_column(DateTime)

    folders = relationship('FolderModel', back_populates='owner')

    def __repr__(self):
        return f"User(name = {self.name}, email = {self.email})"

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        from app import config
        secret_key = config['SECRET_KEY']
        s = Serializer(secret_key, expires_in=expiration)
        # Set last login time
        self.set_last_login()
        return s.dumps({'id': self.id})

    def set_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()

    @staticmethod
    def verify_auth_token(token):
        from app import config
        secret_key = config['SECRET_KEY']
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = UserModel.query.filter_by(id=data['id'], deleted=False).first()
        return user