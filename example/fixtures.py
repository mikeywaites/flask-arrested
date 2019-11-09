from datetime import datetime


def run():
    from example.app import app
    from example.models import db, Character

    created_at = datetime.utcnow().replace(
        month=1, day=1, hour=10, minute=0, second=0, microsecond=0
    )

    with app.test_request_context():
        db.drop_all()
        db.create_all()
        db.session.add(Character(id=1, created_at=created_at, name="Obe Wan"))
        db.session.add(Character(id=2, created_at=created_at, name="Luke Skywalker"))
        db.session.add(Character(id=3, created_at=created_at, name="Yoda"))
        db.session.add(Character(id=4, created_at=created_at, name="Darth Vader"))
        db.session.add(Character(id=5, created_at=created_at, name="Princess Leia"))

        db.session.commit()


if __name__ == "__main__":

    run()
