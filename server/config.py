import os
from pathlib import Path

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

database_url = os.environ.get('DATABASE_URL')
if not database_url:
    database_path = BASE_DIR / 'app.db'
    database_url = f'sqlite:///{database_path}'

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
if os.environ.get('FLASK_ENV') == 'production':
    app.config['SESSION_COOKIE_SECURE'] = True

app.json.compact = False

metadata = MetaData(naming_convention={
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
})

db = SQLAlchemy(metadata=metadata)

migrate = Migrate(app, db)
db.init_app(app)

bcrypt = Bcrypt(app)

api = Api(app)
