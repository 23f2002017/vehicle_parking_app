class config():
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class LocalDevelopmentConfig(config): 
    DEBUG = True 
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.sqlite' 
    SQLALCHEMY_TRACK_MODIFICATIONS = False 