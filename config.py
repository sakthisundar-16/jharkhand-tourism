import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'  # Keep this secure; generate a random one for production
    
    # MySQL Database Configuration for PythonAnywhere
    MYSQL_HOST = 'sakthi16.mysql.pythonanywhere-services.com'  # PythonAnywhere MySQL host
    MYSQL_USER = 'sakthi16'  # Your PythonAnywhere username
    MYSQL_PASSWORD = 'ccXLaj2Sa7E@23F'  # Replace with the password you set in Databases tab (NOT your local '2005')
    MYSQL_DB = 'sakthi16$jharkhand_tourism'  # Your database name (prefixed; update if different)
    MYSQL_CHARSET = 'utf8mb4'
    MYSQL_AUTH_PLUGIN = 'caching_sha2_password'  # Kept as is for compatibility
