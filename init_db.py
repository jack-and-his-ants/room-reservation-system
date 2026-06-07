from datetime import datetime, timedelta, time

from app import app
from extensions import db, bcrypt
from models import User, UserRole, Room, Reservation


def setup_db():
    with app.app_context():

        print("Clearing previous db...")
        db.drop_all()
        print("finished")

        print("Creating new db ...")
        db.create_all()
        print("finished")

        hash_admin = bcrypt.generate_password_hash("admin").decode("utf-8")
        hash_manager = bcrypt.generate_password_hash("manager").decode("utf-8")
        hash_employee = bcrypt.generate_password_hash("employee").decode("utf-8")
        hash_guest = bcrypt.generate_password_hash("guest").decode("utf-8")

        # Tworzenie użytkowników
        admin = User(
            username="admin",
            name="admin",
            surname="admin",
            email="admin@firma.pl",
            password_hash=hash_admin,
            role=UserRole.ADMIN,
            manager_id=None,
        )

        manager = User(
            username="manager",
            name="Andrzej",
            surname="Nowak",
            email="a.nowak@firma.pl",
            password_hash=hash_manager,
            role=UserRole.MANAGER,
            manager_id=None,
        )
        db.session.add_all([admin, manager])
        db.session.flush()

        employee = User(
            username="employee",
            name="Tomasz",
            surname="Wiśniewski",
            email="t.wisniewski@firma.pl",
            password_hash=hash_employee,
            role=UserRole.EMPLOYEE,
            manager_id=manager.id,
        )

        guest = User(
            username="guest",
            name="Jacek",
            surname="Kisiel",
            email="jacek@gosc.pl",
            password_hash=hash_guest,
            role=UserRole.GUEST,
            manager_id=None,
        )
        db.session.add_all([employee, guest])
        db.session.flush()
        db.session.commit()

        # Tworzenie pokojów
        room_1 = Room(number=1, name="Conference room", manager_id=manager.id)
        room_2 = Room(number=2, name="Creative space", manager_id=manager.id)

        db.session.add_all([room_1, room_2])
        db.session.flush()
        db.session.commit()

        jutro = datetime.now().date() + timedelta(days=1)
        pojutrze = datetime.now().date() + timedelta(days=2)

        reservation_1 = Reservation(
            datetime_start=datetime.combine(jutro, time(10, 0)),  # 10:00
            datetime_end=datetime.combine(jutro, time(12, 0)),  # 12:00
            room_id=room_1.id,
            user_id=employee.id,
            accepted=True,
        )

        reservation_2 = Reservation(
            datetime_start=datetime.combine(pojutrze, time(14, 0)),  # 14:00
            datetime_end=datetime.combine(pojutrze, time(15, 0)),  # 15:00
            room_id=room_2.id,
            user_id=guest.id,
            accepted=False,
        )

        db.session.add_all([reservation_1, reservation_2])
        db.session.commit()
        print("DB initialized")


if __name__ == "__main__":
    setup_db()