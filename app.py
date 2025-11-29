from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore
from backend.models import User, Role
from backend.config import LocalDevelopmentConfig
from backend.database import db
from backend.celery_config import celery_init_app
from celery.schedules import crontab
from backend.tasks import monthly_activity_report_task 

def createApp():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, datastore, register_blueprint=False)  
    app.app_context().push()
    return app 

app = createApp()
celery = celery_init_app(app)
#celery.autodiscover_tasks()

from backend.init_data import * 
from backend.routes import *   

# Celery Beat Configuration
@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute='*/1'),
        monthly_activity_report_task.s() 
    )
 
if __name__ == "__main__":
    app.run() 