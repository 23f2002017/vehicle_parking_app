from flask import current_app as app
from .database import db

@app.route('/')
def hello_world():
    return '<h1>Hello, World!</h1>'