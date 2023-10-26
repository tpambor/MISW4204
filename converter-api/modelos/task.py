from enum import IntEnum
from db import db


class TaskStatus(IntEnum):
    UPLOADED = 1
    PROCESSED = 2

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    fileName = db.Column(db.String, nullable=False)
    oldFormat = db.Column(db.String, nullable=False)
    newFormat = db.Column(db.String, nullable=False)
    finished = db.Column(db.DateTime)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
