import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MySQL Settings
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "lost2found")
    DB_SSL = os.getenv("DB_SSL", "false").lower() == "true"
    
    # JWT Settings
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-jwt-key")
    JWT_ACCESS_TOKEN_EXPIRES = 8 * 3600 # 8 hours
    
    # Upload Settings
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024 # 5 MB
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
