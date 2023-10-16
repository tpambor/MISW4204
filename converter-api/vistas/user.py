
from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, create_access_token
import marshmallow as ma
from db import db
from modelos import User

blp = Blueprint("User", __name__, description="API para gestionar registro y login de usuarios")

class UserAuthSchema(ma.Schema):
    username = ma.fields.String(required=True)
    email = ma.fields.String(required=True)
    password1 = ma.fields.String(required=True)
    password2 = ma.fields.String(required=True)
  
@blp.route("/api/auth/signup")
class VistaSignUp(MethodView):
  @blp.arguments(UserAuthSchema)
  def post(self, user):
    username = user['username']
    email = user['email']
    password1 = user['password1']
    password2 = user['password2']

    # Verifica si el username ya existe
    existing_user_username = User.query.filter_by(username=username).first()

    # Verifica si el email ya existe
    existing_user_email = User.query.filter_by(email=email).first()
    
    if(existing_user_username):
       abort(400, message="username already exists.")
    if(existing_user_email):
       abort(400, message="email already exists.")
    if(password1 != password2):
       abort(400, message="password1 and password2 aren't equals.")

    else:
        new_user = User(
            username = username,
            email = email,
            password = password1
        )
        db.session.add(new_user)
        db.session.commit()
        return {
            'message': 'Success sign up!'
        }, 201