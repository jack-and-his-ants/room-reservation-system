# routes/reservations.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Room, Reservation,User,UserRole
from datetime import datetime, timedelta

reservations_bp = Blueprint('reservations', __name__, url_prefix='/reservations')


@reservations_bp.route('/book', methods=['GET', 'POST'])
@login_required
def book_room():
    rooms = db.session.scalars(db.select(Room)).all()
    available_slots = []
    selected_data = {}

    if request.method == 'POST':
        room_id = int(request.form.get('room_id'))
        date_str = request.form.get('date')
        duration = int(request.form.get('duration'))  # w minutach

        if date_str:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            available_slots = get_free_slots(room_id, target_date, duration)
            selected_data = {
                'room_id': room_id,
                'date': date_str,
                'duration': duration
            }

    return render_template('reservations/book.html',
                           rooms=rooms,
                           slots=available_slots,
                           selected_data=selected_data)


def get_free_slots(room_id, date, duration_min):
    """Algorytm szukający wolnych okien czasowych"""
    slots = []
    start_time = datetime.combine(date, datetime.strptime("08:00", "%H:%M").time())
    end_working_day = datetime.combine(date, datetime.strptime("20:00", "%H:%M").time())

    existing_bookings = db.session.scalars(
        db.select(Reservation).where(
            Reservation.room_id == room_id,
            Reservation.datetime_start >= start_time,
            Reservation.datetime_end <= end_working_day,
            Reservation.accepted == True
        )
    ).all()

    current_slot = start_time
    while current_slot + timedelta(minutes=duration_min) <= end_working_day:
        slot_end = current_slot + timedelta(minutes=duration_min)

        collision = False
        for b in existing_bookings:
            if not (slot_end <= b.datetime_start or current_slot >= b.datetime_end):
                collision = True
                break

        if not collision:
            slots.append(current_slot)

        current_slot += timedelta(minutes=30)

    return slots


# Dodaj tę trasę w routes/reservations.py przed @reservations_bp.route('/confirm')

@reservations_bp.route('/summary', methods=['POST'])
@login_required
def booking_summary():
    room_id = int(request.form.get('room_id'))
    start_dt_str = request.form.get('start_dt')
    duration = int(request.form.get('duration'))

    room = db.session.get(Room, room_id)
    start_dt = datetime.strptime(start_dt_str, '%Y-%m-%d %H:%M:%S')
    end_dt = start_dt + timedelta(minutes=duration)

    return render_template('reservations/summary.html',
                           room=room,
                           start_dt=start_dt,
                           end_dt=end_dt,
                           duration=duration,
                           start_dt_str=start_dt_str)
@reservations_bp.route('/confirm', methods=['POST'])
@login_required
def confirm_booking():
    room_id = request.form.get('room_id')
    start_dt = datetime.strptime(request.form.get('start_dt'), '%Y-%m-%d %H:%M:%S')
    duration = int(request.form.get('duration'))

    new_res = Reservation(
        room_id=room_id,
        user_id=current_user.id,
        datetime_start=start_dt,
        datetime_end=start_dt + timedelta(minutes=duration),
        accepted=(current_user.role!=UserRole.GUEST)
    )

    db.session.add(new_res)
    db.session.commit()
    flash("Rezerwacja zakończona sukcesem!")
    return redirect(url_for('main.dashboard'))


@reservations_bp.route('/manage', methods=['GET'])
@login_required
def manage_reservations():
    today = datetime.combine(datetime.now().date(), datetime.min.time())

    lists = {
        'own': [],
        'admin_all': [],
        'subordinates': [],
        'managed_rooms': []
    }

    lists['own'] = db.session.scalars(
        db.select(Reservation)
        .where(Reservation.user_id == current_user.id, Reservation.datetime_start >= today)
        .order_by(Reservation.datetime_start)
    ).all()

    if current_user.role == UserRole.ADMIN:
        lists['admin_all'] = db.session.scalars(
            db.select(Reservation)
            .where(Reservation.user_id != current_user.id, Reservation.datetime_start >= today)
            .order_by(Reservation.datetime_start)
        ).all()

    elif current_user.role == UserRole.MANAGER:
        sub_ids = db.session.scalars(
            db.select(User.id).where(User.manager_id == current_user.id)
        ).all()

        if sub_ids:
            lists['subordinates'] = db.session.scalars(
                db.select(Reservation)
                .where(Reservation.user_id.in_(sub_ids), Reservation.datetime_start >= today)
                .order_by(Reservation.datetime_start)
            ).all()

        room_ids = db.session.scalars(
            db.select(Room.id).where(Room.manager_id == current_user.id)
        ).all()

        if room_ids:
            excluded_user_ids = [current_user.id] + list(sub_ids)
            lists['managed_rooms'] = db.session.scalars(
                db.select(Reservation)
                .where(
                    Reservation.room_id.in_(room_ids),
                    Reservation.user_id.not_in(excluded_user_ids),
                    Reservation.datetime_start >= today
                )
                .order_by(Reservation.datetime_start)
            ).all()

    return render_template('reservations/manage.html', lists=lists, UserRole=UserRole)



@reservations_bp.route('/<int:res_id>/accept', methods=['POST'])
@login_required
def accept_res(res_id):
    # Tylko admin może akceptować w tym widoku (lub manager jeśli dasz mu uprawnienia)
    if current_user.role != UserRole.ADMIN and current_user.role != UserRole.MANAGER:
        flash("Brak uprawnień!", "danger")
        return redirect(url_for('reservations.manage_reservations'))

    res = db.session.get(Reservation, res_id)
    if res:
        res.accepted = True
        db.session.commit()
        flash(f"Rezerwacja nr {res.id} została zaakceptowana.", "success")
    return redirect(url_for('reservations.manage_reservations'))


@reservations_bp.route('/<int:res_id>/reject', methods=['POST'])
@login_required
def reject_res(res_id):
    if current_user.role != UserRole.ADMIN and current_user.role != UserRole.MANAGER:
        flash("Brak uprawnień!", "danger")
        return redirect(url_for('reservations.manage_reservations'))

    res = db.session.get(Reservation, res_id)
    if res:
        res.accepted = False
        db.session.commit()
        flash(f"Cofnięto akceptację rezerwacji nr {res.id}.", "warning")
    return redirect(url_for('reservations.manage_reservations'))


@reservations_bp.route('/<int:res_id>/delete', methods=['POST'])
@login_required
def delete_res(res_id):
    res = db.session.get(Reservation, res_id)
    if not res:
        return redirect(url_for('reservations.manage_reservations'))

    if current_user.role == UserRole.ADMIN or res.user_id == current_user.id or current_user.role == UserRole.MANAGER:
        db.session.delete(res)
        db.session.commit()
        flash("Rezerwacja została usunięta.", "info")
    else:
        flash("Nie możesz usunąć cudzej rezerwacji!", "danger")

    return redirect(url_for('reservations.manage_reservations'))