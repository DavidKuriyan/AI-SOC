import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-for-soc-app'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'database', 'soc.db')
    # Ensure database directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Fix for Windows SQLite URI
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DB_PATH.replace('\\', '/')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email Config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Risk Config
    RISK_THRESHOLD = 85
    
    # Log Paths
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    AUTH_LOG = os.path.join(LOG_DIR, 'auth.log')
    NETWORK_LOG = os.path.join(LOG_DIR, 'network.log')
    FIREWALL_LOG = os.path.join(LOG_DIR, 'firewall.log')
