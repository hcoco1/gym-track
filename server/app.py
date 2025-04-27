#!/usr/bin/env python3

# Standard library imports

# Remote library imports
from flask import request, jsonify, session
from flask_restful import Resource
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

# Local imports
from config import app, db, api

# Add your model imports

from models import User

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Optional: default login view

# Views go here!

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route to register a new user
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409

    new_user = User(
        username=username,
        password_hash=generate_password_hash(password)
    )

    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)
    return jsonify(new_user.to_dict()), 201

# Route to login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify(user.to_dict()), 200

    return jsonify({"error": "Invalid credentials"}), 401

# Route to check who is logged in
@app.route('/check_session')
def check_session():
    if current_user.is_authenticated:
        return jsonify(current_user.to_dict()), 200
    return jsonify({"error": "Unauthorized"}), 401

# Route to logout
@app.route('/logout', methods=['DELETE'])
@login_required
def logout():
    logout_user()
    return {}, 204



@app.route('/')
def index():
    return '<h1>Project Server</h1>'


if __name__ == '__main__':
    app.run(port=5555, debug=True)

