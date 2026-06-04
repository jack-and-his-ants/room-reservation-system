import os
import dotenv
from datetime import datetime
import enum
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_bcrypt import Bcrypt

app = Flask(__name__)
dotenv.load_dotenv()

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get("APP_SECRET_KEY")

# Create SQLAlchemy instance
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


class UserRole(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = 'employee'
    GUEST = 'guest'


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(320), unique=True)
    surname = db.Column(db.String(30), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    banned = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"id: {self.id} | username: {self.username} | role: {self.role} | banned: {self.banned}"

    def get_id(self):
        return str(self.id)


class Room(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(40), nullable=False)


class Reservation(db.Model):
    __tablename__ = 'reservation'
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.now, nullable=False)
    datetime_start = db.Column(db.DateTime, nullable=False)
    datetime_end = db.Column(db.DateTime, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    accepted = db.Column(db.Boolean, nullable=False, default=False)


@login_manager.user_loader
def load_user(user_id):
    user = db.session.get(User, int(user_id))
    if user and user.banned:
        return None
    return user


from forms import LoginForm, RegisterForm, AdminUserEditForm, RoomForm


@app.route('/')
@login_required
def home():
    return redirect(url_for("dashboard"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).filter_by(email=form.email.data))

        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            form.email.errors.append("Błędny adres e-mail lub hasło.")

    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegisterForm()

    if form.validate_on_submit():
        base_username = form.email.data.split('@')[0]
        username = base_username

        counter = 1
        while db.session.scalar(db.select(User).filter_by(username=username)):
            username = f"{base_username}{counter}"
            counter += 1

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        new_user = User(
            username=username,
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            password_hash=hashed_password,
            role=UserRole.GUEST
        )
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    return f"""
        <h1>🔒 Panel Testowy Autoryzacji</h1>
        <p>Status: <strong>Zalogowano pomyślnie!</strong></p>
        <hr>
        <ul>
            <li><strong>Imię i nazwisko:</strong> {current_user.name} {current_user.surname}</li>
            <li><strong>Wygenerowany login (username):</strong> {current_user.username}</li>
            <li><strong>Email:</strong> {current_user.email}</li>
            <li><strong>Twoja rola w systemie:</strong> <span style="color: blue;">{current_user.role.value}</span></li>
        </ul>
        <hr>
        <a href="{url_for('logout')}">➡️ Wyloguj mnie stąd</a>
    """


@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    return render_template('admin/dashboard.html')


@app.route('/admin/rooms', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_rooms():
    form = RoomForm()
    if form.validate_on_submit():
        new_room = Room(
            number=form.number.data,
            name=form.name.data,
            manager_id=form.manager_id.data
        )
        db.session.add(new_room)
        db.session.commit()
        return redirect(url_for('admin_rooms'))

    rooms = db.session.scalars(db.select(Room)).all()
    return render_template('admin/rooms.html', rooms=rooms, form=form)


@app.route('/admin/rooms/delete/<int:room_id>')
@login_required
@admin_required
def delete_room(room_id):
    room = db.get_or_404(Room, room_id)
    db.session.delete(room)
    db.session.commit()
    return redirect(url_for('admin_rooms'))


@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = db.session.scalars(db.select(User)).all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/users/toggle-ban/<int:user_id>')
@login_required
@admin_required
def toggle_ban(user_id):
    user = db.get_or_404(User, user_id)

    if user.id == current_user.id:
        return "Nie możesz zbanować własnego konta!", 400

    user.banned = not user.banned
    db.session.commit()
    return redirect(url_for('admin_users'))


@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = db.get_or_404(User, user_id)
    form = AdminUserEditForm(obj=user)

    if form.validate_on_submit():
        user.name = form.name.data
        user.surname = form.surname.data
        user.email = form.email.data
        user.role = UserRole[form.role.data]
        db.session.commit()
        return redirect(url_for('admin_users'))

    if request.method == 'GET':
        form.role.data = user.role.name

    return render_template('admin/edit_user.html', form=form, user=user)


if __name__ == '__main__':
    app.run(debug=True)