from flask import flash,Blueprint,session ,render_template, redirect, url_for, request, abort
from flask_login import login_user, logout_user, current_user, login_required
from extensions import db,bcrypt,login_manager
from models import User, Room, UserRole
from forms import RegisterForm, LoginForm

import os
import uuid
from dotenv import load_dotenv
from flask_dance.consumer import oauth_authorized
from flask_dance.contrib.github import make_github_blueprint, github

load_dotenv()


auth_bp = Blueprint("auth",__name__,url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).filter_by(email=form.email.data))

        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            session.permanent = True
            return redirect(url_for('main.home'))
        else:
            form.email.errors.append("Błędny adres e-mail lub hasło.")

    return render_template('login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

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

        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


github_bp = make_github_blueprint(
    client_id=os.environ.get("GITHUB_OAUTH_CLIENT_ID"),
    client_secret=os.environ.get("GITHUB_OAUTH_CLIENT_SECRET"),
    scope="user:email",
    redirect_to="main.dashboard"
)


@oauth_authorized.connect_via(github_bp)
def github_logged_in(blueprint, token):
    if not token:
        flash("Nie udało się zalogować przez GitHub.", "danger")
        return False

    resp = github.get("/user")
    if not resp.ok:
        flash("Błąd podczas pobierania profilu z GitHuba.", "danger")
        return False
    github_info = resp.json()

    email_resp = github.get("/user/emails")
    if email_resp.ok:
        emails = email_resp.json()
        email = next((e["email"] for e in emails if e["primary"]), None)
    else:
        email = github_info.get("email")

    if not email:
        flash("Twój profil GitHub nie udostępnia zweryfikowanego adresu e-mail.", "danger")
        return False

    user = User.query.filter_by(email=email).first()

    if not user:
        base_username = github_info.get("login", "github_user")
        username = base_username

        while User.query.filter_by(username=username).first():
            username = f"{base_username}_{uuid.uuid4().hex[:4]}"

        full_name = github_info.get("name") or "Użytkownik GitHub"
        name_parts = full_name.split(" ", 1)
        name = name_parts[0]
        surname = name_parts[1] if len(name_parts) > 1 else "OAuth"

        user = User(
            username=username,
            email=email,
            name=name,
            surname=surname,
            password_hash=bcrypt.generate_password_hash(uuid.uuid4().hex).decode('utf-8'),
            role=UserRole.GUEST,
            banned=False
        )
        db.session.add(user)
        db.session.commit()

    if user.banned:
        flash("Twoje konto zostało zablokowane przez administratora.", "danger")
        return redirect(url_for("auth.login"))

    login_user(user)
    flash(f"Witaj {user.name}! Zalogowano pomyślnie przez GitHub.", "success")
    return False