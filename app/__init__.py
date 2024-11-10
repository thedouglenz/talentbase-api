from flask import Flask
from flask_restful import Api
from dotenv import load_dotenv

from .database import db
from .extensions import jwt, migrate, ma

load_dotenv()

api = Api(prefix='/api')

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    with app.app_context():
        # Hook up the restful routes 
        from . import resources
        api.add_resource(resources.UsersResource, '/users/')
        api.add_resource(resources.UserResource, '/users/<int:id>')
        api.add_resource(resources.LoginResource, '/login/')
        api.add_resource(resources.FoldersResource, '/folders/')
        api.add_resource(resources.FolderResource, '/folders/<int:id>')

        api.init_app(app)

    return app