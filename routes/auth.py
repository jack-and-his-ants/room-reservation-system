from flask import Blueprint,session ,render_template, redirect, url_for, request, abort
from flask_login import login_user, logout_user, current_user, login_required
from extensions import db,bcrypt,login_manager
from models import User, Room, UserRole
from forms import RegisterForm, LoginForm

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

