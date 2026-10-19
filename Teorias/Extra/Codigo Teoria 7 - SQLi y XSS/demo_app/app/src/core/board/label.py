from datetime import datetime

from src.core.database import db


class Label(db.Model):

    __tablename__ = "labels"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String(50))
    description = db.Column(db.String(100))
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now)
    inserted_at = db.Column(db.DateTime, default=datetime.now())
