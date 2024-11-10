import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_JWT_SECRET_KEY = os.getenv('FLASK_JWT_SECRET', 's3cr3t5')
    SECRET_KEY = os.getenv('SECRET_KEY', 's3cr3t5')
