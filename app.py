from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore
from backend.models import User, Role
from backend.config import LocalDevelopmentConfig
from backend.database import db
from backend.resources import api                                               #Currently not in use

def createApp():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    api.init_app(app)                                                           #Currently not in use
    datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, datastore, register_blueprint=False)  
    app.app_context().push()
    return app 

app = createApp()

import backend.init_data  
              
from backend.routes import *   
 
if __name__ == "__main__":
    app.run() 