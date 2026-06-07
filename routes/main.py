from flask import Blueprint, render_template, redirect, url_for, request, abort
from flask_login import login_user, logout_user, current_user, login_required
from models import User


main_bp = Blueprint("main",__name__)

@main_bp.route('/')
@login_required
def home():
    return redirect(url_for("main.dashboard"))



@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html",current_user=current_user)