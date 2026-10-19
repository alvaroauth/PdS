from src.core.database import db
from src.core.auth.user import User
# SQLi
from sqlalchemy import text

def list_users():
    return User.query.all()


def create_user(**kwargs):
    user = User(**kwargs)
    db.session.add(user)
    db.session.commit()

    return user


def find_user_by_email_and_pass(email, password):
    return User.query.filter(User.email == email, User.password == password).first()


def find_user_by_email(email):
    return User.query.filter(User.email == email).first()

# SQLi
def find_user_by_email_and_pass_sqli(email, password):
    sql = text("SELECT * from users WHERE email = '"+email+"' AND password = '"+password+"'")
    return db.session.execute(sql).first()