import os
from datetime import timedelta
from urllib.parse import quote_plus

class Config:
    """Base configuration class."""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ['true', '1', 'yes']
    
    # Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'password'
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'virtual_tryon_db'
    
    # URL-encode the password to handle special characters
    ENCODED_PASSWORD = quote_plus(MYSQL_PASSWORD)
    
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{ENCODED_PASSWORD}@"
        f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() in ['true', '1']
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'user_uploads')
    CLOTHING_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'clothing_items')
    
    # AI Model Configuration
    MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'models', 'trained')
    MEDIAPIPE_MODEL_COMPLEXITY = 1
    MEDIAPIPE_MIN_DETECTION_CONFIDENCE = 0.5
    MEDIAPIPE_MIN_TRACKING_CONFIDENCE = 0.5
    
    # TensorFlow Configuration
    TF_CPP_MIN_LOG_LEVEL = '2'  # Suppress TensorFlow warnings
    GPU_MEMORY_GROWTH = True
    
    # PIFuHD Configuration
    PIFUHD_CHECKPOINT_PATH = os.path.join(MODEL_PATH, 'pifuhd_checkpoint.pth')
    PIFUHD_RESOLUTION = 512
    
    # VITON Configuration
    VITON_CHECKPOINT_PATH = os.path.join(MODEL_PATH, 'viton_checkpoint.pth')
    VITON_IMAGE_SIZE = (256, 192)
    
    # Size Estimation Configuration
    SIZE_MODEL_PATH = os.path.join(MODEL_PATH, 'size_estimation_model.pkl')
    SIZE_SCALER_PATH = os.path.join(MODEL_PATH, 'size_scaler.pkl')
    
    # Camera Configuration
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FPS = 30
    
    # Security Configuration
    JWT_EXPIRATION_DELTA = timedelta(hours=24)
    BCRYPT_LOG_ROUNDS = 12
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = 'virtual_tryon.log'

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    
    # Use environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for production environment")

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
