
import re
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
import marshmallow as ma
from sqlalchemy import exc
from db import db
from modelos import User

blp = Blueprint("Auth", __name__, description="API para gestionar registro y login de usuarios")

class UserSignUpSchema(ma.Schema):
    username = ma.fields.String(required=True, validate=[ma.validate.Length(min=5, max=200)])
    email = ma.fields.String(required=True, validate=[ma.validate.Length(min=5, max=200)])
    password1 = ma.fields.String(required=True, validate=[ma.validate.Length(min=8, max=200)])
    password2 = ma.fields.String(required=True, validate=[ma.validate.Length(min=8, max=200)])

    @ma.validates("password1")
    def validate_password(self, value):
        if not re.search(r'\d', value):
            raise ma.ValidationError("Password password must have at least a digit")
        if not re.search(r'[a-zA-Z]', value):
            raise ma.ValidationError("Password must have at least a letter")
        if not re.search(r'[^a-zA-Z\d]', value):
            raise ma.ValidationError("Password must have at least one non-alphanumeric character")

class UserLoginSchema(ma.Schema):
    username = ma.fields.String(required=True)
    password = ma.fields.String(required=True)

class UserLoginResponseSchema(ma.Schema):
    access_token = ma.fields.String()

@blp.route("/api/auth/signup")
class VistaSignUp(MethodView):
    @blp.arguments(UserSignUpSchema)
    @blp.response(201)
    def post(self, user):
        username = user['username']
        email = user['email']
        password1 = user['password1']
        password2 = user['password2']

        if(password1 != password2):
            abort(422, message = "Password1 and password2 are not equal")

        hashed_password = generate_password_hash(password1)
        new_user = User(
            username = username,
            email = email,
            password = hashed_password
        )

        try:
            db.session.add(new_user)
            db.session.commit()
        except exc.IntegrityError as e:
            db.session.rollback()
            err = str(e.orig)
            if '"user_username_key"' in err:
                abort(409, message = "Provided username already exists")
            elif '"user_email_key"' in err:
                abort(409, message = "Provided email already exists")
            else:
                raise

        return {
            'message': 'Sign up succesfull'
        }


@blp.route("/api/auth/login")
class VistaLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    @blp.response(200, UserLoginResponseSchema)
    @blp.alt_response(401, description="Incorrect password")
    @blp.alt_response(404, description="User not found")
    def post(self, user):
        username = user['username']
        password = user['password']

        current_user = User.query.filter((User.username==username) | (User.email==username)).first()

        if not current_user:
            abort(404, message = "User not found")
        if not check_password_hash(current_user.password, password):
            abort(401, message = "Incorrect password")

        access_token = create_access_token(identity=current_user.id)

        return {
            'access_token': access_token
        }
