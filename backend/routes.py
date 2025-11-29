import traceback
from flask import current_app as app
from flask import render_template, request, jsonify, send_from_directory 
from flask_security import auth_required, roles_required, roles_accepted
from flask_security import current_user, hash_password, verify_password, login_user, logout_user
from datetime import datetime
from pytz import timezone
import math, time
from celery.result import AsyncResult
from .models import User, Role, UsersRoles, ParkingLot, ParkingSpot, Parking
from .database import db
from .tasks import user_csv_report_task, daily_reminder_task
from .cache_config import cache_init_app


datastore = app.security.datastore
cache = cache_init_app(app)


def clear_cache(prefix):
    if cache.has(prefix):
        cache.delete(prefix)


@app.route('/')
def home():
    return render_template('index.html')

# Login
@app.route("/api/login", methods=['POST']) 
def login(): 
    if current_user:
        return jsonify({"message": "Error !! User already logged in"}), 400
    data = request.get_json() 
    email = data.get("email")
    password = data.get("password")
    if not email or not password: 
        return jsonify({"message": "Error !! Email and Password are required"}), 400 
    user = datastore.find_user(email=email) 
    if user: 
        if verify_password(password, user.password): 
            login_user(user)
            return jsonify({"auth_token": user.get_auth_token(), "role" : user.roles[0].name})  # This is JWT authentication token 
        else: 
            return jsonify({"message": "Error !! Incorrect Password"}), 401 
    return jsonify({"message": "Error !! Invalid Email"}), 401 


# Logout
@auth_required("token")
@app.route("/api/logout")
def logout():
    logout_user()
    return jsonify({"message": "User logged out successfully"}), 200


# Registeration
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()   
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    if not name or not email or not password:
        return jsonify({"message": "Error !! Name, Email and Password are required"}), 400
    if datastore.find_user(email=email):
        return jsonify({'message': 'Error !! User already exists'}), 400
    try:
        datastore.create_user(name=name, email=email, password=hash_password(password), roles=['user'])
        db.session.commit()
        clear_cache('users_list')
        return jsonify({'message': 'User registered successfully'}), 201
    except:
        db.session.rollback()
        return jsonify({'message': 'Error !! Something went wrong'}), 500


# Admin Dashboard  ----->  Get the info on all Parking Lots on its Dashboard 
@auth_required("token")
@roles_required("admin")
@app.route('/api/admin')
@cache.cached(timeout=300, key_prefix='admin_dashboard')
def Admin_Dashboard(): 
    parking_lots = ParkingLot.query.order_by(ParkingLot.pincode.asc()).all()
    if not parking_lots:
        return jsonify({"message": "No Parking Lots available"}), 404
    parking_lots_json = []
    for parking_lot in parking_lots:
        no_of_spots_available = len([spot for spot in parking_lot.spots if spot.status == "available"])
        total_vehicles_ever_parked = len(parking_lot.parkings)
        parking_lots_json.append({
            "id": parking_lot.id,
            "name": parking_lot.name,
            "address": parking_lot.address,
            "pincode": parking_lot.pincode,
            "no_of_spots_available": no_of_spots_available,
            "no_of_spots": parking_lot.no_of_spots,
            "price": parking_lot.price,
            "total_vehicles_ever_parked": total_vehicles_ever_parked
        })
    return jsonify({"message":"Welcome to the Admin's Dashboard", "parking_lots": parking_lots_json})


# User List
@auth_required("token")
@roles_required("admin")
@app.route("/api/users")
@cache.cached(timeout=300, key_prefix='users_list')
def Users_List():
    users = User.query.order_by(User.id.asc()).all()                # List of all the users
    users_json = []
    if len(users) > 1:
        for user in users:
            if user.roles[0].name == "user":
                user_dict = {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "is_active": user.active,
                    "total_parkings" : len(user.parkings)
                }
                users_json.append(user_dict)
        return jsonify({"total_users": len(users_json), "user_list": users_json})        
    return jsonify({"message" : "No users on the application yet"}), 404   


#Blocking/Unblocking a User
@auth_required("token")
@roles_required("admin")
@app.route("/api/users/change_status/<int:user_id>", methods=["PUT"])
def Change_User_Status(user_id):
    user = User.query.filter(User.id == user_id).first()
    if not user:
        return jsonify({"message": "Error !! User not found"}), 404
    if user.roles[0].name == "admin":
        return jsonify({"message": "Error !! Cannot block/unblock an admin user"}), 400
    if user.parkings:
        for parking in user.parkings:
            if not parking.exit_time:   
                return jsonify({"message": "Error !! Cannot block a user with active parkings"}), 400
    try:
        if user.active:
            user.active = False
            db.session.commit()
            clear_cache('users_list')
            return jsonify({"message": "User blocked successfully"}), 200
        else:
            user.active = True
            db.session.commit()
            clear_cache('users_list')
            return jsonify({"message": "User unblocked successfully"}), 200
    except:
        return jsonify({"message": "Error !! Something went wrong"}), 500    
    

# Parkings List
@auth_required("token")
@roles_required("admin")
@app.route("/api/parkings")
@cache.cached(timeout=300, key_prefix='parkings_list')
def Parkings_List():
    parkings = Parking.query.order_by(Parking.parking_time.desc()).all()
    if len(parkings) == 0:
        return jsonify({"message": "No Parkings yet"}), 404
    parkings_json = []
    for parking in parkings:
        parking_dict = {
            "id": parking.id,
            "lot_id": parking.lot.id,
            "spot_id": parking.spot.id,
            "spot_no": parking.spot.spot_no,
            "user_id": parking.user_id,
            "lot_address" : parking.lot.address,
            "user_name": parking.driver.name,
            "vehicle_reg_no": parking.vehicle_reg_no,
            "parking_time": parking.parking_time.strftime("%Y-%m-%d %H:%M:%S"),
            "exit_time": parking.exit_time.strftime("%Y-%m-%d %H:%M:%S") if parking.exit_time else None,
            "cost": parking.cost if parking.cost else None
        }
        parkings_json.append(parking_dict)
    return jsonify({"parkings_list": parkings_json, "total_parkings": len(parkings_json)})


# View a Parking Lot
@auth_required("token")
@roles_required("admin")
@app.route("/api/parking_lot/<int:lot_id>")
def View_Parking(lot_id):
    parking_lot = ParkingLot.query.filter(ParkingLot.id == lot_id).first()
    if not parking_lot:
        return jsonify({"message": "Error !! Parking lot not found"}), 404
    spots = parking_lot.spots
    no_of_spots_available = len([spot for spot in spots if spot.status == "available"])
    total_vehicles_ever_parked = len(parking_lot.parkings)
    lot_datails = {
            "id": parking_lot.id,
            "name": parking_lot.name,
            "address": parking_lot.address,
            "pincode": parking_lot.pincode,
            "no_of_spots": parking_lot.no_of_spots,
            "no_of_spots_available": no_of_spots_available,
            "price": parking_lot.price,
            "total_vehicles_ever_parked": total_vehicles_ever_parked
        }
    spots_json = []
    for spot in spots:
        spots_json.append({
            "id" : spot.id,
            "spot_no" : spot.spot_no,
            "status" : spot.status
        })
    return jsonify({"message":"Parking Lot Details", "parking_lot_details": lot_datails, "parking_spots": spots_json})    


# Adding a Parking Lot
@auth_required("token")
@roles_required("admin")
@app.route("/api/parking_lot", methods=["POST"])
def Add_Parking():
    data = request.get_json()
    name = data.get("name")
    address = data.get("address")
    pincode = data.get("pincode")
    no_of_spots = data.get("no_of_spots")
    price = data.get("price")
    print(type(no_of_spots), type(price))
    if None in [name, address, pincode, no_of_spots, price]:
        return jsonify({"message": "Error !! All fields are required"}), 400
    if no_of_spots <= 0:
        return jsonify({"message": "Error !! Number of spots should be greater than 0"}), 400
    try:
        parking_lot = ParkingLot(name=name, address=address, pincode=pincode, no_of_spots=no_of_spots, price=price)
        db.session.add(parking_lot)
        db.session.flush()                   # Flush the session to get the parking_lot.id
        for num in range(no_of_spots):
            parking_spot = ParkingSpot(spot_no=num, lot_id=parking_lot.id)
            db.session.add(parking_spot)
        db.session.commit()
        clear_cache('admin_dashboard')
        clear_cache('parking_lots_list')
        daily_reminder_task.delay(data)
        return jsonify({"message": "Parking lot added successfully"}), 201
    except:
        db.session.rollback()
        return jsonify({"message": "Error !! Something went wrong"}), 500


# Updating a Parking Lot
@auth_required("token")
@roles_required("admin")
@app.route("/api/parking_lot/<int:lot_id>", methods=["PUT"])
def Update_Parking(lot_id):
    parking_lot = ParkingLot.query.filter(ParkingLot.id == lot_id).first()
    if not parking_lot:
        return jsonify({"message": "Error !! Parking lot not found"}), 404
    data = request.get_json()
    try:
        if data.get("name"):
            if data["name"] != parking_lot.name:
                parking_lot.name = data["name"]
        if data.get("address"):
            if data["address"] != parking_lot.address:
                parking_lot.address = data["address"]
        if data.get("pincode"):
            if data["pincode"] != parking_lot.pincode:
                parking_lot.pincode = data["pincode"]
        if data.get("price"):
            if data["price"] != parking_lot.price:
                parking_lot.price = data["price"]  
        if data.get("no_of_spots"):
            if data["no_of_spots"] != parking_lot.no_of_spots:
                if data["no_of_spots"] > parking_lot.no_of_spots:
                    for num in range(parking_lot.no_of_spots, data["no_of_spots"]):
                        parking_spot = ParkingSpot(spot_no=num, lot_id=parking_lot.id)
                        db.session.add(parking_spot) 
                    parking_lot.no_of_spots = data["no_of_spots"]    
                else:
                    return jsonify({"message": "Error !! Number of spots should be greater than current number of spots"}), 400           
        db.session.commit()    
        clear_cache('admin_dashboard')
        clear_cache('parking_lots_list')
        return jsonify({"message": "Parking lot updated successfully"}), 200 
    except:
        db.session.rollback()
        return jsonify({"message": "Error !! Something went wrong"}), 500    


# Deleting a Parking Lot 
@auth_required("token")
@roles_required("admin")
@app.route("/api/parking_lot/<int:lot_id>", methods=["DELETE"])
def Delete_Parking(lot_id):
    parking_lot = ParkingLot.query.filter(ParkingLot.id == lot_id).first()
    if not parking_lot:
        return jsonify({"message": "Error !! Parking lot not found"}), 404
    spots = parking_lot.spots
    for spot in spots:
        if spot.status != "available":
            return jsonify({"message": "Error !! Parking Lot is still occupied"}), 400                 
    try:
        db.session.delete(parking_lot)  
        db.session.commit() 
        clear_cache('admin_dashboard')
        clear_cache('parking_lots_list')
        return jsonify({"message": "Parking lot deleted successfully"}), 200  
    except:
        db.session.rollback()
        print(traceback.format_exc())
        return jsonify({"message": "Error !! Something went wrong"}), 500  


# View a Parking Spot
@auth_required("token")
@roles_required("admin")            
@app.route("/api/parking_spot/<int:spot_id>")
def View_Parking_Spot(spot_id):
    parking_spot = ParkingSpot.query.filter(ParkingSpot.id == spot_id).first()
    if not parking_spot:
        return jsonify({"message": "Error !! Parking Spot not found"}), 404
    total_vehicles_ever_parked = len(parking_spot.parkings)
    if parking_spot.status == "available": 
        return jsonify({
            "id" : parking_spot.id,
            "parking_lot_id" : parking_spot.lot_id,
            "spot_no" : parking_spot.spot_no,
            "total_vehicles_ever_parked" : total_vehicles_ever_parked,
            "status" : parking_spot.status
        })   
    current_parking = Parking.query.filter(Parking.spot_id == parking_spot.id).order_by(Parking.parking_time.desc()).first()
    return jsonify({
        "id" : parking_spot.id,
        "parking_lot_id" : parking_spot.lot_id,
        "spot_no" : parking_spot.spot_no,
        "total_vehicles_ever_parked" : total_vehicles_ever_parked,
        "status" : parking_spot.status,
        "current_parking" : {
            "parking_id" : current_parking.id,
            "customer_id" : current_parking.user_id,
            "vehicle_reg_no" : current_parking.vehicle_reg_no,
            "parking_time" : current_parking.parking_time
        }        
    })


# Delete a Parking Spot
@auth_required("token")
@roles_required("admin")
@app.route("/api/parking_spot/<int:spot_id>", methods=["DELETE"])
def Delete_Parking_Spot(spot_id):
    parking_spot = ParkingSpot.query.filter(ParkingSpot.id == spot_id).first()
    if not parking_spot:
        return jsonify({"message": "Error !! Parking Spot not found"}), 404 
    if parking_spot.status == "occupied":
        return jsonify({"message": "Error !! Parking Spot is still occupied"}), 400
    try: 
        parking_spot.lot.no_of_spots -= 1
        db.session.delete(parking_spot) 
        db.session.commit()
        clear_cache('admin_dashboard')
        clear_cache('parking_lots_list')
        return jsonify({"message": "Parking Spot deleted successfully"}), 200
    except:
        db.session.rollback()
        return jsonify({"message": "Error !! Something went wrong"}), 500
    

# Search
@auth_required("token")
@roles_accepted("admin", "user")
@app.route("/api/search", methods=["POST"])
def Search():
    data = request.get_json()
    search_for = data.get("search_for")
    search_by = data.get("search_by")
    search_value = data.get("search_value")
    if current_user.roles[0].name == "admin":
        if search_for == "user":
            if search_by == "id":
                user = User.query.filter(User.id == search_value).first()
                if not user:
                    return jsonify({"message": "Error !! User not found"}), 404
                return jsonify({"message": "User found", "users_list":[{"id": user.id, "name" : user.name, "email": user.email, "is_active": user.active, "total_parkings": len(user.parkings)}]})
            users = []
            if search_by == "email":
                users = User.query.filter(User.email.ilike(f"%{search_value}%")).order_by(User.name).all()
            if search_by == "name":
                users = User.query.filter(User.name.ilike(f"%{search_value}%")).order_by(User.name).all()    
            if not users:
                return jsonify({"message": "Error !! User not found"}), 404
            users_json = []
            for user in users:
                users_json.append({
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "is_active": user.active,
                    "total_parkings" : len(user.parkings)
                })
            return jsonify({"message": "Users found", "users_list": users_json}) 
        if search_for == "parking_lot":
            if search_by == "id":
                parking_lot = ParkingLot.query.filter(ParkingLot.id == search_value).first()
                if not parking_lot:
                    return jsonify({"message": "Error !! Parking Lot not found"}), 404
                no_of_spots_available = len([spot for spot in parking_lot.spots if spot.status == "available"])
                total_vehicles_ever_parked = len(parking_lot.parkings)
                return jsonify({"message": "Parking Lot found", "parking_lot_list" : [{"id": parking_lot.id, 
                                                                                        "name": parking_lot.name, 
                                                                                        "address": parking_lot.address, 
                                                                                        "pincode": parking_lot.pincode, 
                                                                                        "no_of_spots": parking_lot.no_of_spots, 
                                                                                        "no_of_spots_available": no_of_spots_available, 
                                                                                        "price": parking_lot.price, 
                                                                                        "total_vehicles_ever_parked": total_vehicles_ever_parked }]})
            parking_lots = []
            if search_by == "name":
                parking_lots = ParkingLot.query.filter(ParkingLot.name.ilike(f"%{search_value}%")).order_by(ParkingLot.id).all()
            if search_by == "address":
                parking_lots = ParkingLot.query.filter(ParkingLot.address.ilike(f"%{search_value}%")).order_by(ParkingLot.id).all()
            if search_by == "pincode":
                parking_lots = ParkingLot.query.filter(ParkingLot.pincode == search_value).order_by(ParkingLot.id).all()
            if not parking_lots: 
                return jsonify({"message": "Error !! No Parking Lot found"}), 404    
            parking_lot_json = []
            for lot in parking_lots:
                no_of_spots_available = len([spot for spot in lot.spots if spot.status == "available"])
                total_vehicles_ever_parked = len(lot.parkings)
                parking_lot_json.append({
                    "id": lot.id,
                    "name": lot.name,
                    "address": lot.address,
                    "pincode": lot.pincode,
                    "no_of_spots": lot.no_of_spots,
                    "no_of_spots_available": no_of_spots_available,
                    "price": lot.price,
                    "total_vehicles_ever_parked": total_vehicles_ever_parked
                })
            return jsonify({"message": "Parking Lots found", "parking_lot_list": parking_lot_json})       
        if search_for == "parking":
            if search_by == "id":
                parking = Parking.query.filter(Parking.id == search_value).first()    
                if not parking:
                    return jsonify({"message": "Error !! Parking not found"}), 404
                return jsonify({"message": "Parking found", "parking_list":[{
                    "id" : parking.id, 
                    "lot_id" : parking.lot_id, 
                    "spot_id" : parking.spot.id, 
                    "spot_no" :parking.spot.spot_no, 
                    "user_id" : parking.user_id, 
                    "lot_address" : parking.lot.address,
                    "user_name": parking.driver.name,
                    "vehicle_reg_no" : parking.vehicle_reg_no, 
                    "parking_time": parking.parking_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "exit_time": parking.exit_time.strftime("%Y-%m-%d %H:%M:%S") if parking.exit_time else None,
                    "cost": parking.cost if parking.cost else None
                }]})
            parkings = []
            if search_by == "user_id":
                parkings = Parking.query.filter(Parking.user_id == search_value).order_by(Parking.parking_time).all()
            if search_by == "lot_id":
                parkings = Parking.query.filter(Parking.lot_id == search_value).order_by(Parking.parking_time).all()    
            if search_by == "spot_no":
                parkings = Parking.query.filter(Parking.spot_no == search_value).order_by(Parking.parking_time).all()
            if search_by == "vehicle_reg_no":
                parkings = Parking.query.filter(Parking.vehicle_reg_no.ilike(f"%{search_value}%")).order_by(Parking.parking_time).all()
            if not parkings:
                return jsonify({"message": "Error !! No Parking found"}), 404
            parkings_json = []
            for parking in parkings:
                parkings_json.append({
                    "id" : parking.id, 
                    "lot_id" : parking.lot_id, 
                    "spot_id" : parking.spot.id, 
                    "spot_no" :parking.spot.spot_no, 
                    "user_id" : parking.user_id, 
                    "lot_address" : parking.lot.address,
                    "user_name": parking.driver.name,
                    "vehicle_reg_no" : parking.vehicle_reg_no, 
                    "parking_time": parking.parking_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "exit_time": parking.exit_time.strftime("%Y-%m-%d %H:%M:%S") if parking.exit_time else None,
                    "cost": parking.cost if parking.cost else None
                })
            return jsonify({"message": "Parkings found", "parking_list": parkings_json})           
        return jsonify({"message": "Error !! Invalid search criteria"}), 400
    else: 
        parking_lots = []
        if search_by == "name":
            parking_lots = ParkingLot.query.filter(ParkingLot.name.ilike(f"%{search_value}%")).order_by(ParkingLot.pincode).all()
        elif search_by == "address":
            parking_lots = ParkingLot.query.filter(ParkingLot.address.ilike(f"%{search_value}%")).order_by(ParkingLot.pincode).all()
        elif search_by == "pincode":
            parking_lots = ParkingLot.query.filter(ParkingLot.pincode == search_value).all()
        else:
            return jsonify({"message": "Error !! Invalid search criteria"}), 400
        if not parking_lots:
            return jsonify({"message": "Error !! No Parking Lot found"}), 404    
        parking_lost_json = []
        for lot in parking_lots:
            no_of_spots_available = len([spot for spot in lot.spots if spot.status == "available"])
            parking_lost_json.append({
                "id": lot.id,
                "name": lot.name,
                "address": lot.address,
                "pincode": lot.pincode,
                "price": lot.price,
                "no_of_spots": lot.no_of_spots,
                "no_of_spots_available": no_of_spots_available
            })
        return jsonify({"message": "Parking Lots found", "parking_lot_list": parking_lost_json}) 


# Summary
@auth_required("token")
@roles_accepted("admin", "user")
@app.route("/api/summary")
def summary():
    user = current_user
    if user.roles[0].name == "admin":
        total_users = len(User.query.filter(User.roles.any(name="user")).all())
        total_parking_lots = len(ParkingLot.query.all())
        total_parking_spots = len(ParkingSpot.query.all())
        total_parkings = len(Parking.query.all())
        total_current_parkings = len(Parking.query.filter(Parking.exit_time == None).all())
        total_revenue = sum([parking.cost for parking in Parking.query.filter(Parking.cost != None).all()])
        return jsonify({"total_users": total_users,
                        "total_parking_lots": total_parking_lots,
                        "total_parking_spots": total_parking_spots,
                        "total_parkings": total_parkings,
                        "total_current_parkings": total_current_parkings,
                        "total_revenue": total_revenue})
    else:
        total_parkings = len(user.parkings)
        total_current_parkings = len([parking for parking in user.parkings if not parking.exit_time])
        total_amount_spent = sum([parking.cost for parking in user.parkings if parking.cost])
        return jsonify({"total_parkings": total_parkings,
                        "total_current_parkings": total_current_parkings,
                        "total_amount_spent": total_amount_spent})


# User Profile
@auth_required("token")
@roles_required("user")
@app.route("/api/profile")
def User_Profile():
    user = current_user
    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
    }
    return jsonify({"message":"This is the user profile", "user_profile": user_data})


# Edit User Profile
@auth_required("token")
@roles_required("user")
@app.route("/api/profile", methods=["PUT"])
def Edit_User_Profile():
    user = current_user
    data = request.get_json()
    try:
        if data.get("name"):
            if data["name"] != user.name:
                user.name = data["name"]
        if data.get("email"):
            if data["email"] != user.email:
                if datastore.find_user(email=data["email"]):
                    return jsonify({"message": "Error !! Email already in use"}), 400
                user.email = data["email"]
        if data.get("password"):
            user.password = hash_password(data["password"])
        db.session.commit()    
        return jsonify({"message": "Profile updated successfully"}), 200 
    except:
        db.session.rollback()
        return jsonify({"message": "Error !! Something went wrong"}), 500


@cache.cached(timeout=300, key_prefix='parking_lots_list')
def get_parking_lots():
    return ParkingLot.query.order_by(ParkingLot.pincode.asc()).all()

@cache.memoize(timeout=300)
def get_user_parkings(user):
    return sorted(user.parkings, key= lambda obj : obj.parking_time, reverse=True)


# User Dashboard
@auth_required("token")
@roles_required("user")
@app.route("/api/user")
def User_Dashboard():
    user = current_user
    parking_lots = get_parking_lots()
    parking_lots_json = []
    for parking_lot in parking_lots:
        no_of_spots_available = len([spot for spot in parking_lot.spots if spot.status == "available"])
        parking_lots_json.append({
            "id": parking_lot.id,
            "name": parking_lot.name,
            "address": parking_lot.address,
            "pincode": parking_lot.pincode,
            "price": parking_lot.price,
            "no_of_spots": parking_lot.no_of_spots,
            "no_of_spots_available": no_of_spots_available,
        })
    user_parkings_json = []    
    user_parkings = get_user_parkings(user)
    for parking in user_parkings:
        if not parking.exit_time:
            user_parkings_json.append({
                "id" : parking.id, 
                "lot_id" : parking.lot_id, 
                "spot_id" : parking.spot.id, 
                "spot_no" :parking.spot.spot_no, 
                "lot_name" : parking.lot.name,
                "lot_address" : parking.lot.address,
                "lot_pincode": parking.lot.pincode,
                "lot_price" : parking.lot.price,
                "vehicle_reg_no" : parking.vehicle_reg_no, 
                "parking_time": parking.parking_time.strftime("%Y-%m-%d %H:%M:%S"),
            })
    return jsonify({"message":"This is the user dashboard", 
                    "current_parkings" : user_parkings_json, 
                    "parking_lot_list" : parking_lots_json})    


# Parking History
@auth_required("token")
@roles_required("user")
@app.route("/api/parking_history")
def Parking_History():
    user = current_user
    user_parkings = get_user_parkings(user)
    user_parkings_json = []
    for parking in user_parkings:
        if parking.exit_time:
            user_parkings_json.append({
                "id" : parking.id, 
                "lot_id" : parking.lot_id, 
                "spot_id" : parking.spot.id, 
                "spot_no" :parking.spot.spot_no, 
                "lot_name" : parking.lot.name,
                "lot_address" : parking.lot.address,
                "lot_pincode": parking.lot.pincode,
                "lot_price" : parking.lot.price,
                "vehicle_reg_no" : parking.vehicle_reg_no, 
                "parking_time": parking.parking_time.strftime("%Y-%m-%d %H:%M:%S"),
                "exit_time": parking.exit_time.strftime("%Y-%m-%d %H:%M:%S"),
                "cost": parking.cost
            })
    return jsonify({"message":"This is the Parking History",  
                    "parking_history" : user_parkings_json})


# Function to validate vehicle registration number
def validate_vehicle_reg_no(vehicle_reg_no):
    if len(vehicle_reg_no) == 10:
        if vehicle_reg_no[:2].isalpha():
            if vehicle_reg_no[4:6].isalpha():
                if vehicle_reg_no[2:4].isnumeric():
                    if vehicle_reg_no[6:].isnumeric():
                        return True
    return False


# Booking a Parking Spot
@auth_required("token") 
@roles_required("user") 
@app.route("/api/book_parking/<int:lot_id>", methods=["POST"])
def Book_Parking(lot_id):
    user = current_user
    parking_lot = ParkingLot.query.filter(ParkingLot.id == lot_id).first()
    if not parking_lot:
        return jsonify({"message": "Error !! Parking Lot not found"}), 404
    parking_spot = ParkingSpot.query.filter(ParkingSpot.lot_id == lot_id, ParkingSpot.status == "available").first()
    if not parking_spot:
        return jsonify({"message": "Error !! No Parking Spot available"}), 400
    data = request.get_json()
    vehicle_reg_no = data.get("vehicle_reg_no")
    if not vehicle_reg_no: 
        return jsonify({"message": "Error !! Vehicle Registration Number is required"}), 400
    if not validate_vehicle_reg_no(vehicle_reg_no):
        return jsonify({"message": "Error !! Incorrect format of Vehicle Registration Number"}), 400
    try:
        parking = Parking(spot_id=parking_spot.id, lot_id=parking_lot.id, user_id=user.id, vehicle_reg_no=vehicle_reg_no.upper(), parking_time=datetime.now(timezone("Asia/Kolkata")))
        db.session.add(parking)
        parking_spot.status = "occupied"
        db.session.commit()
        clear_cache('parkings_list')
        clear_cache('admin_dashboard')
        clear_cache('users_list')
        cache.delete_memoized(get_user_parkings, user)
        return jsonify({"message": "Parking booked successfully"}), 201
    except:
        db.session.rollback()
        return jsonify({"message": "Error !! Something went wrong"}), 500


# Releasing a Parking Spot
@auth_required("token")
@roles_required("user")
@app.route("/api/release_parking/<int:parking_id>", methods=["PUT"])
def Release_Parking(parking_id):
    parking = Parking.query.filter(Parking.id == parking_id).first() 
    if not parking:
        return jsonify({"message": "Error !! Parking not found"}), 404
    if parking.exit_time:
        return jsonify({"message": "Error !! Parking already released"}), 400
    lot = parking.lot
    spot = parking.spot 
    local_tz = timezone("Asia/Kolkata")  
    current_time = datetime.now(local_tz)
    parking_time = local_tz.localize(parking.parking_time)
    time_difference = current_time - parking_time
    time_difference_in_seconds = time_difference.total_seconds()
    time_difference_in_hrs = time_difference_in_seconds / 3600
    cost = math.ceil(time_difference_in_hrs) * lot.price
    try:
        parking.exit_time = current_time
        parking.cost = cost
        spot.status = "available"
        db.session.commit()
        clear_cache('parkings_list')
        clear_cache('admin_dashboard')
        clear_cache('users_list')
        return jsonify({"message": "Parking released successfully", "parking_cost": cost}), 200
    except:
        db.session.rollback()
        return jsonify({"message": "Error !! Something went wrong"}), 500
    

# Creatng the user triggered CSV report 
@app.route("/api/create_user_report/<user_id>")
def user_report(user_id):
    result = user_csv_report_task.delay(user_id)
    return jsonify({
        "task_id" : result.id
    })

# Downloading the report  
@app.route("/api/download_user_report/<task_id>")
def get_report(task_id):
    result = AsyncResult(task_id)
    return send_from_directory("csv_reports", result.result)