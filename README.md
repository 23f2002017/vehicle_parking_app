# vehicle_parking_app

It is a multi-user app (one requires an administrator and other users) that manages different parking lots, parking spots and parked vehicles. Assume that this parking app is for 4-wheeler parking.

## How to run the application ?

0. Navigate to the project folder, run the below command to delete all the *Zone.Identifier* files  
`find . -type f -name '*:Zone.Identifier' -exec rm -f {} \;`

1. Create a virtual environment  
`python3 -m venv .venv`  

2. Activate the virtual environment  
`source .venv/bin/activate`

3. Install all the dependencies  
`pip install -r requirements.txt`

4. Start the Flask server  
`python3 app.py`  
Your app is now ready to run at http://127.0.0.1:5000  

5. Start the Redis server  
`redis-server`  
If the above step fails, do `sudo systemctl stop redis` followed by the above code

6. Start a Celery worker  
`celery -A app.celery worker -l info`

7. Start a *local* SMTP server on your computer (Preferably **MailHog**) at port *1025*

8. Start the celery beat  
`celery -A app.celery beat -l info`

The app is now fully configured.