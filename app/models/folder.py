from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, Boolean, func

from . import db

class FolderModel(db.Model):
    __tablename__ = 'folders'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    owner_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('users.id'), nullable=False)
    owner = db.relationship('UserModel', back_populates='folders')

    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    parent_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('folders.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now())
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[datetime] = mapped_column(DateTime)

    def __repr__(self):
        return f"Folder(name = {self.name})"

    def __init__(self, name, parent_id=None):
        self.name = name
        self.parent_id = parent_id