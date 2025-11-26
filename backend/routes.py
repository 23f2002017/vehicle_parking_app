from flask import current_app as app, render_template, request, jsonify 
from flask_security import auth_required, roles_required, roles_accepted
from flask_security import current_user, hash_password, verify_password, login_user
from datetime import datetime
import math
from .models import User, Role, UsersRoles, ParkingLot, ParkingSpot, Parking
from .database import db

datastore = app.security.datastore

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
            return jsonify({"token": user.get_auth_token()})  # This is JWT authentication token 
        else: 
            return jsonify({"error": "Invalid Password"}), 401 
    return jsonify({"message": "Error !! Invalid Email"}), 401 


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
        return jsonify({'message': 'User created successfully'}), 201
    except:
        db.session.rollback()
        return jsonify({'message': 'Error !! Something went wrong'}), 500


# Admin Dashboard  ----->  Get the info on all Parking Lots on its Dashboard 
@app.route('/api/admin') 
@auth_required("token")
@roles_required("admin")
def admin_dashboard(): 
    parking_lots = ParkingLot.query.order_by(ParkingLot.pincode.asc()).all()
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
            "total_no_of_spots": parking_lot.no_of_spots,
            "price/hr": parking_lot.price,
            "total_vehicles_ever_parked": total_vehicles_ever_parked
        })
    return jsonify({"message":"Welcome to the Admin Dashboard", "parking_lots": parking_lots_json})


# User List
@auth_required("token")
@roles_required("admin")
@app.route("/api/users_list", methods=["GET"])
def User_List():
    users = User.query.order_by(User.id.desc()).all()                #List of user objects
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
    return jsonify({"message" : "No users on the application yet"})     


# View a Parking Lot
@auth_required("token")
@roles_required("admin")
@app.route("/api/view_parking_lot/<int:lot_id>")
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
            "total_no_of_spots": parking_lot.no_of_spots,
            "no_of_spots_available": no_of_spots_available,
            "price/hr": parking_lot.price,
            "total_vehicles_ever_parked": total_vehicles_ever_parked
        }
    spots_json = []
    for spot in spots:
        spots_json.append({
            "id" : spot.id,
            "status" : spot.status
        })
    return jsonify({"message":"Parking Lot Details", "parking_lot_details": lot_datails, "parking_spots": spots_json})    


# Adding a Parking Lot
@auth_required("token")
@roles_required("admin")
@app.route("/api/add_parking_lot", methods=["POST"])
def Add_Parking():
    data = request.get_json()
    name = data.get("name")
    address = data.get("address")
    pincode = data.get("pincode")
    no_of_spots = data.get("no_of_spots")
    price = data.get("price")
    if None in [name, address, pincode, no_of_spots, price]:
        return jsonify({"message": "Error !! All fields are required"}), 400
    if no_of_spots <= 0:
        return jsonify({"message": "Error !! Number of spots should be greater than 0"}), 400
    else:
        try:
            parking_lot = ParkingLot(name=name, address=address, pincode=pincode, no_of_spots=no_of_spots, price=price)
            db.session.add(parking_lot)
            db.session.flush()                   # Flush the session to get the parking_lot.id
            for id in range(1, no_of_spots+1):
                parking_spot = ParkingSpot(id=id, lot_id=parking_lot.id)
                db.session.add(parking_spot)
            db.session.commit()
            return jsonify({"message": "Parking lot added successfully"}), 201
        except:
            db.session.rollback()
            return jsonify({"message": "Error !! Something went wrong"}), 500


# Updating a Parking Lot
@auth_required("token")
@roles_required("admin")
@app.route("/api/update_parking_lot/<int:lot_id>", methods=["PUT"])
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
                    for id in range(parking_lot.no_of_spots+1, data["no_of_spots"]+1):
                        parking_spot = ParkingSpot(id=id, lot_id=parking_lot.id)
                        db.session.add(parking_spot) 
                else:
                    return jsonify({"message": "Error !! Number of spots should be greater than current number of spots"}), 400           
        db.session.commit()    
        return jsonify({"message": "Parking lot updated successfully"}), 200 
    except:
        db.session.rollback()
        return jsonify({"message": "Error !! Something went wrong"}), 500    


# Deleting a Parking Lot 
@auth_required("token")
@roles_required("admin")
@app.route("/api/delete_parking_lot/<int:lot_id>", methods=["DELETE"])
def Delete_Parking(lot_id):
    parking_lot = ParkingLot.query.filter(ParkingLot.id == lot_id).first()
    if not parking_lot:
        return jsonify({"message": "Error !! Parking lot not found"}), 404
    spots = parking_lot.spots
    for spot in spots:
        if spot.status != "available":
            return jsonify({"message": "Error !! Parking Lot is still occupied"}), 400
    try: 
        for spot in spots: 
            db.session.delete(spot) 
        db.session.commit()                 # Here, use of db.session.flush() wont work !!
        db.session.delete(parking_lot)
        db.session.commit() 
        return jsonify({"message": "Parking lot deleted successfully"}), 200
    except:
        db.session.rollback()
        return jsonify({"message": "Error !! Something went wrong"}), 500  


# View a Parking Spot
@auth_required("token")
@roles_required("admin")
@app.route("/api/view_parking_spot/<int:lot_id>/<int:spot_id>")
def View_Parking_Spot(lot_id, spot_id):
    parking_spot = ParkingSpot.query.filter(ParkingSpot.lot_id == lot_id, ParkingSpot.id == spot_id).first()
    if not parking_spot:
        return jsonify({"message": "Error !! Parking Spot not found"}), 404
    total_vehicles_ever_parked = len(parking_spot.parkings)
    if parking_spot.status == "available": 
        return jsonify({
            "id" : parking_spot.id,
            "parking_lot_id" : parking_spot.lot_id,
            "total_vehicles_ever_parked" : total_vehicles_ever_parked,
            "status" : parking_spot.status
        })   
    current_parking = Parking.query.filter(Parking.spot_id == parking_spot.id, Parking.lot_id == parking_spot.lot_id).order_by(Parking.parking_time.desc()).first()
    return jsonify({
        "id" : parking_spot.id,
        "parking_lot_id" : parking_spot.lot_id,
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
@app.route("/api/delete_parking_spot/<int:lot_id>/<int:spot_id>", methods=["DELETE"])
def Delete_Parking_Spot(lot_id, spot_id):
    parking_spot = ParkingSpot.query.filter(ParkingSpot.lot_id == lot_id, ParkingSpot.id == spot_id).first()
    if not parking_spot:
        return jsonify({"message": "Error !! Parking Spot not found"}), 404 
    if parking_spot.status == "occupied":
        return jsonify({"message": "Error !! Parking Spot is still occupied"}), 400
    try: 
        parking_spot.lot.no_of_spots -= 1
        db.session.delete(parking_spot) 
        db.session.commit()
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
                return jsonify({"message": "User found", "user_info":{"name" : user.name, "email": user.email, "is_active": user.active, "role": user.roles[0].name}})
            users = []
            if search_by == "email":
                users = User.query.filter(User.email.ilike(f"%{search_value}%")).order_by(User.name).all()
            if search_by == "name":
                users = User.query.filter(User.name.ilike(f"%{search_value}%")).order_by(User.name).all()    
            if not users:
                return jsonify({"message": "Error !! No user not found"}), 404
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
                return jsonify({"message": "Parking Lot found", "parking_lot_details" : {"id": parking_lot.id, 
                                                                                        "name": parking_lot.name, 
                                                                                        "address": parking_lot.address, 
                                                                                        "pincode": parking_lot.pincode, 
                                                                                        "total_no_of_spots": parking_lot.no_of_spots, 
                                                                                        "no_of_spots_available": no_of_spots_available, 
                                                                                        "price/hr": parking_lot.price, 
                                                                                        "total_vehicles_ever_parked": total_vehicles_ever_parked }})
            parking_lots = []
            if search_by == "name":
                parking_lots = ParkingLot.query.filter(ParkingLot.name.ilike(f"%{search_value}%")).order_by(ParkingLot.id).all()
            if search_by == "address":
                parking_lots = ParkingLot.query.filter(ParkingLot.address.ilike(f"%{search_value}%")).order_by(ParkingLot.id).all()
            if search_by == "pincode":
                parking_lots = ParkingLot.query.filter(ParkingLot.pincode == search_value).order_by(ParkingLot.id).all()
            if not parking_lots:
                return jsonify({"message": "Error !! No Parking Lot found"}), 404    
            parking_lost_json = []
            for lot in parking_lots:
                no_of_spots_available = len([spot for spot in lot.spots if spot.status == "available"])
                total_vehicles_ever_parked = len(lot.parkings)
                parking_lost_json.append({
                    "id": lot.id,
                    "name": lot.name,
                    "address": lot.address,
                    "pincode": lot.pincode,
                    "total_no_of_spots": lot.no_of_spots,
                    "no_of_spots_available": no_of_spots_available,
                    "price/hr": lot.price,
                    "total_vehicles_ever_parked": total_vehicles_ever_parked
                })
            return jsonify({"message": "Parking Lots found", "parking_lot_list": parking_lost_json})      
        if search_for == "parking":
            if search_by == "id":
                parking = Parking.query.filter(Parking.id == search_value).first()    
                if not parking:
                    return jsonify({"message": "Error !! Parking not found"}), 404
                if parking.exit_time: 
                    return jsonify({"message": "Parking found", "parking_info":{"id" : parking.id, "lot_id" : parking.lot_id, "spot_id" : parking.spot_id, "user_id" : parking.user_id, "vehicle_reg_no" : parking.vehicle_reg_no, "parking_time" : parking.parking_time, "exit_time" : parking.exit_time, "cost" : parking.cost}})
                return jsonify({"message": "Parking found", "parking_info":{"id" : parking.id, "lot_id" : parking.lot_id, "spot_id" : parking.spot_id, "user_id" : parking.user_id, "vehicle_reg_no" : parking.vehicle_reg_no, "parking_time" : parking.parking_time, "parking_status" : "Occupied"}})
            parkings = []
            if search_by == "user_id":
                parkings = Parking.query.filter(Parking.user_id == search_value).order_by(Parking.parking_time).all()
            if search_by == "lot_id":
                parkings = Parking.query.filter(Parking.lot_id == search_value).order_by(Parking.parking_time).all()
            if search_by == "spot_id":
                parkings = Parking.query.filter(Parking.spot_id == search_value).order_by(Parking.parking_time).all()
            if search_by == "vehicle_reg_no":
                parkings = Parking.query.filter(Parking.vehicle_reg_no.ilike(f"%{search_value}%")).order_by(Parking.parking_time).all()
            if not parkings:
                return jsonify({"message": "Error !! No Parking found"}), 404
            parkings_json = []
            for parking in parkings:
                if parking.exit_time: 
                    parkings_json.append({"id" : parking.id, "lot_id" : parking.lot_id, "spot_id" : parking.spot_id, "user_id" : parking.user_id, "vehicle_reg_no" : parking.vehicle_reg_no, "parking_time" : parking.parking_time, "exit_time" : parking.exit_time, "cost" : parking.cost})
                else:    
                    parkings_json.append({"id" : parking.id, "lot_id" : parking.lot_id, "spot_id" : parking.spot_id, "user_id" : parking.user_id, "vehicle_reg_no" : parking.vehicle_reg_no, "parking_time" : parking.parking_time, "parking_status" : "Occupied"})     
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
                "total_no_of_spots": lot.no_of_spots,
                "no_of_spots_available": no_of_spots_available,
                "price/hr": lot.price
            })
        return jsonify({"message": "Parking Lots found", "parking_lot_list": parking_lost_json}) 


# Summary
@auth_required("token")
@roles_accepted("admin", "user")
@app.route("/api/summary")
def summary():
    user = current_user
    if user.roles[0].name == "admin":
        pass
    else:
        pass


# User Dashboard
@auth_required("token")
@roles_required("user")
@app.route("/api/user")
def User_Dashboard():
    user = current_user
    parking_lots = ParkingLot.query.order_by(ParkingLot.pincode.asc()).all()
    parking_lots_json = []
    for parking_lot in parking_lots:
        no_of_spots_available = len([spot for spot in parking_lot.spots if spot.status == "available"])
        parking_lots_json.append({
            "id": parking_lot.id,
            "name": parking_lot.name,
            "address": parking_lot.address,
            "pincode": parking_lot.pincode,
            "total_no_of_spots": parking_lot.no_of_spots,
            "no_of_spots_available": no_of_spots_available,
            "price": parking_lot.price
        })
    user_parkings = sorted(user.parkings, key= lambda obj : obj.parking_time, reverse=True)
    user_parkings_json = []
    for parking in user_parkings:
        parking_lot = ParkingLot.query.filter(ParkingLot.id == parking.lot_id).first()
        if not parking.exit_time:
            user_parkings_json.append({
                "id" : parking.id,
                "spot_id" : parking.spot_id,
                "parking_lot_name" : parking_lot.name,
                "parking_lot_address" : parking_lot.address,
                "parking_lot_pincode" : parking_lot.pincode,
                "vehicle_reg_no" : parking.vehicle_reg_no,
                "parking_time" : parking.parking_time,
                "parking_status" : "Occupied"
            })
    return jsonify({"message":"This is the user dashboard", 
                    "user_info":{"name" : user.name, "email": user.email, "is_active": user.active}, 
                    "current_parkings" : user_parkings_json, 
                    "parking_lot_list" : parking_lots_json})    


# Parking History
@auth_required("token")
@roles_required("user")
@app.route("/api/parking_history")
def Parking_History():
    user = current_user
    user_parkings = sorted(user.parkings, key= lambda obj : obj.parking_time, reverse=True)
    user_parkings_json = []
    for parking in user_parkings:
        parking_lot = ParkingLot.query.filter(ParkingLot.id == parking.lot_id).first()
        if parking.exit_time:
            user_parkings_json.append({
                "id" : parking.id,
                "spot_id" : parking.spot_id,
                "parking_lot_name" : parking_lot.name,
                "parking_lot_address" : parking_lot.address,
                "parking_lot_pincode" : parking_lot.pincode,
                "vehicle_reg_no" : parking.vehicle_reg_no,
                "parking_time" : parking.parking_time,
                "exit_time" : parking.exit_time,
                "cost" : parking.cost
            })
    return jsonify({"message":"This is the Parking History",  
                    "parking_history" : user_parkings_json})


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
    try:
        parking = Parking(spot_id=parking_spot.id, lot_id=parking_lot.id, user_id=user.id, vehicle_reg_no=vehicle_reg_no)
        db.session.add(parking)
        parking_spot.status = "occupied"
        db.session.commit()
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
    lot = ParkingLot.query.filter(ParkingLot.id == parking.lot_id).first()
    spot = ParkingSpot.query.filter(ParkingSpot.id == parking.spot_id, ParkingSpot.lot_id == parking.lot_id).first()   
    current_time = datetime.now()
    time_difference = current_time - parking.parking_time
    time_difference_in_seconds = time_difference.total_seconds()
    time_difference_in_hrs = time_difference_in_seconds / 3600
    cost = math.ceil(time_difference_in_hrs) * lot.price
    try:
        parking.exit_time = current_time
        parking.cost = cost
        spot.status = "available"
        db.session.commit()
        return jsonify({"message": "Parking released successfully", "parking_cost": cost}), 200
    except:
        db.session.rollback()
        return jsonify({"message": "Error !! Something went wrong"}), 500
    