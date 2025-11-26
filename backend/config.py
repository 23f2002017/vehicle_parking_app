class config():
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class LocalDevelopmentConfig(config): 
    DEBUG = True 
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.sqlite' 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #for flask-security-too
    SECRET_KEY = 'this-is-the-security-key' 
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_PASSWORD_SALT = 'this-is-the-salt'
    WTF_CSRF_ENABLED = False 
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'auth-token'
    SECURITY_ANONYMOUS_USER_DISABLED = True 