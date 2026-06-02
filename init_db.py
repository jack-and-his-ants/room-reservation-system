from app import app, db, User, UserRole,Room,Reservation
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta

def setup_db():
    with (app.app_context()):
        bcrypt = Bcrypt()

        print("Clearing previous db...")
        db.drop_all() # clear previous db
        print("finished")

        print("Creating new db ...")
        db.create_all() # create a new db
        print("finished")

        hash_admin = bcrypt.generate_password_hash('admin').decode("utf-8")
        hash_manager = bcrypt.generate_password_hash('manager').decode("utf-8")
        hash_employee = bcrypt.generate_password_hash("employee").decode("utf-8")
        hash_guest = bcrypt.generate_password_hash('guest').decode('utf-8')

        admin = User(
            username="admin",
            name="Michał",
            surname="Kowalski",
            email="admin@firma.pl",
            password_hash=hash_admin,
            role=UserRole.ADMIN,
            manager_id = None
        )

        manager = User(
            username="manager",
            name="Andrzej",
            surname="Nowak",
            email="a.nowak@firma.pl",
            password_hash=hash_manager,
            role=UserRole.MANAGER,
            manager_id = None
        )
        db.session.add_all([admin,manager])
        db.session.flush()
        employee = User(
            username="employee",
            name="Tomasz",
            surname="Wiśniewski",
            email="t.wisniewski@firma.pl",
            password_hash=hash_employee,
            role=UserRole.EMPLOYEE,
            manager_id=manager.id
        )

        guest = User(
            username="guest",
            name="Jacek",
            surname="Kisiel",
            email="jacek@gosc.pl",
            password_hash=hash_guest,
            role=UserRole.GUEST,
            manager_id=None
        )
        db.session.add_all([employee,guest])
        db.session.flush()
        db.session.commit()

        room_1 = Room(
            number=1,
            name="Conference room",
            manager_id=manager.id
        )

        room_2 = Room(
            number=2,
            name="Creative space",
            manager_id=manager.id
        )
        db.session.add_all([room_1,room_2])
        db.session.flush()
        db.session.commit()

        reservation_1 = Reservation(
            datetime_start=datetime.now() + timedelta(days=1, hours=10),
            datetime_end=datetime.now() + timedelta(days=1, hours=12),
            room_id=room_1.id,
            user_id=employee.id,
            accepted=True
        )

        reservation_2 = Reservation(
            datetime_start=datetime.now() + timedelta(days=2, hours=14),
            datetime_end=datetime.now() + timedelta(days=2, hours=15),
            room_id=room_2.id,
            user_id=guest.id,
            accepted=False
        )

        db.session.add_all([reservation_1, reservation_2])

        db.session.commit()

if __name__ == '__main__':
    setup_db()