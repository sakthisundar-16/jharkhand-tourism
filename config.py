import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # MySQL Database Configuration
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '2005'  # Your MySQL password
    MYSQL_DB = 'arunachal_tourism'
    MYSQL_CHARSET = 'utf8mb4'
    MYSQL_AUTH_PLUGIN = 'caching_sha2_password'  # Added auth plugin
