from datetime import datetime
from typing import Optional

from itsdangerous import (URLSafeTimedSerializer as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Boolean, func
from flask_jwt_extended import create_access_token, create_refresh_token
from flask import jsonify

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
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    folders = relationship('FolderModel', back_populates='owner')

    def __repr__(self):
        return f"User(name = {self.name}, email = {self.email})"

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_jwt(self):
        return jsonify({
            "message": "Logged in as {}".format(self.name),
            "tokens": {
                "access": create_access_token(identity=self),
                "refresh": create_refresh_token(identity=self)
            }
        })

    def set_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'deleted': self.deleted,
            'deleted_at': self.deleted_at,
            'last_login': self.last_login
        }

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