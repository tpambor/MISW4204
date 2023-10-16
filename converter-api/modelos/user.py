from db import db

class User(db.Model):
  username = db.Column(db.String, primary_key=True)
  password = db.Column(db.String, nullable=False)
  email = db.Column(db.String, nullable=False) 