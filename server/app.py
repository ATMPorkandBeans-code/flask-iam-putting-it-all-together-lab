#!/usr/bin/env python3

from flask import request, session, send_from_directory
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
# from pathlib import Path

from config import app, db, api
from models import User, Recipe, UserSchema, RecipeSchema

# BASE_DIR = Path(__file__).resolve().parent.parent
# CLIENT_BUILD_DIR = BASE_DIR / 'client' / 'build'

class Signup(Resource):
   def post(self):
        request_json = request.get_json()

        # id = request_json.get('id')
        username = request_json.get('username')
        password = request_json.get('password')
        image_url = request_json.get('image_url')
        bio = request_json.get('bio')

        user = User(
            # id=id,
            username=username,
            image_url=image_url,
            bio=bio
        )
        user.password_hash = password
        
        try:
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return UserSchema().dump(user), 201
        except IntegrityError:
            return {'error': '422 Unprocessable Entity'}, 422



class CheckSession(Resource):
    def get(self):

        if session.get('user_id'):
            user = User.query.filter(User.id == session['user_id']).first()
            return UserSchema().dump(user), 200
        
        return {'error': '401 Unauthorized'}, 401

class Login(Resource):
    def post(self):
        username = request.get_json()['username']
        password = request.get_json()['password']

        user = User.query.filter(User.username == username).first()

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return UserSchema().dump(user), 200
        
        return {'error': '401 Unauthorized'}, 401

class Logout(Resource):
    def delete(self):

        if session.get('user_id'):
            session['user_id'] = None
            return {}, 204
        return {'error': '401 Unauthorized'}, 401

class RecipeIndex(Resource):
    def get(self):
        if session.get('user_id'):
            recipes = [RecipeSchema().dump(r) for r in Recipe.query.all()]
            return recipes, 200
        return {'error': '401 Unauthorized'}, 401
    
    def post(self):
        if session.get('user_id'):
            request_json = request.get_json()

            recipe = Recipe(
                title = request_json.get('title'),
                instructions = request_json.get('instructions'),
                minutes_to_complete = request_json.get('minutes_to_complete'),
                user_id=session.get('user_id')
            )

            try:
                db.session.add(recipe)
                db.session.commit()
                return RecipeSchema().dump(recipe), 201

            except IntegrityError:
                return {'error': '422 Unprocessable Entity'}, 422
        else:  
            return {'error': '401 Unauthorized'}, 401

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

# @app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
# def serve_react(path):
#     if CLIENT_BUILD_DIR.exists():
#         if path and (CLIENT_BUILD_DIR / path).exists():
#             return send_from_directory(str(CLIENT_BUILD_DIR), path)
#         return send_from_directory(str(CLIENT_BUILD_DIR), 'index.html')
#     return {
#         'error': 'React build not found. Run npm install && npm run build in client'
#     }, 404


if __name__ == '__main__':
    app.run(port=5555, debug=True)