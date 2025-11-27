from flask import current_app as app
from flask_security import hash_password
from .database import db

with app.app_context():
    db.create_all()

    app.security.datastore.find_or_create_role(name = "admin", description = "It is the superuser with full control over other users and data.")
    app.security.datastore.find_or_create_role(name = "user", description = "It is the general user of the application which can reserve a parking spot.")
    db.session.commit()

    if not app.security.datastore.find_user(email = "khanikram6519@admin.com"):
        app.security.datastore.create_user(name = "Ikram Khan", email = "khanikram6519@admin.com", password = hash_password("6519"), roles = ["admin"])
        db.session.commit() 