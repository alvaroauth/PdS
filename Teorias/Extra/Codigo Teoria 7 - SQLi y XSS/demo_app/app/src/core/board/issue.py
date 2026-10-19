from datetime import datetime

from src.core.database import db

issue_labels = db.Table(
    "issue_labels",
    db.Column("issue_id", db.Integer, db.ForeignKey("issues.id"), primary_key=True),
    db.Column("label_id", db.Integer, db.ForeignKey("labels.id"), primary_key=True),
)


class Issue(db.Model):

    __tablename__ = "issues"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    email = db.Column(db.String(50))
    title = db.Column(db.String(100))
    description = db.Column(db.String(255))
    status = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship("User", back_populates="issues")
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now)
    inserted_at = db.Column(db.DateTime, default=datetime.now())

    labels = db.relationship("Label", secondary=issue_labels)
