import os
import dotenv
from flask import Flask

from extensions import db, bcrypt, login_manager
# MODYFIKACJA: Dodano UserRole do importu z modeli
from models import User, UserRole

from routes.main import main_bp
from routes.auth import auth_bp
from routes.admin import admin_blueprint
from routes.reservations import reservations_bp

from datetime import timedelta

app = Flask(__name__)
dotenv.load_dotenv()

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI")
app.config['SECRET_KEY'] = os.environ.get("APP_SECRET_KEY")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)

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

# ====================================================================
# DODANO: Globalny wtrysk Enuma UserRole do wszystkich szablonów Jinja2
# ====================================================================
@app.context_processor
def inject_user_role():
    return dict(UserRole=UserRole)

# Blueprints
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_blueprint)
app.register_blueprint(reservations_bp)

if __name__ == '__main__':
    app.run(debug=True)