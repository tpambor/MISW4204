
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
import marshmallow as ma
from db import db
from modelos import User

blp = Blueprint("Auth", __name__, description="API para gestionar registro y login de usuarios")

def passwordFormat(password):
    if len(password) < 8:
        return "Password should have at least 8 characters."
    if not any(char.isalpha() for char in password):
        return "Password should have at least a letter."
    if not any(char.isdigit() for char in password):
        return "Password password should have at least a digit."
    return None


class UserSignUpSchema(ma.Schema):
    username = ma.fields.String(required=True)
    email = ma.fields.String(required=True)
    password1 = ma.fields.String(required=True)
    password2 = ma.fields.String(required=True)

class UserLoginSchema(ma.Schema):
    username = ma.fields.String(required=True)
    password = ma.fields.String(required=True)


@blp.route("/api/auth/signup")
class VistaSignUp(MethodView):
  @blp.arguments(UserSignUpSchema)
  def post(self, user):
    username = user['username']
    email = user['email']
    password1 = user['password1']
    password2 = user['password2']

    # Verifica si el username ya existe
    existing_user_username = User.query.filter_by(username=username).first()

    # Verifica si el email ya existe
    existing_user_email = User.query.filter_by(email=email).first()
    
    # Verifica requisitos mínimos para la contraseña
    password_format = passwordFormat(password1)

    if(existing_user_username):
       abort(400, message = "Provided username already exists.")
    if(existing_user_email):
       abort(400, message = "Provided email already exists.")
    if(password1 != password2):
       abort(400, message = "Provided password1 and password2 aren't equals.")
    if(password_format):
       abort(400, message = password_format)

    else:
        hashed_password = generate_password_hash(password1)
        new_user = User(
            username = username,
            email = email,
            password = hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        return {
            'message': 'Success sign up!'
        }, 201


@blp.route("/api/auth/login")
class VistaLogin(MethodView):
  @blp.arguments(UserLoginSchema)
  def post(self, user):
        username = user['username']
        password = user['password']
        current_user = User.query.get(username)

        if not current_user:
           abort(401, message = "User doesn't found.")
        if not check_password_hash(current_user.password, password):
           abort(401, message = "Incorrect password.")

        access_token = create_access_token(identity=current_user.username)

        return {
            'access_token': access_token
        }, 200      