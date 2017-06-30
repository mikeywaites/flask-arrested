def init():
    from example.app import app as app_, db
    with app_.test_request_context() as ctx:
        db.create_all()


if __name__ == "__main__":
    init()
