from flask import Flask
import datetime
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager
)
from flask_wtf.csrf import CSRFProtect

app = Flask('__main__',template_folder = 'templates')

CORS(app,resources={r"/*": {"origins": "*"}})
app.config['SECRET_KEY']='super-secret'
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)

jwt = JWTManager(app)
csrf = CSRFProtect(app)