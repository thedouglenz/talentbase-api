from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow

jwt = JWTManager()
migrate = Migrate()
ma = Marshmallow()