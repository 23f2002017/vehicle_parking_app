from flask import current_app as app
from .database import db 
from datetime import datetime

# Models 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    parkings = db.relationship("Parking", backref="driver", lazy=True)

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.Text(6), nullable=False)
    price = db.Column(db.Float, nullable=False)
    spots = db.relationship("ParkingSpot", backref="lot", lazy=True)

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.String(20), nullable=False) 
    parkings = db.relationship("Parking", backref="spot", lazy=True) 

class Parking(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vehicle_reg_no = db.Column(db.String(10), nullable=False)
    parking_time = db.Column(db.DateTime, default=datetime.now())
    exit_time = db.Column(db.DateTime, nullable=True)
    cost = db.Column(db.Float, nullable=True) 

with app.app_context():
    db.create_all()    