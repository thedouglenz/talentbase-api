from flask_restful import fields

user_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String,
}

auth_fields = {
    'token': fields.String,
}