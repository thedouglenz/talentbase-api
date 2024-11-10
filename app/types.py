from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from .models.folder import FolderModel
from .models.user import UserModel

from marshmallow import Schema, fields

# Non-ORM Schema
class LoginSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True)

class RegisterSchema(Schema):
    name = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True)

class FolderQuerySchema(Schema):
    user_id = fields.Int(required=True)
    page = fields.Int(missing=1)
    per_page = fields.Int(missing=10)

class CreateFolderSchema(Schema):
    name = fields.Str(required=True)
    parent_id = fields.Int()


# ORM Schema
class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_instance = True

class FolderSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = FolderModel
        include_fk = True
        load_instance = True

        # Don't require owner_id field for POST requests
        exclude = ["owner_id"]
