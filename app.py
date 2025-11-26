from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore
from backend.models import User, Role
from backend.config import LocalDevelopmentConfig
from backend.database import db

def createApp():
    app = Flask(__name__, template_folder="frontend", static_folder="frontend", static_url_path="/static")
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, datastore, register_blueprint=False)  
    app.app_context().push()
    return app 

app = createApp()

from backend.init_data import *     
from backend.routes import *   
 
if __name__ == "__main__":
    app.run() 