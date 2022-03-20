from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app_settings.settings import settings

db = SQLAlchemy()


def init_db(app: Flask):
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL
    db.init_app(app)

