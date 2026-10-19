from datetime import datetime

from src.core.database import db


class User(db.Model):

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    issues = db.relationship("Issue", back_populates="user")
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now)
    inserted_at = db.Column(db.DateTime, default=datetime.now())
