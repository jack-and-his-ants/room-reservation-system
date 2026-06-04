from flask import Blueprint, render_template, redirect, url_for, request, abort
from flask_login import login_required, current_user
from extensions import db
from models import User, Room, UserRole
from forms import AdminUserEditForm, RoomForm
from functools import wraps

admin_blueprint = Blueprint('admin',__name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin_blueprint.route('/')
@login_required
@admin_required
def admin_panel():
    return render_template('admin/dashboard.html')

@admin_blueprint.route('/rooms', methods=['GET', 'POST'])
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
        return redirect(url_for('admin.admin_rooms'))

    rooms = db.session.scalars(db.select(Room)).all()
    return render_template('admin/rooms.html', rooms=rooms, form=form)


@admin_blueprint.route('/rooms/delete/<int:room_id>')
@login_required
@admin_required
def delete_room(room_id):
    room = db.get_or_404(Room, room_id)
    db.session.delete(room)
    db.session.commit()
    return redirect(url_for('admin.admin_rooms'))

@admin_blueprint.route('/users')
@login_required
@admin_required
def admin_users():
    users = db.session.scalars(db.select(User)).all()
    return render_template('admin/users.html', users=users)

@admin_blueprint.route('/users/toggle-ban/<int:user_id>')
@login_required
@admin_required
def toggle_ban(user_id):
    user = db.get_or_404(User, user_id)

    if user.id == current_user.id:
        return "Nie możesz zbanować własnego konta!", 400

    user.banned = not user.banned
    db.session.commit()
    return redirect(url_for('admin.admin_users'))

@admin_blueprint.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
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
        return redirect(url_for('admin.admin_users'))

    if request.method == 'GET':
        form.role.data = user.role.name

    return render_template('admin/edit_user.html', form=form, user=user)

