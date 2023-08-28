from restaurant.models import table, item, User
from restaurant import db, app

for i in table:
    with app.app_context():
        db.session.add(i)
        db.session.commit()

for i in item:
    with app.app_context():
        db.session.add(i)
        db.session.commit()

with app.app_context():
    db.session.add(User(
        username = 'admin',
        fullname = 'admin',
        address = 'admin',
        phone_number = 1234567890,
        password = 'admin'
    ))
    db.session.commit()