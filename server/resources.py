from flask import request
from flask_jwt_extended import (JWTManager, jwt_required,
                                create_access_token, get_jwt_identity)
from flask_restful import Resource, Api

from server import app
from server.models import User

api = Api(app)
jwt = JWTManager(app)

class Login(Resource):
    def post(self):
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        user = User.query.filter_by(username=username).first()
        if not user:
            return {'msg': 'No such user'}, 401
        if not user.verify_password(password):
            return {'msg': 'Invalid password'}, 401
        access_token = create_access_token(identity=username)
        return {'access_token': access_token}

class Profile(Resource):
    @jwt_required
    def get(self):
        username = get_jwt_identity()
        return {'username': username}

api.add_resource(Login, '/login')
api.add_resource(Profile, '/profile')
