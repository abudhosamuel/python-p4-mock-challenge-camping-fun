#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return ''


# GET /campers - Retrieve all campers
@app.route('/campers', methods=['GET'])
def get_campers():
    campers = Camper.query.all()
    return jsonify([camper.to_dict(only=('id', 'name', 'age')) for camper in campers])


# GET /campers/<int:id> - Retrieve a single camper by ID
@app.route('/campers/<int:id>', methods=['GET'])
def get_camper(id):
    camper = db.session.get(Camper, id)
    if camper:
        return jsonify(camper.to_dict(only=('id', 'name', 'age', 'signups')))
    else:
        return jsonify({"error": "Camper not found"}), 404


# POST /campers - Create a new camper
@app.route('/campers', methods=['POST'])
def create_camper():
    data = request.get_json()
    try:
        camper = Camper(name=data['name'], age=data['age'])
        db.session.add(camper)
        db.session.commit()
        return jsonify(camper.to_dict(only=('id', 'name', 'age')))
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400


# PATCH /campers/<int:id> - Update an existing camper by ID
@app.route('/campers/<int:id>', methods=['PATCH'])
def update_camper(id):
    camper = db.session.get(Camper, id)
    if not camper:
        return jsonify({"error": "Camper not found"}), 404

    data = request.get_json()
    try:
        if 'name' in data:
            if data['name'] == '':
                raise ValueError("Camper must have a name")
            camper.name = data['name']
        if 'age' in data:
            camper.age = data['age']
        db.session.commit()
        return jsonify(camper.to_dict(only=('id', 'name', 'age')))
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400


# GET /activities - Retrieve all activities
@app.route('/activities', methods=['GET'])
def get_activities():
    activities = Activity.query.all()
    return jsonify([activity.to_dict(only=('id', 'name', 'difficulty')) for activity in activities])


# DELETE /activities/<int:id> - Delete an activity by ID (cascades to delete related signups)
@app.route('/activities/<int:id>', methods=['DELETE'])
def delete_activity(id):
    activity = db.session.get(Activity, id)
    if activity:
        db.session.delete(activity)
        db.session.commit()
        return '', 204
    else:
        return jsonify({"error": "Activity not found"}), 404


# POST /signups - Create a new signup (camper signs up for an activity)
@app.route('/signups', methods=['POST'])
def create_signup():
    data = request.get_json()
    try:
        if data['time'] < 0 or data['time'] > 23:
            raise ValueError("Time must be between 0 and 23")
        signup = Signup(camper_id=data['camper_id'], activity_id=data['activity_id'], time=data['time'])
        db.session.add(signup)
        db.session.commit()
        return jsonify(signup.to_dict()), 201
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400


if __name__ == '__main__':
    app.run(port=5555, debug=True)
