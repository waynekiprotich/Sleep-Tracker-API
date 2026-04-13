from app import app
from models import db, User, SleepEntry
from datetime import datetime, timedelta

with app.app_context():
    db.drop_all()
    db.create_all()

    user1 = User(username="wayne", email="wayne@gmail.com")
    user1.password = "12345"

    db.session.add(user1)
    db.session.commit()

    sleep1 = SleepEntry(
        sleep_time=datetime.now() - timedelta(hours=8),
        wake_time=datetime.now(),
        quality=8,
        notes="Good sleep",
        user_id=user1.id
    )

    db.session.add(sleep1)
    db.session.commit()

    print("Seeded successfully")