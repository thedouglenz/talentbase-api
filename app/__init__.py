from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()
api = Api(prefix='/api')

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from . import resources

        api.add_resource(resources.UsersResource, '/users/')
        api.add_resource(resources.UserResource, '/users/<int:id>')

        api.init_app(app)

    print(api.blueprint)
    return app