from .database import db 
from flask_security import UserMixin, RoleMixin 

# Models 

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    fs_uniquifier = db.Column(db.String, unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)
    roles = db.relationship('Role', backref='users', secondary='users_roles')
    parkings = db.relationship("Parking", backref="driver", lazy=True)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    name = db.Column(db.String(20), unique=True, nullable=False)   
    description = db.Column(db.String(200), nullable=False)

class UsersRoles(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)   
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False) 

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.String(6), nullable=False)
    no_of_spots = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    spots = db.relationship("ParkingSpot", backref="lot", cascade="all,delete", lazy=True)
    parkings = db.relationship("Parking", backref="lot", cascade="all,delete", lazy=True) 

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spot_no = db.Column(db.Integer, nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey("parking_lot.id"), nullable=False) 
    status = db.Column(db.String(20), default="available") 
    parkings = db.relationship("Parking" , backref="spot", cascade="all,delete", lazy='subquery') 

class Parking(db.Model):        
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lot_id = db.Column(db.Integer, db.ForeignKey("parking_lot.id"), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey("parking_spot.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    vehicle_reg_no = db.Column(db.String(10), nullable=False)
    parking_time = db.Column(db.DateTime)
    exit_time = db.Column(db.DateTime, nullable=True)
    cost = db.Column(db.Float, nullable=True) 