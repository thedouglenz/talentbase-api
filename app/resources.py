from flask_restful import Resource, abort
from flask import g, request
from marshmallow import ValidationError
from sqlalchemy import func
from flask_jwt_extended import jwt_required, current_user

from .models.user import UserModel, db
from .models.folder import FolderModel
from .types import UserSchema, FolderSchema, LoginSchema, RegisterSchema, FolderQuerySchema, CreateFolderSchema
from .extensions import jwt

create_folder_schema = CreateFolderSchema()
folder_schema = FolderSchema()
folder_query_schema = FolderQuerySchema()
user_schema = UserSchema()

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return UserModel.query.filter_by(id=identity).one_or_none()

class LoginResource(Resource):
    def post(self):
        schema = LoginSchema()
        try:
            args = schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation errors", "errors": err.messages}, 400

        user = UserModel.query.filter_by(email=args['email']).one_or_none()
        if not user or not user.verify_password(args['password']):
            abort(401, message="Invalid credentials")
        return user.generate_jwt()

class UsersResource(Resource):
    def get(self):
        users = UserModel.query.filter_by(deleted=False).all()
        return user_schema.dump(users, many=True)

    def post(self):
        """New user registration"""
        schema = RegisterSchema()
        try:
            args = schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation errors", "errors": err.messages}, 400

        user = UserModel(
            name = args['name'],
            email = args['email']
        )
        user.hash_password(args['password'])
        db.session.add(user)
        db.session.commit()

        return user.generate_jwt()

class UserResource(Resource):
    def get(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")
        return user_schema.dump(user)

    def patch(self, id):
        try:
            args = user_schema.load(request.json, partial=True)
        except ValidationError as err:
            return {"message": "Validation errors", "errors": err.messages}, 400

        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")

        user.name = args["name"]
        user.email = args["email"]
        user.updated_at = func.now()

        db.session.commit()
        return user_schema.dump(user)

    def delete(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")
        user.deleted = True
        user.deleted_at = func.now()
        db.session.commit()
        return user_schema.dump(user)

class FoldersResource(Resource):
    @jwt_required()
    def get(self):
        errors = folder_query_schema.validate(request.args)
        if errors:
            abort(400, message="Validation errors", errors=errors)
        if not current_user:
            abort(401, message="Unauthorized") 
        args = folder_query_schema.dump(request.args)
        if current_user.id != args["user_id"]:
            abort(403, message="Forbidden")
        folders = FolderModel.query.filter_by(owner_id=args["user_id"], deleted=False).paginate(page=args["page"], per_page=args["per_page"])
        if not folders:
            abort(404, message="No folders found")
        return folder_schema.dump(folders.items, many=True)

    @jwt_required()
    def post(self):
        try:
           args = create_folder_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation errors", "errors": err.messages}, 400
        folder = FolderModel(name=args['name'], owner_id=current_user.id, parent_id=args.get('parent_id'))
        db.session.add(folder)
        db.session.commit()
        return folder_schema.dump(folder)

class FolderResource(Resource):
    @jwt_required()
    def patch(self, id):
        try:
            args = folder_schema.load(request.json, partial=True)
        except ValidationError as err:
            return {"message": "Validation errors", "errors": err.messages}, 400

        folder = FolderModel.query.filter_by(id=id).first()
        if not folder:
            abort(404, message="Folder not found")

        if(current_user.id != folder.owner_id):
            abort(403, message="Unauthorized")

        name = args.get("name")
        parent_id = args.get("parent_id")
        if not name and not parent_id:
            abort(400, message="No fields to update")

        if name:
            colliding_folder = FolderModel.query.filter_by(name=name, owner_id=current_user.id).one_or_none()
            if colliding_folder:
                abort(400, message="Folder with this name already exists")
            folder.name = name if name else folder.name

        if parent_id:
            new_parent = FolderModel.query.filter_by(
                id=args["parent_id"], owner_id=current_user.id).one_or_none()
            if not new_parent:
                abort(404, message="Parent folder not found")
            folder.parent_id = args["parent_id"]

        if name or parent_id:
            folder.updated_at = func.now()

        db.session.commit()