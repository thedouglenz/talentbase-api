from flask_restful import Resource, reqparse, marshal_with, abort
from flask_httpauth import HTTPBasicAuth
from flask import g

from .models import UserModel, db
from .types import user_fields, auth_fields

user_args = reqparse.RequestParser()
user_args.add_argument('name', type=str, required=True, help="Name cannot be blank")
user_args.add_argument('email', type=str, required=True, help="Email cannot be blank")
user_args.add_argument('password', type=str)

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = UserModel.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = UserModel.query.filter_by(name=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

class UsersResource(Resource):
    @marshal_with(user_fields)
    def get(self):
        users = UserModel.query.all()
        return users

    @marshal_with(user_fields)
    def post(self):
        args = user_args.parse_args()
        if not args['password']:
            abort(400, message="New user registration requires password")
        user = UserModel(
            name = args['name'],
            email = args['email']
        )
        user.hash_password(args['password'])
        db.session.add(user)
        db.session.commit()
        return user, 201

class UserResource(Resource):

    @marshal_with(auth_fields)
    @auth.login_required
    def get_auth_token(self):
        token = g.user.generate_auth_token()
        return {'token': token.decode('ascii')}

    @marshal_with(user_fields)
    def get(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")
        return user

    @marshal_with(user_fields)
    @auth.login_required
    def patch(self, id):
        args = user_args.parse_args()
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")
        user.name = args["name"]
        user.email = args["email"]
        db.session.commit()
        return user

    @marshal_with(user_fields)
    def delete(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="User not found")
        db.session.delete(user)
        user.deleted = True
        db.session.commit()
        return user