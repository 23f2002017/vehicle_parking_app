from celery import shared_task
from .models import User
from .send_mail import send_email
from datetime import datetime, timedelta
from pytz import timezone
from jinja2 import Template
import csv
import requests


@shared_task(ignore_result=False, name='user_csv_report')
def user_csv_report_task(id):
    user = User.query.get(id)
    csv_file_name = f"user_{user.id}_{datetime.now(timezone("Asia/Kolkata")).strftime("%d%m%Y-%H%M%S")}_report.csv"
    with open(f"csv_reports/{csv_file_name}", mode='w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Name", user.name])
        csv_writer.writerow(["E-Mail", user.email])
        csv_writer.writerow(["Total Parkings", len(user.parkings)])
        csv_writer.writerow([])
        csv_writer.writerow(["Parking ID", "Vehicle Registration Number", "Parking Lot ID", "Parking Lot Name", "Parking Lot Address", "Spot Number", "Parking Time", "Exit Time", "Status", "Cost"])
        for parking in user.parkings:
            csv_writer.writerow([
                parking.id,
                parking.vehicle_reg_no,
                parking.lot.id,
                parking.lot.name,
                f"{parking.lot.address}, {parking.lot.pincode}",
                parking.spot.spot_no,
                parking.parking_time.strftime("%d-%m-%Y %H:%M:%S"),
                parking.exit_time.strftime("%d-%m-%Y %H:%M:%S") if parking.exit_time else "N/A",
                "Released" if parking.exit_time else "Occupied",
                parking.cost if parking.cost else "N/A"
            ])   
    return csv_file_name

@shared_task(ignore_result=False, name='monthly_activity_report')
def monthly_activity_report_task():
    users = User.query.all()
    for user in users[1:]:
        data = {
            'name' : user.name,
            'total_parkings': len(user.parkings),
            'total_spent': 0,
            'parkings' : []
        }
        local_tz = timezone("Asia/Kolkata")
        parkings = [parking for parking in user.parkings if local_tz.localize(parking.parking_time) >= datetime.now(local_tz) - timedelta(days=30)]
        for parking in parkings:
            parking_data = {
                'id': parking.id,
                'vehicle_reg_no': parking.vehicle_reg_no,
                'lot_name': parking.lot.name,
                'lot_address': f"{parking.lot.address}, {parking.lot.pincode}",
                'spot_no': parking.spot.spot_no,
                'parking_time': parking.parking_time.strftime("%d-%m-%Y %H:%M:%S"),
                'exit_time': parking.exit_time.strftime("%d-%m-%Y %H:%M:%S") if parking.exit_time else "N/A",
                'status': "Released" if parking.exit_time else "Occupied",
                'cost': parking.cost if parking.cost else "N/A"
            }
            data['parkings'].append(parking_data)   
            data['total_spent'] += parking.cost if parking.cost else 0
        
        with open('./templates/report_template.html') as file:
            mail_template = Template(file.read())

        to = user.email
        subject = "Your Monthly Parking Activity Report"
        body = mail_template.render(data = data)
        send_email(to, subject, body)
    return "OK"  

@shared_task(ignore_result=False, name='daily_reminder')
def daily_reminder_task(data):
    chat_template = Template("""
        Dear Users, 
                             
        A new parking lot has been added to ParkEase.  
                                                
        Here are the details:
            Name: {{ data.name }}
            Address: {{ data.address }}
            Pincode: {{ data.pincode }}
            Number of Spots: {{ data.no_of_spots }}
            Price per Hour: ₹{{ data.price }}  (Prices correct at the time of booking)
                     
        Visit our platform to book your spot now!
        Thank you for choosing ParkEase!
    """)
    url = "https://chat.googleapis.com/v1/spaces/AAQAahwCgc8/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=G3VWWgQUSoBiH4QsJA0jI5KLLYKNIx81It14Ob_dTLM"
    text = chat_template.render(data = data)
    res = requests.post(url, json = {"text": text})
    return res.status_code