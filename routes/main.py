from flask import Blueprint, render_template, redirect, url_for, request, abort
from flask_login import login_user, logout_user, current_user, login_required


main_bp = Blueprint("main",__name__)

@main_bp.route('/')
@login_required
def home():
    return redirect(url_for("main.dashboard"))



@main_bp.route('/dashboard')
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
        <a href="{url_for('auth.logout')}"> Wyloguj mnie stąd</a>
    """