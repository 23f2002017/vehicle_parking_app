from flask import Flask
from backend.config import LocalDevelopmentConfig
from backend.database import db

def createApp():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    app.app_context().push()
    return app

app = createApp()

from backend.models import *                
from backend.routes import *   
 
if __name__ == "__main__":
    app.run() 