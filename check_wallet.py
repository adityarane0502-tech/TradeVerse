from app import app
from models import db, User


with app.app_context():
    user = User.query.first()

    if user:
        print("User:", user.name)
        print("Email:", user.email)
        print("Virtual Balance:", user.virtual_balance)
    else:
        print("No user found.")