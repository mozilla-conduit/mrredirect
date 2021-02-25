from mrredirect.app import app
from mrredirect.models import Review, ReviewRequest
from mrredirect.storage import db


def dbinit():
    with app.app_context():
        db.create_all()
        db.session.commit()


if __name__ == "__main__":
    dbinit()
