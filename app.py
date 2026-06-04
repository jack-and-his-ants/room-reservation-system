import os
import dotenv
from flask import Flask

from extensions import db, bcrypt, login_manager
from models import User

from routes.main import main_bp
from routes.auth import auth_bp
from routes.admin import admin_blueprint

from datetime import timedelta

app = Flask(__name__)
dotenv.load_dotenv()

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI")
app.config['SECRET_KEY'] = os.environ.get("APP_SECRET_KEY")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)

db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    user = db.session.get(User, int(user_id))
    if user and user.banned:
        return None
    return user

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_blueprint)

if __name__ == '__main__':
    app.run(debug=True)